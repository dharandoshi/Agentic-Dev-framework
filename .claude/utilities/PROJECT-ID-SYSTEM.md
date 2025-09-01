# Project ID System for Agent Army

## Overview
The Agent Army framework now supports multiple projects running in parallel, each with its own unique project ID and isolated data storage.

## Architecture

### 1. Project Configuration
Each project has a `.claude/project.json` file:
```json
{
  "project_id": "agent-army-trial",
  "project_name": "Agent Army Trial",
  "version": "1.0.0",
  "created": "2025-01-09",
  "settings": {
    "log_retention_days": 30,
    "enable_human_logs": true,
    "mcp_isolation": true
  }
}
```

### 2. Data Isolation
All data is stored within each project's folder structure:
```
project-root/
└── .claude/
    ├── project.json           # Project configuration
    ├── mcp/
    │   └── data/
    │       ├── logging/        # Project-specific logs
    │       ├── communication/  # Project-specific tasks/messages
    │       └── project-management/
    └── logs/                   # Human-readable logs
```

### 3. MCP Server Updates
All MCP servers now:
- Auto-detect the project root by finding `.claude` directory
- Load project configuration from `project.json`
- Store data within the project's `.claude/mcp/data/` directory
- Use project ID for namespacing (future enhancement)

### 4. Updated Components

#### Logging Server (`logging_server.py`)
- Detects project root dynamically
- Stores logs in project-specific directory
- Loads project ID from configuration

#### Coordination Server (`coord.py`)
- Uses project-aware paths
- Maintains task/message isolation per project

#### Project Management MCP
- No longer has hardcoded paths
- Works with any project location

#### Utilities
- Auto-detect current project
- Display project ID in status/help
- Work from any subdirectory within project

## Usage

### Single Project
```bash
cd /path/to/project
pid-agentarmy status  # Shows project ID and status
```

### Multiple Projects
```bash
# Terminal 1 - Project A
cd /path/to/projectA
# MCP servers use projectA's data

# Terminal 2 - Project B
cd /path/to/projectB
# MCP servers use projectB's data
```

### Creating New Project
1. Copy `.claude/` template to new project
2. Run `init-project.sh` to generate unique ID
3. Start using utilities - they auto-detect context

## Benefits

1. **Complete Isolation**: Each project's data stays within its folder
2. **Portability**: Copy entire project folder anywhere
3. **Parallel Execution**: Run multiple projects simultaneously
4. **No Conflicts**: Each project has separate logs, tasks, messages
5. **Project Awareness**: Utilities show which project you're working on

## Future Enhancements

### Port Management
Could add port configuration in `project.json`:
```json
{
  "mcp_ports": {
    "logging": 8001,
    "coordination": 8002,
    "workspace": 8003
  }
}
```

### Global Registry
Optional central registry at `~/.agent-army/registry.json` for:
- Tracking all projects
- Quick project switching
- Global statistics

### Project Templates
Create templates for different project types:
- Web application
- API service
- Data pipeline
- ML project

## Migration Guide

For existing projects:
1. Create `.claude/project.json` with unique project_id
2. Restart MCP servers (they'll use new paths)
3. Use updated utilities

## Summary

The project ID system provides:
- ✅ Complete data isolation per project
- ✅ Dynamic project detection
- ✅ Support for parallel projects
- ✅ All data stored within project folder
- ✅ No hardcoded paths
- ✅ Portable project structures