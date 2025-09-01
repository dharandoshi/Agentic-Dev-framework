#!/bin/bash
# Global install script for PensionID Agent Army utilities
# This installs the utilities globally so they work with any Agent Army project

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"

echo "🚀 Installing PensionID Agent Army utilities globally..."

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Copy utilities to global location
echo "Copying utilities to $INSTALL_DIR..."
cp "$SCRIPT_DIR/pid-agentarmy" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/agentlog" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/logview" "$INSTALL_DIR/"

# Make them executable
chmod +x "$INSTALL_DIR/pid-agentarmy"
chmod +x "$INSTALL_DIR/agentlog"
chmod +x "$INSTALL_DIR/logview"

# Check if ~/.local/bin is in PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo ""
    echo "Adding $INSTALL_DIR to PATH..."
    
    # Add to bashrc
    if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# PensionID Agent Army utilities" >> ~/.bashrc
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc
    fi
    
    # Also add to zshrc if it exists
    if [[ -f ~/.zshrc ]]; then
        if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.zshrc; then
            echo "" >> ~/.zshrc
            echo "# PensionID Agent Army utilities" >> ~/.zshrc
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc
        fi
    fi
fi

echo ""
echo "✅ Global installation complete!"
echo ""
echo "Available commands (work in any Agent Army project):"
echo "  pid-agentarmy - Main command center"
echo "  agentlog      - Quick log viewer"
echo "  logview       - Advanced log viewer"
echo ""
echo "Usage:"
echo "  1. Navigate to any Agent Army project (with .claude directory)"
echo "  2. Run: pid-agentarmy help"
echo ""
echo "Note: Run 'source ~/.bashrc' or start a new terminal for PATH changes."