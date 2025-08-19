#!/usr/bin/env python3
"""
Monitoring Integration Hook
Connects Claude Code events to the Agent Army monitoring system
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

try:
    from monitoring_system import AgentArmyMonitor, MonitoringEvent, EventType, AlertSeverity
    monitor = AgentArmyMonitor()
except ImportError:
    monitor = None

def main():
    """Process Claude Code hook event and send to monitoring"""
    
    # Read hook input from stdin
    input_data = sys.stdin.read()
    
    try:
        event = json.loads(input_data) if input_data else {}
    except json.JSONDecodeError:
        event = {"error": "Invalid JSON input"}
    
    if not monitor:
        # If monitoring not available, just pass through
        print(json.dumps({"status": "monitoring_unavailable"}))
        return
    
    # Determine event type from hook context
    hook_type = event.get("hook_type", os.environ.get("CLAUDE_HOOK_TYPE", "unknown"))
    
    # Map Claude Code events to monitoring events
    if hook_type == "ToolUse":
        handle_tool_use(event)
    elif hook_type == "UserPromptSubmit":
        handle_user_prompt(event)
    elif hook_type == "Stop":
        handle_stop_event(event)
    elif hook_type == "Error":
        handle_error_event(event)
    else:
        handle_generic_event(event)
    
    # Return success to Claude Code
    print(json.dumps({"status": "monitored"}))

def handle_tool_use(event):
    """Monitor tool usage"""
    tool_name = event.get("tool", "unknown")
    agent = event.get("agent", "claude")
    success = event.get("success", True)
    
    if not success:
        # Log tool failure
        monitor.add_event(MonitoringEvent(
            timestamp=datetime.now(),
            event_type=EventType.AGENT_ERROR,
            severity=AlertSeverity.MEDIUM,
            component=f"{agent}/{tool_name}",
            message=f"Tool execution failed: {tool_name}",
            details=event
        ))
    
    # Track MCP tool usage
    if tool_name.startswith("mcp__"):
        server = tool_name.split("__")[1] if "__" in tool_name else "unknown"
        
        if not success:
            monitor.add_event(MonitoringEvent(
                timestamp=datetime.now(),
                event_type=EventType.MCP_FAILURE,
                severity=AlertSeverity.HIGH,
                component=f"MCP/{server}",
                message=f"MCP tool failure: {tool_name}",
                details=event
            ))

def handle_user_prompt(event):
    """Monitor user interactions"""
    prompt = event.get("prompt", "")
    
    # Track agent invocations
    if "Act as" in prompt:
        agent = extract_agent_name(prompt)
        monitor.add_event(MonitoringEvent(
            timestamp=datetime.now(),
            event_type=EventType.SYSTEM_HEALTH,
            severity=AlertSeverity.INFO,
            component=f"Agent/{agent}",
            message=f"Agent invoked: {agent}",
            details={"prompt_snippet": prompt[:100]}
        ))

def handle_stop_event(event):
    """Monitor task completion"""
    duration = event.get("duration", 0)
    agent = event.get("agent", "claude")
    
    if duration > 300:  # More than 5 minutes
        monitor.add_event(MonitoringEvent(
            timestamp=datetime.now(),
            event_type=EventType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.MEDIUM,
            component=agent,
            message=f"Long-running task: {duration}s",
            details=event
        ))

def handle_error_event(event):
    """Monitor errors"""
    error_type = event.get("error_type", "unknown")
    message = event.get("message", "Unknown error")
    
    severity = AlertSeverity.HIGH if "critical" in message.lower() else AlertSeverity.MEDIUM
    
    monitor.add_event(MonitoringEvent(
        timestamp=datetime.now(),
        event_type=EventType.AGENT_ERROR,
        severity=severity,
        component="Claude",
        message=message,
        details=event
    ))

def handle_generic_event(event):
    """Handle any other events"""
    monitor.add_event(MonitoringEvent(
        timestamp=datetime.now(),
        event_type=EventType.SYSTEM_HEALTH,
        severity=AlertSeverity.INFO,
        component="System",
        message="Generic event",
        details=event
    ))

def extract_agent_name(prompt):
    """Extract agent name from prompt"""
    if "Act as" in prompt:
        parts = prompt.split("Act as")[1].split()
        if parts:
            return parts[0].strip().replace("-", "_")
    return "unknown"

if __name__ == "__main__":
    main()