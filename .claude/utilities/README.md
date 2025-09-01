# PensionID Agent Army Utilities

## 🚀 Quick Start

### Local Installation (single project)
```bash
.claude/utilities/install.sh
source ~/.bashrc
```

### Global Installation (multiple projects)
```bash
.claude/utilities/install-global.sh
source ~/.bashrc
```

## 📦 Portability Features

- **Auto-detects project**: Works from any directory within an Agent Army project
- **Multiple projects**: Can manage multiple Agent Army projects simultaneously
- **Project isolation**: Each project's logs and settings remain separate
- **Global commands**: Once installed globally, commands work from anywhere

## 📊 Available Commands

### Main Command: `pid-agentarmy`
The central command for managing the PensionID Agent Army framework.

```bash
pid-agentarmy help                    # Show all commands
pid-agentarmy status                  # System status overview
pid-agentarmy logs view 50            # View last 50 log lines
pid-agentarmy logs tail               # Live log monitoring
pid-agentarmy logs stats              # Log statistics
pid-agentarmy logs search "term"      # Search in logs
pid-agentarmy monitor                 # Live system monitoring
pid-agentarmy list agents             # List all agents
```

### Direct Log Commands

#### `agentlog` - Quick log management
```bash
agentlog view 100            # View last 100 lines
agentlog tail                # Follow logs in real-time
agentlog stats               # Show statistics
agentlog agents              # Agent activity summary
agentlog errors              # Show only errors
agentlog files               # Show file operations
agentlog decisions           # Show decisions made
agentlog tasks               # Show task lifecycle
agentlog search "FILE WRITE" # Search for specific term
agentlog clear               # Archive old logs (keeps today)
agentlog purge               # DELETE ALL logs permanently
```

#### `logview` - Advanced Python viewer
```bash
logview monitor              # Live monitoring with colors
logview summary              # Statistics with graphs
logview timeline             # Event timeline
logview errors               # Filter errors only
logview search "term"        # Search with highlighting
```

## 📁 Log Locations

- **Human-readable logs**: `.claude/logs/agents_YYYYMMDD.log`
- **JSON logs**: `.claude/logs/logs_YYYYMMDD.jsonl`
- **MCP logs**: `.claude/mcp/data/logging/agents_YYYYMMDD.log`

## 📝 Log Format

```
[TIMESTAMP] AGENT_NAME | LOG_TYPE | DETAILS
```

Example:
```
[2025-01-09 10:15:24] REQUIREMENTS     | FILE READ     | docs/requirements.md
[2025-01-09 10:16:12] REQUIREMENTS     | FILE WRITE    | docs/project-brief.md
[2025-01-09 10:20:20] SYSTEM-ARCH      | DECISION      | Selected PostgreSQL
```

## 🔍 Log Types

- **TASK START/COMPLETE** - Task lifecycle
- **FILE READ/WRITE/EDIT** - File operations
- **TOOL USE** - MCP tool usage (✓ success, ✗ failure)
- **DECISION** - Important decisions with rationale
- **HANDOFF** - Task transfers between agents
- **CODE ANALYSIS** - Code inspection
- **API CALL** - External service calls
- **DISCOVERY** - Information found
- **VALIDATION** - Checks and tests
- **ERROR** - Problems encountered

## 🎯 Common Use Cases

### Monitor agent activity during a task:
```bash
pid-agentarmy logs tail
```

### Check what files were modified:
```bash
pid-agentarmy logs files
agentlog search "FILE WRITE"
```

### See decision history:
```bash
agentlog decisions
```

### Debug errors:
```bash
pid-agentarmy logs errors
logview errors
```

### Get daily summary:
```bash
pid-agentarmy status
agentlog stats
```

### Clean up logs:
```bash
agentlog clear  # Archives logs older than today
agentlog purge  # DELETE ALL logs (requires typing 'DELETE ALL LOGS')
```

## 🔧 Troubleshooting

If logs aren't appearing:
1. Check MCP logging server is running
2. Verify agents have logging protocol in their tools
3. Check log directories exist: `.claude/logs/` and `.claude/mcp/data/logging/`
4. Run an agent task to generate real logs

## 📚 Architecture

```
.claude/
├── utilities/               # Log management tools
│   ├── pid-agentarmy       # Main command center
│   ├── agentlog            # Bash log manager
│   ├── logview             # Python log viewer
│   └── install.sh          # Installation script
├── logs/                   # Standard logs
│   └── agents_YYYYMMDD.log
└── mcp/data/logging/       # MCP server logs
    └── agents_YYYYMMDD.log
```