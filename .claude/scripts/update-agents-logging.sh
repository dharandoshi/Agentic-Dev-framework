#!/bin/bash

# Script to update all agent definitions with logging and monitoring tools

AGENTS_DIR=".claude/agents"
LOGGING_TOOLS="mcp__logging__log_event, mcp__logging__log_task_start, mcp__logging__log_task_complete, mcp__logging__log_task_failed, mcp__logging__log_handoff, mcp__logging__log_decision, mcp__logging__log_tool_use"
MONITORING_TOOLS="mcp__monitoring__heartbeat, mcp__monitoring__report_health, mcp__monitoring__report_performance, mcp__monitoring__report_metric"

echo "Updating all agents with logging and monitoring tools..."

for agent_file in $AGENTS_DIR/*.md; do
    agent_name=$(basename "$agent_file" .md)
    
    # Skip if already has logging tools
    if grep -q "mcp__logging__" "$agent_file"; then
        echo "✓ $agent_name already has logging tools"
        continue
    fi
    
    echo "Updating $agent_name..."
    
    # Add logging and monitoring tools to the tools line
    # This finds the tools: line and appends the new tools
    sed -i "/^tools:/ s/$/, $LOGGING_TOOLS, $MONITORING_TOOLS/" "$agent_file"
    
    # Add logging protocol section if it doesn't exist
    if ! grep -q "Logging and Monitoring Protocol" "$agent_file"; then
        # Find where to insert (before "Development Coordination Protocol" or at end of Purpose section)
        cat >> "$agent_file" << 'EOF'

## 📊 Logging and Monitoring Protocol

**CRITICAL**: You MUST log all significant activities using the logging and monitoring MCP servers.

### Task Lifecycle Logging
1. **Starting a task:**
   ```
   mcp__logging__log_task_start(
     agent="AGENT_NAME",
     task_id="<task_id>",
     description="<what you're doing>",
     estimated_duration=<minutes>
   )
   mcp__monitoring__heartbeat(agent="AGENT_NAME", task_count=<active_tasks>)
   ```

2. **Making decisions:**
   ```
   mcp__logging__log_decision(
     agent="AGENT_NAME",
     decision="<decision made>",
     rationale="<why this decision>",
     alternatives=["option1", "option2"],
     task_id="<task_id>"
   )
   ```

3. **Delegating/Handing off work:**
   ```
   mcp__logging__log_handoff(
     from_agent="AGENT_NAME",
     to_agent="<target_agent>",
     task_id="<task_id>",
     handoff_reason="<why delegating>",
     context={...}
   )
   ```

4. **Completing tasks:**
   ```
   mcp__logging__log_task_complete(
     agent="AGENT_NAME",
     task_id="<task_id>",
     result="success|partial|skipped",
     outputs={...}
   )
   mcp__monitoring__report_performance(
     agent="AGENT_NAME",
     operation="<operation_name>",
     duration_ms=<duration>,
     success=true
   )
   ```

5. **Error handling:**
   ```
   mcp__logging__log_task_failed(
     agent="AGENT_NAME",
     task_id="<task_id>",
     error="<error_message>",
     recovery_action="<what_to_do_next>"
   )
   ```

### Regular Monitoring
- Send heartbeat every 5 minutes: `mcp__monitoring__heartbeat(agent="AGENT_NAME")`
- Log all significant events and decisions
- Report performance metrics for operations
EOF
        
        # Replace AGENT_NAME with actual agent name
        sed -i "s/AGENT_NAME/$agent_name/g" "$agent_file"
    fi
    
    echo "✓ Updated $agent_name"
done

echo ""
echo "✅ All agents updated with logging and monitoring capabilities!"
echo ""
echo "Summary:"
echo "- Added logging tools to all agents"
echo "- Added monitoring tools to all agents"
echo "- Added logging protocol documentation to each agent"