# Agent Specifications

This directory contains the complete specifications for all 15 agents in the Agent Army system.

## Agent List

### Level 1: Strategic Management
- **scrum-master** - Agile project management and sprint coordination
- **requirements-analyst** - Requirements gathering and validation

### Level 2: Technical Leadership
- **system-architect** - System design and architecture
- **engineering-manager** - Parallel task orchestration and quality verification

### Level 3: Core Development
- **senior-backend-engineer** - Backend development and APIs
- **senior-frontend-engineer** - Frontend development and UI/UX
- **data-engineer** - Data pipelines and analytics

### Level 4: Quality & Operations
- **qa-engineer** - Testing and quality assurance
- **security-engineer** - Security and compliance
- **devops-engineer** - CI/CD and deployment

### Level 5: Documentation
- **technical-writer** - Documentation and guides

### Special Agents
- **god-agent** - Meta-agent for agent management

## Agent File Locations

All agent specifications are stored in `.claude/agents/` directory:

```
.claude/agents/
├── scrum-master.md
├── requirements-analyst.md
├── system-architect.md
├── engineering-manager.md
├── senior-backend-engineer.md
├── senior-frontend-engineer.md
├── data-engineer.md
├── qa-engineer.md
├── security-engineer.md
├── devops-engineer.md
├── technical-writer.md
├── god-agent.md
└── agent-registry.json
```

## Agent Structure

Each agent specification follows a standard format:

```markdown
# Agent Name

## Purpose
Brief description of the agent's role

## Instructions
Detailed instructions for the agent

## Role Boundaries
### ✅ YOU CAN:
- Allowed actions

### ❌ YOU ABSOLUTELY CANNOT:
- Prohibited actions

### 🔄 YOU MUST COORDINATE WITH:
- Required handoffs

## Commands
- Available commands

## Report / Response
Expected output format
```

## Usage

To invoke an agent, use:
```
Act as [agent-name] and [task description]
```

Example:
```
Act as senior-backend-engineer and implement user authentication
```

## Coordination

Agents coordinate through:
- MCP coordination tools
- Orchestrator hook system
- Defined handoff patterns
- Standard communication protocols

Refer to [coordination-matrix.md](coordination-matrix.md) for detailed coordination rules.