---
allowed-tools: Task
description: Deploy specific agent from the army
argument-hint: [agent-name] [task-description]
---

<!-- Usage: /army-deploy [agent-name] [task-description]
     Examples:
     /army-deploy senior-backend-engineer "implement user authentication API"
     /army-deploy qa-engineer "write tests for login feature"
     /army-deploy devops-engineer "setup CI/CD pipeline"
     
     Available agents:
     - senior-frontend-engineer
     - senior-backend-engineer
     - qa-engineer
     - devops-engineer
     - security-engineer
     - data-engineer
     - system-architect
     - requirements-analyst
     - technical-writer
     - scrum-master
     - engineering-manager
-->

Deploy the $1 agent with the following mission:

$2

Use the Task tool with subagent_type: "$1" to activate this specialist from the Agent Army.