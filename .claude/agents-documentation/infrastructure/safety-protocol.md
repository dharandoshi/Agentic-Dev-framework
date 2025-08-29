# 🛡️ UNIVERSAL SAFETY PROTOCOL FOR ALL AGENTS

## MANDATORY: Before Starting ANY Task

### 1. Understand the Project
```
ALWAYS START WITH:
1. mcp__workspace__analyze - Full project analysis
2. mcp__workspace__context - Get AI-optimized summary  
3. mcp__workspace__standards - Understand coding conventions
```

### 2. Before Creating ANY File
```
MUST CHECK:
1. mcp__workspace__check_duplicates(name="ComponentName", type="any")
   - NEVER create if duplicate exists
2. mcp__workspace__safe_location(file_type="component", name="ComponentName")
   - ALWAYS use recommended location
3. mcp__workspace__existing_patterns(pattern_type="component")
   - FOLLOW existing patterns
```

### 3. Before Modifying ANY File
```
CRITICAL CHECKS:
1. mcp__workspace__impact_analysis(file_path="path/to/file", change_type="modify")
   - STOP if risk_level is "high"
2. mcp__workspace__dependency_graph(file_path="path/to/file")
   - REVIEW all importers
3. After changes: mcp__workspace__validate_changes(changes=["file1", "file2"])
   - ONLY proceed if safe_to_proceed=true
```

## Tech Stack Agnostic Rules

### ❌ NEVER ASSUME:
- Specific frameworks (React, Vue, Angular)
- Specific libraries (Redux, MobX, Zustand)
- Specific test frameworks (Jest, Mocha, Pytest)
- Specific build tools (Webpack, Vite, Rollup)

### ✅ ALWAYS DETECT:
- Use `mcp__workspace__detect` to identify actual tech stack
- Use `mcp__workspace__analyze` for comprehensive project understanding
- Use existing tool detection capabilities
- Adapt to whatever technology is actually in use

## Example Workflow

```python
# 1. Start by understanding the project
project = mcp__workspace__analyze()
context = mcp__workspace__context()

# 2. Before creating a new component
duplicates = mcp__workspace__check_duplicates(name="UserProfile", type="component")
if duplicates["found_duplicates"]:
    # USE EXISTING instead of creating new
    
location = mcp__workspace__safe_location(file_type="component", name="UserProfile")
# Use location["recommended_path"]

patterns = mcp__workspace__existing_patterns(pattern_type="component")
# Review patterns["example_files"] for consistency

# 3. Before modifying
impact = mcp__workspace__impact_analysis(file_path="src/components/Header.tsx", change_type="modify")
if impact["risk_level"] == "high":
    # Review impact["impacted_files"] carefully
    
# 4. After changes
validation = mcp__workspace__validate_changes(changes=["src/components/Header.tsx"])
if not validation["safe_to_proceed"]:
    # FIX ISSUES before proceeding
```

## Handoff Protocol

When handing off to another agent, ALWAYS include:
1. Tech stack summary from `mcp__workspace__context`
2. Files modified/created
3. Validation status from `mcp__workspace__validate_changes`
4. Any failing tests or issues

## Zero-Break Policy

**CRITICAL**: Your changes must NEVER break existing functionality
- Run tests before and after changes
- Check all dependencies
- Validate all modifications
- If unsure, escalate to engineering-manager

## Technology Adaptation

Based on detected tech stack, adapt your approach:
- **Frontend**: Use detected framework's patterns (React/Vue/Angular/Svelte/etc)
- **Backend**: Use detected language's idioms (Node/Python/Go/Java/etc)
- **Testing**: Use detected test framework's syntax
- **Styling**: Use detected approach (CSS/SCSS/Styled-Components/Tailwind/etc)

Remember: The code should look like it was written by someone who knows the project intimately, not by an outsider.