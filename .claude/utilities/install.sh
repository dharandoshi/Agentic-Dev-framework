#!/bin/bash
# Install script for PensionID Agent Army utilities
# Adds commands to PATH and creates aliases

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(dirname "$SCRIPT_DIR")"
UTIL_DIR="$SCRIPT_DIR"

echo "Setting up PensionID Agent Army utilities..."

# Add to PATH for current session
export PATH="$UTIL_DIR:$PATH"

# Add to bashrc for permanent access
if ! grep -q "agent-army-trial/.claude/utilities" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# PensionID Agent Army utilities" >> ~/.bashrc
    echo "export PATH=\"$UTIL_DIR:\$PATH\"" >> ~/.bashrc
    echo "✅ Added to ~/.bashrc"
fi

# Create convenient aliases
if ! grep -q "alias pid-agentarmy=" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# PensionID Agent Army aliases" >> ~/.bashrc
    echo "alias pid-agentarmy='$UTIL_DIR/pid-agentarmy'" >> ~/.bashrc
    echo "alias agentlog='$UTIL_DIR/agentlog'" >> ~/.bashrc
    echo "alias logview='python3 $UTIL_DIR/logview'" >> ~/.bashrc
    echo "✅ Added aliases"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  pid-agentarmy - Main command center"
echo "  agentlog      - Quick log viewer"
echo "  logview       - Advanced log viewer"
echo ""
echo "Try: pid-agentarmy help"
echo ""
echo "Note: Run 'source ~/.bashrc' or start a new terminal for changes to take effect."