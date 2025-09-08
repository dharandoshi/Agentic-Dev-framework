---
allowed-tools: mcp__logging__log_task_start, mcp__logging__log_task_complete, mcp__logging__log_event
description: Log Agent Army task progress
argument-hint: [action: start/complete/event] [details]
---

<!-- Usage: /army-log [action] [details]
     Examples:
     /army-log start "task-123 by senior-backend-engineer: API implementation"
     /army-log complete "task-123 success: All tests passing"
     /army-log event "Escalation from qa-engineer to engineering-manager"
     
     Actions:
     - start: Log task beginning
     - complete: Log task completion
     - event: Log general event or milestone
-->

Log Agent Army activity: $1

Details: $2

Use the appropriate logging tools to track agent activities and maintain audit trails.