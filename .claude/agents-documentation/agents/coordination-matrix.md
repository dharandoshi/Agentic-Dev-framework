# Agent Army Coordination Matrix

## Communication Hierarchy

```
Level 1: Strategic (Project Management)
├── scrum-master (Project Coordinator)
│
Level 2: Tactical (Technical Leadership)  
├── system-architect (Design Authority)
├── tech-lead (Implementation Director)
│
Level 3: Operational (Implementation)
├── requirements-analyst (Requirements & Design)
├── senior-backend-engineer (Backend Development)
├── senior-frontend-engineer (Frontend Development)
├── integration-engineer (External Integration)
├── data-engineer (Data & Analytics)
│
Level 4: Quality & Operations
├── qa-engineer (Quality Assurance)
├── security-engineer (Security)
├── devops-engineer (CI/CD & Deployment)
├── sre-engineer (Site Reliability)
├── performance-engineer (Performance)
├── cloud-architect (Infrastructure)
│
Level 5: Documentation
└── technical-writer (Documentation)
```

## Required Communication Tools by Role

### Level 1: Strategic Management
**scrum-master** (Orchestra Conductor)
- `task_create` - Create tasks for the team
- `task_assign` - Assign tasks to agents
- `task_list` - View all tasks
- `task_status` - Track task progress
- `workflow_start` - Initiate workflows
- `workflow_status` - Monitor workflow progress
- `agent_workload` - Check agent capacity
- `message_broadcast` - Broadcast to all agents

### Level 2: Technical Leadership
**system-architect** (Design Authority)
- `task_status` - Update design task status
- `task_handoff` - Hand off designs to tech-lead
- `message_send` - Communicate with teams
- `checkpoint_create` - Create design checkpoints

**tech-lead** (Implementation Director)
- `task_assign` - Assign to developers
- `task_list` - View development tasks
- `task_status` - Update implementation status
- `message_send` - Coordinate teams
- `agent_workload` - Check developer capacity
- `escalation_create` - Escalate blockers

### Level 3: Implementation Teams
**requirements-analyst**
- `task_status` - Update requirements status
- `task_handoff` - Hand off to architects
- `message_send` - Clarify requirements
- `checkpoint_create` - Save requirement versions

**senior-backend-engineer**
- `task_status` - Update backend progress
- `task_handoff` - Hand off to integration
- `message_send` - Coordinate with frontend
- `checkpoint_create` - Save code milestones
- `escalation_create` - Escalate technical issues

**senior-frontend-engineer**
- `task_status` - Update frontend progress
- `task_handoff` - Hand off to QA
- `message_send` - Coordinate with backend
- `checkpoint_create` - Save UI milestones
- `escalation_create` - Escalate UI/UX issues

**integration-engineer**
- `task_status` - Update integration status
- `task_handoff` - Hand off to testing
- `message_send` - Coordinate APIs

**data-engineer**
- `task_status` - Update data pipeline status
- `message_send` - Share data insights

### Level 4: Quality & Operations
**qa-engineer**
- `task_status` - Update test status
- `task_handoff` - Hand off to DevOps
- `message_send` - Report bugs
- `escalation_create` - Escalate quality issues

**security-engineer**
- `task_status` - Update security review
- `message_send` - Report vulnerabilities
- `escalation_create` - Escalate security risks

**devops-engineer**
- `task_status` - Update deployment status
- `task_handoff` - Hand off to SRE
- `message_send` - Deployment notifications
- `checkpoint_create` - Save deployment states

**sre-engineer**
- `task_status` - Update reliability status
- `message_send` - Incident notifications
- `escalation_create` - Escalate incidents

**cloud-architect**
- `task_status` - Update infrastructure status
- `message_send` - Infrastructure updates

### Level 5: Documentation
**technical-writer**
- `task_status` - Update documentation status
- `message_send` - Request clarifications

## Communication Flows

### 1. Feature Development Flow
```
scrum-master → requirements-analyst → system-architect → tech-lead
    ↓                                                         ↓
workflow_start                                    task_assign to:
                                                  - senior-backend-engineer
                                                  - senior-frontend-engineer
                                                  - data-engineer
```

### 2. Quality Assurance Flow
```
senior-backend-engineer/senior-frontend-engineer → qa-engineer → security-engineer
            ↓                                           ↓              ↓
     task_handoff                                task_handoff    escalation_create
```

### 3. Deployment Flow
```
qa-engineer → devops-engineer → sre-engineer → cloud-architect
      ↓              ↓               ↓              ↓
task_handoff  checkpoint_create  escalation   message_send
```

### 4. Incident Response Flow
```
sre-engineer → tech-lead → scrum-master
      ↓            ↓            ↓
escalation    task_assign  message_broadcast
```

### 5. Documentation Flow
```
all-agents → technical-writer
     ↓              ↓
message_send   task_status
```

## Coordination Rules

### Task Assignment Rules
1. Only `scrum-master` and `tech-lead` can assign tasks
2. Tasks flow downward in hierarchy
3. Escalations flow upward in hierarchy

### Handoff Rules
1. Handoffs must include context and artifacts
2. Receiving agent must acknowledge handoff
3. Handoffs create audit trail

### Message Rules
1. `message_broadcast` only for scrum-master
2. Direct messages for specific coordination
3. Escalations for blockers and critical issues

### Checkpoint Rules
1. Create checkpoints at major milestones
2. Include version and metadata
3. Enable rollback capability

## Expected Communication Patterns

### Daily Standup Pattern
```python
# Scrum Master initiates
scrum_master.workflow_start("daily_standup")
scrum_master.message_broadcast("Daily standup starting")

# Each agent reports
for agent in all_agents:
    agent.task_status(current_tasks)
    agent.message_send(blockers)
```

### Feature Implementation Pattern
```python
# Requirements → Design → Implementation
requirements_analyst.task_handoff(
    to="system-architect",
    artifacts=["requirements.md"]
)

system_architect.task_handoff(
    to="tech-lead", 
    artifacts=["architecture.md", "api-spec.yaml"]
)

tech_lead.task_assign(
    to=["senior-backend-engineer", "senior-frontend-engineer"],
    tasks=implementation_tasks
)
```

### Deployment Pattern
```python
# QA → DevOps → SRE
qa_engineer.task_handoff(
    to="devops-engineer",
    context={"tests_passed": True}
)

devops_engineer.checkpoint_create(
    name="pre-deployment",
    state=current_state
)

devops_engineer.task_handoff(
    to="sre-engineer",
    artifacts=["deployment.yaml"]
)
```

## Verification Checklist

- [ ] All agents have minimum required tools
- [ ] Hierarchy is properly established
- [ ] Handoff chains are complete
- [ ] Escalation paths are clear
- [ ] Message flows are bidirectional
- [ ] Checkpoints cover critical states
- [ ] Workload monitoring is active
- [ ] Broadcast capability exists