---
allowed-tools: mcp__coord__task_create, mcp__coord__task_assign, mcp__coord__message_send
description: Coordinate tasks between agents
argument-hint: [action: create/assign/message] [details]
---

<!-- Usage: /army-coordinate [action] [details]
     Examples:
     /army-coordinate create "Build user authentication feature"
     /army-coordinate assign "task-123 to senior-backend-engineer"
     /army-coordinate message "from scrum-master to engineering-manager: Sprint planning complete"
     
     Actions:
     - create: Create a new task
     - assign: Assign task to an agent
     - message: Send message between agents
-->

Coordinate Agent Army task: $1

Details: $2

Use the appropriate coordination tools (mcp__coord__*) to manage agent collaboration.