#!/bin/bash
# Update all agents to include proper file operation logging

AGENTS_DIR="/home/dhara/PensionID/agent-army-trial/.claude/agents"
SHARED_LOGGING="/home/dhara/PensionID/agent-army-trial/.claude/agents/shared-logging-protocol.md"

echo "Updating agents with file operation logging protocol..."

# For each agent file
for agent_file in "$AGENTS_DIR"/*.md; do
    if [[ -f "$agent_file" && "$agent_file" != *"shared-"* ]]; then
        agent_name=$(basename "$agent_file" .md)
        echo "Updating $agent_name..."
        
        # Check if agent already has the new logging section
        if ! grep -q "mcp__logging__log_file_operation" "$agent_file"; then
            
            # Check if agent has old logging section to replace
            if grep -q "## 📊 Logging and Monitoring Protocol" "$agent_file"; then
                echo "  - Replacing old logging section with new one"
                
                # Create a temporary file with updated content
                temp_file="${agent_file}.tmp"
                
                # Process the file
                awk '
                    /^## 📊 Logging and Monitoring Protocol/ {
                        print "## 📊 Human-Readable Logging Protocol"
                        print ""
                        print "**CRITICAL**: You MUST log all activities in a human-readable format."
                        print ""
                        print "### File Operations (ALWAYS LOG THESE):"
                        print "```python"
                        print "# Before reading any file:"
                        print "mcp__logging__log_file_operation("
                        print "  agent=\"'$agent_name'\","
                        print "  operation=\"read\","
                        print "  file_path=\"/path/to/file\","
                        print "  task_id=\"current_task_id\""
                        print ")"
                        print ""
                        print "# Before writing any file:"
                        print "mcp__logging__log_file_operation("
                        print "  agent=\"'$agent_name'\","
                        print "  operation=\"write\","
                        print "  file_path=\"/path/to/file\","
                        print "  details=\"What you are writing\","
                        print "  task_id=\"current_task_id\""
                        print ")"
                        print ""
                        print "# Before editing any file:"
                        print "mcp__logging__log_file_operation("
                        print "  agent=\"'$agent_name'\","
                        print "  operation=\"edit\","
                        print "  file_path=\"/path/to/file\","
                        print "  details=\"What you are changing\","
                        print "  task_id=\"current_task_id\""
                        print ")"
                        print "```"
                        print ""
                        
                        # Skip the old logging section
                        in_logging_section = 1
                        next
                    }
                    
                    # Skip content until we hit the next section or end
                    in_logging_section && /^##[^#]/ {
                        in_logging_section = 0
                    }
                    
                    # Print lines that are not in the old logging section
                    !in_logging_section {
                        print
                    }
                ' "$agent_file" > "$temp_file"
                
                # Replace the original file
                mv "$temp_file" "$agent_file"
                echo "  - Updated $agent_name with new logging protocol"
            else
                echo "  - No logging section found, skipping $agent_name"
            fi
            
            # Add mcp__logging__log_file_operation to tools if not present
            if grep -q "^tools:" "$agent_file"; then
                if ! grep -q "mcp__logging__log_file_operation" "$agent_file"; then
                    # Add the new logging tool to the tools list
                    sed -i "/^tools:/ s/$/, mcp__logging__log_file_operation/" "$agent_file"
                    echo "  - Added log_file_operation to tools list"
                fi
            fi
        else
            echo "  - $agent_name already has file operation logging"
        fi
    fi
done

echo ""
echo "✅ Agent logging update complete!"
echo ""
echo "Agents will now log:"
echo "  - File operations (read/write/edit) with paths"
echo "  - Tool usage with success/failure"
echo "  - Decisions with rationale"
echo "  - Task lifecycle events"
echo ""
echo "Logs location: .claude/logs/agents_YYYYMMDD.log"