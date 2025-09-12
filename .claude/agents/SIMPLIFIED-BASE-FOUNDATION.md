# Simplified Base Foundation for All Agents

## 🎯 Working Directory Rules

**CRITICAL**: Always work in the CURRENT directory structure. Never create project subfolders.

Before starting ANY task:
1. Run `pwd` to verify working directory
2. Check existing structure with `ls`
3. Use paths relative to current directory

✅ CORRECT: `./src/file.js`, `./tests/test.js`
❌ WRONG: `./my-app/src/file.js`, `/absolute/path/file.js`

## 📋 Essential Protocols

### Starting Tasks
- Log task start: `mcp__logging__log_task_start(agent="[your-name]", task_id="[id]", description="[task]")`
- Check project context: `mcp__workspace__context()`
- Verify no duplicates: `mcp__workspace__check_duplicates(name="[component]", type="file")`

### Completing Tasks
- Log completion: `mcp__logging__log_task_complete(agent="[your-name]", task_id="[id]", result="success")`
- Update status: `mcp__coord__task_status(task_id="[id]", status="completed", progress=100)`

### When Blocked
- Log the issue: `mcp__logging__log_task_failed(agent="[your-name]", task_id="[id]", error="[error]")`
- Escalate if needed: `mcp__coord__escalation_create(task_id="[id]", from_agent="[your-name]", reason="[details]")`

### Document Registration
Always register documents you create:
```python
mcp__docs__register(
    path="./docs/mydoc.md",
    title="Document Title",
    owner="[your-name]",
    category="requirements|architecture|testing|etc"
)
```

## ⚠️ Remember
- The tools in your frontmatter are automatically available
- Use them naturally based on your purpose and the task at hand
- Focus on your domain expertise rather than tool mechanics