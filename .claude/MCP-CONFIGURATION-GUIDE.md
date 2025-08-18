# MCP Configuration Guide

## ✅ MCP Servers Properly Registered

All 4 MCP servers are now correctly configured in `.claude/claude.json`:

### 1. Docs Server
- **Path**: `.claude/mcp/servers/core/docs.py`
- **Tools**: 7 document management tools
- **Prefix**: `mcp__docs__`

### 2. Workspace Server  
- **Path**: `.claude/mcp/servers/core/workspace.py`
- **Tools**: 12 project analysis tools
- **Prefix**: `mcp__workspace__`

### 3. Validation Server
- **Path**: `.claude/mcp/servers/core/validation.py`
- **Tools**: 7 code validation tools  
- **Prefix**: `mcp__validation__`

### 4. Execution Server
- **Path**: `.claude/mcp/servers/core/execution.py`
- **Tools**: 7 code execution tools
- **Prefix**: `mcp__execution__`

## Configuration File: `.claude/claude.json`

```json
{
  "mcpServers": {
    "docs": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/docs.py"],
      "env": {},
      "cwd": "/home/dhara/PensionID/agent-army-trial"
    },
    "workspace": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/workspace.py"],
      "env": {},
      "cwd": "/home/dhara/PensionID/agent-army-trial"
    },
    "validation": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/validation.py"],
      "env": {},
      "cwd": "/home/dhara/PensionID/agent-army-trial"
    },
    "execution": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/execution.py"],
      "env": {},
      "cwd": "/home/dhara/PensionID/agent-army-trial"
    }
  }
}
```

## Key Configuration Details

### Python Environment
- **Virtual Environment**: `.claude/mcp/venv/`
- **Python Path**: `/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python`
- **Dependencies**: mcp, psutil (installed in venv)

### File Paths
- All paths use absolute paths for reliability
- Working directory set to project root: `/home/dhara/PensionID/agent-army-trial`
- Server files in: `.claude/mcp/servers/core/`

## MCP Tool Naming Convention

All MCP tools follow the pattern: `mcp__[server]__[tool]`

### Examples:
- `mcp__docs__register` - Register a document
- `mcp__workspace__analyze` - Analyze project
- `mcp__validation__lint` - Lint code
- `mcp__execution__test` - Run tests

## Agent Integration

All 16 agents have been updated with:
1. Correct MCP tool names in their YAML frontmatter
2. Proper document creation workflow
3. Role-appropriate tool assignments

### Document Creation Workflow
```python
# Step 1: Create document
Write(file_path="docs/document.md", content="...")

# Step 2: Register with MCP
mcp__docs__register(
    path="docs/document.md",
    title="Document Title",
    owner="agent-name",
    category="category"
)
```

## Verification Status

✅ **All Systems Operational**
- MCP servers properly configured
- Virtual environment set up with dependencies
- Agents updated with correct tool references
- Document creation workflow standardized

## Troubleshooting

### If MCP tools don't work:
1. Check virtual environment: `.claude/mcp/venv/bin/python --version`
2. Verify MCP installed: `.claude/mcp/venv/bin/pip list | grep mcp`
3. Test server directly: `.claude/mcp/venv/bin/python .claude/mcp/servers/core/[server].py`
4. Check claude.json syntax: Valid JSON with absolute paths

### Common Issues:
- **Import errors**: Ensure using venv Python, not system Python
- **Path errors**: Use absolute paths in claude.json
- **Tool not found**: Check tool name follows `mcp__[server]__[tool]` pattern

## Summary

The MCP infrastructure is fully configured and operational with:
- ✅ 4 MCP servers registered in claude.json
- ✅ Virtual environment with all dependencies
- ✅ 16 agents with correct MCP tool references
- ✅ Standardized document creation workflow
- ✅ Production-ready configuration