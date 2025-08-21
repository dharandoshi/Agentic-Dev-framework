# Agent Army Delegation System

## Overview
The delegation system enables semi-automatic task delegation where agents can instruct each other and report back through the coordination chain.

## How It Works

### 1. Task Creation & Assignment
- **Scrum Master** creates high-level feature tasks
- Tasks are assigned to **Tech Lead** using `mcp__coord__task_assign`
- The orchestrator hook intercepts and triggers delegation

### 2. Automatic Delegation
When Tech Lead receives a task, the orchestrator:
- Creates subtasks for appropriate developers
- Sends delegation messages via `mcp__coord__message_send`
- Tracks task dependencies and status

### 3. Developer Work & Reporting
Developers:
- Receive task assignments through messages
- Complete their work
- Report back to Tech Lead using `mcp__coord__task_status`
- Send completion messages via `mcp__coord__message_send`

### 4. Tech Lead Aggregation
Tech Lead:
- Receives completion reports from developers
- Validates all subtasks are complete
- Reports feature completion to Scrum Master

### 5. Reporting Chain
```
Senior Backend Engineer ─┐
Senior Frontend Engineer ├─→ Tech Lead ─→ Scrum Master
QA Engineer ─────────────┘
```

## Key Components

### Orchestrator Hook (`hooks/orchestrator.py`)
- Intercepts MCP coordination tools
- Triggers delegation chains
- Enforces reporting structure
- Stores messages and reminders

### Coordination Data Storage
- `mcp/data/communication/tasks.json` - Task tracking
- `mcp/data/communication/messages.json` - Agent messages
- `mcp/data/communication/reminders.json` - Status check reminders
- `mcp/data/communication/sprint_summary.json` - Sprint progress

### Agent Boundaries
Each agent has self-contained boundaries in their `.md` file:
- **YOU CAN** - Allowed actions
- **YOU CANNOT** - Prohibited actions
- **YOU MUST COORDINATE** - Required handoffs

## Usage Examples

### Creating a Feature Task (Scrum Master)
```python
mcp__coord__task_create(
    title="Implement User Authentication",
    description="Add login/logout with JWT",
    created_by="scrum-master",
    priority="high"
)
```

### Assigning to Tech Lead
```python
mcp__coord__task_assign(
    task_id="task_123",
    agent_name="tech-lead"
)
# Orchestrator automatically triggers delegation
```

### Developer Reporting Back
```python
mcp__coord__task_status(
    task_id="task_123_backend",
    status="completed",
    progress=100
)
# Orchestrator creates report to tech-lead
```

### Tech Lead Reporting to Scrum Master
```python
mcp__coord__message_send(
    from_agent="tech-lead",
    to_agent="scrum-master",
    subject="Feature Complete",
    content="Authentication implemented and tested",
    type="status"
)
```

## Testing the System

Run the test script to see the full delegation chain:
```bash
python3 .claude/scripts/test_delegation.py
```

This demonstrates:
1. Task creation by Scrum Master
2. Delegation to Tech Lead
3. Sub-delegation to developers
4. Developer completion reports
5. Tech Lead aggregation
6. Final report to Scrum Master

## Current Limitations

1. **Semi-Automatic**: Requires Claude Code to trigger actions
2. **No Full Automation**: Can't run completely independently
3. **Message Polling**: Agents must check for messages

## Future Enhancements

1. **Webhook Integration**: Real-time message delivery
2. **Status Dashboard**: Visual task tracking
3. **Automated Reminders**: Follow-up on stalled tasks
4. **Performance Metrics**: Track completion times