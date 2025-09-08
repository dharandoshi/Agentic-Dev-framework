---
allowed-tools: mcp__coord__system_reset
description: Reset Agent Army coordination system
argument-hint: [component: all/tasks/messages/agents]
---

<!-- Usage: /reset-army [component]
     Examples:
     /reset-army all        # Reset everything
     /reset-army tasks      # Reset only tasks
     /reset-army messages   # Reset only messages
     /reset-army agents     # Reset only agent data
     
     WARNING: This will permanently clear data!
     Default: all (if no component specified)
-->

Reset the Agent Army coordination system.

Component to reset: $1 (default: all)

Use mcp__coord__system_reset with component: "$1" and confirm: "RESET_CONFIRMED"

Warning: This will clear all data for the specified component.