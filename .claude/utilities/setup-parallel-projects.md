# Setting Up Parallel Agent Army Projects

## The Challenge
MCP servers store data in fixed locations within each project. To run multiple projects in parallel, each needs its own MCP server instances.

## Solution Architecture

### Option 1: Project-Isolated MCPs (Recommended)
Each project runs its own MCP servers on different ports.

```bash
# Project 1: /home/user/project1/
cd /home/user/project1
export MCP_PORT_BASE=8000
.claude/mcp/start-servers.sh

# Project 2: /home/user/project2/
cd /home/user/project2  
export MCP_PORT_BASE=9000
.claude/mcp/start-servers.sh
```

### Option 2: Shared MCPs with Project Namespacing
Single MCP instance handles multiple projects using project IDs.

```python
# In MCP servers, namespace data by project:
project_id = self.get_project_id()
self.data_dir = base_dir / f"projects/{project_id}/data"
```

### Option 3: Docker Containers (Most Isolated)
Each project runs in its own container with complete isolation.

```dockerfile
# Dockerfile for Agent Army project
FROM python:3.11
COPY .claude /app/.claude
WORKDIR /app
CMD [".claude/mcp/start-servers.sh"]
```

## Current Implementation Status

✅ **Utilities**: Fully portable, auto-detect project
✅ **Logs**: Project-specific, isolated per project
⚠️ **MCP Data**: Currently shared if using same MCP instance
❌ **MCP Ports**: Fixed ports would conflict between projects

## Quick Fix for Parallel Projects

1. **Copy entire `.claude/` to new project**
2. **Start MCPs from within each project directory**
3. **Use project-specific terminals/shells**

```bash
# Terminal 1 - Project A
cd /path/to/projectA
# MCP servers use relative paths from here

# Terminal 2 - Project B  
cd /path/to/projectB
# MCP servers use relative paths from here
```

## Recommended Approach

For true parallel execution:
1. Run each project's MCPs in separate terminal sessions
2. Keep project directories completely separate
3. Use the global utilities that auto-detect context

This ensures:
- Complete data isolation
- No port conflicts
- Independent agent operations
- Separate logs and state