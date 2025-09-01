#!/bin/bash
# Uninstall script for PensionID Agent Army utilities
# Removes both global and local installations

echo "🗑️  Uninstalling PensionID Agent Army utilities..."

# Remove from global location if exists
if [[ -f "$HOME/.local/bin/pid-agentarmy" ]]; then
    rm -f "$HOME/.local/bin/pid-agentarmy"
    rm -f "$HOME/.local/bin/agentlog"
    rm -f "$HOME/.local/bin/logview"
    echo "✅ Removed global installation"
fi

# Remove PATH entry
if grep -q "agent-army-trial/.claude/utilities" ~/.bashrc; then
    sed -i '/agent-army-trial\/.claude\/utilities/d' ~/.bashrc
    echo "✅ Removed PATH entry"
fi

# Remove aliases
if grep -q "alias pid-agentarmy=" ~/.bashrc; then
    sed -i '/alias pid-agentarmy=/d' ~/.bashrc
    echo "✅ Removed pid-agentarmy alias"
fi

if grep -q "alias agentlog=" ~/.bashrc; then
    sed -i '/alias agentlog=/d' ~/.bashrc
    echo "✅ Removed agentlog alias"
fi

if grep -q "alias logview=" ~/.bashrc; then
    sed -i '/alias logview=/d' ~/.bashrc
    echo "✅ Removed logview alias"
fi

# Clean up empty lines and headers
sed -i '/# PensionID Agent Army utilities/d' ~/.bashrc
sed -i '/# PensionID Agent Army aliases/d' ~/.bashrc

echo ""
echo "✅ Uninstall complete!"
echo ""
echo "The utilities are still in .claude/utilities/ but are no longer in PATH."
echo "To remove completely, delete: .claude/utilities/"
echo ""
echo "Note: Run 'source ~/.bashrc' or start a new terminal for changes to take effect."