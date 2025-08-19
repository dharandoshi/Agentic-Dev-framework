#!/usr/bin/env python3
"""
Agent Army Error Monitoring and Alerting System
Real-time monitoring, error tracking, and notification system for Agent Army
"""

import os
import sys
import json
import time
import logging
import smtplib
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AgentArmyMonitor')

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"  # System failure, immediate action required
    HIGH = "high"          # Major issue, needs attention soon
    MEDIUM = "medium"      # Notable issue, should be addressed
    LOW = "low"            # Minor issue, informational
    INFO = "info"          # Informational only

class EventType(Enum):
    """Types of events to monitor"""
    AGENT_ERROR = "agent_error"
    MCP_FAILURE = "mcp_failure"
    HOOK_ERROR = "hook_error"
    WORKFLOW_TIMEOUT = "workflow_timeout"
    HANDOFF_FAILURE = "handoff_failure"
    COMMUNICATION_ERROR = "communication_error"
    RESOURCE_LIMIT = "resource_limit"
    SECURITY_VIOLATION = "security_violation"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SYSTEM_HEALTH = "system_health"

@dataclass
class MonitoringEvent:
    """Represents a monitoring event"""
    timestamp: datetime
    event_type: EventType
    severity: AlertSeverity
    component: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    error_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate unique error ID if not provided"""
        if not self.error_id:
            content = f"{self.timestamp}{self.event_type}{self.component}{self.message}"
            self.error_id = hashlib.md5(content.encode()).hexdigest()[:8]

@dataclass
class AlertRule:
    """Defines when to trigger alerts"""
    name: str
    description: str
    event_type: EventType
    severity_threshold: AlertSeverity
    frequency_threshold: int  # Number of events
    time_window: int  # Seconds
    action: str  # "notify", "log", "escalate"
    enabled: bool = True

class NotificationChannel:
    """Base class for notification channels"""
    
    def send(self, event: MonitoringEvent, message: str) -> bool:
        """Send notification through this channel"""
        raise NotImplementedError

class FileNotificationChannel(NotificationChannel):
    """Write notifications to file"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
    def send(self, event: MonitoringEvent, message: str) -> bool:
        """Write notification to file"""
        try:
            with open(self.file_path, 'a') as f:
                notification = {
                    "timestamp": event.timestamp.isoformat(),
                    "error_id": event.error_id,
                    "severity": event.severity.value,
                    "type": event.event_type.value,
                    "component": event.component,
                    "message": message,
                    "details": event.details
                }
                f.write(json.dumps(notification) + '\n')
            return True
        except Exception as e:
            logger.error(f"Failed to write notification: {e}")
            return False

class ConsoleNotificationChannel(NotificationChannel):
    """Print notifications to console"""
    
    COLORS = {
        AlertSeverity.CRITICAL: '\033[91m',  # Red
        AlertSeverity.HIGH: '\033[93m',      # Yellow
        AlertSeverity.MEDIUM: '\033[94m',    # Blue
        AlertSeverity.LOW: '\033[92m',       # Green
        AlertSeverity.INFO: '\033[96m',      # Cyan
    }
    RESET = '\033[0m'
    
    def send(self, event: MonitoringEvent, message: str) -> bool:
        """Print colored notification to console"""
        color = self.COLORS.get(event.severity, '')
        print(f"{color}[{event.severity.value.upper()}] {message}{self.RESET}")
        return True

class WebhookNotificationChannel(NotificationChannel):
    """Send notifications to webhook (Slack, Discord, etc.)"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send(self, event: MonitoringEvent, message: str) -> bool:
        """Send notification to webhook"""
        try:
            import requests
            
            payload = {
                "text": f"🚨 Agent Army Alert",
                "attachments": [{
                    "color": self._get_color(event.severity),
                    "fields": [
                        {"title": "Severity", "value": event.severity.value, "short": True},
                        {"title": "Component", "value": event.component, "short": True},
                        {"title": "Type", "value": event.event_type.value, "short": True},
                        {"title": "Error ID", "value": event.error_id, "short": True},
                        {"title": "Message", "value": message, "short": False},
                        {"title": "Time", "value": event.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                    ]
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            return response.status_code == 200
            
        except ImportError:
            logger.warning("requests library not available for webhook notifications")
            return False
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
            
    def _get_color(self, severity: AlertSeverity) -> str:
        """Get color for severity level"""
        colors = {
            AlertSeverity.CRITICAL: "#FF0000",  # Red
            AlertSeverity.HIGH: "#FF9900",      # Orange
            AlertSeverity.MEDIUM: "#FFFF00",    # Yellow
            AlertSeverity.LOW: "#00FF00",       # Green
            AlertSeverity.INFO: "#0099FF",      # Blue
        }
        return colors.get(severity, "#808080")

class AgentArmyMonitor:
    """Main monitoring system for Agent Army"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.claude_dir = self.project_root / ".claude"
        self.logs_dir = self.claude_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Event storage
        self.events: deque = deque(maxlen=10000)  # Keep last 10k events
        self.event_counts: Dict[EventType, Dict[AlertSeverity, int]] = defaultdict(lambda: defaultdict(int))
        
        # Alert rules
        self.alert_rules: List[AlertRule] = []
        self.load_alert_rules()
        
        # Notification channels
        self.notification_channels: List[NotificationChannel] = []
        self.setup_notification_channels()
        
        # Monitoring threads
        self.monitoring_active = False
        self.monitoring_threads: List[threading.Thread] = []
        
        # Performance metrics
        self.metrics = {
            "events_processed": 0,
            "alerts_triggered": 0,
            "notifications_sent": 0,
            "errors_detected": 0
        }
        
    def load_alert_rules(self):
        """Load alert rules configuration"""
        self.alert_rules = [
            # Critical alerts
            AlertRule(
                name="mcp_server_failure",
                description="MCP server connection failure",
                event_type=EventType.MCP_FAILURE,
                severity_threshold=AlertSeverity.CRITICAL,
                frequency_threshold=1,
                time_window=60,
                action="escalate"
            ),
            AlertRule(
                name="security_violation",
                description="Security violation detected",
                event_type=EventType.SECURITY_VIOLATION,
                severity_threshold=AlertSeverity.CRITICAL,
                frequency_threshold=1,
                time_window=1,
                action="escalate"
            ),
            
            # High priority alerts
            AlertRule(
                name="workflow_timeout",
                description="Workflow execution timeout",
                event_type=EventType.WORKFLOW_TIMEOUT,
                severity_threshold=AlertSeverity.HIGH,
                frequency_threshold=2,
                time_window=300,
                action="notify"
            ),
            AlertRule(
                name="agent_errors",
                description="Multiple agent errors",
                event_type=EventType.AGENT_ERROR,
                severity_threshold=AlertSeverity.HIGH,
                frequency_threshold=5,
                time_window=300,
                action="notify"
            ),
            
            # Medium priority alerts
            AlertRule(
                name="handoff_failures",
                description="Agent handoff failures",
                event_type=EventType.HANDOFF_FAILURE,
                severity_threshold=AlertSeverity.MEDIUM,
                frequency_threshold=3,
                time_window=600,
                action="log"
            ),
            AlertRule(
                name="performance_issues",
                description="Performance degradation",
                event_type=EventType.PERFORMANCE_DEGRADATION,
                severity_threshold=AlertSeverity.MEDIUM,
                frequency_threshold=5,
                time_window=900,
                action="notify"
            ),
            
            # Low priority alerts
            AlertRule(
                name="communication_warnings",
                description="Communication issues",
                event_type=EventType.COMMUNICATION_ERROR,
                severity_threshold=AlertSeverity.LOW,
                frequency_threshold=10,
                time_window=1800,
                action="log"
            ),
        ]
        
    def setup_notification_channels(self):
        """Setup notification channels"""
        # Always add file and console channels
        self.notification_channels.append(
            FileNotificationChannel(self.logs_dir / "alerts.jsonl")
        )
        self.notification_channels.append(
            ConsoleNotificationChannel()
        )
        
        # Add webhook if configured
        webhook_url = os.environ.get("AGENT_ARMY_WEBHOOK_URL")
        if webhook_url:
            self.notification_channels.append(
                WebhookNotificationChannel(webhook_url)
            )
            
    def add_event(self, event: MonitoringEvent):
        """Add monitoring event and check alert rules"""
        self.events.append(event)
        self.event_counts[event.event_type][event.severity] += 1
        self.metrics["events_processed"] += 1
        
        if event.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            self.metrics["errors_detected"] += 1
            
        # Check alert rules
        self.check_alert_rules(event)
        
        # Log event
        self._log_event(event)
        
    def check_alert_rules(self, event: MonitoringEvent):
        """Check if event triggers any alert rules"""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
                
            if rule.event_type != event.event_type:
                continue
                
            # Check severity threshold
            if self._compare_severity(event.severity, rule.severity_threshold) < 0:
                continue
                
            # Check frequency threshold
            recent_events = self._get_recent_events(
                rule.event_type,
                rule.time_window
            )
            
            if len(recent_events) >= rule.frequency_threshold:
                self.trigger_alert(rule, event, recent_events)
                
    def trigger_alert(self, rule: AlertRule, event: MonitoringEvent, recent_events: List[MonitoringEvent]):
        """Trigger alert based on rule"""
        self.metrics["alerts_triggered"] += 1
        
        message = self._format_alert_message(rule, event, recent_events)
        
        if rule.action == "escalate":
            self._escalate_alert(event, message)
        elif rule.action == "notify":
            self._send_notifications(event, message)
        elif rule.action == "log":
            self._log_alert(event, message)
            
    def _format_alert_message(self, rule: AlertRule, event: MonitoringEvent, recent_events: List[MonitoringEvent]) -> str:
        """Format alert message"""
        return (
            f"Alert: {rule.description}\n"
            f"Component: {event.component}\n"
            f"Message: {event.message}\n"
            f"Frequency: {len(recent_events)} events in {rule.time_window}s\n"
            f"Error ID: {event.error_id}"
        )
        
    def _escalate_alert(self, event: MonitoringEvent, message: str):
        """Escalate critical alert"""
        # Send to all channels
        self._send_notifications(event, f"🚨 CRITICAL ALERT 🚨\n{message}")
        
        # Also create escalation file
        escalation_file = self.logs_dir / f"escalation_{event.error_id}.json"
        with open(escalation_file, 'w') as f:
            json.dump({
                "timestamp": event.timestamp.isoformat(),
                "event": {
                    "type": event.event_type.value,
                    "severity": event.severity.value,
                    "component": event.component,
                    "message": event.message,
                    "details": event.details
                },
                "alert_message": message
            }, f, indent=2)
            
    def _send_notifications(self, event: MonitoringEvent, message: str):
        """Send notifications through all channels"""
        for channel in self.notification_channels:
            try:
                if channel.send(event, message):
                    self.metrics["notifications_sent"] += 1
            except Exception as e:
                logger.error(f"Failed to send notification through {channel.__class__.__name__}: {e}")
                
    def _log_alert(self, event: MonitoringEvent, message: str):
        """Log alert to file"""
        alert_log = self.logs_dir / "alerts.log"
        with open(alert_log, 'a') as f:
            f.write(f"[{event.timestamp}] {message}\n")
            
    def _log_event(self, event: MonitoringEvent):
        """Log event to file"""
        event_log = self.logs_dir / "events.jsonl"
        with open(event_log, 'a') as f:
            f.write(json.dumps({
                "timestamp": event.timestamp.isoformat(),
                "error_id": event.error_id,
                "type": event.event_type.value,
                "severity": event.severity.value,
                "component": event.component,
                "message": event.message,
                "details": event.details
            }) + '\n')
            
    def _get_recent_events(self, event_type: EventType, time_window: int) -> List[MonitoringEvent]:
        """Get events of specified type within time window"""
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        return [
            e for e in self.events
            if e.event_type == event_type and e.timestamp >= cutoff_time
        ]
        
    def _compare_severity(self, sev1: AlertSeverity, sev2: AlertSeverity) -> int:
        """Compare severity levels (-1: less, 0: equal, 1: greater)"""
        severity_order = {
            AlertSeverity.INFO: 0,
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4
        }
        
        val1 = severity_order.get(sev1, 0)
        val2 = severity_order.get(sev2, 0)
        
        if val1 < val2:
            return -1
        elif val1 > val2:
            return 1
        else:
            return 0
            
    def monitor_mcp_servers(self):
        """Monitor MCP server health"""
        while self.monitoring_active:
            try:
                # Check MCP server status
                result = subprocess.run(
                    ["claude", "mcp", "list"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode != 0:
                    self.add_event(MonitoringEvent(
                        timestamp=datetime.now(),
                        event_type=EventType.MCP_FAILURE,
                        severity=AlertSeverity.CRITICAL,
                        component="MCP",
                        message="Failed to query MCP server status",
                        details={"stderr": result.stderr}
                    ))
                else:
                    # Check each server
                    expected_servers = ["workspace", "docs", "execution", "coord", "validation"]
                    for server in expected_servers:
                        if server not in result.stdout:
                            self.add_event(MonitoringEvent(
                                timestamp=datetime.now(),
                                event_type=EventType.MCP_FAILURE,
                                severity=AlertSeverity.HIGH,
                                component=f"MCP/{server}",
                                message=f"MCP server '{server}' not responding",
                                details={"server": server}
                            ))
                            
            except subprocess.TimeoutExpired:
                self.add_event(MonitoringEvent(
                    timestamp=datetime.now(),
                    event_type=EventType.MCP_FAILURE,
                    severity=AlertSeverity.HIGH,
                    component="MCP",
                    message="MCP server query timeout",
                    details={"timeout": 15}
                ))
            except Exception as e:
                logger.error(f"Error monitoring MCP servers: {e}")
                
            time.sleep(60)  # Check every minute
            
    def monitor_log_files(self):
        """Monitor log files for errors"""
        log_patterns = {
            "ERROR": AlertSeverity.HIGH,
            "CRITICAL": AlertSeverity.CRITICAL,
            "WARNING": AlertSeverity.MEDIUM,
            "TIMEOUT": AlertSeverity.HIGH,
            "FAILED": AlertSeverity.HIGH,
            "EXCEPTION": AlertSeverity.HIGH
        }
        
        while self.monitoring_active:
            try:
                # Monitor communication logs
                comm_log = self.logs_dir / "communication.jsonl"
                if comm_log.exists():
                    # Read last 100 lines
                    with open(comm_log, 'r') as f:
                        lines = f.readlines()[-100:]
                        
                    for line in lines:
                        try:
                            entry = json.loads(line)
                            for pattern, severity in log_patterns.items():
                                if pattern in entry.get("message", "").upper():
                                    self.add_event(MonitoringEvent(
                                        timestamp=datetime.now(),
                                        event_type=EventType.COMMUNICATION_ERROR,
                                        severity=severity,
                                        component="Communication",
                                        message=f"Log pattern '{pattern}' detected",
                                        details=entry
                                    ))
                        except json.JSONDecodeError:
                            pass
                            
            except Exception as e:
                logger.error(f"Error monitoring log files: {e}")
                
            time.sleep(30)  # Check every 30 seconds
            
    def monitor_system_resources(self):
        """Monitor system resource usage"""
        while self.monitoring_active:
            try:
                import psutil
                
                # Check CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > 90:
                    self.add_event(MonitoringEvent(
                        timestamp=datetime.now(),
                        event_type=EventType.RESOURCE_LIMIT,
                        severity=AlertSeverity.HIGH,
                        component="System",
                        message=f"High CPU usage: {cpu_percent}%",
                        details={"cpu_percent": cpu_percent}
                    ))
                    
                # Check memory usage
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    self.add_event(MonitoringEvent(
                        timestamp=datetime.now(),
                        event_type=EventType.RESOURCE_LIMIT,
                        severity=AlertSeverity.HIGH,
                        component="System",
                        message=f"High memory usage: {memory.percent}%",
                        details={
                            "memory_percent": memory.percent,
                            "available_mb": memory.available / (1024 * 1024)
                        }
                    ))
                    
                # Check disk usage
                disk = psutil.disk_usage(self.project_root)
                if disk.percent > 90:
                    self.add_event(MonitoringEvent(
                        timestamp=datetime.now(),
                        event_type=EventType.RESOURCE_LIMIT,
                        severity=AlertSeverity.MEDIUM,
                        component="System",
                        message=f"High disk usage: {disk.percent}%",
                        details={
                            "disk_percent": disk.percent,
                            "free_gb": disk.free / (1024 * 1024 * 1024)
                        }
                    ))
                    
            except ImportError:
                logger.info("psutil not available for resource monitoring")
                break
            except Exception as e:
                logger.error(f"Error monitoring system resources: {e}")
                
            time.sleep(60)  # Check every minute
            
    def start_monitoring(self):
        """Start all monitoring threads"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
            
        self.monitoring_active = True
        
        # Start monitoring threads
        monitors = [
            ("MCP Monitor", self.monitor_mcp_servers),
            ("Log Monitor", self.monitor_log_files),
            ("Resource Monitor", self.monitor_system_resources)
        ]
        
        for name, func in monitors:
            thread = threading.Thread(target=func, name=name, daemon=True)
            thread.start()
            self.monitoring_threads.append(thread)
            logger.info(f"Started {name}")
            
        logger.info("Agent Army monitoring system started")
        
    def stop_monitoring(self):
        """Stop all monitoring threads"""
        self.monitoring_active = False
        
        # Wait for threads to stop
        for thread in self.monitoring_threads:
            thread.join(timeout=5)
            
        self.monitoring_threads.clear()
        logger.info("Agent Army monitoring system stopped")
        
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate current status report"""
        # Count events by type and severity
        event_summary = {}
        for event_type in EventType:
            event_summary[event_type.value] = {}
            for severity in AlertSeverity:
                count = self.event_counts[event_type][severity]
                if count > 0:
                    event_summary[event_type.value][severity.value] = count
                    
        # Get recent critical events
        recent_critical = [
            {
                "timestamp": e.timestamp.isoformat(),
                "component": e.component,
                "message": e.message,
                "error_id": e.error_id
            }
            for e in self.events
            if e.severity == AlertSeverity.CRITICAL and 
            e.timestamp >= datetime.now() - timedelta(hours=1)
        ]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "metrics": self.metrics,
            "event_summary": event_summary,
            "recent_critical_events": recent_critical,
            "total_events": len(self.events),
            "active_monitors": len(self.monitoring_threads),
            "notification_channels": len(self.notification_channels)
        }
        
    def print_status(self):
        """Print current monitoring status"""
        report = self.generate_status_report()
        
        print("\n📊 Agent Army Monitoring Status")
        print("=" * 50)
        print(f"Status: {'🟢 Active' if report['monitoring_active'] else '🔴 Inactive'}")
        print(f"Total Events: {report['total_events']}")
        print(f"Alerts Triggered: {report['metrics']['alerts_triggered']}")
        print(f"Notifications Sent: {report['metrics']['notifications_sent']}")
        print(f"Errors Detected: {report['metrics']['errors_detected']}")
        
        if report['recent_critical_events']:
            print(f"\n🚨 Recent Critical Events:")
            for event in report['recent_critical_events'][:5]:
                print(f"  • [{event['error_id']}] {event['component']}: {event['message']}")
                
        print(f"\n📡 Active Monitors: {report['active_monitors']}")
        print(f"📢 Notification Channels: {report['notification_channels']}")

def main():
    """Main monitoring execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Army Monitoring System")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--status", action="store_true", help="Show monitoring status")
    parser.add_argument("--test", action="store_true", help="Test alert system")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    monitor = AgentArmyMonitor()
    
    if args.test:
        print("🧪 Testing alert system...")
        
        # Test different severity levels
        test_events = [
            MonitoringEvent(
                timestamp=datetime.now(),
                event_type=EventType.MCP_FAILURE,
                severity=AlertSeverity.CRITICAL,
                component="Test",
                message="Test critical alert"
            ),
            MonitoringEvent(
                timestamp=datetime.now(),
                event_type=EventType.AGENT_ERROR,
                severity=AlertSeverity.HIGH,
                component="Test",
                message="Test high severity alert"
            ),
            MonitoringEvent(
                timestamp=datetime.now(),
                event_type=EventType.COMMUNICATION_ERROR,
                severity=AlertSeverity.MEDIUM,
                component="Test",
                message="Test medium severity alert"
            ),
        ]
        
        for event in test_events:
            monitor.add_event(event)
            time.sleep(1)
            
        print("✅ Test alerts sent")
        
    elif args.status:
        monitor.print_status()
        
    elif args.start or args.daemon:
        monitor.start_monitoring()
        
        if args.daemon:
            print("🔄 Monitoring daemon started. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(60)
                    monitor.print_status()
            except KeyboardInterrupt:
                print("\n⏹️  Stopping monitoring...")
                monitor.stop_monitoring()
        else:
            print("✅ Monitoring started")
            monitor.print_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()