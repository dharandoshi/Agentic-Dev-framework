# Agent Army Onboarding Guide

> Welcome to Agent Army! This guide will get you up and running with our multi-agent development system.

## 🎯 Quick Start (5 Minutes)

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone <repository-url> agent-army-trial
cd agent-army-trial

# Start the system
./start-agent-army.sh
```

### Step 2: Verify Installation
```bash
# Check system status
python3 .claude/scripts/monitoring-dashboard.py --simple

# Run quick test
./.claude/scripts/run-tests.sh environment
```

### Step 3: Try Your First Command
```bash
# In Claude Code
claude

# Type:
"Act as scrum-master and show me the project status"
```

## 📚 What is Agent Army?

Agent Army is a sophisticated multi-agent orchestration system that enhances Claude Code with:

- **15 Specialized AI Agents**: Each expert in their domain
- **6 MCP Servers**: Providing tools for development tasks
- **Automated Workflows**: Complex tasks broken into coordinated steps
- **Real-time Monitoring**: Track everything happening in the system
- **Self-healing Infrastructure**: Automatic recovery from failures

## 🏢 System Architecture

```
┌─────────────────────────────────────────┐
│           Claude Code CLI                │
├─────────────────────────────────────────┤
│                                          │
│  Agents    Hooks    MCP Servers         │
│    (15)  ←→  (3)  ←→    (6)            │
│                                          │
│         Monitoring & Orchestration       │
│                                          │
└─────────────────────────────────────────┘
```

## 👥 The Agent Team

### Hierarchy Levels

**Level 1 - Strategic**
- `scrum-master`: Project coordination and sprint planning

**Level 2 - Architectural**  
- `system-architect`: System design and architecture
- `tech-lead`: Technical direction and code reviews

**Level 3 - Implementation**
- `senior-backend-engineer`: Backend development
- `senior-frontend-engineer`: Frontend development
- `requirements-analyst`: Requirements gathering
- `data-engineer`: Data pipelines and analytics
- `integration-engineer`: Third-party integrations

**Level 4 - Quality & Operations**
- `qa-engineer`: Testing and quality assurance
- `security-engineer`: Security and compliance
- `devops-engineer`: CI/CD and deployment
- `sre-engineer`: Site reliability
- `cloud-architect`: Cloud infrastructure

**Level 5 - Documentation**
- `technical-writer`: Documentation and guides

**Special Agents**
- `god-agent`: Meta-agent for agent management

## 🛠️ Available Tools (MCP Servers)

### Core Servers
- **workspace**: Project analysis and file operations
- **docs**: Document creation and management
- **coord**: Task creation and agent communication
- **validation**: Code validation and quality checks

### Project Management
- **project-management**: Advanced project coordination

### Integration
- **execution**: Code execution and testing tools

## 💻 Common Workflows

### 1. Feature Development
```bash
# Start a new feature
"Act as scrum-master and create a task for user authentication feature"

# Design the architecture
"Act as system-architect and design the authentication system"

# Implement backend
"Act as senior-backend-engineer and implement JWT authentication"

# Add frontend
"Act as senior-frontend-engineer and create login UI"

# Test the feature
"Act as qa-engineer and test the authentication flow"

# Deploy
"Act as devops-engineer and deploy to staging"
```

### 2. Bug Fixing
```bash
# Report bug
"Act as qa-engineer and document the login error bug"

# Assign to developer
"Act as tech-lead and assign the bug to backend team"

# Fix the bug
"Act as senior-backend-engineer and fix the authentication timeout issue"

# Verify fix
"Act as qa-engineer and verify the bug is resolved"
```

### 3. Code Review
```bash
# Request review
"Act as tech-lead and review the recent changes"

# Security review
"Act as security-engineer and audit the authentication implementation"

# Performance review
"Act as sre-engineer and check for performance issues"
```

## 📊 Monitoring Your Work

### View System Status
```bash
# Interactive dashboard
python3 .claude/scripts/monitoring-dashboard.py

# Simple status report
python3 .claude/scripts/monitoring-dashboard.py --simple

# Check monitoring
python3 .claude/scripts/monitoring-system.py --status
```

### Understanding the Dashboard

```
🚀 Agent Army Monitoring Dashboard
==================================
📊 System Overview
  CPU: 45.2%  Memory: 62.1%  Disk: 38.5%

🔧 MCP Servers
  workspace: 🟢 Connected  docs: 🟢 Connected
  coord: 🟢 Connected  validation: 🟢 Connected
  project-management: 🟢 Connected
  execution: 🟢 Connected

🤖 Agent System
  Total Agents: 15  Hierarchy Levels: 5

📈 Event Statistics
  Total: 1,234  🔴 Critical: 0  🟠 High: 2
```

## 🧪 Testing Your Changes

### Run Tests
```bash
# Quick environment check
./.claude/scripts/run-tests.sh environment

# Test MCP servers
./.claude/scripts/run-tests.sh mcp

# Test agent workflows
./.claude/scripts/run-tests.sh workflow

# Full test suite
./.claude/scripts/run-tests.sh all
```

### Integration Tests
```bash
# Run comprehensive integration tests
python3 .claude/scripts/integration-tests.py
```

## 💾 Backup and Recovery

### Create Backups
```bash
# Full system backup
python3 .claude/scripts/backup-system.py --type full

# Incremental backup
python3 .claude/scripts/backup-system.py --type incremental

# List backups
python3 .claude/scripts/backup-system.py --list
```

### Recovery
```bash
# If something goes wrong
git checkout HEAD -- .claude/
./.claude/scripts/register-mcp-servers.sh
./start-agent-army.sh
```

## 🔧 Configuration

### Key Configuration Files

| File | Purpose |
|------|--------|
| `.claude/settings.json` | Hook configuration |
| `.claude/agents/agent-registry.json` | Agent definitions |
| `.claude/config/alerting-config.json` | Alert rules |
| `.claude/scripts/test-scenarios.json` | Test workflows |

### Environment Variables
```bash
# Optional configurations
export AGENT_ARMY_WEBHOOK_URL="https://..."  # For Slack/Discord alerts
export AGENT_ARMY_LOG_LEVEL="INFO"  # Logging verbosity
```

## 🚀 Advanced Usage

### Direct MCP Tool Usage
```bash
# In Claude Code
"Use mcp__workspace__analyze to understand the project structure"
"Use mcp__coord__task_create to create a new development task"
"Use mcp__validation__validate to run code quality checks"
```

### Custom Workflows
```bash
# Execute predefined workflows
python3 .claude/scripts/agent-army-orchestrator.py --workflow feature_development
```

### Monitoring Specific Events
```bash
# Test alert system
python3 .claude/scripts/monitoring-system.py --test

# View alerts
tail -f .claude/logs/alerts.jsonl
```

## 🐛 Troubleshooting

### Common Issues

**MCP Servers Not Connected**
```bash
# Re-register servers
./.claude/scripts/register-mcp-servers.sh

# Check status
claude mcp list
```

**Monitoring Not Working**
```bash
# Restart monitoring
pkill -f monitoring-system.py
python3 .claude/scripts/monitoring-system.py --start --daemon
```

**Hooks Not Firing**
```bash
# Check hook configuration
cat .claude/settings.json | grep hooks

# Verify hook scripts are executable
ls -la .claude/hooks/*.py
```

**Agent Not Responding**
```bash
# Validate agent definitions
python3 .claude/scripts/validate-environment.py

# Check agent registry
cat .claude/agents/agent-registry.json | jq '.total_agents'
```

## 📝 Daily Workflow

### Morning Startup
```bash
# 1. Start the system
./start-agent-army.sh

# 2. Check system health
python3 .claude/scripts/monitoring-dashboard.py --simple

# 3. Review any overnight alerts
tail -20 .claude/logs/alerts.jsonl
```

### During Development
```bash
# Use agents for tasks
"Act as [agent-name] and [task description]"

# Monitor progress
"Show me current task status"

# Run tests frequently
"Run tests for the feature I just implemented"
```

### End of Day
```bash
# 1. Create backup
python3 .claude/scripts/backup-system.py --type incremental

# 2. Check for any issues
python3 .claude/scripts/monitoring-system.py --status

# 3. Optional: Stop services
./stop-agent-army.sh
```

## 🎓 Learning Resources

### Understanding Agents
- Each agent has specific expertise
- Agents can hand off tasks to each other
- Higher-level agents coordinate lower-level ones

### Understanding MCP
- MCP servers provide tools to Claude Code
- Tools are namespaced: `mcp__server__tool`
- All tool usage is monitored and logged

### Understanding Hooks
- Hooks intercept Claude Code events
- They enable monitoring and orchestration
- Hooks run automatically, no manual intervention needed

## 🆘 Getting Help

### Documentation
- System Overview: `.claude/agents-documentation/system/overview.md`
- Agent Reference: `.claude/agents-documentation/agents/team-reference.md`
- Tool Reference: `.claude/agents-documentation/infrastructure/tool-reference.md`

### Logs and Debugging
```bash
# View recent logs
tail -f .claude/logs/orchestrator.log
tail -f .claude/logs/monitoring.log

# Check communication logs
cat .claude/logs/communication.jsonl | jq '.'

# Debug mode
AGENT_ARMY_LOG_LEVEL=DEBUG ./start-agent-army.sh
```

### Support Channels
- Check system health first: `./run-tests.sh all`
- Review documentation in `.claude/agents-documentation/`
- Check example configurations in `.claude/example-*`

## ✅ Onboarding Checklist

- [ ] System started successfully
- [ ] All MCP servers connected
- [ ] Monitoring dashboard accessible
- [ ] Successfully invoked an agent
- [ ] Ran environment tests
- [ ] Created a test task
- [ ] Viewed monitoring dashboard
- [ ] Understood agent hierarchy
- [ ] Familiar with common workflows
- [ ] Know how to check logs
- [ ] Created a backup
- [ ] Bookmarked this guide

## 🎉 Welcome Aboard!

You're now ready to use Agent Army! Remember:
- **Start simple**: Use one agent at a time initially
- **Monitor actively**: Keep the dashboard open while working
- **Test frequently**: Run tests after making changes
- **Backup regularly**: Daily backups are recommended

Happy coding with your AI agent team! 🚀