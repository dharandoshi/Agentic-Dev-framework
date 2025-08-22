# Agent Army Shared Context

## 🎯 CRITICAL: Working Directory Rules

### ABSOLUTE REQUIREMENTS:
1. **ALWAYS use the CURRENT working directory** - DO NOT create project subfolders
2. **Check working directory first** - Use `pwd` or `os.getcwd()` before any file operations
3. **Share the same workspace** - All agents work in the SAME directory
4. **No nested project folders** - Place files directly in the current directory structure

### Working Directory Protocol:

```bash
# ✅ CORRECT - Use current directory
./src/index.js
./package.json
./README.md

# ❌ WRONG - Don't create project subfolder
./my-todo-app/src/index.js
./inventory-system/package.json
```

### For All Agents:

1. **Before starting work:**
   ```bash
   pwd  # Verify current directory
   ls   # Check existing structure
   ```

2. **When creating files:**
   - Place source code in `./src/` (if it exists) or `./` 
   - Place tests in `./tests/` or `./test/`
   - Place docs in `./docs/`
   - Use existing structure if present

3. **Project Structure Example:**
   ```
   ./ (current working directory)
   ├── src/           # Source code
   ├── tests/         # Test files
   ├── docs/          # Documentation
   ├── public/        # Static assets (frontend)
   ├── api/           # API routes (backend)
   ├── models/        # Data models
   ├── package.json   # Dependencies
   └── README.md      # Project info
   ```

### Environment Variables:
- `CLAUDE_PROJECT_ROOT` = Current working directory
- `PWD` = Current working directory
- All agents should reference these for consistency

### File Creation Rules:
1. **Check if directory exists** before creating files
2. **Use relative paths** from current directory
3. **Never use absolute paths** unless required
4. **Share file locations** in handoffs

### Coordination Context:
When handing off tasks, ALWAYS include:
```json
{
  "working_directory": "/current/path",
  "files_created": ["./src/file1.js", "./tests/test1.js"],
  "project_structure": "standard|custom",
  "entry_point": "./src/index.js"
}
```

## 🔧 Implementation Checklist for Agents:

- [ ] Read this shared context before starting
- [ ] Verify working directory with `pwd`
- [ ] Use existing project structure
- [ ] Don't create unnecessary subfolders
- [ ] Share file paths in messages
- [ ] Use relative paths from current directory

## Example Correct Behavior:

```bash
# Agent 1: Tech Lead
$ pwd
/home/user/my-project
$ ls
# (empty or existing files)

# Creates structure:
$ mkdir -p src tests docs
$ touch src/index.js package.json

# Agent 2: Backend Engineer (handoff)
$ pwd
/home/user/my-project  # Same directory!
$ ls
src/ tests/ docs/ package.json
# Continues work in same structure
```

## ⚠️ Common Mistakes to Avoid:

1. ❌ `mkdir my-todo-app && cd my-todo-app`
2. ❌ `mkdir /home/user/projects/new-project`
3. ❌ Creating duplicate project structures
4. ❌ Using different working directories
5. ❌ Not checking existing structure

## 📝 Notes:
- This context is shared across ALL agents
- Updated regularly based on project needs
- Enforced by orchestrator hooks
- Part of agent coordination protocol