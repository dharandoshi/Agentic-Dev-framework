---
allowed-tools: mcp__coord__system_reset, mcp__logging__query_logs, Bash
description: Reset Agent Army coordination system and logs
argument-hint: [component: all/tasks/messages/agents/logs]
---

<!-- Usage: /reset-army [component]
     Examples:
     /reset-army all        # Reset everything (coordination + logs)
     /reset-army tasks      # Reset only tasks
     /reset-army messages   # Reset only messages
     /reset-army agents     # Reset only agent data
     /reset-army logs       # Reset only logs
     
     WARNING: This will permanently clear data!
     Default: all (if no component specified)
-->

Reset the Agent Army coordination system and/or logs.

Component to reset: $1 (default: all)

If component is "logs" or "all":
1. First check if logs exist using mcp__logging__query_logs with limit: 1
2. Use Bash to remove all log files and databases:
   - Run: rm -f data/communication/logs.db
   - Run: rm -f .claude/.claude/logs/startup-validation.log
   - Run: rm -f .claude/mcp/logs/document-registry.log
   - Run: rm -f logs/*.jsonl
   - Confirm deletion with message "All logs cleared successfully"

If component is not "logs":
1. Use mcp__coord__system_reset with component: "$1" (or "all" if not specified) and confirm: "RESET_CONFIRMED"

If component is "all":
1. Do both the coordination reset AND the log deletion

Warning: This will permanently clear all data for the specified component.