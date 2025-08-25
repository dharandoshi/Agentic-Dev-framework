#!/usr/bin/env python3
"""
Monitoring MCP Server - Real-time System Monitoring for Agent Army Framework

Provides monitoring capabilities including:
- Agent health and performance tracking
- Workflow progress monitoring
- System metrics and dashboards
- Alert management
- Performance analytics
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
from collections import defaultdict
import statistics

from mcp import types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio


# Alert Severity
class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Health Status
class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


# Metric Types
class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMING = "timing"


# Storage for server state
agent_health: Dict[str, Dict] = {}
workflow_status: Dict[str, Dict] = {}
system_metrics: Dict[str, Dict] = defaultdict(lambda: {"values": [], "type": MetricType.GAUGE})
alerts: List[Dict] = []
alert_rules: Dict[str, Dict] = {}
performance_data: Dict[str, List] = defaultdict(list)

# Persistence
data_dir = Path(__file__).parent.parent.parent / "data" / "monitoring"
data_dir.mkdir(parents=True, exist_ok=True)

# File paths
HEALTH_FILE = data_dir / "agent_health.json"
METRICS_FILE = data_dir / "system_metrics.json"
ALERTS_FILE = data_dir / "alerts.json"
ALERT_RULES_FILE = data_dir / "alert_rules.json"
PERFORMANCE_FILE = data_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"


def load_data():
    """Load persisted data from disk"""
    global agent_health, workflow_status, alerts, alert_rules
    
    try:
        if HEALTH_FILE.exists():
            with open(HEALTH_FILE, 'r') as f:
                agent_health = json.load(f)
        
        if ALERTS_FILE.exists():
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
        
        if ALERT_RULES_FILE.exists():
            with open(ALERT_RULES_FILE, 'r') as f:
                alert_rules = json.load(f)
                
    except Exception as e:
        print(f"Error loading monitoring data: {e}")


def save_health():
    """Save agent health data"""
    try:
        with open(HEALTH_FILE, 'w') as f:
            json.dump(agent_health, f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving health data: {e}")


def save_alerts():
    """Save alerts"""
    try:
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving alerts: {e}")


def save_alert_rules():
    """Save alert rules"""
    try:
        with open(ALERT_RULES_FILE, 'w') as f:
            json.dump(alert_rules, f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving alert rules: {e}")


def save_performance_data(data: Dict):
    """Append performance data to daily file"""
    try:
        with open(PERFORMANCE_FILE, 'a') as f:
            f.write(json.dumps(data, default=str) + '\n')
    except Exception as e:
        print(f"Error saving performance data: {e}")


def check_alert_conditions():
    """Check if any alert conditions are met"""
    triggered_alerts = []
    
    for rule_id, rule in alert_rules.items():
        if rule.get("enabled", True):
            metric = rule["metric"]
            threshold = rule["threshold"]
            condition = rule["condition"]
            
            # Get current metric value
            if metric in system_metrics:
                values = system_metrics[metric]["values"]
                if values:
                    current_value = values[-1]["value"]
                    
                    # Check condition
                    triggered = False
                    if condition == "greater_than" and current_value > threshold:
                        triggered = True
                    elif condition == "less_than" and current_value < threshold:
                        triggered = True
                    elif condition == "equals" and current_value == threshold:
                        triggered = True
                    
                    if triggered:
                        alert = {
                            "id": str(uuid.uuid4()),
                            "rule_id": rule_id,
                            "metric": metric,
                            "value": current_value,
                            "threshold": threshold,
                            "severity": rule.get("severity", AlertSeverity.MEDIUM),
                            "message": rule.get("message", f"Alert: {metric} {condition} {threshold}"),
                            "timestamp": datetime.now().isoformat()
                        }
                        triggered_alerts.append(alert)
                        alerts.append(alert)
    
    if triggered_alerts:
        save_alerts()
    
    return triggered_alerts


def calculate_agent_health(agent: str) -> str:
    """Calculate overall health status for an agent"""
    if agent not in agent_health:
        return HealthStatus.OFFLINE
    
    health = agent_health[agent]
    
    # Check last heartbeat
    if "last_heartbeat" in health:
        last_heartbeat = datetime.fromisoformat(health["last_heartbeat"])
        if datetime.now() - last_heartbeat > timedelta(minutes=5):
            return HealthStatus.OFFLINE
    
    # Check error rate
    if health.get("error_rate", 0) > 0.2:  # >20% errors
        return HealthStatus.UNHEALTHY
    elif health.get("error_rate", 0) > 0.05:  # >5% errors
        return HealthStatus.DEGRADED
    
    # Check response time
    if health.get("avg_response_time", 0) > 5000:  # >5s average
        return HealthStatus.DEGRADED
    
    return HealthStatus.HEALTHY


# Initialize server
server = Server("monitoring")

# Load persisted data
load_data()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available monitoring tools"""
    return [
        # Health Monitoring
        types.Tool(
            name="report_health",
            description="Report agent health status",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["healthy", "degraded", "unhealthy", "offline"],
                        "description": "Health status"
                    },
                    "metrics": {
                        "type": "object",
                        "properties": {
                            "cpu_usage": {"type": "number"},
                            "memory_usage": {"type": "number"},
                            "active_tasks": {"type": "integer"},
                            "error_rate": {"type": "number"},
                            "avg_response_time": {"type": "number"}
                        },
                        "description": "Health metrics"
                    }
                },
                "required": ["agent", "status"]
            }
        ),
        
        types.Tool(
            name="heartbeat",
            description="Send heartbeat signal from agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name"
                    },
                    "task_count": {
                        "type": "integer",
                        "description": "Number of active tasks"
                    }
                },
                "required": ["agent"]
            }
        ),
        
        # Metrics Reporting
        types.Tool(
            name="report_metric",
            description="Report a system metric",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Metric name"
                    },
                    "value": {
                        "type": "number",
                        "description": "Metric value"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["counter", "gauge", "histogram", "timing"],
                        "default": "gauge",
                        "description": "Metric type"
                    },
                    "tags": {
                        "type": "object",
                        "description": "Metric tags for categorization"
                    },
                    "unit": {
                        "type": "string",
                        "description": "Unit of measurement"
                    }
                },
                "required": ["name", "value"]
            }
        ),
        
        types.Tool(
            name="report_performance",
            description="Report performance metrics for an operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name"
                    },
                    "operation": {
                        "type": "string",
                        "description": "Operation name"
                    },
                    "duration_ms": {
                        "type": "integer",
                        "description": "Duration in milliseconds"
                    },
                    "success": {
                        "type": "boolean",
                        "description": "Whether operation succeeded"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional performance data"
                    }
                },
                "required": ["agent", "operation", "duration_ms", "success"]
            }
        ),
        
        # Workflow Monitoring
        types.Tool(
            name="update_workflow_status",
            description="Update workflow execution status",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["started", "running", "paused", "completed", "failed"],
                        "description": "Workflow status"
                    },
                    "current_step": {
                        "type": "string",
                        "description": "Current execution step"
                    },
                    "progress": {
                        "type": "integer",
                        "description": "Progress percentage (0-100)"
                    },
                    "agents_involved": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Agents involved in workflow"
                    }
                },
                "required": ["workflow_id", "status"]
            }
        ),
        
        # Alert Management
        types.Tool(
            name="create_alert_rule",
            description="Create an alert rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Rule name"
                    },
                    "metric": {
                        "type": "string",
                        "description": "Metric to monitor"
                    },
                    "condition": {
                        "type": "string",
                        "enum": ["greater_than", "less_than", "equals"],
                        "description": "Alert condition"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Threshold value"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "medium"
                    },
                    "message": {
                        "type": "string",
                        "description": "Alert message template"
                    }
                },
                "required": ["name", "metric", "condition", "threshold"]
            }
        ),
        
        types.Tool(
            name="trigger_alert",
            description="Manually trigger an alert",
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "message": {
                        "type": "string",
                        "description": "Alert message"
                    },
                    "source": {
                        "type": "string",
                        "description": "Alert source (agent or system)"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context"
                    }
                },
                "required": ["severity", "message", "source"]
            }
        ),
        
        # Query Tools
        types.Tool(
            name="get_system_dashboard",
            description="Get comprehensive system dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_agents": {
                        "type": "boolean",
                        "default": true,
                        "description": "Include agent health"
                    },
                    "include_workflows": {
                        "type": "boolean",
                        "default": true,
                        "description": "Include workflow status"
                    },
                    "include_metrics": {
                        "type": "boolean",
                        "default": true,
                        "description": "Include system metrics"
                    },
                    "include_alerts": {
                        "type": "boolean",
                        "default": true,
                        "description": "Include recent alerts"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_agent_health",
            description="Get health status for specific agent or all agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name (omit for all agents)"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_workflow_status",
            description="Get status of specific workflow or all workflows",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID (omit for all workflows)"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_metrics",
            description="Get system metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_name": {
                        "type": "string",
                        "description": "Specific metric name (omit for all)"
                    },
                    "time_range_minutes": {
                        "type": "integer",
                        "default": 60,
                        "description": "Time range in minutes"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_alerts",
            description="Get recent alerts",
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Filter by severity"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "description": "Maximum alerts to return"
                    },
                    "active_only": {
                        "type": "boolean",
                        "default": false,
                        "description": "Only show unresolved alerts"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_performance_report",
            description="Get performance report for agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name (omit for all)"
                    },
                    "time_range_hours": {
                        "type": "integer",
                        "default": 24,
                        "description": "Time range in hours"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution"""
    
    if name == "report_health":
        agent = arguments["agent"]
        agent_health[agent] = {
            "status": arguments["status"],
            "last_update": datetime.now().isoformat(),
            "metrics": arguments.get("metrics", {}),
            "calculated_health": calculate_agent_health(agent)
        }
        
        # Update metrics if provided
        if "metrics" in arguments:
            for metric_name, value in arguments["metrics"].items():
                system_metrics[f"agent.{agent}.{metric_name}"]["values"].append({
                    "value": value,
                    "timestamp": datetime.now().isoformat()
                })
        
        save_health()
        
        # Check for alerts
        triggered = check_alert_conditions()
        
        return [types.TextContent(
            type="text",
            text=f"Health reported for {agent}: {arguments['status']}"
        )]
    
    elif name == "heartbeat":
        agent = arguments["agent"]
        
        if agent not in agent_health:
            agent_health[agent] = {}
        
        agent_health[agent]["last_heartbeat"] = datetime.now().isoformat()
        agent_health[agent]["task_count"] = arguments.get("task_count", 0)
        agent_health[agent]["calculated_health"] = calculate_agent_health(agent)
        
        save_health()
        
        return [types.TextContent(
            type="text",
            text=f"Heartbeat received from {agent}"
        )]
    
    elif name == "report_metric":
        metric_name = arguments["name"]
        value = arguments["value"]
        metric_type = arguments.get("type", MetricType.GAUGE)
        
        # Store metric
        system_metrics[metric_name] = {
            "type": metric_type,
            "values": system_metrics[metric_name]["values"][-100:] + [{  # Keep last 100 values
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "tags": arguments.get("tags", {}),
                "unit": arguments.get("unit")
            }]
        }
        
        # Check alerts
        triggered = check_alert_conditions()
        
        return [types.TextContent(
            type="text",
            text=f"Metric recorded: {metric_name} = {value}{' ' + arguments.get('unit', '') if arguments.get('unit') else ''}"
        )]
    
    elif name == "report_performance":
        # Store performance data
        perf_data = {
            "agent": arguments["agent"],
            "operation": arguments["operation"],
            "duration_ms": arguments["duration_ms"],
            "success": arguments["success"],
            "metadata": arguments.get("metadata", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        performance_data[arguments["agent"]].append(perf_data)
        save_performance_data(perf_data)
        
        # Update metrics
        agent_key = f"agent.{arguments['agent']}.performance"
        system_metrics[agent_key]["values"].append({
            "value": arguments["duration_ms"],
            "timestamp": datetime.now().isoformat()
        })
        
        return [types.TextContent(
            type="text",
            text=f"Performance recorded: {arguments['operation']} took {arguments['duration_ms']}ms"
        )]
    
    elif name == "update_workflow_status":
        workflow_id = arguments["workflow_id"]
        
        workflow_status[workflow_id] = {
            "status": arguments["status"],
            "current_step": arguments.get("current_step"),
            "progress": arguments.get("progress", 0),
            "agents_involved": arguments.get("agents_involved", []),
            "last_update": datetime.now().isoformat()
        }
        
        # Record workflow metric
        system_metrics[f"workflow.{workflow_id}.progress"]["values"].append({
            "value": arguments.get("progress", 0),
            "timestamp": datetime.now().isoformat()
        })
        
        return [types.TextContent(
            type="text",
            text=f"Workflow {workflow_id} status: {arguments['status']}"
        )]
    
    elif name == "create_alert_rule":
        rule_id = str(uuid.uuid4())
        alert_rules[rule_id] = {
            "name": arguments["name"],
            "metric": arguments["metric"],
            "condition": arguments["condition"],
            "threshold": arguments["threshold"],
            "severity": arguments.get("severity", AlertSeverity.MEDIUM),
            "message": arguments.get("message"),
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        
        save_alert_rules()
        
        return [types.TextContent(
            type="text",
            text=f"Alert rule created: {arguments['name']} (ID: {rule_id})"
        )]
    
    elif name == "trigger_alert":
        alert = {
            "id": str(uuid.uuid4()),
            "severity": arguments["severity"],
            "message": arguments["message"],
            "source": arguments["source"],
            "context": arguments.get("context", {}),
            "timestamp": datetime.now().isoformat(),
            "manual": True
        }
        
        alerts.append(alert)
        save_alerts()
        
        return [types.TextContent(
            type="text",
            text=f"Alert triggered: {arguments['message']}"
        )]
    
    elif name == "get_system_dashboard":
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_agents": len(agent_health),
                "healthy_agents": sum(1 for a in agent_health.values() 
                                    if a.get("calculated_health") == HealthStatus.HEALTHY),
                "active_workflows": sum(1 for w in workflow_status.values() 
                                      if w.get("status") in ["started", "running"]),
                "recent_alerts": len([a for a in alerts[-10:] 
                                    if datetime.fromisoformat(a["timestamp"]) > 
                                    datetime.now() - timedelta(hours=1)])
            }
        }
        
        if arguments.get("include_agents", True):
            dashboard["agents"] = {
                agent: {
                    "health": health.get("calculated_health", HealthStatus.OFFLINE),
                    "last_heartbeat": health.get("last_heartbeat"),
                    "task_count": health.get("task_count", 0)
                }
                for agent, health in agent_health.items()
            }
        
        if arguments.get("include_workflows", True):
            dashboard["workflows"] = workflow_status
        
        if arguments.get("include_metrics", True):
            # Get recent metrics
            dashboard["metrics"] = {}
            for metric_name, metric_data in system_metrics.items():
                if metric_data["values"]:
                    recent_values = [v["value"] for v in metric_data["values"][-10:]]
                    dashboard["metrics"][metric_name] = {
                        "current": recent_values[-1] if recent_values else None,
                        "average": statistics.mean(recent_values) if recent_values else None,
                        "min": min(recent_values) if recent_values else None,
                        "max": max(recent_values) if recent_values else None
                    }
        
        if arguments.get("include_alerts", True):
            dashboard["recent_alerts"] = alerts[-10:]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(dashboard, indent=2, default=str)
        )]
    
    elif name == "get_agent_health":
        if arguments.get("agent"):
            health = agent_health.get(arguments["agent"], {})
            health["calculated_health"] = calculate_agent_health(arguments["agent"])
            result = {arguments["agent"]: health}
        else:
            result = {}
            for agent, health in agent_health.items():
                health["calculated_health"] = calculate_agent_health(agent)
                result[agent] = health
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    elif name == "get_workflow_status":
        if arguments.get("workflow_id"):
            result = workflow_status.get(arguments["workflow_id"], {})
        else:
            result = workflow_status
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    elif name == "get_metrics":
        time_range = arguments.get("time_range_minutes", 60)
        cutoff = datetime.now() - timedelta(minutes=time_range)
        
        result = {}
        
        if arguments.get("metric_name"):
            if arguments["metric_name"] in system_metrics:
                metric = system_metrics[arguments["metric_name"]]
                recent_values = [v for v in metric["values"] 
                               if datetime.fromisoformat(v["timestamp"]) > cutoff]
                result[arguments["metric_name"]] = {
                    "type": metric["type"],
                    "values": recent_values
                }
        else:
            for name, metric in system_metrics.items():
                recent_values = [v for v in metric["values"] 
                               if datetime.fromisoformat(v["timestamp"]) > cutoff]
                if recent_values:
                    result[name] = {
                        "type": metric["type"],
                        "values": recent_values
                    }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    elif name == "get_alerts":
        filtered_alerts = alerts
        
        if arguments.get("severity"):
            filtered_alerts = [a for a in filtered_alerts 
                             if a.get("severity") == arguments["severity"]]
        
        if arguments.get("active_only"):
            # Assuming alerts without "resolved" field are active
            filtered_alerts = [a for a in filtered_alerts 
                             if not a.get("resolved")]
        
        limit = arguments.get("limit", 50)
        filtered_alerts = filtered_alerts[-limit:]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(filtered_alerts, indent=2, default=str)
        )]
    
    elif name == "get_performance_report":
        hours = arguments.get("time_range_hours", 24)
        cutoff = datetime.now() - timedelta(hours=hours)
        
        report = {}
        
        if arguments.get("agent"):
            agent_perf = performance_data.get(arguments["agent"], [])
            recent = [p for p in agent_perf 
                     if datetime.fromisoformat(p["timestamp"]) > cutoff]
            
            if recent:
                durations = [p["duration_ms"] for p in recent]
                success_rate = sum(1 for p in recent if p["success"]) / len(recent)
                
                report[arguments["agent"]] = {
                    "total_operations": len(recent),
                    "success_rate": success_rate,
                    "avg_duration_ms": statistics.mean(durations),
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
                }
        else:
            for agent, perf_list in performance_data.items():
                recent = [p for p in perf_list 
                         if datetime.fromisoformat(p["timestamp"]) > cutoff]
                
                if recent:
                    durations = [p["duration_ms"] for p in recent]
                    success_rate = sum(1 for p in recent if p["success"]) / len(recent)
                    
                    report[agent] = {
                        "total_operations": len(recent),
                        "success_rate": success_rate,
                        "avg_duration_ms": statistics.mean(durations),
                        "min_duration_ms": min(durations),
                        "max_duration_ms": max(durations)
                    }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(report, indent=2, default=str)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the server using stdin/stdout streams"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="monitoring",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())