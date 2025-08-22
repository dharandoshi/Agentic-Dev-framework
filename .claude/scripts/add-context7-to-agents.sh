#!/bin/bash

# Script to add Context7 MCP tools and instructions to all technical agents

AGENTS_DIR=".claude/agents"

# Context7 tools to add
CONTEXT7_TOOLS="mcp__context7__resolve-library-id, mcp__context7__get-library-docs"

# Context7 instructions section
read -r -d '' CONTEXT7_SECTION << 'EOF'

## MANDATORY: Documentation Fetching with Context7 MCP

### ⚠️ CRITICAL REQUIREMENT
**BEFORE implementing ANY code, you MUST:**
1. **Identify all libraries and frameworks** being used
2. **Check exact versions** from package.json, requirements.txt, pom.xml, go.mod, etc.
3. **Fetch documentation** using Context7 MCP for the EXACT versions
4. **Review the documentation** before writing any code

### Context7 MCP Usage Protocol

#### Step 1: Version Detection (MANDATORY)
Before any implementation, check version files:
- **Node.js/JavaScript**: package.json, package-lock.json
- **Python**: requirements.txt, Pipfile, pyproject.toml
- **Java**: pom.xml, build.gradle
- **Go**: go.mod
- **Ruby**: Gemfile
- **PHP**: composer.json
- **.NET**: *.csproj, packages.config

#### Step 2: Resolve Library IDs (MANDATORY)
For each library/framework found:
```
mcp__context7__resolve-library-id(
  libraryName="[library-name]"
)
```

#### Step 3: Fetch Version-Specific Documentation (MANDATORY)
```
mcp__context7__get-library-docs(
  context7CompatibleLibraryID="/org/project/version",
  tokens=10000,
  topic="[specific-topic-if-needed]"
)
```

#### Example Workflow
```
1. Find React version: package.json shows "react": "18.2.0"
2. Resolve: mcp__context7__resolve-library-id(libraryName="react")
3. Fetch: mcp__context7__get-library-docs(
     context7CompatibleLibraryID="/facebook/react/18.2.0",
     tokens=10000,
     topic="hooks"
   )
4. ONLY THEN start implementing React hooks
```

### Documentation Priority Order
1. **Exact version match** (e.g., React 18.2.0)
2. **Minor version match** (e.g., React 18.2.x)
3. **Major version match** (e.g., React 18.x)
4. **Latest stable** (only if specific version unavailable)

### When to Use Context7 (ALWAYS)
- Before writing ANY new code
- Before modifying existing code using unfamiliar libraries
- When debugging library-specific issues
- When optimizing performance
- When implementing security features
- When integrating third-party services

### Failure Protocol
If Context7 documentation is unavailable:
1. Alert the user that documentation couldn't be fetched
2. Ask if they want to proceed without documentation
3. Document the risk of potential version incompatibilities
4. Use WebSearch as fallback for critical information

EOF

# Technical agents that need Context7
TECHNICAL_AGENTS=(
    "senior-backend-engineer"
    "senior-frontend-engineer"
    "tech-lead"
    "devops-engineer"
    "cloud-architect"
    "integration-engineer"
    "security-engineer"
    "data-engineer"
    "sre-engineer"
    "qa-engineer"
    "system-architect"
)

echo "Adding Context7 MCP tools and instructions to technical agents..."

for agent in "${TECHNICAL_AGENTS[@]}"; do
    agent_file="$AGENTS_DIR/${agent}.md"
    
    if [ -f "$agent_file" ]; then
        echo "Processing $agent..."
        
        # Check if Context7 tools are already in the tools list
        if ! grep -q "mcp__context7__" "$agent_file"; then
            echo "  Adding Context7 tools to $agent..."
            # Add Context7 tools to the end of the tools list (before the closing)
            sed -i "s/^tools: \(.*\)$/tools: \1, ${CONTEXT7_TOOLS}/" "$agent_file"
        fi
        
        # Check if Context7 section exists
        if ! grep -q "MANDATORY: Documentation Fetching with Context7" "$agent_file"; then
            echo "  Adding Context7 instructions to $agent..."
            # Find where to insert (after the Purpose section, before Best Practices or at end)
            if grep -q "## Best Practices" "$agent_file"; then
                # Insert before Best Practices
                awk -v section="$CONTEXT7_SECTION" '
                    /^## Best Practices/ {print section; print ""}
                    {print}
                ' "$agent_file" > "${agent_file}.tmp" && mv "${agent_file}.tmp" "$agent_file"
            else
                # Append at the end
                echo "$CONTEXT7_SECTION" >> "$agent_file"
            fi
        else
            echo "  Context7 instructions already exist in $agent, updating to mandatory version..."
            # Remove old section and add new mandatory one
            sed -i '/^## Documentation Fetching with Context7/,/^##[^#]/d' "$agent_file"
            sed -i '/^## Context7 MCP/,/^##[^#]/d' "$agent_file"
            
            if grep -q "## Best Practices" "$agent_file"; then
                awk -v section="$CONTEXT7_SECTION" '
                    /^## Best Practices/ {print section; print ""}
                    {print}
                ' "$agent_file" > "${agent_file}.tmp" && mv "${agent_file}.tmp" "$agent_file"
            else
                echo "$CONTEXT7_SECTION" >> "$agent_file"
            fi
        fi
    else
        echo "Warning: $agent_file not found"
    fi
done

# Also update non-technical agents that might benefit
NON_TECHNICAL_AGENTS=(
    "technical-writer"  # Needs accurate API documentation
    "god-agent"        # Oversees all agents
)

echo -e "\nAdding Context7 to non-technical agents that need it..."

for agent in "${NON_TECHNICAL_AGENTS[@]}"; do
    agent_file="$AGENTS_DIR/${agent}.md"
    
    if [ -f "$agent_file" ]; then
        echo "Processing $agent..."
        
        if ! grep -q "mcp__context7__" "$agent_file"; then
            sed -i "s/^tools: \(.*\)$/tools: \1, ${CONTEXT7_TOOLS}/" "$agent_file"
        fi
        
        if ! grep -q "MANDATORY: Documentation Fetching with Context7" "$agent_file"; then
            echo "$CONTEXT7_SECTION" >> "$agent_file"
        fi
    fi
done

echo -e "\nContext7 MCP integration complete!"
echo "All technical agents now have:"
echo "  ✓ Context7 tools in their tool list"
echo "  ✓ Mandatory documentation fetching instructions"
echo "  ✓ Version-specific documentation requirements"