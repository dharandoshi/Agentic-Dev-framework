#!/bin/bash
# Initialize a new Agent Army project with unique ID

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Global registry location
GLOBAL_REGISTRY="$HOME/.agent-army/registry.json"
GLOBAL_DIR="$HOME/.agent-army"

# Function to generate project ID
generate_project_id() {
    local project_name="$1"
    # Create ID from project name (alphanumeric, lowercase)
    local base_id=$(echo "$project_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//')
    
    # Add timestamp if ID exists
    if grep -q "\"$base_id\"" "$GLOBAL_REGISTRY" 2>/dev/null; then
        echo "${base_id}-$(date +%s)"
    else
        echo "$base_id"
    fi
}

# Initialize global registry if not exists
init_global_registry() {
    if [[ ! -f "$GLOBAL_REGISTRY" ]]; then
        mkdir -p "$GLOBAL_DIR"
        cat > "$GLOBAL_REGISTRY" << EOF
{
  "projects": {},
  "mcp_servers": {
    "base_url": "http://localhost",
    "base_port": 8000
  }
}
EOF
        echo -e "${GREEN}✓ Created global registry at $GLOBAL_REGISTRY${NC}"
    fi
}

# Register project
register_project() {
    local project_id="$1"
    local project_path="$2"
    local project_name="$3"
    
    # Update registry using Python for proper JSON handling
    python3 << EOF
import json
from pathlib import Path

registry_file = Path("$GLOBAL_REGISTRY")
registry = json.loads(registry_file.read_text())

registry["projects"]["$project_id"] = {
    "id": "$project_id",
    "name": "$project_name",
    "path": "$project_path",
    "created": "$(date -I)",
    "active": True
}

registry_file.write_text(json.dumps(registry, indent=2))
print("✓ Project registered with ID: $project_id")
EOF
}

# Create project config
create_project_config() {
    local project_id="$1"
    local claude_dir="$2"
    
    cat > "$claude_dir/project.json" << EOF
{
  "project_id": "$project_id",
  "version": "1.0.0",
  "created": "$(date -I)",
  "mcp_data_namespace": "projects/$project_id"
}
EOF
}

# Main logic
main() {
    echo -e "${CYAN}🚀 Agent Army Project Initializer${NC}"
    echo ""
    
    # Check if in a directory with .claude
    if [[ ! -d ".claude" ]]; then
        echo -e "${YELLOW}No .claude directory found. Creating new Agent Army project...${NC}"
        
        # TODO: Copy template .claude structure
        echo "Please copy the .claude template first, then run this script again."
        exit 1
    fi
    
    # Get project details
    PROJECT_PATH=$(pwd)
    PROJECT_NAME=$(basename "$PROJECT_PATH")
    
    # Check if already initialized
    if [[ -f ".claude/project.json" ]]; then
        PROJECT_ID=$(grep '"project_id"' .claude/project.json | cut -d'"' -f4)
        echo -e "${GREEN}Project already initialized with ID: $PROJECT_ID${NC}"
        exit 0
    fi
    
    # Initialize global registry
    init_global_registry
    
    # Generate project ID
    echo -n "Enter project name (default: $PROJECT_NAME): "
    read -r input_name
    PROJECT_NAME="${input_name:-$PROJECT_NAME}"
    
    PROJECT_ID=$(generate_project_id "$PROJECT_NAME")
    
    echo ""
    echo -e "${CYAN}Project Details:${NC}"
    echo "  Name: $PROJECT_NAME"
    echo "  ID: $PROJECT_ID"
    echo "  Path: $PROJECT_PATH"
    echo ""
    
    # Register project
    register_project "$PROJECT_ID" "$PROJECT_PATH" "$PROJECT_NAME"
    
    # Create project config
    create_project_config "$PROJECT_ID" "$PROJECT_PATH/.claude"
    
    echo ""
    echo -e "${GREEN}✅ Project initialized successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start MCP servers (if not running): mcp-start"
    echo "  2. Use project: pid-agentarmy status"
    echo ""
    echo "Your project ID: ${CYAN}$PROJECT_ID${NC}"
    echo "This ID will be used for all MCP data isolation."
}

main "$@"