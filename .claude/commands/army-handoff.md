---
allowed-tools: mcp__coord__task_handoff
description: Hand off task from one agent to another
argument-hint: [from-agent] [to-agent] [task-id]
---

<!-- Usage: /army-handoff [from-agent] [to-agent] [task-id]
     Examples:
     /army-handoff senior-backend-engineer qa-engineer task-123
     /army-handoff requirements-analyst system-architect task-456
     /army-handoff engineering-manager scrum-master task-789
     
     This transfers a task from one agent to another with:
     - Full context preservation
     - Artifact transfer
     - Handoff tracking
-->

Hand off task from $1 to $2

Task ID: $3

Use mcp__coord__task_handoff to transfer the task with proper context and artifacts.