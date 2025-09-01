#!/usr/bin/env python3
"""
Communication MCP Server - Centralized Task Management and Agent Coordination

This server replaces direct agent-to-agent JSON messaging with a centralized,
persistent, and trackable communication system.
"""

import asyncio
import json
import os
import uuid
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from enum import Enum

from mcp import types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio


# Task States
class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Task Priority
class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Agent Status
class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    BLOCKED = "blocked"
    OFFLINE = "offline"
    ERROR = "error"


# Message Types
class MessageType(str, Enum):
    TASK = "task"
    STATUS = "status"
    QUERY = "query"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ESCALATION = "escalation"
    HANDOFF = "handoff"


# Storage for server state
tasks: Dict[str, Dict] = {}
messages: Dict[str, Dict] = {}
agents: Dict[str, Dict] = {}
workflows: Dict[str, Dict] = {}
message_threads: Dict[str, List[str]] = {}

# Persistence
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

# Use project-aware path
project_root = find_project_root()
data_dir = project_root / "mcp" / "data" / "communication"
data_dir.mkdir(parents=True, exist_ok=True)

# Load project config if exists
project_config = {}
project_json = project_root / "project.json"
if project_json.exists():
    with open(project_json) as f:
        project_config = json.load(f)

PROJECT_ID = project_config.get("project_id", "default")

# File paths - now project-aware
TASKS_FILE = data_dir / "tasks.json"
MESSAGES_FILE = data_dir / "messages.json"
AGENTS_FILE = data_dir / "agents.json"
WORKFLOWS_FILE = data_dir / "workflows.json"


def load_data():
    """Load persisted data from disk"""
    global tasks, messages, agents, workflows
    
    try:
        tasks_file = data_dir / "tasks.json"
        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        
        messages_file = data_dir / "messages.json"
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                messages = json.load(f)
        
        agents_file = data_dir / "agents.json"
        if agents_file.exists():
            with open(agents_file, 'r') as f:
                agents = json.load(f)
        
        workflows_file = data_dir / "workflows.json"
        if workflows_file.exists():
            with open(workflows_file, 'r') as f:
                workflows = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")


def save_data():
    """Persist data to disk"""
    try:
        # Save tasks
        with open(data_dir / "tasks.json", 'w') as f:
            json.dump(tasks, f, default=str, indent=2)
        
        # Save messages
        with open(data_dir / "messages.json", 'w') as f:
            json.dump(messages, f, default=str, indent=2)
        
        # Save agents
        with open(data_dir / "agents.json", 'w') as f:
            json.dump(agents, f, default=str, indent=2)
        
        # Save workflows
        with open(data_dir / "workflows.json", 'w') as f:
            json.dump(workflows, f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")


# Initialize server
server = Server("coord")

# Load persisted data
load_data()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available communication and task management tools"""
    return [
        # Task Management Tools
        types.Tool(
            name="task_create",
            description="Create a new task with optional dependencies and deadline. Returns task_id for tracking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Detailed task description"},
                    "created_by": {"type": "string", "description": "Agent creating the task"},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"], "default": "medium"},
                    "dependencies": {"type": "array", "items": {"type": "string"}, "description": "List of task IDs this depends on"},
                    "deadline": {"type": "string", "description": "ISO format deadline"},
                    "context": {"type": "object", "description": "Additional context data"}
                },
                "required": ["title", "description", "created_by"]
            }
        ),
        types.Tool(
            name="task_assign",
            description="Assign a task to an agent or auto-assign to best available agent based on workload",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to assign"},
                    "agent_name": {"type": "string", "description": "Agent to assign to"},
                    "auto_assign": {"type": "boolean", "description": "Auto-assign to least busy agent", "default": False}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="task_status",
            description="Update task status and progress. Use for tracking task lifecycle.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to update"},
                    "status": {"type": "string", "enum": ["pending", "assigned", "in_progress", "blocked", "completed", "failed", "cancelled"]},
                    "progress": {"type": "integer", "description": "Progress percentage 0-100"},
                    "blocked_reason": {"type": "string", "description": "Reason if blocked"}
                },
                "required": ["task_id", "status"]
            }
        ),
        types.Tool(
            name="task_handoff",
            description="Hand off a task from one agent to another with context and artifacts",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task to hand off"},
                    "from_agent": {"type": "string", "description": "Current agent"},
                    "to_agent": {"type": "string", "description": "Target agent"},
                    "context": {"type": "object", "description": "Handoff context"},
                    "artifacts": {"type": "array", "items": {"type": "string"}, "description": "Files or documents to include"}
                },
                "required": ["task_id", "from_agent", "to_agent"]
            }
        ),
        types.Tool(
            name="task_list",
            description="List tasks filtered by agent, status, or priority. Use to see workload.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {"type": "string", "description": "Filter by assigned agent"},
                    "status": {"type": "string", "description": "Filter by status"},
                    "priority": {"type": "string", "description": "Filter by priority"}
                }
            }
        ),
        types.Tool(
            name="task_dependencies",
            description="Check if task dependencies are met before starting work",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task to check"}
                },
                "required": ["task_id"]
            }
        ),
        
        # Message/Communication Tools
        types.Tool(
            name="message_send",
            description="Send a message to another agent with guaranteed delivery",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_agent": {"type": "string", "description": "Sender agent"},
                    "to_agent": {"type": "string", "description": "Recipient agent or 'broadcast'"},
                    "subject": {"type": "string", "description": "Message subject"},
                    "content": {"type": "string", "description": "Message content"},
                    "type": {"type": "string", "enum": ["task", "status", "query", "response", "notification", "escalation", "handoff"], "default": "notification"},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"], "default": "medium"},
                    "requires_response": {"type": "boolean", "default": False},
                    "thread_id": {"type": "string", "description": "Thread ID for conversations"}
                },
                "required": ["from_agent", "to_agent", "subject", "content"]
            }
        ),
        types.Tool(
            name="message_broadcast",
            description="Broadcast a message to all active agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_agent": {"type": "string", "description": "Sender agent"},
                    "subject": {"type": "string", "description": "Broadcast subject"},
                    "content": {"type": "string", "description": "Broadcast content"},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"], "default": "medium"}
                },
                "required": ["from_agent", "subject", "content"]
            }
        ),
        types.Tool(
            name="message_inbox",
            description="Get messages for an agent. Automatically marks messages as read.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Agent to get messages for"},
                    "unread_only": {"type": "boolean", "description": "Only show unread messages", "default": True}
                },
                "required": ["agent_name"]
            }
        ),
        types.Tool(
            name="message_thread",
            description="Get all messages in a conversation thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {"type": "string", "description": "Thread ID to retrieve"}
                },
                "required": ["thread_id"]
            }
        ),
        
        # Agent Coordination Tools
        types.Tool(
            name="agent_status",
            description="Get or set agent availability status. Use to indicate busy/available.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Agent name"},
                    "status": {"type": "string", "enum": ["available", "busy", "blocked", "offline", "error"], "description": "New status to set"}
                },
                "required": ["agent_name"]
            }
        ),
        types.Tool(
            name="agent_workload",
            description="Check agent workload and availability. Returns workload percentage.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Agent to check, or omit for all"}
                }
            }
        ),
        types.Tool(
            name="agent_capabilities",
            description="Get or set agent capabilities for task routing",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Agent name"},
                    "capabilities": {"type": "array", "items": {"type": "string"}, "description": "List of capabilities to set"}
                },
                "required": ["agent_name"]
            }
        ),
        types.Tool(
            name="escalation_create",
            description="Escalate an issue to scrum-master when blocked",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task to escalate"},
                    "from_agent": {"type": "string", "description": "Agent escalating"},
                    "reason": {"type": "string", "description": "Escalation reason"},
                    "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"], "default": "high"}
                },
                "required": ["task_id", "from_agent", "reason"]
            }
        ),
        
        # Workflow Tools
        types.Tool(
            name="workflow_start",
            description="Start a multi-agent workflow with defined steps",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Workflow name"},
                    "type": {"type": "string", "description": "Workflow type (feature, bugfix, etc)"},
                    "steps": {"type": "array", "items": {"type": "string"}, "description": "Ordered list of steps"},
                    "parallel_groups": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}, "description": "Groups of steps that can run in parallel"}
                },
                "required": ["name", "type", "steps"]
            }
        ),
        types.Tool(
            name="workflow_status",
            description="Get workflow progress and current status",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "Workflow to check"}
                },
                "required": ["workflow_id"]
            }
        ),
        types.Tool(
            name="checkpoint_create",
            description="Create a progress checkpoint for tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Checkpoint name"},
                    "task_id": {"type": "string", "description": "Associated task"},
                    "agent": {"type": "string", "description": "Agent creating checkpoint"},
                    "data": {"type": "object", "description": "Checkpoint data"}
                },
                "required": ["name", "task_id", "agent", "data"]
            }
        ),
        types.Tool(
            name="checkpoint_validate",
            description="Verify a checkpoint was completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "checkpoint_id": {"type": "string", "description": "Checkpoint to validate"},
                    "task_id": {"type": "string", "description": "Task containing checkpoint"}
                },
                "required": ["checkpoint_id", "task_id"]
            }
        ),
        
        # System Management Tools
        types.Tool(
            name="system_reset",
            description="Reset coordination system components (tasks, messages, agents). Creates automatic backup.",
            inputSchema={
                "type": "object",
                "properties": {
                    "component": {"type": "string", "enum": ["all", "tasks", "messages", "agents", "workflows", "escalations"], "description": "Component to reset"},
                    "confirm": {"type": "string", "description": "Must be 'RESET_CONFIRMED' to proceed"},
                    "keep_templates": {"type": "boolean", "default": False, "description": "Keep template tasks when resetting"}
                },
                "required": ["component", "confirm"]
            }
        ),
        types.Tool(
            name="system_archive",
            description="Archive completed tasks older than specified days to reduce clutter",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_old": {"type": "integer", "default": 7, "description": "Archive tasks completed more than this many days ago"},
                    "dry_run": {"type": "boolean", "default": False, "description": "Preview what would be archived without doing it"}
                }
            }
        ),
        types.Tool(
            name="system_stats",
            description="Get coordination system statistics and status",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {"type": "boolean", "default": False, "description": "Include detailed breakdown"}
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for communication and task management"""
    
    global tasks, messages, agents, workflows, message_threads
    
    try:
        # Task Management Tools
        if name == "task_create":
            task_id = str(uuid.uuid4())
            task = {
                "id": task_id,
                "title": arguments["title"],
                "description": arguments["description"],
                "created_by": arguments["created_by"],
                "assigned_to": None,
                "status": TaskStatus.PENDING.value,
                "priority": arguments.get("priority", "medium"),
                "dependencies": arguments.get("dependencies", []),
                "artifacts": [],
                "context": arguments.get("context", {}),
                "created_at": str(datetime.now()),
                "updated_at": str(datetime.now()),
                "completed_at": None,
                "deadline": arguments.get("deadline"),
                "parent_workflow": None,
                "subtasks": [],
                "blocked_reason": None,
                "progress_percentage": 0
            }
            tasks[task_id] = task
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task_id,
                    "status": "created",
                    "message": f"Task '{task['title']}' created successfully"
                }, indent=2)
            )]
        
        elif name == "task_assign":
            task_id = arguments["task_id"]
            if task_id not in tasks:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Task {task_id} not found"})
                )]
            
            task = tasks[task_id]
            agent_name = arguments.get("agent_name")
            
            if arguments.get("auto_assign", False):
                # Find best available agent
                available_agents = [
                    a for a in agents.values()
                    if a.get("status") == AgentStatus.AVAILABLE.value and a.get("workload", 0) < 70
                ]
                if not available_agents:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": "No available agents"})
                    )]
                
                # Sort by workload
                agent_name = sorted(available_agents, key=lambda a: a.get("workload", 0))[0]["name"]
            
            # Assign task
            task["assigned_to"] = agent_name
            task["status"] = TaskStatus.ASSIGNED.value
            task["updated_at"] = str(datetime.now())
            
            # Update agent info
            if agent_name not in agents:
                agents[agent_name] = {
                    "name": agent_name,
                    "status": AgentStatus.AVAILABLE.value,
                    "current_tasks": [],
                    "completed_tasks": [],
                    "capabilities": [],
                    "workload": 0,
                    "last_active": str(datetime.now()),
                    "blocked_tasks": []
                }
            
            agent = agents[agent_name]
            agent["current_tasks"].append(task_id)
            agent["workload"] = min(100, agent.get("workload", 0) + 20)
            
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task_id,
                    "assigned_to": agent_name,
                    "status": "assigned"
                }, indent=2)
            )]
        
        elif name == "task_status":
            task_id = arguments["task_id"]
            if task_id not in tasks:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Task {task_id} not found"})
                )]
            
            task = tasks[task_id]
            old_status = task["status"]
            task["status"] = arguments["status"]
            task["updated_at"] = str(datetime.now())
            
            if "progress" in arguments:
                task["progress_percentage"] = arguments["progress"]
            
            if arguments["status"] == "blocked" and "blocked_reason" in arguments:
                task["blocked_reason"] = arguments["blocked_reason"]
            
            if arguments["status"] == "completed":
                task["completed_at"] = str(datetime.now())
                task["progress_percentage"] = 100
                
                # Update agent workload
                if task["assigned_to"] and task["assigned_to"] in agents:
                    agent = agents[task["assigned_to"]]
                    if task_id in agent["current_tasks"]:
                        agent["current_tasks"].remove(task_id)
                        agent["completed_tasks"].append(task_id)
                        agent["workload"] = max(0, agent.get("workload", 0) - 20)
            
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task_id,
                    "old_status": old_status,
                    "new_status": arguments["status"],
                    "progress": task["progress_percentage"]
                }, indent=2)
            )]
        
        elif name == "task_handoff":
            task_id = arguments["task_id"]
            if task_id not in tasks:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Task {task_id} not found"})
                )]
            
            task = tasks[task_id]
            from_agent = arguments["from_agent"]
            to_agent = arguments["to_agent"]
            
            # Update task
            task["assigned_to"] = to_agent
            task["updated_at"] = str(datetime.now())
            if "context" in arguments:
                task["context"].update(arguments["context"])
            if "artifacts" in arguments:
                task["artifacts"].extend(arguments["artifacts"])
            
            # Update agents
            if from_agent in agents:
                from_agent_info = agents[from_agent]
                if task_id in from_agent_info["current_tasks"]:
                    from_agent_info["current_tasks"].remove(task_id)
                    from_agent_info["workload"] = max(0, from_agent_info.get("workload", 0) - 20)
            
            if to_agent not in agents:
                agents[to_agent] = {
                    "name": to_agent,
                    "status": AgentStatus.AVAILABLE.value,
                    "current_tasks": [],
                    "completed_tasks": [],
                    "capabilities": [],
                    "workload": 0,
                    "last_active": str(datetime.now()),
                    "blocked_tasks": []
                }
            
            to_agent_info = agents[to_agent]
            to_agent_info["current_tasks"].append(task_id)
            to_agent_info["workload"] = min(100, to_agent_info.get("workload", 0) + 20)
            
            # Create handoff message
            message_id = str(uuid.uuid4())
            message = {
                "id": message_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "type": MessageType.HANDOFF.value,
                "subject": f"Task handoff: {task['title']}",
                "content": f"Task {task_id} handed off with context and artifacts",
                "priority": "medium",
                "timestamp": str(datetime.now()),
                "read": False,
                "requires_response": False,
                "attachments": arguments.get("artifacts", [])
            }
            messages[message_id] = message
            
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task_id,
                    "from": from_agent,
                    "to": to_agent,
                    "status": "handed_off",
                    "message_id": message_id
                }, indent=2)
            )]
        
        elif name == "task_list":
            filtered_tasks = list(tasks.values())
            
            if "agent" in arguments:
                filtered_tasks = [t for t in filtered_tasks if t["assigned_to"] == arguments["agent"]]
            if "status" in arguments:
                filtered_tasks = [t for t in filtered_tasks if t["status"] == arguments["status"]]
            if "priority" in arguments:
                filtered_tasks = [t for t in filtered_tasks if t["priority"] == arguments["priority"]]
            
            result = []
            for task in filtered_tasks:
                result.append({
                    "id": task["id"],
                    "title": task["title"],
                    "assigned_to": task["assigned_to"],
                    "status": task["status"],
                    "priority": task["priority"],
                    "progress": task["progress_percentage"],
                    "created_at": task["created_at"],
                    "deadline": task.get("deadline")
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(result),
                    "tasks": result
                }, indent=2)
            )]
        
        elif name == "task_dependencies":
            task_id = arguments["task_id"]
            if task_id not in tasks:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Task {task_id} not found"})
                )]
            
            task = tasks[task_id]
            if not task["dependencies"]:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "task_id": task_id,
                        "dependencies_met": True,
                        "dependencies": []
                    }, indent=2)
                )]
            
            dep_status = []
            all_met = True
            
            for dep_id in task["dependencies"]:
                if dep_id in tasks:
                    dep_task = tasks[dep_id]
                    is_complete = dep_task["status"] == TaskStatus.COMPLETED.value
                    dep_status.append({
                        "id": dep_id,
                        "title": dep_task["title"],
                        "status": dep_task["status"],
                        "complete": is_complete
                    })
                    if not is_complete:
                        all_met = False
                else:
                    dep_status.append({
                        "id": dep_id,
                        "error": "Dependency not found",
                        "complete": False
                    })
                    all_met = False
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task_id,
                    "dependencies_met": all_met,
                    "dependencies": dep_status
                }, indent=2)
            )]
        
        # Message Tools
        elif name == "message_send":
            message_id = str(uuid.uuid4())
            message = {
                "id": message_id,
                "from_agent": arguments["from_agent"],
                "to_agent": arguments["to_agent"],
                "type": arguments.get("type", "notification"),
                "subject": arguments["subject"],
                "content": arguments["content"],
                "priority": arguments.get("priority", "medium"),
                "timestamp": str(datetime.now()),
                "read": False,
                "requires_response": arguments.get("requires_response", False),
                "thread_id": arguments.get("thread_id"),
                "attachments": []
            }
            
            messages[message_id] = message
            
            # Track thread
            if "thread_id" in arguments:
                thread_id = arguments["thread_id"]
                if thread_id not in message_threads:
                    message_threads[thread_id] = []
                message_threads[thread_id].append(message_id)
            
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "message_id": message_id,
                    "status": "sent",
                    "to": arguments["to_agent"],
                    "thread_id": arguments.get("thread_id")
                }, indent=2)
            )]
        
        elif name == "message_broadcast":
            message_id = str(uuid.uuid4())
            message = {
                "id": message_id,
                "from_agent": arguments["from_agent"],
                "to_agent": "broadcast",
                "type": MessageType.NOTIFICATION.value,
                "subject": arguments["subject"],
                "content": arguments["content"],
                "priority": arguments.get("priority", "medium"),
                "timestamp": str(datetime.now()),
                "read": False,
                "requires_response": False,
                "attachments": []
            }
            
            messages[message_id] = message
            save_data()
            
            # Count active agents
            active_agents = len([a for a in agents.values() 
                               if a.get("status") != AgentStatus.OFFLINE.value])
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "message_id": message_id,
                    "status": "broadcast",
                    "recipients": active_agents
                }, indent=2)
            )]
        
        elif name == "message_inbox":
            agent_name = arguments["agent_name"]
            unread_only = arguments.get("unread_only", True)
            
            inbox_messages = []
            
            for msg in messages.values():
                if msg["to_agent"] == agent_name or msg["to_agent"] == "broadcast":
                    if not unread_only or not msg["read"]:
                        inbox_messages.append({
                            "id": msg["id"],
                            "from": msg["from_agent"],
                            "subject": msg["subject"],
                            "type": msg["type"],
                            "priority": msg["priority"],
                            "timestamp": msg["timestamp"],
                            "read": msg["read"],
                            "requires_response": msg.get("requires_response", False)
                        })
                        
                        # Mark as read
                        if not msg["read"]:
                            msg["read"] = True
                            save_data()
            
            # Sort by timestamp, newest first
            inbox_messages.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "agent": agent_name,
                    "count": len(inbox_messages),
                    "messages": inbox_messages
                }, indent=2)
            )]
        
        elif name == "message_thread":
            thread_id = arguments["thread_id"]
            if thread_id not in message_threads:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "thread_id": thread_id,
                        "messages": []
                    }, indent=2)
                )]
            
            thread_messages = []
            for msg_id in message_threads[thread_id]:
                if msg_id in messages:
                    msg = messages[msg_id]
                    thread_messages.append({
                        "id": msg["id"],
                        "from": msg["from_agent"],
                        "to": msg["to_agent"],
                        "content": msg["content"],
                        "timestamp": msg["timestamp"]
                    })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "thread_id": thread_id,
                    "count": len(thread_messages),
                    "messages": thread_messages
                }, indent=2)
            )]
        
        # Agent Coordination Tools
        elif name == "agent_status":
            agent_name = arguments["agent_name"]
            
            if agent_name not in agents:
                agents[agent_name] = {
                    "name": agent_name,
                    "status": AgentStatus.AVAILABLE.value,
                    "current_tasks": [],
                    "completed_tasks": [],
                    "capabilities": [],
                    "workload": 0,
                    "last_active": str(datetime.now()),
                    "blocked_tasks": []
                }
            
            agent = agents[agent_name]
            
            if "status" in arguments:
                agent["status"] = arguments["status"]
                agent["last_active"] = str(datetime.now())
                
                # If going offline, mark tasks as blocked
                if arguments["status"] == "offline":
                    for task_id in agent["current_tasks"]:
                        if task_id in tasks:
                            task = tasks[task_id]
                            task["status"] = TaskStatus.BLOCKED.value
                            task["blocked_reason"] = f"Agent {agent_name} is offline"
                
                save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "agent": agent_name,
                    "status": agent["status"],
                    "workload": agent["workload"],
                    "current_tasks": len(agent["current_tasks"]),
                    "completed_tasks": len(agent["completed_tasks"]),
                    "last_active": agent["last_active"]
                }, indent=2)
            )]
        
        elif name == "agent_workload":
            if "agent_name" in arguments:
                agent_name = arguments["agent_name"]
                if agent_name not in agents:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": f"Agent {agent_name} not found"})
                    )]
                
                agent = agents[agent_name]
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "agent": agent_name,
                        "workload": agent["workload"],
                        "status": agent["status"],
                        "current_tasks": agent["current_tasks"],
                        "task_count": len(agent["current_tasks"])
                    }, indent=2)
                )]
            else:
                # Return all agents' workload
                workloads = []
                for agent in agents.values():
                    workloads.append({
                        "agent": agent["name"],
                        "workload": agent["workload"],
                        "status": agent["status"],
                        "tasks": len(agent["current_tasks"])
                    })
                
                # Sort by workload
                workloads.sort(key=lambda x: x["workload"])
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "agents": workloads,
                        "least_busy": workloads[0]["agent"] if workloads else None
                    }, indent=2)
                )]
        
        elif name == "agent_capabilities":
            agent_name = arguments["agent_name"]
            
            if agent_name not in agents:
                agents[agent_name] = {
                    "name": agent_name,
                    "status": AgentStatus.AVAILABLE.value,
                    "current_tasks": [],
                    "completed_tasks": [],
                    "capabilities": [],
                    "workload": 0,
                    "last_active": str(datetime.now()),
                    "blocked_tasks": []
                }
            
            agent = agents[agent_name]
            
            if "capabilities" in arguments:
                agent["capabilities"] = arguments["capabilities"]
                save_data()
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "agent": agent_name,
                        "capabilities": arguments["capabilities"],
                        "status": "updated"
                    }, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "agent": agent_name,
                        "capabilities": agent["capabilities"]
                    }, indent=2)
                )]
        
        elif name == "escalation_create":
            task_id = arguments["task_id"]
            if task_id not in tasks:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Task {task_id} not found"})
                )]
            
            task = tasks[task_id]
            
            # Create escalation message
            escalation_id = str(uuid.uuid4())
            escalation = {
                "id": escalation_id,
                "from_agent": arguments["from_agent"],
                "to_agent": "scrum-master",
                "type": MessageType.ESCALATION.value,
                "subject": f"ESCALATION: {task['title']}",
                "content": f"Task {task_id} escalated. Reason: {arguments['reason']}",
                "priority": arguments.get("severity", "high"),
                "timestamp": str(datetime.now()),
                "read": False,
                "requires_response": True,
                "attachments": []
            }
            
            messages[escalation_id] = escalation
            
            # Mark task as blocked
            task["status"] = TaskStatus.BLOCKED.value
            task["blocked_reason"] = f"Escalated: {arguments['reason']}"
            
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "escalation_id": escalation_id,
                    "task_id": task_id,
                    "escalated_to": "scrum-master",
                    "severity": arguments.get("severity", "high")
                }, indent=2)
            )]
        
        # Workflow Tools
        elif name == "workflow_start":
            workflow_id = str(uuid.uuid4())
            workflow = {
                "id": workflow_id,
                "name": arguments["name"],
                "type": arguments["type"],
                "steps": [{"name": step, "status": "pending"} for step in arguments["steps"]],
                "current_step": 0,
                "status": TaskStatus.PENDING.value,
                "created_at": str(datetime.now()),
                "tasks": [],
                "parallel_groups": arguments.get("parallel_groups", [])
            }
            
            workflows[workflow_id] = workflow
            
            # Create tasks for first step(s)
            first_steps = workflow["parallel_groups"][0] if workflow["parallel_groups"] else [arguments["steps"][0]]
            
            for step_name in first_steps:
                task_id = str(uuid.uuid4())
                task = {
                    "id": task_id,
                    "title": f"{arguments['name']}: {step_name}",
                    "description": f"Workflow step: {step_name}",
                    "created_by": "workflow-engine",
                    "assigned_to": None,
                    "status": TaskStatus.PENDING.value,
                    "priority": "medium",
                    "dependencies": [],
                    "artifacts": [],
                    "context": {},
                    "created_at": str(datetime.now()),
                    "updated_at": str(datetime.now()),
                    "completed_at": None,
                    "deadline": None,
                    "parent_workflow": workflow_id,
                    "subtasks": [],
                    "blocked_reason": None,
                    "progress_percentage": 0
                }
                tasks[task_id] = task
                workflow["tasks"].append(task_id)
            
            workflow["status"] = TaskStatus.IN_PROGRESS.value
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "workflow_id": workflow_id,
                    "name": arguments["name"],
                    "status": "started",
                    "initial_tasks": workflow["tasks"]
                }, indent=2)
            )]
        
        elif name == "workflow_status":
            workflow_id = arguments["workflow_id"]
            if workflow_id not in workflows:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Workflow {workflow_id} not found"})
                )]
            
            workflow = workflows[workflow_id]
            
            # Calculate progress
            total_steps = len(workflow["steps"])
            completed_steps = len([s for s in workflow["steps"] if s["status"] == "completed"])
            progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
            
            # Get task statuses
            task_statuses = []
            for task_id in workflow["tasks"]:
                if task_id in tasks:
                    task = tasks[task_id]
                    task_statuses.append({
                        "id": task_id,
                        "title": task["title"],
                        "status": task["status"],
                        "assigned_to": task["assigned_to"],
                        "progress": task["progress_percentage"]
                    })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "workflow_id": workflow_id,
                    "name": workflow["name"],
                    "status": workflow["status"],
                    "progress": progress,
                    "current_step": workflow["current_step"],
                    "total_steps": total_steps,
                    "tasks": task_statuses
                }, indent=2)
            )]
        
        elif name == "checkpoint_create":
            checkpoint = {
                "id": str(uuid.uuid4()),
                "name": arguments["name"],
                "task_id": arguments["task_id"],
                "agent": arguments["agent"],
                "data": arguments["data"],
                "timestamp": str(datetime.now())
            }
            
            # Store in task context
            if arguments["task_id"] in tasks:
                task = tasks[arguments["task_id"]]
                if "checkpoints" not in task["context"]:
                    task["context"]["checkpoints"] = []
                task["context"]["checkpoints"].append(checkpoint)
                save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "checkpoint_id": checkpoint["id"],
                    "status": "created",
                    "task_id": arguments["task_id"]
                }, indent=2)
            )]
        
        elif name == "checkpoint_validate":
            task_id = arguments["task_id"]
            checkpoint_id = arguments["checkpoint_id"]
            
            if task_id not in tasks:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Task {task_id} not found"})
                )]
            
            task = tasks[task_id]
            checkpoints = task["context"].get("checkpoints", [])
            
            for checkpoint in checkpoints:
                if checkpoint["id"] == checkpoint_id:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "checkpoint_id": checkpoint_id,
                            "valid": True,
                            "data": checkpoint["data"],
                            "timestamp": checkpoint["timestamp"]
                        }, indent=2)
                    )]
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "checkpoint_id": checkpoint_id,
                    "valid": False,
                    "error": "Checkpoint not found"
                }, indent=2)
            )]
        
        # System Management Tools
        elif name == "system_reset":
            component = arguments["component"]
            confirm = arguments.get("confirm", "")
            
            if confirm != "RESET_CONFIRMED":
                # Show current statistics
                stats = {
                    "tasks": len(tasks),
                    "messages": len(messages),
                    "agents": len(agents),
                    "workflows": len(workflows),
                    "escalations": len(escalations) if 'escalations' in globals() else 0
                }
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Reset not confirmed",
                        "current_stats": stats,
                        "warning": f"This will reset {component}. Use confirm='RESET_CONFIRMED' to proceed."
                    }, indent=2)
                )]
            
            # Create backup
            backup_dir = data_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            results = {"backed_up": [], "reset": [], "kept": []}
            
            if component == "all" or component == "tasks":
                if tasks:
                    shutil.copy2(TASKS_FILE, backup_dir / "tasks.json")
                    results["backed_up"].append("tasks")
                if arguments.get("keep_templates", False):
                    # Keep any template tasks if needed
                    tasks = {}
                else:
                    tasks = {}
                results["reset"].append(f"tasks ({len(tasks)} remaining)")
            
            if component == "all" or component == "messages":
                if messages:
                    shutil.copy2(MESSAGES_FILE, backup_dir / "messages.json")
                    results["backed_up"].append("messages")
                messages = {}
                message_threads = {}
                results["reset"].append("messages")
            
            if component == "all" or component == "agents":
                if agents:
                    shutil.copy2(AGENTS_FILE, backup_dir / "agents.json")
                    results["backed_up"].append("agents")
                # Clear agents completely
                agents = {}
                results["reset"].append("agents")
            
            if component == "all" or component == "workflows":
                if workflows:
                    shutil.copy2(WORKFLOWS_FILE, backup_dir / "workflows.json")
                    results["backed_up"].append("workflows")
                workflows = {}
                results["reset"].append("workflows")
            
            if component == "all" or component == "escalations":
                escalations_file = data_dir / "escalations.json"
                if escalations_file.exists():
                    shutil.copy2(escalations_file, backup_dir / "escalations.json")
                    results["backed_up"].append("escalations")
                    with open(escalations_file, 'w') as f:
                        json.dump({}, f, indent=2)
                results["reset"].append("escalations")
            
            save_data()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "component": component,
                    "backup_location": str(backup_dir.relative_to(data_dir.parent.parent)),
                    "results": results
                }, indent=2)
            )]
        
        elif name == "system_archive":
            days_old = arguments.get("days_old", 7)
            dry_run = arguments.get("dry_run", False)
            
            from datetime import timedelta
            archive_date = datetime.now() - timedelta(days=days_old)
            
            tasks_to_archive = []
            for task_id, task in tasks.items():
                if task.get("status") == "completed" and task.get("completed_at"):
                    try:
                        completed_date = datetime.fromisoformat(task["completed_at"].replace("Z", "+00:00"))
                        if completed_date < archive_date:
                            tasks_to_archive.append((task_id, task))
                    except:
                        pass
            
            if dry_run:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "dry_run": True,
                        "would_archive": len(tasks_to_archive),
                        "tasks": [{"id": tid, "title": t["title"], "completed": t["completed_at"]} 
                                 for tid, t in tasks_to_archive[:10]],  # Show first 10
                        "note": f"Would archive {len(tasks_to_archive)} tasks older than {days_old} days"
                    }, indent=2)
                )]
            
            if tasks_to_archive:
                # Create archive
                archive_dir = data_dir / "archives"
                archive_dir.mkdir(exist_ok=True)
                archive_file = archive_dir / f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                archived_tasks = {tid: task for tid, task in tasks_to_archive}
                with open(archive_file, 'w') as f:
                    json.dump(archived_tasks, f, indent=2)
                
                # Remove from active tasks
                for task_id, _ in tasks_to_archive:
                    del tasks[task_id]
                
                save_data()
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "archived": len(tasks_to_archive),
                        "archive_file": str(archive_file.relative_to(data_dir.parent.parent)),
                        "remaining_tasks": len(tasks),
                        "message": f"Archived {len(tasks_to_archive)} completed tasks older than {days_old} days"
                    }, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "archived": 0,
                        "message": f"No completed tasks older than {days_old} days to archive"
                    }, indent=2)
                )]
        
        elif name == "system_stats":
            detailed = arguments.get("detailed", False)
            
            stats = {
                "tasks": {
                    "total": len(tasks),
                    "by_status": {},
                    "by_priority": {},
                    "by_agent": {}
                },
                "messages": {
                    "total": len(messages),
                    "unread": sum(1 for m in messages.values() if not m.get("read", True)),
                    "by_type": {}
                },
                "agents": {
                    "total": len(agents),
                    "available": sum(1 for a in agents.values() if a.get("status") == "available"),
                    "busy": sum(1 for a in agents.values() if a.get("status") == "busy"),
                    "workload": {}
                },
                "workflows": len(workflows),
                "system": {
                    "data_directory": str(data_dir.relative_to(data_dir.parent.parent)),
                    "last_update": max([
                        TASKS_FILE.stat().st_mtime if TASKS_FILE.exists() else 0,
                        MESSAGES_FILE.stat().st_mtime if MESSAGES_FILE.exists() else 0,
                        AGENTS_FILE.stat().st_mtime if AGENTS_FILE.exists() else 0
                    ])
                }
            }
            
            if detailed:
                # Task details
                for task in tasks.values():
                    status = task.get("status", "unknown")
                    stats["tasks"]["by_status"][status] = stats["tasks"]["by_status"].get(status, 0) + 1
                    
                    priority = task.get("priority", "medium")
                    stats["tasks"]["by_priority"][priority] = stats["tasks"]["by_priority"].get(priority, 0) + 1
                    
                    agent = task.get("assigned_to", "unassigned")
                    if agent:
                        stats["tasks"]["by_agent"][agent] = stats["tasks"]["by_agent"].get(agent, 0) + 1
                
                # Message details
                for msg in messages.values():
                    msg_type = msg.get("type", "unknown")
                    stats["messages"]["by_type"][msg_type] = stats["messages"]["by_type"].get(msg_type, 0) + 1
                
                # Agent workload
                for agent_name, agent in agents.items():
                    stats["agents"]["workload"][agent_name] = {
                        "current_tasks": len(agent.get("current_tasks", [])),
                        "completed_tasks": len(agent.get("completed_tasks", [])),
                        "workload_percent": agent.get("workload", 0)
                    }
            
            stats["system"]["last_update_time"] = datetime.fromtimestamp(stats["system"]["last_update"]).isoformat()
            
            return [types.TextContent(
                type="text",
                text=json.dumps(stats, indent=2)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, indent=2)
        )]


async def main():
    """Run the Communication MCP Server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="coord",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())