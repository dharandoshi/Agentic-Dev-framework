# Claude Hooks Guide for Agent Army

## Overview
Claude hooks are shell commands that execute automatically during your Claude Code session. They can intercept, modify, or log interactions between you and Claude, as well as Claude's tool usage.

## Available Hooks

### 1. User Prompt Submit Hook
**When it runs:** Before your message is sent to Claude
**Use cases:**
- Add context automatically
- Enforce coding standards
- Log all prompts
- Block sensitive information

### 2. Agent Prompt Submit Hook  
**When it runs:** Before Claude executes a tool
**Use cases:**
- Validate tool parameters
- Enforce security policies
- Log tool usage
- Modify tool behavior

### 3. Tool Result Hook
**When it runs:** After a tool completes execution
**Use cases:**
- Process tool output
- Log results
- Trigger notifications
- Update external systems

## Hook Response Format

Hooks must return a JSON response:

```json
{
    "action": "allow" | "block" | "modify",
    "message": "Optional message to display",
    "modifiedPrompt": "Modified prompt (only for modify action)",
    "metadata": { /* optional metadata */ }
}
```

## Setting Up Hooks

### 1. Create Hook Scripts
Place your hook scripts in `.claude/hooks/` directory:

```bash
.claude/
└── hooks/
    ├── log-agent-communication.py
    ├── enforce-coordination.py
    └── auto-todo-tracker.sh
```

### 2. Update Settings
Add hooks to your Claude settings (`~/.claude/settings.json` or project-specific):

```json
{
  "hooks": {
    "user-prompt-submit-hook": {
      "command": "bash",
      "args": [".claude/hooks/auto-todo-tracker.sh"]
    },
    "agent-prompt-submit-hook": {
      "command": "python3",
      "args": [".claude/hooks/log-agent-communication.py"]
    }
  }
}
```

## Agent Army Specific Hooks

### 1. Communication Logger (`log-agent-communication.py`)
**Purpose:** Track all agent coordination
**Features:**
- Logs all mcp__communication__ tool usage
- Creates daily log files
- Tracks task handoffs and escalations

### 2. Coordination Enforcer (`enforce-coordination.py`)
**Purpose:** Enforce agent hierarchy rules
**Features:**
- Only scrum-master can broadcast
- Only scrum-master and engineering-manager can assign tasks
- Validates escalation paths

### 3. Auto Todo Tracker (`auto-todo-tracker.sh`)
**Purpose:** Remind about task tracking
**Features:**
- Detects when tasks are mentioned
- Suggests using TodoWrite tool
- Helps maintain task visibility

## Example Hook Workflows

### Workflow 1: Logging Agent Communication
```python
# When Claude uses: mcp__communication__task_assign
# Hook logs: timestamp, from_agent, to_agent, task_id
# Output: .claude/logs/agent-communication-20240819.jsonl
```

### Workflow 2: Enforcing Hierarchy
```python
# User asks: "As data-engineer, broadcast message to all"
# Hook detects: data-engineer trying to use message_broadcast
# Hook blocks: "Only scrum-master can broadcast"
```

### Workflow 3: Auto Task Tracking
```bash
# User says: "Implement user authentication with OAuth"
# Hook detects: Implementation task mentioned
# Hook suggests: "Consider using TodoWrite tool"
```

## Advanced Hook Patterns

### 1. Chain of Command Validation
```python
def validate_chain_of_command(from_agent, to_agent, action):
    """Ensure communication follows hierarchy"""
    hierarchy = {
        1: ["scrum-master"],
        2: ["system-architect", "engineering-manager"],
        3: ["senior-backend-engineer", "senior-frontend-engineer"],
    }
    # Validate based on levels
```

### 2. Automatic Context Injection
```python
def inject_agent_context(prompt, current_agent):
    """Add agent-specific context to prompts"""
    context = load_agent_profile(current_agent)
    return f"[Acting as {current_agent}]\n{context}\n\n{prompt}"
```

### 3. Workflow State Tracking
```python
def track_workflow_state(tool_name, parameters):
    """Maintain workflow state across sessions"""
    state = load_workflow_state()
    state.update_from_tool_call(tool_name, parameters)
    save_workflow_state(state)
```

## Environment Variables

Hooks receive these environment variables:
- `CLAUDE_HOOK_INPUT` - JSON with prompt/tool details
- `CLAUDE_SESSION_ID` - Current session identifier
- `CLAUDE_PROJECT_ROOT` - Project root directory
- `CLAUDE_CURRENT_FILE` - Currently open file (if any)

## Testing Hooks

### Test Individual Hook:
```bash
# Test user prompt hook
export CLAUDE_HOOK_INPUT='{"prompt": "Create a new feature"}'
python3 .claude/hooks/auto-todo-tracker.sh

# Test tool hook
export CLAUDE_HOOK_INPUT='{"tool": {"name": "mcp__communication__task_assign"}}'
python3 .claude/hooks/log-agent-communication.py
```

### Debug Hook Output:
```bash
# Enable debug logging
export CLAUDE_HOOK_DEBUG=true
```

## Best Practices

1. **Keep hooks fast** - They run synchronously and can slow down interactions
2. **Always return valid JSON** - Invalid responses will cause errors
3. **Use "allow" by default** - Only block when necessary
4. **Log errors gracefully** - Don't let hook errors break the session
5. **Test thoroughly** - Hooks can significantly impact workflow

## Security Considerations

1. **Validate all inputs** - Hooks receive user input
2. **Sanitize file paths** - Prevent directory traversal
3. **Limit permissions** - Run hooks with minimal privileges
4. **No sensitive data** - Don't log passwords or keys
5. **Rate limiting** - Prevent hook abuse

## Troubleshooting

### Hook not running:
- Check file permissions (`chmod +x`)
- Verify path in settings
- Check JSON syntax in settings

### Hook blocking everything:
- Ensure "allow" is default action
- Check error handling
- Review blocking conditions

### Performance issues:
- Profile hook execution time
- Move heavy operations to async
- Cache frequently used data

## Integration with Agent Army

The hooks integrate with the Communication MCP server to:
1. Track all agent communications
2. Generate coordination reports
3. Enforce role-based permissions
4. Maintain audit trails
5. Detect coordination issues

Use hooks to enhance the agent army's coordination and maintain proper command structure!