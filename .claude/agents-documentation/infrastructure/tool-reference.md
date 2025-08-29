# Complete MCP Tools Reference

## All Available MCP Tools (33 Total)

This is the complete reference for all MCP tools available to agents in the system. Tools are organized by server and include performance characteristics and usage guidelines.

## 📚 Document Management (7 tools)
**Server**: `docs` | **Prefix**: `mcp__docs__`

| Tool | Purpose | Parameters | Performance |
|------|---------|------------|-------------|
| `register` | Register new document in system | `path, title, owner, category` | Instant |
| `find` | Find documents by metadata | `owner, category, title_pattern` | Fast |
| `search` | Full-text search in document content | `query, limit` | Fast |
| `get` | Retrieve document by ID | `doc_id` | Instant |
| `update` | Update document content/metadata | `doc_id, content, metadata` | Instant |
| `related` | Find related documents | `doc_id, limit` | Fast |
| `tree` | Get document hierarchy/structure | `root_category` | Fast |

### Usage Example
```python
# Register documentation created by agent
mcp__docs__register(
    path="api/user-auth.md",
    title="User Authentication API", 
    owner="senior-backend-engineer",
    category="api-docs"
)
```

## 🔍 Project Analysis (12 tools)
**Server**: `workspace` | **Prefix**: `mcp__workspace__`

| Tool | Purpose | Parameters | Performance |
|------|---------|------------|-------------|
| `analyze` | Complete project analysis | `include_dependencies` | 2-5s |
| `detect` | Quick framework/language detection | None | <1s |
| `context` | AI-optimized project summary | `focus_area` | Instant |
| `standards` | Extract coding standards/conventions | None | Fast |
| `entry_points` | Find main application entry files | None | Fast |
| `find` | Find files by glob pattern | `pattern, exclude` | Fast |
| `test_command` | Auto-detect test command | None | Instant |
| `build_command` | Auto-detect build command | None | Instant |
| `packages` | Package manager info | None | Instant |
| `deps` | Analyze dependencies | `check_updates` | 1-2s |
| `git` | Git repository status | None | Instant |
| `metrics` | Project metrics (LOC, complexity) | `include_tests` | 2-3s |

### Usage Example
```python
# Before implementing new feature
context = mcp__workspace__context(focus_area="authentication")
standards = mcp__workspace__standards()  
test_cmd = mcp__workspace__test_command()
```

## ✅ Code Quality (7 tools)
**Server**: `validation` | **Prefix**: `mcp__validation__`

| Tool | Purpose | Parameters | Performance |
|------|---------|------------|-------------|
| `syntax` | Check for syntax errors | `file_path, language` | Fast |
| `lint` | Run linter with optional auto-fix | `file_path, fix` | 1-2s |
| `format` | Auto-format code | `file_path, language` | Instant |
| `types` | Type checking (TypeScript, Python) | `file_path` | 1-2s |
| `imports` | Verify all imports exist | `file_path` | Fast |
| `validate` | Run all validations at once | `file_path` | 2-3s |
| `tools` | Detect available linting/formatting tools | None | Instant |

### Auto-Detection
- **JavaScript/TypeScript**: ESLint, Prettier, tsc
- **Python**: pylint, black, mypy, ruff  
- **Java**: SpotBugs, Checkstyle, Google Java Format
- **Go**: golint, gofmt, go vet
- **Rust**: clippy, rustfmt
- **And more...**

### Usage Example
```python
# Validate implementation before handoff
result = mcp__validation__validate("src/auth/login.py")
if not result.valid:
    # Fix issues automatically where possible
    mcp__validation__lint("src/auth/login.py", fix=True)
    mcp__validation__format("src/auth/login.py")
```

## ⚡ Code Execution (7 tools) 
**Server**: `execution` | **Prefix**: `mcp__execution__`

| Tool | Purpose | Parameters | Performance |
|------|---------|------------|-------------|
| `run` | Execute code snippet safely | `code, language, timeout` | Varies |
| `script` | Run existing script file | `script_path, args` | Varies |
| `test` | Run project tests | `test_path, coverage` | Varies |
| `api` | Test API endpoints | `method, url, headers, body` | 1-10s |
| `command` | Execute shell command safely | `command, timeout` | Varies |
| `debug` | Debug errors and suggest fixes | `error_message, context` | Fast |
| `profile` | Profile code performance | `code, iterations` | Varies |

### Safety Features
- **Sandboxed Execution**: Isolated from system
- **Timeout Protection**: Configurable limits (default 30s)
- **Memory Monitoring**: Prevents resource exhaustion
- **Error Handling**: Comprehensive error analysis

### Usage Example
```python
# Test implementation works correctly
mcp__execution__test("tests/test_auth.py", coverage=True)

# Test API endpoint
response = mcp__execution__api(
    method="POST",
    url="http://localhost:8000/api/login", 
    headers={"Content-Type": "application/json"},
    body={"username": "test", "password": "pass"}
)
```

## 🤝 Agent Coordination (7 tools)
**Server**: `coord` | **Prefix**: `mcp__coord__`

| Tool | Purpose | Parameters | Performance |
|------|---------|------------|-------------|
| `task_create` | Create new task | `task_id, title, description, priority` | Instant |
| `task_assign` | Assign task to agent | `task_id, agent_name` | Instant |
| `task_status` | Update task progress | `task_id, status, progress, notes` | Instant |
| `task_handoff` | Transfer task between agents | `task_id, from_agent, to_agent, artifacts` | Instant |
| `message_send` | Send message to specific agent | `to_agent, subject, content, priority` | Instant |
| `workflow_start` | Initialize multi-agent workflow | `workflow_type, participants, config` | Instant |
| `escalation_create` | Escalate blocked/failed tasks | `task_id, reason, severity, to_agent` | Instant |

### Coordination Patterns
```python
# Standard task handoff
mcp__coord__task_handoff(
    task_id="FEAT-001",
    from_agent="requirements-analyst", 
    to_agent="system-architect",
    artifacts=["requirements.md", "user-stories.md"]
)

# Escalate blocking issue
mcp__coord__escalation_create(
    task_id="BUG-042",
    reason="Database connection failing in production",
    severity="critical", 
)
```

## Tool Assignment by Agent Type

### Full-Stack Engineers (All 33 tools)
**Agents**: `senior-backend-engineer`, `senior-frontend-engineer`
- Complete access to all MCP tools for comprehensive development

### Specialist Engineers (15-25 tools each)
**Roles**: QA, Security, DevOps, SRE, Cloud, Integration, Data
- Workspace tools: Project understanding
- Validation tools: Code quality (where applicable)
- Execution tools: Testing and deployment  
- Coordination tools: Task management
- Docs tools: Documentation

### Architects & Leads (15-36 tools)
**Roles**: System Architect, Tech Lead, Project Initializer
- Focus on analysis, design, and coordination tools
- Tech Lead has access to all tools for oversight

### Management & Documentation (7-15 tools)
**Roles**: Scrum Master, Requirements Analyst, Technical Writer  
- Primary focus on coordination and documentation tools
- Limited technical execution tools

## Performance Guidelines

### Tool Selection
- **Fast Operations** (<1s): Use for real-time decisions
- **Medium Operations** (1-3s): Use for validation and analysis  
- **Slow Operations** (>3s): Use sparingly, consider caching

### Optimization Tips
1. **Cache Results**: Workspace analysis results are cached
2. **Parallel Execution**: Run independent tools simultaneously
3. **Incremental Updates**: Only re-analyze changed components
4. **Selective Analysis**: Use focused analysis when possible

## Error Handling

### Common Error Types
- **Tool Not Found**: Check tool name follows `mcp__server__tool` pattern
- **Permission Denied**: Verify agent has access to required tools
- **Timeout**: Increase timeout for long-running operations
- **Resource Limits**: Check memory/CPU usage with profiling tools

### Debugging Tools
```python
# Debug execution issues
mcp__execution__debug(
    error_message="ImportError: No module named 'requests'",
    context="Python FastAPI project"
)

# Profile performance issues  
mcp__execution__profile("slow_function()", iterations=10)
```

---

**Total Tools**: 33 across 5 MCP servers  
**Supported Languages**: 10+  
**Average Response Time**: <2s  
**Reliability**: 99.9% uptime  
**Last Updated**: 2025-08-19