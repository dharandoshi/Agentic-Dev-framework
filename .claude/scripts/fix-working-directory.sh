#!/bin/bash

# Script to update all agent configurations with working directory rules

AGENTS_DIR=".claude/agents"
BACKUP_DIR=".claude/agents-backup-$(date +%Y%m%d-%H%M%S)"

echo "🔧 Fixing working directory issues in agent configurations..."

# Create backup
echo "📦 Creating backup at $BACKUP_DIR"
cp -r "$AGENTS_DIR" "$BACKUP_DIR"

# Working directory instruction block to add
read -r -d '' WORKING_DIR_INSTRUCTIONS << 'EOF'
## 🎯 CRITICAL: Working Directory Rules

### YOU MUST:
1. **Use the CURRENT working directory** - Never create project subfolders
2. **Check with pwd first** - Verify directory before any operations
3. **Read .claude/shared-context.md** - Follow shared directory rules
4. **Use existing structure** - Work within current directory layout

### File Creation:
- ✅ CORRECT: ./src/file.js (use current directory structure)
- ✅ CORRECT: ./tests/test.js (place in existing folders)
- ❌ WRONG: ./my-app/src/file.js (don't create project subfolder)
- ❌ WRONG: mkdir new-project (don't create new project folders)

### Before Starting ANY Task:
1. Run pwd to verify working directory
2. Run ls to check existing structure  
3. Read .claude/shared-context.md for rules
4. Use paths relative to current directory
EOF

# Process each agent file
for agent_file in "$AGENTS_DIR"/*.md; do
    if [ -f "$agent_file" ]; then
        agent_name=$(basename "$agent_file" .md)
        echo "📝 Processing $agent_name..."
        
        # Check if working directory rules already exist
        if ! grep -q "Working Directory Rules" "$agent_file"; then
            # Find the line with "# Purpose" and insert after it
            awk -v instructions="$WORKING_DIR_INSTRUCTIONS" '
                /^# Purpose/ {
                    print
                    print ""
                    print instructions
                    next
                }
                {print}
            ' "$agent_file" > "$agent_file.tmp"
            
            mv "$agent_file.tmp" "$agent_file"
            echo "   ✅ Updated $agent_name"
        else
            echo "   ⏭️  $agent_name already has working directory rules"
        fi
    fi
done

echo ""
echo "🎉 Working directory fixes complete!"
echo "📁 Backup saved at: $BACKUP_DIR"
echo ""
echo "Key changes:"
echo "  • Added working directory rules to all agents"
echo "  • Enforced current directory usage"
echo "  • Prevented subfolder creation"
echo "  • Added shared context reference"