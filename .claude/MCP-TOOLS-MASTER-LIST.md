# Complete MCP Tools Master List

## All Available MCP Tools (33 Total)

### Docs Server (7 tools)
- `mcp__docs__register` - Register new document
- `mcp__docs__find` - Find documents  
- `mcp__docs__search` - Search content
- `mcp__docs__get` - Get document by ID
- `mcp__docs__update` - Update document
- `mcp__docs__related` - Find related docs
- `mcp__docs__tree` - Get document tree

### Workspace Server (12 tools)
- `mcp__workspace__analyze` - Complete project analysis
- `mcp__workspace__detect` - Quick framework detection
- `mcp__workspace__context` - AI-optimized project context
- `mcp__workspace__standards` - Extract coding standards
- `mcp__workspace__entry_points` - Find main entry files
- `mcp__workspace__find` - Find files by pattern
- `mcp__workspace__test_command` - Get test command
- `mcp__workspace__build_command` - Get build command
- `mcp__workspace__packages` - Package manager info
- `mcp__workspace__deps` - Analyze dependencies
- `mcp__workspace__git` - Git repository status
- `mcp__workspace__metrics` - Project metrics and LOC

### Validation Server (7 tools)
- `mcp__validation__syntax` - Check syntax errors
- `mcp__validation__lint` - Run linter with auto-fix
- `mcp__validation__format` - Auto-format code
- `mcp__validation__types` - Type checking
- `mcp__validation__imports` - Verify imports exist
- `mcp__validation__validate` - Run all validations
- `mcp__validation__tools` - Detect available tools

### Execution Server (7 tools)
- `mcp__execution__run` - Execute code snippet
- `mcp__execution__script` - Run script file
- `mcp__execution__test` - Run tests with coverage
- `mcp__execution__api` - Test API endpoints
- `mcp__execution__command` - Run shell commands
- `mcp__execution__debug` - Debug and analyze errors
- `mcp__execution__profile` - Profile performance

## Agent Tool Assignments

### Requirements & Planning
**requirements-analyst**: Documentation focus
- All `mcp__docs__*` tools
- `mcp__workspace__analyze`
- `mcp__workspace__context`
- `mcp__workspace__find`

### Architecture & Design  
**system-architect**: System design and structure
- `mcp__workspace__analyze`
- `mcp__workspace__detect`
- `mcp__workspace__context`
- `mcp__workspace__standards`
- `mcp__workspace__deps`
- `mcp__workspace__metrics`
- `mcp__docs__register`
- `mcp__docs__find`

**tech-lead**: Technical decisions and code quality
- All `mcp__workspace__*` tools
- All `mcp__validation__*` tools
- `mcp__execution__debug`
- `mcp__execution__profile`
- `mcp__docs__register`

### Development
**senior-backend-engineer**: Backend implementation
- All `mcp__workspace__*` tools
- All `mcp__validation__*` tools
- All `mcp__execution__*` tools
- `mcp__docs__register`

**senior-frontend-engineer**: Frontend implementation
- All `mcp__workspace__*` tools
- All `mcp__validation__*` tools
- All `mcp__execution__*` tools
- `mcp__docs__register`

**senior-fullstack-engineer**: Full-stack development
- All `mcp__workspace__*` tools
- All `mcp__validation__*` tools
- All `mcp__execution__*` tools
- `mcp__docs__register`

### Quality & Testing
**qa-engineer**: Testing and quality
- `mcp__workspace__test_command`
- `mcp__workspace__find`
- `mcp__validation__syntax`
- `mcp__validation__validate`
- `mcp__execution__test`
- `mcp__execution__api`
- `mcp__execution__debug`
- `mcp__docs__register`

### Operations
**devops-engineer**: Infrastructure and deployment
- `mcp__workspace__build_command`
- `mcp__workspace__packages`
- `mcp__workspace__deps`
- `mcp__workspace__git`
- `mcp__execution__command`
- `mcp__execution__script`
- `mcp__docs__register`

### Specialized Roles
**api-designer**: API design
- `mcp__workspace__analyze`
- `mcp__workspace__standards`
- `mcp__execution__api`
- `mcp__docs__register`

**database-architect**: Database design
- `mcp__workspace__analyze`
- `mcp__workspace__context`
- `mcp__execution__command`
- `mcp__docs__register`

**security-engineer**: Security
- `mcp__workspace__deps`
- `mcp__validation__imports`
- `mcp__execution__debug`
- `mcp__docs__register`

**performance-engineer**: Performance optimization
- `mcp__workspace__metrics`
- `mcp__execution__profile`
- `mcp__execution__run`
- `mcp__docs__register`

**ui-ux-designer**: UI/UX design
- `mcp__workspace__find`
- `mcp__workspace__context`
- `mcp__docs__register`

**documentation-writer**: Documentation
- All `mcp__docs__*` tools
- `mcp__workspace__context`
- `mcp__workspace__find`

**code-reviewer**: Code review
- All `mcp__validation__*` tools
- `mcp__workspace__standards`
- `mcp__workspace__git`
- `mcp__execution__debug`

**mobile-app-developer**: Mobile development
- All `mcp__workspace__*` tools
- All `mcp__validation__*` tools
- `mcp__execution__run`
- `mcp__execution__debug`
- `mcp__docs__register`