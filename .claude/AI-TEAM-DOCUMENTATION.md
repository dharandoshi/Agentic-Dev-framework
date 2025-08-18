# AI Development Team Documentation

## Overview
This document provides a comprehensive overview of the AI development team agents, their specializations, and coordination system. The team consists of 27 specialized agents working through a standardized communication protocol to deliver production-grade software.

### Coordination System
All agents follow the standardized communication protocol defined in `.claude/agents/team-coordination.md`. The system ensures seamless collaboration through:
- Unified message format with UUID tracking
- Hierarchical task flow from strategic to implementation levels
- Real-time status broadcasting and monitoring
- Clear escalation paths and dependency resolution
- Parallel execution capabilities with synchronization points

## Agent Directory

### 🎯 Agent Hierarchy

#### Level 0: Meta Management
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **god** | Agent Architecture & Management | opus | Creates/modifies agents, manages agent configurations, maintains agent registry |

#### Level 1: Strategic Decision Makers
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **product-owner** | Business Decisions | opus | Defines acceptance criteria, prioritizes features, manages roadmap |
| **system-architect** | Technical Architecture | opus | Transforms requirements into system design, database schemas, API contracts |
| **cloud-architect** | Cloud Infrastructure | sonnet | Cloud design, multi-cloud strategies, serverless, cost optimization |

#### Level 2: Tactical Coordinators
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **scrum-master** | Agile Project Management | sonnet | Sprint planning, task assignment, team coordination, backlog management |
| **tech-lead** | Code Quality & Standards | opus | Code reviews, enforces standards, design patterns, technical mentorship |

#### Level 3: Operational Orchestration
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **team-orchestrator** | Workflow Coordination | sonnet | Orchestrates multi-agent workflows, dependency resolution, resource management |

### 🛠️ Level 4: Implementation Teams

#### 💻 Development Team
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **senior-backend-engineer** | Backend Development | sonnet | API development, database optimization, microservices, server performance |
| **senior-frontend-engineer** | Frontend Development | sonnet | UI/UX implementation, responsive design, performance optimization |
| **database-engineer** | Database Design | sonnet | Schema design, query optimization, migrations, indexing strategies |
| **api-designer** | API Architecture | sonnet | RESTful/GraphQL design, OpenAPI documentation, versioning |
| **integration-engineer** | Third-party Integrations | sonnet | External service integration, webhooks, message queues |
| **data-engineer** | Data Infrastructure | sonnet | ETL pipelines, data warehouse, streaming, data integration |

#### 🧪 Quality Assurance
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **qa-engineer** | Quality Assurance | sonnet | Test planning, test cases, bug tracking, acceptance testing |
| **automation-engineer** | Test Automation | sonnet | Automated tests, E2E scenarios, integration tests, CI testing |
| **performance-engineer** | Performance Testing | sonnet | Load testing, bottleneck identification, optimization strategies |

#### 🚀 Operations & Infrastructure
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **devops-engineer** | CI/CD & Deployment | sonnet | Pipeline setup, containerization, infrastructure as code |
| **sre-engineer** | Site Reliability | sonnet | Monitoring, incident response, system resilience, uptime |

#### 🔒 Security & Compliance
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **security-engineer** | Security Implementation | sonnet | Security audits, vulnerability assessment, penetration testing |
| **compliance-officer** | Regulatory Compliance | opus | GDPR/HIPAA/SOC2, audit trails, data privacy, documentation |

#### 📝 Documentation & Analytics
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **technical-writer** | Technical Documentation | sonnet | API docs, developer guides, system documentation |
| **ux-writer** | User Content | haiku | UI copy, error messages, onboarding content, tooltips |
| **analytics-engineer** | Analytics & Metrics | sonnet | KPI definition, dashboards, A/B testing, business intelligence |
| **project-initializer** | Project Setup | sonnet | Parses documentation, extracts requirements, initializes backlogs |
| **requirements-analyst** | Requirements Gathering | opus | Interactive BA that gathers requirements through conversation, validates concepts |
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **technical-writer** | Technical Documentation | sonnet | API docs, developer guides, system documentation |
| **ux-writer** | User Content | haiku | UI copy, error messages, onboarding content, tooltips |
| **analytics-engineer** | Analytics & Metrics | sonnet | KPI definition, dashboards, A/B testing, business intelligence |

#### 🎉 Utility Agents
| Agent Name | Specialization | Model | Key Responsibilities |
|------------|---------------|--------|---------------------|
| **hello-world-agent** | Greeting | haiku | Simple greeting responses |

## Agent Coordination Infrastructure

The team uses the following coordination infrastructure located in `.claude/agents/`:

### Core Files
- **team-coordination.md** - Complete communication protocol and coordination system
- **agent-registry.json** - Real-time agent status and hierarchy tracking
- **Individual agent files** - 27 specialized agent definitions with embedded protocols

### Working Directory Structure
Agents work within the actual project structure (not a fake `core/` directory):
- Agents analyze and work with existing project files
- No predefined directory structure is enforced
- Agents adapt to the project's actual organization
- Communication happens through the protocol, not file directories

## Agent Communication Protocol

### Message Format
All agents communicate using the standardized format defined in `.claude/agents/team-coordination.md`:

```json
{
  "id": "uuid-v4",
  "from": "sending-agent-name",
  "to": "receiving-agent-name",
  "type": "task|report|query|response|notification|status|handoff",
  "priority": "critical|high|medium|low",
  "subject": "brief description",
  "payload": {
    "content": "detailed message content",
    "context": {},
    "dependencies": [],
    "deadline": "ISO-8601 (optional)",
    "artifacts": []
  },
  "status": "pending|in_progress|completed|blocked|failed",
  "timestamp": "ISO-8601",
  "correlation_id": "original-request-id",
  "thread_id": "conversation-thread-id"
}
```

### Agent Status States
- **available**: Ready to receive tasks
- **busy**: Currently executing a task
- **blocked**: Waiting for dependencies
- **error**: Task failed, needs intervention
- **offline**: Agent not available

## Workflow Example

### Task Flow Through Hierarchy

1. **Strategic Level (Level 1)**
   - `product-owner` defines business requirements
   - `system-architect` creates technical design
   - `cloud-architect` designs infrastructure

2. **Tactical Level (Level 2)**
   - `scrum-master` receives requirements from product-owner
   - Plans sprints and breaks down into tasks
   - `tech-lead` defines technical standards

3. **Operational Level (Level 3)**
   - `team-orchestrator` receives tasks from scrum-master
   - Checks agent availability
   - Assigns tasks to implementation agents
   - Resolves dependencies

4. **Implementation Level (Level 4)**
   - Agents receive tasks from team-orchestrator
   - Report progress at 25%, 50%, 75%, 100%
   - Escalate blockers to appropriate level
   - Hand off completed work to tech-lead for review

### Parallel Execution Example
```json
{
  "type": "task",
  "from": "team-orchestrator",
  "to": "broadcast",
  "payload": {
    "parallel": true,
    "tasks": [
      {"agent": "database-engineer", "task": "design-schema"},
      {"agent": "api-designer", "task": "design-endpoints"},
      {"agent": "senior-frontend-engineer", "task": "design-ui"}
    ]
  }
}
```

## Production Standards

All agents adhere to these production standards:

### Code Quality
- ✅ No stub code or TODOs
- ✅ Complete error handling
- ✅ Minimum 80% test coverage
- ✅ Performance benchmarks met
- ✅ Security vulnerabilities: zero

### Documentation
- ✅ Inline code documentation
- ✅ API documentation
- ✅ User guides
- ✅ Deployment instructions

### Testing
- ✅ Unit tests
- ✅ Integration tests
- ✅ E2E tests
- ✅ Performance tests
- ✅ Security tests

### Deployment
- ✅ Containerized applications
- ✅ Infrastructure as Code
- ✅ CI/CD pipelines
- ✅ Monitoring and alerting
- ✅ Rollback procedures

## Escalation Paths

### Technical Issues
`implementation-agent → tech-lead → system-architect`

### Scope/Requirement Issues
`implementation-agent → scrum-master → product-owner`

### Resource Conflicts
`implementation-agent → team-orchestrator → scrum-master`

### Critical Failures
`any-agent → scrum-master → broadcast to all coordinators`

## Usage Guidelines

### Starting a New Project
1. Invoke `requirements-analyst` to gather requirements interactively
2. Invoke `project-initializer` to parse requirements into tasks
3. Invoke `scrum-master` to plan sprints and prioritize
4. Let `team-orchestrator` manage task distribution

### Agent Invocation Methods
- **Automatic**: Based on task keywords matching agent specialization
- **Explicit**: By mentioning agent name directly
- **Hierarchical**: Through proper chain of command
- **Parallel**: Via team-orchestrator for concurrent tasks

### Communication Best Practices
1. Always include correlation_id for task tracking
2. Use appropriate priority levels (critical > high > medium > low)
3. Report status changes immediately
4. Include artifacts in handoff messages
5. Escalate blockers through proper channels

## Maintenance

### Adding New Agents
Use `god-agent` to create new agents with proper configuration

### Updating Agents
Use `god-agent` to modify existing agent capabilities

### Agent Health Checks
- Check `agent-registry.json` for current agent status
- team-orchestrator monitors agent availability
- scrum-master tracks task completion rates

---

*Last Updated: 2025-08-06*
*Total Agents: 27*
*Models Used: Opus (7), Sonnet (18), Haiku (2)*