#!/bin/bash

# Batch update all agents to add new safety tools

AGENT_DIR="/home/dhara/PensionID/agent-army-trial/.claude/agents"
NEW_TOOLS="mcp__workspace__check_duplicates, mcp__workspace__impact_analysis, mcp__workspace__dependency_graph, mcp__workspace__safe_location, mcp__workspace__validate_changes, mcp__workspace__existing_patterns"

echo "Updating agents with new safety tools..."

# Update each agent file
for agent_file in "$AGENT_DIR"/*.md; do
    if [ -f "$agent_file" ]; then
        agent_name=$(basename "$agent_file" .md)
        echo "Updating $agent_name..."
        
        # Check if agent already has workspace tools
        if grep -q "mcp__workspace__analyze" "$agent_file"; then
            # Add new tools after mcp__workspace__metrics if not already present
            if ! grep -q "mcp__workspace__check_duplicates" "$agent_file"; then
                sed -i "s/mcp__workspace__metrics/mcp__workspace__metrics, $NEW_TOOLS/g" "$agent_file"
                echo "  ✓ Added new safety tools to $agent_name"
            else
                echo "  - $agent_name already has safety tools"
            fi
        fi
    fi
done

echo "Done updating agents!"