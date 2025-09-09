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

# Setup sound notifications (optional)
echo ""
read -p "Would you like to setup sound notifications? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ -x "$CLAUDE_DIR/scripts/setup-sound-notifications.sh" ]]; then
        "$CLAUDE_DIR/scripts/setup-sound-notifications.sh"
    else
        echo "Sound setup script not found. Run manually:"
        echo "  $CLAUDE_DIR/scripts/setup-sound-notifications.sh"
    fi
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