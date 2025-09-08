#!/bin/bash
# Dynamic hook runner that finds project root automatically

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set environment variables
export CLAUDE_PROJECT_ROOT="$PROJECT_ROOT"

# Get the hook type and script name from arguments
HOOK_SCRIPT="$1"
shift  # Remove first argument so $@ contains only additional args

# Change to project root and run the hook
cd "$PROJECT_ROOT"
python3 "hooks/$HOOK_SCRIPT" "$@"