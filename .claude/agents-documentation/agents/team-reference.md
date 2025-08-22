# Agent Team Reference

## Complete Agent Directory (15 Agents)

### 🎯 Hierarchical Organization

#### Level 1: Strategic Management
| Agent | Specialization | Key Responsibilities | MCP Tools |
|-------|---------------|---------------------|-----------|
| **scrum-master** | Agile Project Management | Sprint planning, backlog management, team coordination | coord, docs, workspace |
| **requirements-analyst** | Requirements Gathering | Interactive requirement gathering, validation, documentation | docs, workspace |

#### Level 2: Technical Leadership  
| Agent | Specialization | Key Responsibilities | MCP Tools |
|-------|---------------|---------------------|-----------|
| **system-architect** | System Design | Architecture design, database schemas, API contracts | workspace, docs, validation |
| **tech-lead** | Code Quality & Standards | Code reviews, technical standards, design patterns | All MCP tools |

#### Level 3: Core Development
| Agent | Specialization | Key Responsibilities | MCP Tools |
|-------|---------------|---------------------|-----------|
| **senior-backend-engineer** | Backend Development | API development, database optimization, microservices | All MCP tools |
| **senior-frontend-engineer** | Frontend Development | UI/UX implementation, responsive design, performance | All MCP tools |  
| **integration-engineer** | Third-party Integration | External service integration, webhooks, message queues | workspace, execution, docs |
| **data-engineer** | Data Infrastructure | ETL pipelines, data warehouses, streaming, analytics | workspace, execution, coord, docs |

#### Level 4: Quality & Operations
| Agent | Specialization | Key Responsibilities | MCP Tools |
|-------|---------------|---------------------|-----------|
| **qa-engineer** | Quality Assurance | Test planning, test cases, bug tracking, acceptance testing | workspace, validation, execution, coord, docs |
| **security-engineer** | Security Implementation | Security audits, vulnerability assessment, compliance | workspace, validation, execution, coord, docs |
| **devops-engineer** | CI/CD & Deployment | Pipeline setup, containerization, infrastructure as code | workspace, execution, coord, docs |
| **sre-engineer** | Site Reliability | Monitoring, incident response, system resilience | workspace, execution, coord, docs |
| **cloud-architect** | Cloud Infrastructure | Cloud design, multi-cloud strategies, serverless | workspace, execution, coord, docs |

#### Level 5: Documentation & Support
| Agent | Specialization | Key Responsibilities | MCP Tools |
|-------|---------------|---------------------|-----------|
| **technical-writer** | Documentation | API docs, developer guides, system documentation | docs, workspace |

## Agent Coordination Framework

### Communication Protocol
All agents use standardized MCP coordination tools:
- `mcp__coord__task_create` - Create new tasks
- `mcp__coord__task_assign` - Assign tasks to agents  
- `mcp__coord__task_status` - Update task progress
- `mcp__coord__task_handoff` - Transfer work between agents
- `mcp__coord__message_send` - Direct agent communication
- `mcp__coord__workflow_start` - Initiate workflows
- `mcp__coord__escalation_create` - Escalate issues

### Standard Handoff Chains
```
requirements-analyst → system-architect → tech-lead → engineers
engineers → qa-engineer → devops-engineer → sre-engineer  
Any agent → tech-lead (code review)
Any agent → scrum-master (project issues)
```

## Tool Distribution by Agent Type

### Full Stack Engineers (2 agents)
**Tools**: All MCP tools across 6 servers (core + project-management)
- senior-backend-engineer
- senior-frontend-engineer

### Specialized Engineers (7 agents)  
**Tools**: Subset based on specialization
- integration-engineer, data-engineer, qa-engineer
- security-engineer, devops-engineer, sre-engineer, cloud-architect

### Architects & Leads (2 agents)
**Tools**: Analysis and coordination focused
- system-architect, tech-lead

### Management & Documentation (4 agents)
**Tools**: Communication and documentation focused
- scrum-master, requirements-analyst, technical-writer, god-agent

## Agent Capabilities Matrix

### Development Capabilities
| Capability | Backend | Frontend | Integration | Data | QA | Security | DevOps | SRE | Cloud |
|------------|---------|----------|-------------|------|----|---------|---------|----|-------|
| Code Implementation | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Code Review | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Testing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Deployment | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Monitoring | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |

### Coordination Capabilities
All agents can:
- ✅ Create and update task status
- ✅ Send messages to other agents  
- ✅ Hand off work following proper chains
- ✅ Escalate issues when blocked
- ✅ Access project documentation

## Usage Guidelines

### Agent Invocation Best Practices
1. **Direct Assignment**: Use `@agent-name` for specific tasks
2. **Chain Command**: Follow hierarchical handoff patterns
3. **Parallel Work**: Use scrum-master to coordinate multiple agents
4. **Escalation**: Route issues through proper channels

### Task Coordination Examples

#### Feature Development Flow
```
1. @requirements-analyst gather requirements for user authentication
2. Auto-handoff to @system-architect for design  
3. Auto-handoff to @tech-lead for implementation planning
4. @tech-lead assigns to @senior-backend-engineer and @senior-frontend-engineer
5. Engineers hand off to @qa-engineer for testing
6. @qa-engineer hands off to @devops-engineer for deployment
```

#### Issue Resolution Flow
```
1. Any agent detects issue
2. Escalate to @tech-lead (technical) or @scrum-master (process)
3. Lead triages and assigns to appropriate specialist
4. Specialist resolves and reports back
5. Lead validates resolution
```

## Agent Status Management

### Status Types
- **available**: Ready for new tasks
- **busy**: Currently executing assigned work
- **blocked**: Waiting for dependencies or escalation
- **offline**: Not available for task assignment

### Workload Monitoring
Use `mcp__coord__agent_workload` to check capacity before assignment.

---

**Total Agents**: 15  
**MCP Servers**: 6 (core + project-management)  
**Coordination System**: orchestrator.py hook + MCP coord server  
**Last Updated**: 2025-08-22