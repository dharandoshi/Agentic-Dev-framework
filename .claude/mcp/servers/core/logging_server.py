#!/usr/bin/env python3
"""
Logging MCP Server - Centralized Logging for Agent Army Framework

Provides structured logging capabilities for all agents with:
- Agent-aware context tracking
- Task and workflow correlation
- Query and analysis capabilities
- Performance metrics collection
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

from mcp import types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio


# Log Levels
class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Log Entry Types
class LogType(str, Enum):
    EVENT = "event"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    HANDOFF = "handoff"
    DECISION = "decision"
    DELEGATION = "delegation"
    ERROR = "error"
    METRIC = "metric"
    TOOL_USE = "tool_use"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_EDIT = "file_edit"
    CODE_ANALYSIS = "code_analysis"
    API_CALL = "api_call"
    DISCOVERY = "discovery"
    VALIDATION = "validation"


# Storage for server state
logs: List[Dict] = []
task_logs: Dict[str, List[Dict]] = defaultdict(list)
agent_logs: Dict[str, List[Dict]] = defaultdict(list)
workflow_logs: Dict[str, List[Dict]] = defaultdict(list)
metrics: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "total_duration": 0, "errors": 0})

# Function to find project root
def find_project_root():
    """Find the project root by looking for .claude directory"""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.claude').exists():
            return current / '.claude'
        current = current.parent
    # Fallback to relative path from script location
    return Path(__file__).parent.parent.parent

# Persistence - with project detection
project_root = find_project_root()
data_dir = project_root / "mcp" / "data" / "logging"
data_dir.mkdir(parents=True, exist_ok=True)

# Load project config if exists
project_config = {}
project_json = project_root / "project.json"
if project_json.exists():
    with open(project_json) as f:
        project_config = json.load(f)

PROJECT_ID = project_config.get("project_id", "default")

# File paths - now project-aware
LOGS_FILE = data_dir / f"logs_{datetime.now().strftime('%Y%m%d')}.jsonl"
HUMAN_LOG_FILE = data_dir / f"agents_{datetime.now().strftime('%Y%m%d')}.log"  # Human-readable log
METRICS_FILE = data_dir / "metrics.json"
ACTIVE_TASKS_FILE = data_dir / "active_tasks.json"

# Active task tracking
active_tasks: Dict[str, Dict] = {}


def load_data():
    """Load persisted data from disk"""
    global logs, metrics, active_tasks
    
    try:
        # Load today's logs
        if LOGS_FILE.exists():
            logs = []
            with open(LOGS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        log_entry = json.loads(line)
                        logs.append(log_entry)
                        # Rebuild indices
                        if "task_id" in log_entry:
                            task_logs[log_entry["task_id"]].append(log_entry)
                        if "agent" in log_entry:
                            agent_logs[log_entry["agent"]].append(log_entry)
                        if "workflow_id" in log_entry:
                            workflow_logs[log_entry["workflow_id"]].append(log_entry)
        
        # Load metrics
        if METRICS_FILE.exists():
            with open(METRICS_FILE, 'r') as f:
                loaded_metrics = json.load(f)
                for key, value in loaded_metrics.items():
                    metrics[key] = value
        
        # Load active tasks
        if ACTIVE_TASKS_FILE.exists():
            with open(ACTIVE_TASKS_FILE, 'r') as f:
                active_tasks = json.load(f)
                
    except Exception as e:
        print(f"Error loading logging data: {e}")


def save_log_entry(entry: Dict):
    """Persist a single log entry in both JSON and human-readable format"""
    try:
        # Save JSON for programmatic access
        with open(LOGS_FILE, 'a') as f:
            f.write(json.dumps(entry, default=str) + '\n')
        
        # Save human-readable log
        with open(HUMAN_LOG_FILE, 'a') as f:
            f.write(format_human_log(entry) + '\n')
    except Exception as e:
        print(f"Error saving log entry: {e}")

def format_human_log(entry: Dict) -> str:
    """Format log entry for human readability"""
    timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    agent = entry.get('agent', 'SYSTEM').upper()
    level = entry.get('level', 'info').upper()
    log_type = entry.get('type', 'event').upper().replace('_', ' ')
    message = entry.get('message', '')
    task_id = entry.get('task_id', '')
    
    # Color codes for terminal (optional)
    level_colors = {
        'DEBUG': '\033[90m',  # Gray
        'INFO': '\033[0m',    # Default
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',   # Red
        'CRITICAL': '\033[91m\033[1m'  # Bold Red
    }
    reset = '\033[0m'
    
    # Format based on log type
    if entry.get('type') == LogType.FILE_READ:
        file_path = entry.get('context', {}).get('file_path', 'unknown')
        return f"[{timestamp}] {agent:15} | FILE READ     | {file_path}"
    elif entry.get('type') == LogType.FILE_WRITE:
        file_path = entry.get('context', {}).get('file_path', 'unknown')
        return f"[{timestamp}] {agent:15} | FILE WRITE    | {file_path}"
    elif entry.get('type') == LogType.FILE_EDIT:
        file_path = entry.get('context', {}).get('file_path', 'unknown')
        changes = entry.get('context', {}).get('changes', 'unknown')
        return f"[{timestamp}] {agent:15} | FILE EDIT     | {file_path} - {changes}"
    elif entry.get('type') == LogType.TOOL_USE:
        tool = entry.get('context', {}).get('tool', 'unknown')
        success = '✓' if entry.get('context', {}).get('success') else '✗'
        return f"[{timestamp}] {agent:15} | TOOL USE      | {tool} {success}"
    elif entry.get('type') == LogType.TASK_START:
        desc = entry.get('context', {}).get('description', message)[:60]
        return f"[{timestamp}] {agent:15} | TASK START    | {task_id}: {desc}"
    elif entry.get('type') == LogType.TASK_COMPLETE:
        result = entry.get('context', {}).get('result', 'unknown')
        return f"[{timestamp}] {agent:15} | TASK COMPLETE | {task_id}: {result}"
    elif entry.get('type') == LogType.HANDOFF:
        to_agent = entry.get('context', {}).get('to_agent', 'unknown')
        return f"[{timestamp}] {agent:15} | HANDOFF       | {task_id} → {to_agent}"
    elif entry.get('type') == LogType.DECISION:
        decision = entry.get('context', {}).get('decision', message)[:60]
        return f"[{timestamp}] {agent:15} | DECISION      | {decision}"
    elif entry.get('type') == LogType.ERROR:
        error = message[:80]
        return f"[{timestamp}] {agent:15} | ERROR         | {error}"
    else:
        # Default format
        msg = message[:80] if message else f"{log_type}"
        task_str = f"[{task_id}] " if task_id else ""
        return f"[{timestamp}] {agent:15} | {log_type:13} | {task_str}{msg}"


def save_metrics():
    """Save metrics to disk"""
    try:
        with open(METRICS_FILE, 'w') as f:
            json.dump(dict(metrics), f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving metrics: {e}")


def save_active_tasks():
    """Save active tasks to disk"""
    try:
        with open(ACTIVE_TASKS_FILE, 'w') as f:
            json.dump(active_tasks, f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving active tasks: {e}")


def create_log_entry(
    agent: str,
    level: str,
    message: str,
    log_type: str = LogType.EVENT,
    task_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    context: Optional[Dict] = None
) -> Dict:
    """Create a standardized log entry"""
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "level": level,
        "type": log_type,
        "message": message,
        "task_id": task_id,
        "workflow_id": workflow_id,
        "context": context or {}
    }
    
    # Add to main logs
    logs.append(entry)
    
    # Add to indices
    if task_id:
        task_logs[task_id].append(entry)
    if agent:
        agent_logs[agent].append(entry)
    if workflow_id:
        workflow_logs[workflow_id].append(entry)
    
    # Persist immediately
    save_log_entry(entry)
    
    return entry


# Initialize server
server = Server("logging")

# Load persisted data
load_data()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available logging tools"""
    return [
        # Core Logging Tools
        types.Tool(
            name="log_event",
            description="Log a general event or message",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name logging the event"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["debug", "info", "warning", "error", "critical"],
                        "default": "info"
                    },
                    "message": {
                        "type": "string",
                        "description": "Log message"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Associated task ID"
                    },
                    "workflow_id": {
                        "type": "string",
                        "description": "Associated workflow ID"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context data"
                    }
                },
                "required": ["agent", "message"]
            }
        ),
        
        # Task Lifecycle Logging
        types.Tool(
            name="log_task_start",
            description="Log the start of a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent starting the task"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description"
                    },
                    "estimated_duration": {
                        "type": "integer",
                        "description": "Estimated duration in minutes"
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task dependencies"
                    },
                    "workflow_id": {
                        "type": "string",
                        "description": "Associated workflow ID"
                    }
                },
                "required": ["agent", "task_id", "description"]
            }
        ),
        
        types.Tool(
            name="log_task_complete",
            description="Log task completion",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent completing the task"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID"
                    },
                    "result": {
                        "type": "string",
                        "enum": ["success", "partial", "skipped"],
                        "description": "Task result"
                    },
                    "outputs": {
                        "type": "object",
                        "description": "Task outputs or artifacts"
                    },
                    "metrics": {
                        "type": "object",
                        "description": "Performance metrics"
                    }
                },
                "required": ["agent", "task_id", "result"]
            }
        ),
        
        types.Tool(
            name="log_task_failed",
            description="Log task failure",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent where task failed"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "stack_trace": {
                        "type": "string",
                        "description": "Stack trace if available"
                    },
                    "recovery_action": {
                        "type": "string",
                        "description": "Planned recovery action"
                    }
                },
                "required": ["agent", "task_id", "error"]
            }
        ),
        
        # Agent Coordination Logging
        types.Tool(
            name="log_handoff",
            description="Log task handoff between agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_agent": {
                        "type": "string",
                        "description": "Agent handing off"
                    },
                    "to_agent": {
                        "type": "string",
                        "description": "Agent receiving"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task being handed off"
                    },
                    "handoff_reason": {
                        "type": "string",
                        "description": "Reason for handoff"
                    },
                    "context": {
                        "type": "object",
                        "description": "Handoff context and artifacts"
                    }
                },
                "required": ["from_agent", "to_agent", "task_id"]
            }
        ),
        
        types.Tool(
            name="log_decision",
            description="Log important decisions made by agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent making the decision"
                    },
                    "decision": {
                        "type": "string",
                        "description": "Decision made"
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Reasoning behind the decision"
                    },
                    "alternatives": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Alternatives considered"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Associated task ID"
                    }
                },
                "required": ["agent", "decision", "rationale"]
            }
        ),
        
        # Tool Usage Logging
        types.Tool(
            name="log_file_operation",
            description="Log file operations (read, write, edit)",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent performing the operation"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "edit", "delete"],
                        "description": "Type of file operation"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "details": {
                        "type": "string",
                        "description": "Additional details (e.g., lines edited, bytes written)"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Associated task ID"
                    }
                },
                "required": ["agent", "operation", "file_path"]
            }
        ),
        
        types.Tool(
            name="log_tool_use",
            description="Log tool usage by agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent using the tool"
                    },
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool used"
                    },
                    "duration_ms": {
                        "type": "integer",
                        "description": "Execution duration in milliseconds"
                    },
                    "success": {
                        "type": "boolean",
                        "description": "Whether tool execution succeeded"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Associated task ID"
                    }
                },
                "required": ["agent", "tool_name", "success"]
            }
        ),
        
        # Query Tools
        types.Tool(
            name="query_logs",
            description="Query logs with filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Filter by agent"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Filter by task ID"
                    },
                    "workflow_id": {
                        "type": "string",
                        "description": "Filter by workflow ID"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["debug", "info", "warning", "error", "critical"],
                        "description": "Minimum log level"
                    },
                    "log_type": {
                        "type": "string",
                        "description": "Filter by log type"
                    },
                    "time_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string"},
                            "end": {"type": "string"}
                        },
                        "description": "Time range filter (ISO format)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum results to return"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_task_timeline",
            description="Get complete timeline of events for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to get timeline for"
                    }
                },
                "required": ["task_id"]
            }
        ),
        
        types.Tool(
            name="get_agent_activity",
            description="Get recent activity for an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "description": "Number of recent activities"
                    }
                },
                "required": ["agent"]
            }
        ),
        
        types.Tool(
            name="get_active_tasks",
            description="Get all currently active tasks across agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Filter by specific agent"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_error_summary",
            description="Get summary of recent errors",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_range_hours": {
                        "type": "integer",
                        "default": 24,
                        "description": "Hours to look back"
                    },
                    "group_by": {
                        "type": "string",
                        "enum": ["agent", "task", "error_type"],
                        "default": "agent",
                        "description": "How to group errors"
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
    
    if name == "log_event":
        entry = create_log_entry(
            agent=arguments["agent"],
            level=arguments.get("level", "info"),
            message=arguments["message"],
            log_type=LogType.EVENT,
            task_id=arguments.get("task_id"),
            workflow_id=arguments.get("workflow_id"),
            context=arguments.get("context")
        )
        
        return [types.TextContent(
            type="text",
            text=f"Logged event: {entry['id']}"
        )]
    
    elif name == "log_task_start":
        # Track active task
        task_id = arguments["task_id"]
        active_tasks[task_id] = {
            "agent": arguments["agent"],
            "description": arguments["description"],
            "start_time": datetime.now().isoformat(),
            "estimated_duration": arguments.get("estimated_duration"),
            "dependencies": arguments.get("dependencies", []),
            "workflow_id": arguments.get("workflow_id")
        }
        save_active_tasks()
        
        entry = create_log_entry(
            agent=arguments["agent"],
            level="info",
            message=f"Task started: {arguments['description']}",
            log_type=LogType.TASK_START,
            task_id=task_id,
            workflow_id=arguments.get("workflow_id"),
            context={
                "estimated_duration": arguments.get("estimated_duration"),
                "dependencies": arguments.get("dependencies", [])
            }
        )
        
        # Update metrics
        agent_key = f"agent:{arguments['agent']}"
        metrics[agent_key]["count"] += 1
        save_metrics()
        
        return [types.TextContent(
            type="text",
            text=f"Task start logged: {task_id}"
        )]
    
    elif name == "log_task_complete":
        task_id = arguments["task_id"]
        
        # Calculate duration if task was tracked
        duration = None
        if task_id in active_tasks:
            start_time = datetime.fromisoformat(active_tasks[task_id]["start_time"])
            duration = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            agent_key = f"agent:{arguments['agent']}"
            metrics[agent_key]["total_duration"] += duration
            
            # Remove from active tasks
            del active_tasks[task_id]
            save_active_tasks()
        
        entry = create_log_entry(
            agent=arguments["agent"],
            level="info",
            message=f"Task completed: {arguments['result']}",
            log_type=LogType.TASK_COMPLETE,
            task_id=task_id,
            context={
                "result": arguments["result"],
                "outputs": arguments.get("outputs"),
                "metrics": arguments.get("metrics"),
                "duration_seconds": duration
            }
        )
        
        save_metrics()
        
        return [types.TextContent(
            type="text",
            text=f"Task completion logged: {task_id} ({arguments['result']})"
        )]
    
    elif name == "log_task_failed":
        task_id = arguments["task_id"]
        
        # Remove from active tasks
        if task_id in active_tasks:
            del active_tasks[task_id]
            save_active_tasks()
        
        # Update error metrics
        agent_key = f"agent:{arguments['agent']}"
        metrics[agent_key]["errors"] += 1
        save_metrics()
        
        entry = create_log_entry(
            agent=arguments["agent"],
            level="error",
            message=f"Task failed: {arguments['error']}",
            log_type=LogType.TASK_FAILED,
            task_id=task_id,
            context={
                "error": arguments["error"],
                "stack_trace": arguments.get("stack_trace"),
                "recovery_action": arguments.get("recovery_action")
            }
        )
        
        return [types.TextContent(
            type="text",
            text=f"Task failure logged: {task_id}"
        )]
    
    elif name == "log_handoff":
        entry = create_log_entry(
            agent=arguments["from_agent"],
            level="info",
            message=f"Handoff from {arguments['from_agent']} to {arguments['to_agent']}",
            log_type=LogType.HANDOFF,
            task_id=arguments["task_id"],
            context={
                "from_agent": arguments["from_agent"],
                "to_agent": arguments["to_agent"],
                "reason": arguments.get("handoff_reason"),
                "handoff_context": arguments.get("context")
            }
        )
        
        return [types.TextContent(
            type="text",
            text=f"Handoff logged: {arguments['from_agent']} → {arguments['to_agent']}"
        )]
    
    elif name == "log_decision":
        entry = create_log_entry(
            agent=arguments["agent"],
            level="info",
            message=f"Decision: {arguments['decision']}",
            log_type=LogType.DECISION,
            task_id=arguments.get("task_id"),
            context={
                "decision": arguments["decision"],
                "rationale": arguments["rationale"],
                "alternatives": arguments.get("alternatives", [])
            }
        )
        
        return [types.TextContent(
            type="text",
            text=f"Decision logged: {arguments['decision']}"
        )]
    
    elif name == "log_file_operation":
        operation = arguments["operation"]
        log_type_map = {
            "read": LogType.FILE_READ,
            "write": LogType.FILE_WRITE,
            "edit": LogType.FILE_EDIT,
            "delete": LogType.FILE_WRITE  # Treat delete as write
        }
        
        entry = create_log_entry(
            agent=arguments["agent"],
            level="debug",
            message=f"File {operation}: {arguments['file_path']}",
            log_type=log_type_map[operation],
            task_id=arguments.get("task_id"),
            context={
                "operation": operation,
                "file_path": arguments["file_path"],
                "details": arguments.get("details"),
                "changes": arguments.get("details", "")
            }
        )
        
        return [types.TextContent(
            type="text",
            text=f"File operation logged: {operation} {arguments['file_path']}"
        )]
    
    elif name == "log_tool_use":
        # Update tool usage metrics
        tool_key = f"tool:{arguments['tool_name']}"
        metrics[tool_key]["count"] += 1
        if arguments.get("duration_ms"):
            metrics[tool_key]["total_duration"] += arguments["duration_ms"]
        if not arguments["success"]:
            metrics[tool_key]["errors"] += 1
        save_metrics()
        
        entry = create_log_entry(
            agent=arguments["agent"],
            level="debug",
            message=f"Tool used: {arguments['tool_name']}",
            log_type=LogType.TOOL_USE,
            task_id=arguments.get("task_id"),
            context={
                "tool": arguments["tool_name"],
                "duration_ms": arguments.get("duration_ms"),
                "success": arguments["success"]
            }
        )
        
        return [types.TextContent(
            type="text",
            text=f"Tool usage logged: {arguments['tool_name']}"
        )]
    
    elif name == "query_logs":
        filtered_logs = logs
        
        # Apply filters
        if arguments.get("agent"):
            filtered_logs = [l for l in filtered_logs if l.get("agent") == arguments["agent"]]
        
        if arguments.get("task_id"):
            filtered_logs = [l for l in filtered_logs if l.get("task_id") == arguments["task_id"]]
        
        if arguments.get("workflow_id"):
            filtered_logs = [l for l in filtered_logs if l.get("workflow_id") == arguments["workflow_id"]]
        
        if arguments.get("level"):
            level_priority = {"debug": 0, "info": 1, "warning": 2, "error": 3, "critical": 4}
            min_level = level_priority[arguments["level"]]
            filtered_logs = [l for l in filtered_logs 
                           if level_priority.get(l.get("level", "info"), 1) >= min_level]
        
        if arguments.get("log_type"):
            filtered_logs = [l for l in filtered_logs if l.get("type") == arguments["log_type"]]
        
        # Time range filter
        if arguments.get("time_range"):
            start = datetime.fromisoformat(arguments["time_range"]["start"])
            end = datetime.fromisoformat(arguments["time_range"]["end"])
            filtered_logs = [l for l in filtered_logs 
                           if start <= datetime.fromisoformat(l["timestamp"]) <= end]
        
        # Limit results
        limit = arguments.get("limit", 100)
        filtered_logs = filtered_logs[-limit:]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(filtered_logs, indent=2, default=str)
        )]
    
    elif name == "get_task_timeline":
        task_id = arguments["task_id"]
        timeline = task_logs.get(task_id, [])
        
        # Sort by timestamp
        timeline = sorted(timeline, key=lambda x: x["timestamp"])
        
        # Format as timeline
        formatted = []
        for entry in timeline:
            time = datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M:%S")
            formatted.append(f"[{time}] [{entry['agent']}] {entry['message']}")
        
        return [types.TextContent(
            type="text",
            text="\n".join(formatted) if formatted else f"No timeline found for task {task_id}"
        )]
    
    elif name == "get_agent_activity":
        agent = arguments["agent"]
        limit = arguments.get("limit", 50)
        
        activity = agent_logs.get(agent, [])[-limit:]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(activity, indent=2, default=str)
        )]
    
    elif name == "get_active_tasks":
        filtered_tasks = active_tasks
        
        if arguments.get("agent"):
            filtered_tasks = {k: v for k, v in filtered_tasks.items() 
                            if v["agent"] == arguments["agent"]}
        
        # Add duration for each active task
        for task_id, task in filtered_tasks.items():
            start_time = datetime.fromisoformat(task["start_time"])
            task["duration_minutes"] = int((datetime.now() - start_time).total_seconds() / 60)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(filtered_tasks, indent=2, default=str)
        )]
    
    elif name == "get_error_summary":
        hours = arguments.get("time_range_hours", 24)
        group_by = arguments.get("group_by", "agent")
        
        # Filter errors in time range
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [l for l in logs 
                        if l.get("level") in ["error", "critical"] 
                        and datetime.fromisoformat(l["timestamp"]) >= cutoff]
        
        # Group errors
        summary = defaultdict(list)
        for error in recent_errors:
            if group_by == "agent":
                key = error.get("agent", "unknown")
            elif group_by == "task":
                key = error.get("task_id", "no_task")
            else:  # error_type
                key = error.get("context", {}).get("error", "unknown_error")[:50]
            
            summary[key].append({
                "time": error["timestamp"],
                "message": error["message"][:100],
                "task_id": error.get("task_id")
            })
        
        # Format summary
        formatted = {}
        for key, errors in summary.items():
            formatted[key] = {
                "count": len(errors),
                "recent": errors[-5:]  # Last 5 errors
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(formatted, indent=2, default=str)
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
                server_name="logging",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())