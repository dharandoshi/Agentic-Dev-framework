# Quick Start Guide

## Getting Started with Agent Army

This guide helps you quickly get up and running with the Agent Army system. Follow these steps to start coordinating development work using intelligent agents.

## ✅ Prerequisites

### 1. Verify MCP Servers
Check that all 5 MCP servers are loaded:
```bash
/mcp
```
You should see:
- **docs** (7 tools) - Document management
- **workspace** (12 tools) - Project analysis  
- **validation** (7 tools) - Code quality
- **execution** (7 tools) - Testing & execution
- **coord** (7 tools) - Agent coordination

### 2. Check Agent Configuration
All 16 agents should have proper MCP tool access configured. The system includes:
- 2 Full-stack engineers (all 33 tools)
- 7 Specialist engineers (15-25 tools each)
- 3 Architects & leads (15-36 tools)
- 4 Management & documentation (7-15 tools)

## 🚀 Basic Usage

### Starting a New Feature
```bash
# 1. Assign work to requirements analyst
@requirements-analyst gather requirements for user authentication system

# The agent will:
# - Use mcp__docs__ tools to research existing documentation
# - Use mcp__workspace__ tools to understand current system
# - Create detailed requirements documentation
# - Automatically hand off to system-architect when complete
```

### Code Implementation
```bash
# 2. System architect designs, then hands off to tech lead
@tech-lead plan implementation of authentication system

# Tech lead will:
# - Use mcp__workspace__ tools to understand codebase
# - Use mcp__validation__ tools to check code standards  
# - Assign specific tasks to senior engineers
# - Coordinate parallel development
```

### Development Execution
```bash
# 3. Engineers implement features
@senior-backend-engineer implement OAuth authentication API
@senior-frontend-engineer create login/signup UI components

# Engineers will:
# - Use mcp__workspace__ tools to understand project structure
# - Use mcp__validation__ tools to ensure code quality
# - Use mcp__execution__ tools to test implementations
# - Use mcp__coord__ tools to report progress
```

## 🎯 Common Workflows

### Simple Feature Development
```
1. @scrum-master create sprint for user management features
2. Auto-assigned: requirements-analyst → system-architect → tech-lead → engineers
3. Engineers coordinate using mcp__coord__ tools
4. QA and deployment handled automatically through handoff chain
```

### Bug Investigation & Fix
```
1. @qa-engineer investigate login performance issue  
2. Uses mcp__execution__debug to analyze problem
3. Escalates to @senior-backend-engineer with findings
4. Backend engineer uses mcp__validation__ and mcp__execution__ tools to fix
5. Hands back to QA for verification
```

### Architecture Review
```
1. @system-architect review current API design
2. Uses mcp__workspace__analyze for complete system understanding
3. Creates improvement recommendations
4. Coordinates with @tech-lead for implementation planning
```

## 🛠️ Key Agent Roles

### Strategic Level
- **scrum-master**: Project coordination, sprint planning, task assignment
- **requirements-analyst**: Gather requirements through conversation, validate concepts

### Technical Level  
- **system-architect**: System design, database schemas, API contracts
- **tech-lead**: Code quality, technical standards, team coordination

### Implementation Level
- **senior-backend-engineer**: API development, database work, microservices
- **senior-frontend-engineer**: UI/UX implementation, responsive design  
- **integration-engineer**: Third-party services, webhooks, message queues
- **data-engineer**: ETL pipelines, data warehouses, analytics

### Quality & Operations
- **qa-engineer**: Testing, quality assurance, bug tracking
- **security-engineer**: Security audits, vulnerability assessment
- **devops-engineer**: CI/CD, containerization, infrastructure  
- **sre-engineer**: Monitoring, incident response, system reliability
- **cloud-architect**: Cloud design, serverless, cost optimization

## 📋 Task Coordination

### Create Tasks (scrum-master)
```python
mcp__coord__task_create(
    task_id="FEAT-001",
    title="User Authentication System", 
    description="Implement OAuth 2.0 with JWT tokens",
    priority="high"
)
```

### Report Progress (any agent)
```python
mcp__coord__task_status(
    task_id="FEAT-001",
    status="in_progress",
    progress=75,
    notes="API implementation complete, testing in progress"
)
```

### Hand Off Work (any agent)
```python
mcp__coord__task_handoff(
    task_id="FEAT-001", 
    from_agent="senior-backend-engineer",
    to_agent="qa-engineer",
    artifacts=["auth-api.py", "test_auth.py", "api-docs.md"]
)
```

## 🔍 Monitoring Progress

### Check Agent Workloads
```python
# Before assigning work
mcp__coord__agent_workload("senior-backend-engineer")
```

### View Task Status
```python
# Check specific task progress
mcp__coord__task_status("FEAT-001")
```

### Monitor System Health
```bash
# View MCP server status
/mcp

# Check agent configurations
ls .claude/agents/
```

## 🚨 Common Issues & Solutions

### Issue: Agent Not Responding
**Solution**: Check if agent has access to required MCP tools
```bash
# Verify agent's tool assignments in .claude/agents/[agent-name].md
# Ensure MCP servers are loaded: /mcp
```

### Issue: Task Stuck in Progress  
**Solution**: Check for escalations or blockers
```python
mcp__coord__escalation_create(
    task_id="FEAT-001",
    reason="Waiting for external API documentation",
    severity="medium", 
    to_agent="tech-lead"
)
```

### Issue: Code Quality Problems
**Solution**: Use validation tools before handoff
```python
# Always validate before completing tasks
mcp__validation__validate("src/auth.py")
mcp__execution__test("tests/test_auth.py")
```

## 💡 Pro Tips

### Efficient Development
1. **Start with Analysis**: Always use `@requirements-analyst` for new features
2. **Follow Handoff Chains**: Don't skip steps in the coordination flow
3. **Use Parallel Development**: Coordinate frontend/backend work simultaneously
4. **Validate Early**: Run code quality checks throughout development
5. **Document Everything**: Use `@technical-writer` for important documentation

### Agent Coordination
1. **Specify Context**: Always use "as [agent-name]" when working
2. **Report Progress**: Update task status at 25%, 50%, 75%, 100% completion
3. **Escalate Blockers**: Don't let tasks sit blocked without escalation
4. **Include Artifacts**: Always attach relevant files during handoffs
5. **Monitor Workloads**: Check agent capacity before assignment

### Quality Assurance
1. **Test Everything**: Use `mcp__execution__test` for all implementations
2. **Validate Code**: Use `mcp__validation__validate` before handoffs
3. **Check Performance**: Use `mcp__execution__profile` for optimization
4. **Security Review**: Include `@security-engineer` for sensitive features
5. **Documentation**: Keep docs updated with `@technical-writer`

## 🎉 Success Metrics

When the system is working correctly, you should see:
- ✅ Smooth task handoffs between agents
- ✅ Consistent code quality across implementations  
- ✅ Comprehensive testing and validation
- ✅ Proper documentation at each step
- ✅ Clear progress tracking and reporting
- ✅ Quick escalation and resolution of blockers

## 📖 Next Steps

Once you're comfortable with basic usage:
1. Read [Agent Team Reference](agents/team-reference.md) for detailed agent capabilities
2. Review [Coordination Guide](guides/coordination-guide.md) for advanced workflows  
3. Study [MCP Architecture](infrastructure/mcp-architecture.md) for system internals
4. Explore [Tool Reference](infrastructure/tool-reference.md) for all available tools

---

**Quick Commands**:
- `/mcp` - Check MCP server status
- `@agent-name` - Assign work to specific agent
- Progress updates at 25%, 50%, 75%, 100%
- Always validate code before handoff

**Last Updated**: 2025-08-19