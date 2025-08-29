# Agent Coordination Guide

## Overview

This guide explains how agents coordinate work using the MCP coordination system. All agents follow standardized communication patterns to ensure efficient collaboration and proper task handoffs.

## 🔄 Coordination Workflow

### Standard Work Flow
```
1. Task Creation (scrum-master)
2. Requirements Gathering (requirements-analyst)  
3. System Design (system-architect)
4. Implementation Planning (engineering-manager)
5. Development (engineers)
6. Quality Assurance (qa-engineer)
7. Deployment (devops-engineer)
```

### Handoff Chain Rules
| From Agent | To Agent | Trigger |
|------------|----------|---------|
| requirements-analyst | system-architect | Requirements complete |
| system-architect | engineering-manager | Design approved |
| engineering-manager | Engineers | Tasks assigned |
| Engineers | qa-engineer | Implementation complete |
| qa-engineer | devops-engineer | Tests passing |

## 🛠️ Coordination Tools

### Core Coordination Commands

#### Task Management
```python
# Create new task (scrum-master only)
mcp__coord__task_create(
    task_id="FEAT-001",
    title="User Authentication System",
    description="Implement OAuth 2.0 login with JWT tokens",
    priority="high"
)

# Assign task to agent  
mcp__coord__task_assign(
    task_id="FEAT-001",
    agent_name="requirements-analyst"
)

# Update task progress
mcp__coord__task_status(
    task_id="FEAT-001", 
    status="in_progress",
    progress=25,
    notes="Requirements gathering started"
)
```

#### Agent Communication
```python
# Send direct message
mcp__coord__message_send(
    to_agent="senior-backend-engineer",
    subject="API Design Review",
    content="Please review the authentication endpoints design",
    priority="medium"
)

# Hand off completed work
mcp__coord__task_handoff(
    task_id="FEAT-001",
    from_agent="requirements-analyst",
    to_agent="system-architect", 
    artifacts=["requirements.md", "user-stories.md", "acceptance-criteria.md"]
)
```

#### Workflow Orchestration
```python
# Start multi-agent workflow
mcp__coord__workflow_start(
    workflow_type="feature_development",
    participants=["system-architect", "senior-backend-engineer", "senior-frontend-engineer"],
    config={"parallel_development": true, "review_required": true}
)

# Escalate blocking issue
mcp__coord__escalation_create(
    task_id="FEAT-001",
    reason="Third-party API documentation incomplete", 
    severity="medium",
)
```

## 📋 Task Status Management

### Status Types
- **pending**: Task created, not yet started
- **in_progress**: Agent actively working on task
- **review**: Work complete, awaiting review
- **blocked**: Cannot proceed due to dependencies
- **completed**: Task fully finished and verified
- **failed**: Task could not be completed

### Progress Reporting
Agents should report progress at key milestones:
- **25%**: Initial analysis/planning complete
- **50%**: Core implementation started  
- **75%**: Implementation complete, testing started
- **100%**: All work complete, ready for handoff

### Example Progress Updates
```python
# Requirements gathering progress
mcp__coord__task_status(
    task_id="FEAT-001",
    status="in_progress", 
    progress=25,
    notes="Stakeholder interviews completed, documenting requirements"
)

# Implementation progress
mcp__coord__task_status(
    task_id="FEAT-001",
    status="in_progress",
    progress=75, 
    notes="Authentication service implemented, unit tests 85% complete"
)

# Ready for handoff
mcp__coord__task_status(
    task_id="FEAT-001",
    status="review",
    progress=100,
    notes="Implementation complete with 95% test coverage"
)
```

## 🏗️ Workflow Patterns

### Sequential Development
For features requiring strict dependencies:
```
requirements-analyst → system-architect → engineering-manager → engineer → qa-engineer
```

### Parallel Development  
For features with independent components:
```python
mcp__coord__workflow_start(
    workflow_type="parallel_feature",
    participants=[
        "senior-backend-engineer",  # API development
        "senior-frontend-engineer", # UI development  
        "data-engineer"            # Database schema
    ],
    config={"sync_points": ["design_review", "integration_testing"]}
)
```

### Cross-Team Coordination
For features involving multiple specializations:
```
```

## 🚨 Escalation Procedures

### When to Escalate
- **Technical Blocker**: Cannot resolve technical issue
- **Resource Conflict**: Need prioritization decision
- **Scope Change**: Requirements changed during development
- **External Dependency**: Waiting on external team/service
- **Quality Issue**: Cannot meet acceptance criteria

### Escalation Targets
| Issue Type | Escalate To |
|------------|-------------|
| Technical problems | engineering-manager |
| Resource/priority conflicts | scrum-master |
| Architecture decisions | system-architect |
| Quality standards | qa-engineer |
| Security concerns | security-engineer |

### Escalation Examples
```python
# Technical escalation
mcp__coord__escalation_create(
    task_id="FEAT-001",
    reason="Database performance below requirements, need architecture review",
    severity="high",
    to_agent="engineering-manager"
)

# Resource escalation
mcp__coord__escalation_create(
    task_id="FEAT-001", 
    reason="Frontend engineer unavailable, blocking integration testing",
    severity="medium",
    to_agent="scrum-master"
)

# Critical production escalation
mcp__coord__escalation_create(
    task_id="INC-001",
    reason="Authentication service down, users cannot login", 
    severity="critical",
)
```

## 🎯 Best Practices

### Communication Guidelines
1. **Be Specific**: Include exact error messages, file paths, line numbers
2. **Include Context**: Share relevant background information
3. **Attach Artifacts**: Include code, logs, screenshots as needed
4. **Set Priority**: Use appropriate priority levels
5. **Follow Up**: Confirm receipt of important messages

### Task Handoff Checklist
- [ ] All work completed as specified
- [ ] Code validated and tested
- [ ] Documentation updated
- [ ] Artifacts organized and accessible
- [ ] Next agent has necessary context
- [ ] Dependencies clearly identified

### Coordination Examples

#### Feature Development Example
```python
# 1. Scrum master creates task
mcp__coord__task_create(
    task_id="FEAT-001", 
    title="User Profile Management",
    description="Allow users to update their profile information"
)

# 2. Assign to requirements analyst
mcp__coord__task_assign(task_id="FEAT-001", agent_name="requirements-analyst")

# 3. Requirements analyst updates progress
mcp__coord__task_status(
    task_id="FEAT-001",
    status="in_progress", 
    progress=50,
    notes="User interviews complete, creating wireframes"
)

# 4. Hand off to system architect
mcp__coord__task_handoff(
    task_id="FEAT-001",
    from_agent="requirements-analyst",
    to_agent="system-architect",
    artifacts=["requirements.md", "user-personas.md", "wireframes.pdf"]
)
```

#### Bug Fix Example
```python
# 1. QA engineer discovers bug
mcp__coord__task_create(
    task_id="BUG-001",
    title="Login form validation error",
    description="Email validation allows invalid formats"
)

# 2. Escalate to tech lead for triage
mcp__coord__escalation_create(
    task_id="BUG-001",
    reason="Security implications of invalid email validation", 
    severity="high",
    to_agent="engineering-manager"
)

# 3. Tech lead assigns to frontend engineer
mcp__coord__task_assign(task_id="BUG-001", agent_name="senior-frontend-engineer")
```

## 🔍 Monitoring and Tracking

### Check Agent Workloads
```python
# Before assigning new work
workload = mcp__coord__agent_workload("senior-backend-engineer")
if workload.active_tasks < 3:
    mcp__coord__task_assign(task_id="NEW-001", agent_name="senior-backend-engineer")
```

### Track Workflow Progress
```python
# Check overall project status
status = mcp__coord__workflow_status("feature_development")
print(f"Progress: {status.completed}/{status.total} tasks complete")
```

---

**Key Principles**:
- Follow handoff chains
- Report progress regularly  
- Escalate blockers quickly
- Document all decisions
- Coordinate with team

**Last Updated**: 2025-08-19