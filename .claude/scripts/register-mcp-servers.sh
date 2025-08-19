#!/bin/bash
"""
Agent Army MCP Server Registration Script
Registers all required MCP servers with Claude Code
"""

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PYTHON="$PROJECT_ROOT/.claude/mcp/venv/bin/python"

echo "🔧 Agent Army MCP Server Registration"
echo "======================================"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Check if Claude CLI is available
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI not found. Please install Claude Code first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ MCP virtual environment not found at: $VENV_PYTHON"
    echo "Please run setup script first to create the virtual environment."
    exit 1
fi

echo "✅ Claude Code CLI found"
echo "✅ MCP virtual environment found"
echo ""

# Define MCP servers to register
declare -A servers=(
    ["workspace"]="workspace.py"
    ["docs"]="docs.py" 
    ["execution"]="execution.py"
    ["coord"]="coord.py"
    ["validation"]="validation.py"
)

# Check if servers are already registered
echo "📋 Checking existing MCP server registration..."
existing_servers=$(claude mcp list 2>/dev/null | grep -E "(workspace|docs|execution|coord|validation)" | wc -l || echo "0")

if [ "$existing_servers" -eq 5 ]; then
    echo "✅ All MCP servers already registered"
    claude mcp list
    exit 0
fi

# Remove any existing servers first to avoid conflicts
echo "🧹 Cleaning up any existing MCP server registrations..."
for server_name in "${!servers[@]}"; do
    claude mcp remove "$server_name" 2>/dev/null || true
done

echo ""
echo "📦 Registering MCP servers..."

# Register each server
for server_name in "${!servers[@]}"; do
    server_file="${servers[$server_name]}"
    server_path="./.claude/mcp/servers/core/$server_file"
    
    # Check if server file exists
    if [ ! -f "$PROJECT_ROOT/$server_path" ]; then
        echo "❌ Server file not found: $server_path"
        continue
    fi
    
    echo "  📡 Registering $server_name..."
    
    # Create JSON configuration for the server
    server_config='{
        "type": "stdio",
        "command": "./.claude/mcp/venv/bin/python",
        "args": ["'$server_path'"],
        "env": {
            "PYTHONPATH": "./.claude/mcp"
        },
        "cwd": "."
    }'
    
    # Register the server using claude mcp add-json
    if claude mcp add-json "$server_name" "$server_config" >/dev/null 2>&1; then
        echo "  ✅ $server_name registered successfully"
    else
        echo "  ❌ Failed to register $server_name"
    fi
done

echo ""
echo "🔍 Verifying MCP server registration..."

# Wait a moment for servers to initialize
sleep 2

# Check server health
if claude mcp list | grep -q "Connected"; then
    echo "✅ MCP servers registered and connected successfully!"
    echo ""
    claude mcp list
else
    echo "⚠️  Some MCP servers may not be connected properly"
    echo "Please check the server status:"
    claude mcp list
fi

echo ""
echo "🎉 MCP server registration completed!"
echo ""
echo "Next steps:"
echo "1. Test MCP functionality with: python3 .claude/scripts/validate-environment.py"
echo "2. Test agent functionality in Claude Code"
echo "3. Run a sample agent workflow"