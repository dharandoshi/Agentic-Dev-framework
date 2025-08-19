# MCP Infrastructure Architecture

## Overview

The Agent Army uses a Model Context Protocol (MCP) infrastructure with 5 specialized servers providing 33 operational tools. This architecture enables agents to understand projects, validate code, execute tests, manage documentation, and coordinate work seamlessly.

## MCP Server Architecture

### 🏗️ Server Configuration

All MCP servers are configured in the global Claude Code configuration at `~/.claude.json`:

```json
{
  "mcpServers": {
    "docs": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/docs.py"]
    },
    "workspace": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python", 
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/workspace.py"]
    },
    "validation": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/validation.py"]
    },
    "execution": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/execution.py"]
    },
    "coord": {
      "command": "/home/dhara/PensionID/agent-army-trial/.claude/mcp/venv/bin/python",
      "args": ["/home/dhara/PensionID/agent-army-trial/.claude/mcp/servers/core/coord.py"]
    }
  }
}
```

### 🔧 Technical Details

- **Python Environment**: Dedicated virtual environment at `.claude/mcp/venv/`
- **Dependencies**: `mcp`, `psutil`, and project-specific packages
- **Data Storage**: `.claude/data/` directory for persistent data
- **Security**: Sandboxed execution with timeout protection

## Server Specifications

### 1. Docs Server (7 tools)
**Purpose**: Document management and knowledge base  
**Prefix**: `mcp__docs__`

| Tool | Function | Performance |
|------|----------|-------------|
| `register` | Register new documents | Instant |
| `find` | Search documents by criteria | Fast |
| `search` | Full-text content search | Fast |
| `get` | Retrieve document by ID | Instant |
| `update` | Update document content | Instant |
| `related` | Find related documents | Fast |
| `tree` | Get document hierarchy | Fast |

### 2. Workspace Server (12 tools)
**Purpose**: Universal project understanding and analysis  
**Prefix**: `mcp__workspace__`

| Tool | Function | Performance |
|------|----------|-------------|
| `analyze` | Complete project analysis | 2-5s |
| `detect` | Quick framework detection | <1s |
| `context` | AI-optimized project summary | Instant |
| `standards` | Extract coding conventions | Fast |
| `entry_points` | Find main entry files | Fast |
| `find` | Find files by glob pattern | Fast |
| `test_command` | Get project test command | Instant |
| `build_command` | Get project build command | Instant |
| `packages` | Package manager information | Instant |
| `deps` | Dependency analysis | 1-2s |
| `git` | Git repository status | Instant |
| `metrics` | Project metrics and LOC | 2-3s |

**Supports**: Python, JavaScript, TypeScript, Go, Rust, Java, C#, PHP, Ruby, and more

### 3. Validation Server (7 tools)
**Purpose**: Universal code validation and quality assurance  
**Prefix**: `mcp__validation__`

| Tool | Function | Performance |
|------|----------|-------------|
| `syntax` | Check syntax errors | Fast |
| `lint` | Run linter with auto-fix | 1-2s |
| `format` | Auto-format code | Instant |
| `types` | Type checking | 1-2s |
| `imports` | Verify imports exist | Fast |
| `validate` | Run all validations | 2-3s |
| `tools` | Detect available tools | Instant |

**Auto-detects**: ESLint, Prettier, Pylint, Black, TypeScript, mypy, etc.

### 4. Execution Server (7 tools)
**Purpose**: Safe code execution and testing  
**Prefix**: `mcp__execution__`

| Tool | Function | Performance |
|------|----------|-------------|
| `run` | Execute code snippet | Varies |
| `script` | Run script file | Varies |
| `test` | Run tests with coverage | Varies |
| `api` | Test API endpoints | 1-10s |
| `command` | Run shell commands | Varies |
| `debug` | Debug and analyze errors | Fast |
| `profile` | Performance profiling | Varies |

**Features**: Sandboxed execution, timeout protection, memory monitoring

### 5. Coordination Server (7 tools)
**Purpose**: Agent coordination and workflow management  
**Prefix**: `mcp__coord__`

| Tool | Function | Performance |
|------|----------|-------------|
| `task_create` | Create new tasks | Instant |
| `task_assign` | Assign tasks to agents | Instant |
| `task_status` | Update task status | Instant |
| `task_handoff` | Transfer task ownership | Instant |
| `message_send` | Send direct messages | Instant |
| `workflow_start` | Start workflows | Instant |
| `escalation_create` | Escalate issues | Instant |

## Universal Compatibility

### Auto-Detection System
Each MCP server automatically detects and adapts to your project:

1. **Language Detection**: Identifies primary languages from file extensions
2. **Framework Detection**: Recognizes React, Django, Spring Boot, etc.
3. **Tool Detection**: Finds linters, formatters, test runners
4. **Package Manager**: Detects npm, pip, maven, cargo, etc.
5. **Configuration**: Reads project configs automatically

### Example: Same Tools, Different Projects

#### React TypeScript Project
```
workspace.detect() → "React 18, TypeScript, Vite, Jest"
validation.lint() → "ESLint with React rules" 
execution.test() → "npm test (Jest + React Testing Library)"
```

#### Django Python Project  
```
workspace.detect() → "Django 4.2, Python 3.11, pytest"
validation.lint() → "pylint + black + mypy"
execution.test() → "pytest with Django test client"
```

#### Spring Boot Java Project
```
workspace.detect() → "Spring Boot 3, Java 17, Maven"
validation.lint() → "SpotBugs + Checkstyle"  
execution.test() → "mvn test (JUnit 5 + MockMvc)"
```

## Data Management

### Storage Structure
```
.claude/data/
├── coordination/           # Agent coordination data
│   ├── active-workflows.json
│   ├── task-assignments.json
│   └── communication-logs/
├── docs/                  # Document database
│   ├── documents.json
│   └── content/
├── workspace/             # Project analysis cache
│   └── analysis-cache.json
├── validation/           # Validation results
│   └── validation-history.json
└── execution/           # Execution logs
    └── execution-history.json
```

### Performance Optimization
- **Caching**: Workspace analysis results cached for reuse
- **Incremental Updates**: Only re-analyze changed files  
- **Parallel Processing**: Multiple tools can run simultaneously
- **Resource Limits**: Memory and CPU limits for safety

## Integration Architecture

### Agent → MCP → System Flow
```
Agent Request → MCP Tool → Server Process → System Command → Result → Agent
```

### Example: Code Validation Flow
```
1. senior-backend-engineer writes Python code
2. Calls mcp__validation__validate()
3. Validation server detects Python project
4. Runs: pylint + black + mypy in sequence  
5. Returns: syntax ✅, style ✅, types ❌ (3 errors)
6. Agent fixes type errors and re-validates
```

## Troubleshooting

### Common Issues

#### MCP Server Not Loading
```bash
# Check virtual environment
.claude/mcp/venv/bin/python --version

# Test server directly  
.claude/mcp/venv/bin/python .claude/mcp/servers/core/workspace.py
```

#### Tool Not Found
```bash
# Verify tool naming convention
/mcp                    # List all available tools
# Look for: mcp__server__tool pattern
```

#### Performance Issues
```bash
# Check resource usage
mcp__execution__profile()  # Profile tool performance
mcp__workspace__metrics()  # Check project size/complexity
```

## Future Enhancements

### Planned Improvements
- **Intelligence Server**: AI-powered code analysis and suggestions
- **Database Server**: Universal database management tools
- **Security Server**: Automated security scanning and fixes
- **Monitoring Server**: Production observability tools

### Scalability Features
- **Multi-Project Support**: Handle multiple projects simultaneously
- **Cloud Integration**: Remote MCP server deployment
- **Load Balancing**: Distribute tools across multiple servers
- **Caching Layer**: Advanced caching for faster responses

---

**Total Servers**: 5  
**Total Tools**: 33  
**Supported Languages**: 10+  
**Performance**: <3s for most operations  
**Last Updated**: 2025-08-19