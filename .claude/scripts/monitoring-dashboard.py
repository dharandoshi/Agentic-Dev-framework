#!/usr/bin/env python3
"""
Agent Army Monitoring Dashboard
Real-time dashboard for system health and metrics visualization
"""

import os
import sys
import json
import time
import curses
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
import subprocess

class MonitoringDashboard:
    """Interactive monitoring dashboard for Agent Army"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.claude_dir = self.project_root / ".claude"
        self.logs_dir = self.claude_dir / "logs"
        
        # Dashboard data
        self.mcp_status = {}
        self.agent_status = {}
        self.recent_events = deque(maxlen=50)
        self.metrics = {
            "total_events": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0
        }
        self.last_update = datetime.now()
        
    def fetch_mcp_status(self) -> Dict[str, Any]:
        """Fetch current MCP server status"""
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                servers = ["workspace", "docs", "execution", "coord", "validation"]
                status = {}
                
                for server in servers:
                    if server in result.stdout:
                        if "Connected" in result.stdout:
                            status[server] = "🟢 Connected"
                        else:
                            status[server] = "🟡 Available"
                    else:
                        status[server] = "🔴 Offline"
                        
                return status
            else:
                return {server: "🔴 Error" for server in ["workspace", "docs", "execution", "coord", "validation"]}
                
        except Exception as e:
            return {"error": str(e)}
            
    def fetch_agent_status(self) -> Dict[str, Any]:
        """Fetch agent registry status"""
        registry_path = self.claude_dir / "agents" / "agent-registry.json"
        
        try:
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                    
                return {
                    "total_agents": registry.get("total_agents", 0),
                    "hierarchy_levels": len(registry.get("hierarchy", {})),
                    "coordination_rules": len(registry.get("coordination", {}))
                }
        except Exception as e:
            return {"error": str(e)}
            
        return {"total_agents": 0}
        
    def fetch_recent_events(self) -> List[Dict[str, Any]]:
        """Fetch recent monitoring events"""
        events = []
        events_file = self.logs_dir / "events.jsonl"
        
        if events_file.exists():
            try:
                with open(events_file, 'r') as f:
                    lines = f.readlines()[-20:]  # Last 20 events
                    
                for line in lines:
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass
                
        return events
        
    def fetch_system_metrics(self) -> Dict[str, Any]:
        """Fetch system resource metrics"""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage(self.project_root).percent,
                "processes": len(psutil.pids())
            }
        except ImportError:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "processes": 0
            }
            
    def update_data(self):
        """Update all dashboard data"""
        self.mcp_status = self.fetch_mcp_status()
        self.agent_status = self.fetch_agent_status()
        
        # Update events
        events = self.fetch_recent_events()
        for event in events:
            if event not in self.recent_events:
                self.recent_events.append(event)
                self.metrics["total_events"] += 1
                
                severity = event.get("severity", "").lower()
                if severity == "critical":
                    self.metrics["critical_count"] += 1
                elif severity == "high":
                    self.metrics["high_count"] += 1
                elif severity == "medium":
                    self.metrics["medium_count"] += 1
                elif severity == "low":
                    self.metrics["low_count"] += 1
                    
        self.last_update = datetime.now()
        
    def draw_dashboard(self, stdscr):
        """Draw the dashboard interface"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        
        # Define colors
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        while True:
            try:
                # Update data
                self.update_data()
                
                # Clear screen
                stdscr.clear()
                height, width = stdscr.getmaxyx()
                
                # Header
                header = "🚀 Agent Army Monitoring Dashboard"
                stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD)
                stdscr.addstr(1, 0, "=" * width)
                
                row = 3
                
                # System Overview
                stdscr.addstr(row, 0, "📊 System Overview", curses.A_BOLD)
                row += 1
                
                system_metrics = self.fetch_system_metrics()
                stdscr.addstr(row, 2, f"CPU: {system_metrics['cpu_percent']:.1f}%")
                stdscr.addstr(row, 20, f"Memory: {system_metrics['memory_percent']:.1f}%")
                stdscr.addstr(row, 40, f"Disk: {system_metrics['disk_percent']:.1f}%")
                row += 2
                
                # MCP Server Status
                stdscr.addstr(row, 0, "🔧 MCP Servers", curses.A_BOLD)
                row += 1
                
                col = 2
                for server, status in self.mcp_status.items():
                    if "🟢" in str(status):
                        color = curses.color_pair(1)
                    elif "🟡" in str(status):
                        color = curses.color_pair(2)
                    else:
                        color = curses.color_pair(3)
                        
                    stdscr.addstr(row, col, f"{server}: {status}", color)
                    col += 25
                    if col > width - 20:
                        row += 1
                        col = 2
                row += 2
                
                # Agent Status
                stdscr.addstr(row, 0, "🤖 Agent System", curses.A_BOLD)
                row += 1
                
                if "error" not in self.agent_status:
                    stdscr.addstr(row, 2, f"Total Agents: {self.agent_status.get('total_agents', 0)}")
                    stdscr.addstr(row, 25, f"Hierarchy Levels: {self.agent_status.get('hierarchy_levels', 0)}")
                    stdscr.addstr(row, 50, f"Coordination Rules: {self.agent_status.get('coordination_rules', 0)}")
                else:
                    stdscr.addstr(row, 2, f"Error: {self.agent_status['error']}", curses.color_pair(3))
                row += 2
                
                # Event Statistics
                stdscr.addstr(row, 0, "📈 Event Statistics", curses.A_BOLD)
                row += 1
                
                stdscr.addstr(row, 2, f"Total Events: {self.metrics['total_events']}")
                stdscr.addstr(row, 20, f"🔴 Critical: {self.metrics['critical_count']}", curses.color_pair(3))
                stdscr.addstr(row, 35, f"🟠 High: {self.metrics['high_count']}", curses.color_pair(2))
                stdscr.addstr(row, 48, f"🟡 Medium: {self.metrics['medium_count']}", curses.color_pair(2))
                stdscr.addstr(row, 63, f"🟢 Low: {self.metrics['low_count']}", curses.color_pair(1))
                row += 2
                
                # Recent Events
                stdscr.addstr(row, 0, "📜 Recent Events", curses.A_BOLD)
                row += 1
                
                # Display last few events
                event_display_count = min(len(self.recent_events), height - row - 3)
                if event_display_count > 0:
                    for i in range(event_display_count):
                        event = list(self.recent_events)[-1 - i]
                        
                        # Format event display
                        timestamp = event.get("timestamp", "")[:19]  # Just date and time
                        severity = event.get("severity", "info")
                        component = event.get("component", "Unknown")[:15]
                        message = event.get("message", "")[:width - 50]
                        
                        # Color based on severity
                        if severity == "critical":
                            color = curses.color_pair(3)
                        elif severity == "high":
                            color = curses.color_pair(2)
                        else:
                            color = curses.color_pair(5)
                            
                        event_line = f"{timestamp} [{severity:8}] {component:15} {message}"
                        if row < height - 2:
                            stdscr.addstr(row, 2, event_line[:width-3], color)
                            row += 1
                else:
                    stdscr.addstr(row, 2, "No recent events", curses.color_pair(5))
                    
                # Footer
                footer_row = height - 1
                update_time = self.last_update.strftime("%H:%M:%S")
                footer = f"Last Update: {update_time} | Press 'q' to quit | Press 'r' to refresh"
                stdscr.addstr(footer_row, 0, footer[:width-1], curses.A_DIM)
                
                # Refresh display
                stdscr.refresh()
                
                # Check for user input
                key = stdscr.getch()
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    continue  # Force refresh
                    
                # Auto-refresh every 5 seconds
                time.sleep(5)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                # Display error and continue
                stdscr.addstr(height // 2, 2, f"Error: {str(e)}", curses.color_pair(3))
                stdscr.refresh()
                time.sleep(2)
                
    def run(self):
        """Run the dashboard"""
        try:
            curses.wrapper(self.draw_dashboard)
        except Exception as e:
            print(f"Error running dashboard: {e}")
            
    def print_simple_status(self):
        """Print simple status (non-interactive)"""
        self.update_data()
        
        print("\n🚀 Agent Army Status Report")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # MCP Servers
        print("🔧 MCP Server Status:")
        for server, status in self.mcp_status.items():
            print(f"  {server:15} {status}")
        print()
        
        # Agent System
        print("🤖 Agent System:")
        if "error" not in self.agent_status:
            print(f"  Total Agents:       {self.agent_status.get('total_agents', 0)}")
            print(f"  Hierarchy Levels:   {self.agent_status.get('hierarchy_levels', 0)}")
            print(f"  Coordination Rules: {self.agent_status.get('coordination_rules', 0)}")
        else:
            print(f"  Error: {self.agent_status['error']}")
        print()
        
        # System Resources
        system_metrics = self.fetch_system_metrics()
        print("💻 System Resources:")
        print(f"  CPU Usage:    {system_metrics['cpu_percent']:.1f}%")
        print(f"  Memory Usage: {system_metrics['memory_percent']:.1f}%")
        print(f"  Disk Usage:   {system_metrics['disk_percent']:.1f}%")
        print(f"  Processes:    {system_metrics['processes']}")
        print()
        
        # Event Summary
        print("📈 Event Summary:")
        print(f"  Total Events:    {self.metrics['total_events']}")
        print(f"  Critical Events: {self.metrics['critical_count']}")
        print(f"  High Priority:   {self.metrics['high_count']}")
        print(f"  Medium Priority: {self.metrics['medium_count']}")
        print(f"  Low Priority:    {self.metrics['low_count']}")
        print()
        
        # Recent Critical Events
        critical_events = [e for e in self.recent_events if e.get("severity") == "critical"]
        if critical_events:
            print("🚨 Recent Critical Events:")
            for event in critical_events[-5:]:
                print(f"  [{event.get('timestamp', '')[:19]}] {event.get('component', 'Unknown')}: {event.get('message', '')}")

def main():
    """Main dashboard execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Army Monitoring Dashboard")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run interactive dashboard (default)")
    parser.add_argument("--simple", "-s", action="store_true", 
                       help="Print simple status report")
    
    args = parser.parse_args()
    
    dashboard = MonitoringDashboard()
    
    if args.simple:
        dashboard.print_simple_status()
    else:
        print("Starting Agent Army Monitoring Dashboard...")
        print("Press 'q' to quit, 'r' to refresh")
        time.sleep(2)
        dashboard.run()

if __name__ == "__main__":
    main()