#!/usr/bin/env python3
"""
Agent Army Monitoring and Logging System
Tracks agent communications, performance, and health
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict, deque
import threading

class AgentMonitor:
    """Monitor agent communications and performance"""
    
    def __init__(self):
        self.logs_dir = Path("/home/dhara/PensionID/agent-army-trial/.claude/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics storage
        self.metrics = {
            "agent_activities": defaultdict(list),
            "handoff_metrics": [],
            "task_metrics": [],
            "error_logs": [],
            "performance_metrics": defaultdict(list)
        }
        
        # Real-time monitoring
        self.active_agents = {}
        self.task_queue = deque(maxlen=100)
        self.recent_handoffs = deque(maxlen=50)
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def log_agent_activity(self, agent: str, action: str, details: Dict):
        """Log agent activity"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "details": details
        }
        
        self.metrics["agent_activities"][agent].append(activity)
        self._write_log("agent-activity", activity)
        
        # Update active agent status
        self.active_agents[agent] = {
            "last_activity": datetime.now(),
            "status": "active",
            "current_task": details.get("task_id")
        }
    
    def log_handoff(self, from_agent: str, to_agent: str, task_id: str, 
                    success: bool, duration_ms: int):
        """Log agent handoff metrics"""
        handoff = {
            "timestamp": datetime.now().isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_id": task_id,
            "success": success,
            "duration_ms": duration_ms
        }
        
        self.metrics["handoff_metrics"].append(handoff)
        self.recent_handoffs.append(handoff)
        self._write_log("handoffs", handoff)
    
    def log_task_completion(self, task_id: str, agent: str, duration_minutes: int, 
                            status: str, story_points: int = 0):
        """Log task completion metrics"""
        task_metric = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "completed_by": agent,
            "duration_minutes": duration_minutes,
            "status": status,
            "story_points": story_points
        }
        
        self.metrics["task_metrics"].append(task_metric)
        self._write_log("task-completions", task_metric)
    
    def log_error(self, agent: str, error_type: str, error_message: str, 
                  context: Optional[Dict] = None):
        """Log errors and issues"""
        error = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        self.metrics["error_logs"].append(error)
        self._write_log("errors", error)
    
    def log_performance(self, agent: str, operation: str, duration_ms: int, 
                       memory_mb: float = 0):
        """Log performance metrics"""
        perf_metric = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "operation": operation,
            "duration_ms": duration_ms,
            "memory_mb": memory_mb
        }
        
        self.metrics["performance_metrics"][agent].append(perf_metric)
        self._write_log("performance", perf_metric)
    
    def get_agent_health(self) -> Dict:
        """Get current health status of all agents"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "overall_health": "healthy"
        }
        
        now = datetime.now()
        
        for agent, status in self.active_agents.items():
            last_activity = status["last_activity"]
            time_since_activity = (now - last_activity).seconds
            
            if time_since_activity < 300:  # Active in last 5 minutes
                agent_health = "active"
            elif time_since_activity < 900:  # Active in last 15 minutes
                agent_health = "idle"
            else:
                agent_health = "inactive"
            
            health["agents"][agent] = {
                "status": agent_health,
                "last_activity": last_activity.isoformat(),
                "current_task": status.get("current_task")
            }
        
        # Check for errors
        recent_errors = [e for e in self.metrics["error_logs"] 
                        if datetime.fromisoformat(e["timestamp"]) > now - timedelta(hours=1)]
        
        if len(recent_errors) > 10:
            health["overall_health"] = "degraded"
        elif len(recent_errors) > 20:
            health["overall_health"] = "critical"
        
        return health
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_activities": sum(len(activities) for activities in self.metrics["agent_activities"].values()),
            "total_handoffs": len(self.metrics["handoff_metrics"]),
            "successful_handoffs": sum(1 for h in self.metrics["handoff_metrics"] if h["success"]),
            "total_tasks_completed": len(self.metrics["task_metrics"]),
            "total_errors": len(self.metrics["error_logs"]),
            "active_agents": len([a for a, s in self.active_agents.items() 
                                 if (datetime.now() - s["last_activity"]).seconds < 300]),
            "agent_breakdown": {}
        }
        
        # Agent-specific metrics
        for agent, activities in self.metrics["agent_activities"].items():
            summary["agent_breakdown"][agent] = {
                "total_activities": len(activities),
                "errors": sum(1 for e in self.metrics["error_logs"] if e["agent"] == agent),
                "tasks_completed": sum(1 for t in self.metrics["task_metrics"] if t["completed_by"] == agent)
            }
        
        # Calculate success rates
        if summary["total_handoffs"] > 0:
            summary["handoff_success_rate"] = (summary["successful_handoffs"] / summary["total_handoffs"]) * 100
        else:
            summary["handoff_success_rate"] = 100
        
        return summary
    
    def get_agent_utilization(self) -> Dict:
        """Calculate agent utilization metrics"""
        utilization = {
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }
        
        for agent, activities in self.metrics["agent_activities"].items():
            if not activities:
                utilization["agents"][agent] = {"utilization": 0, "tasks": 0}
                continue
            
            # Calculate time working
            first_activity = datetime.fromisoformat(activities[0]["timestamp"])
            last_activity = datetime.fromisoformat(activities[-1]["timestamp"])
            total_time = (last_activity - first_activity).total_seconds() / 3600  # hours
            
            # Count tasks
            tasks = sum(1 for t in self.metrics["task_metrics"] if t["completed_by"] == agent)
            
            utilization["agents"][agent] = {
                "utilization": min(100, (len(activities) / max(1, total_time)) * 10),  # activities per hour * 10
                "tasks": tasks,
                "avg_task_duration": sum(t["duration_minutes"] for t in self.metrics["task_metrics"] 
                                        if t["completed_by"] == agent) / max(1, tasks)
            }
        
        return utilization
    
    def _write_log(self, log_type: str, data: Dict):
        """Write log entry to file"""
        log_file = self.logs_dir / f"{log_type}-{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Check for idle agents
                now = datetime.now()
                for agent, status in self.active_agents.items():
                    if (now - status["last_activity"]).seconds > 600:  # 10 minutes idle
                        self.log_agent_activity(agent, "idle_detected", {
                            "idle_duration_seconds": (now - status["last_activity"]).seconds
                        })
                
                # Write periodic summary
                if now.minute % 15 == 0:  # Every 15 minutes
                    summary = self.get_metrics_summary()
                    self._write_log("summary", summary)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.log_error("monitor", "monitoring_error", str(e))
    
    def generate_report(self) -> str:
        """Generate monitoring report"""
        health = self.get_agent_health()
        summary = self.get_metrics_summary()
        utilization = self.get_agent_utilization()
        
        report = f"""
# Agent Army Monitoring Report
Generated: {datetime.now().isoformat()}

## System Health
Overall Status: {health['overall_health']}
Active Agents: {summary['active_agents']}

## Activity Summary
- Total Activities: {summary['total_activities']}
- Tasks Completed: {summary['total_tasks_completed']}
- Total Handoffs: {summary['total_handoffs']}
- Handoff Success Rate: {summary['handoff_success_rate']:.1f}%
- Total Errors: {summary['total_errors']}

## Agent Utilization
"""
        
        for agent, util in utilization["agents"].items():
            report += f"""
### {agent}
- Utilization: {util['utilization']:.1f}%
- Tasks Completed: {util['tasks']}
- Avg Task Duration: {util.get('avg_task_duration', 0):.1f} minutes
"""
        
        # Recent errors
        if self.metrics["error_logs"]:
            report += "\n## Recent Errors\n"
            for error in self.metrics["error_logs"][-5:]:
                report += f"- [{error['timestamp']}] {error['agent']}: {error['error_message']}\n"
        
        return report
    
    def shutdown(self):
        """Shutdown monitoring"""
        self.monitoring = False
        self.monitor_thread.join(timeout=5)
        
        # Write final summary
        final_summary = {
            "shutdown_time": datetime.now().isoformat(),
            "final_metrics": self.get_metrics_summary()
        }
        self._write_log("shutdown", final_summary)

# Global monitor instance
monitor = AgentMonitor()

def log_activity(agent: str, action: str, details: Dict = None):
    """Convenience function for logging agent activity"""
    monitor.log_agent_activity(agent, action, details or {})

def log_handoff(from_agent: str, to_agent: str, task_id: str, success: bool = True):
    """Convenience function for logging handoffs"""
    monitor.log_handoff(from_agent, to_agent, task_id, success, 0)

def log_error(agent: str, error: str):
    """Convenience function for logging errors"""
    monitor.log_error(agent, "general_error", error)

def get_health():
    """Get system health"""
    return monitor.get_agent_health()

def get_report():
    """Get monitoring report"""
    return monitor.generate_report()

if __name__ == "__main__":
    # Test monitoring
    print("Starting Agent Monitor...")
    
    # Simulate some activity
    log_activity("scrum-master", "sprint_planning", {"sprint": 1})
    log_activity("requirements-analyst", "gathering_requirements", {"stories": 5})
    log_handoff("scrum-master", "requirements-analyst", "task-001", True)
    log_activity("tech-lead", "task_assignment", {"tasks": 10})
    
    time.sleep(2)
    
    # Generate report
    print(get_report())
    
    # Shutdown
    monitor.shutdown()
    print("Monitor shutdown complete.")