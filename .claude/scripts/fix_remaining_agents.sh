#!/bin/bash

# Add workspace tools to agents that completely lack them

AGENT_DIR="/home/dhara/PensionID/agent-army-trial/.claude/agents"
WORKSPACE_TOOLS="mcp__workspace__analyze, mcp__workspace__detect, mcp__workspace__context, mcp__workspace__standards, mcp__workspace__find, mcp__workspace__check_duplicates, mcp__workspace__impact_analysis, mcp__workspace__dependency_graph, mcp__workspace__safe_location, mcp__workspace__validate_changes, mcp__workspace__existing_patterns"

echo "Adding workspace tools to agents that lack them..."

# List of agents that need workspace tools added
agents_to_fix=(
    "devops-engineer"
    "qa-engineer"
    "security-engineer"
    "scrum-master"
    "technical-writer"
    "god-agent"
)

for agent in "${agents_to_fix[@]}"; do
    agent_file="$AGENT_DIR/$agent.md"
    if [ -f "$agent_file" ]; then
        echo "Fixing $agent..."
        # Add workspace tools after the existing tools
        sed -i "s/tools: /tools: $WORKSPACE_TOOLS, /" "$agent_file"
        echo "  ✓ Added workspace tools to $agent"
    fi
done

echo "Done fixing agents!"