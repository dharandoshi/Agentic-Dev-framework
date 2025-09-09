#!/bin/bash
# Test script for Claude Code sound notifications

echo "Testing Claude Code Sound Notifications"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOUND_SCRIPT="$SCRIPT_DIR/sound-notifications.py"

# Test different event types
declare -A test_events=(
    ["SessionStart"]='{"hook_event_name": "SessionStart", "session_id": "test123"}'
    ["AgentComplete"]='{"hook_event_name": "Stop", "session_id": "test123"}'
    ["Permission"]='{"hook_event_name": "Notification", "message": "Awaiting permission from user"}'
    ["Error"]='{"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_response": {"error": "Command failed"}}'
    ["TaskStart"]='{"hook_event_name": "PreToolUse", "tool_name": "Task"}'
    ["SessionEnd"]='{"hook_event_name": "SessionEnd", "reason": "exit"}'
)

echo "This will play different sounds for each event type."
echo "Make sure your volume is on!"
echo ""

for event_name in "${!test_events[@]}"; do
    echo "Testing: $event_name"
    echo "${test_events[$event_name]}" | python3 "$SOUND_SCRIPT"
    sleep 1.5  # Brief pause between sounds
done

echo ""
echo "Sound test complete!"
echo ""
echo "If you didn't hear sounds, check:"
echo "1. Your system volume is on"
echo "2. You have audio output device connected"
echo "3. Required audio players are installed:"
echo "   - macOS: afplay (built-in)"
echo "   - Linux: paplay, aplay, or play"
echo "   - Windows: PowerShell (built-in)"