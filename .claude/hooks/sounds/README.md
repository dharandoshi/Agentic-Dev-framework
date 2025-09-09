# Custom Sound Files for Claude Code Notifications

Place your custom sound files in this directory with the following names:

## Required Sound Files

1. **agent-start.wav** - Plays when an agent or subagent starts
2. **agent-complete.wav** - Plays when an agent completes successfully  
3. **agent-error.wav** - Plays when an agent encounters an error
4. **permission-required.wav** - Plays when Claude needs user permission
5. **session-end.wav** - Plays when a conversation/session ends
6. **notification.wav** - General notification sound
7. **task-start.wav** - Plays when a new task begins
8. **tool-blocked.wav** - Plays when a tool is blocked

## Sound File Formats

Recommended formats:
- WAV (universally supported)
- MP3 (may require additional players on Linux)
- OGG (good for Linux systems)
- AIFF (native on macOS)

## System Fallbacks

If custom sounds are not provided, the system will use:

### macOS
- Built-in system sounds from `/System/Library/Sounds/`

### Linux  
- FreeDesktop sounds from `/usr/share/sounds/`
- System beep as last resort

### Windows
- Windows system sounds via winsound module

## Testing Sounds

You can test individual sounds by running:
```bash
# macOS
afplay sounds/agent-start.wav

# Linux
paplay sounds/agent-start.wav

# Windows (PowerShell)
(New-Object Media.SoundPlayer "sounds\agent-start.wav").PlaySync()
```

## Creating Custom Sounds

You can create or download custom sounds from:
- [Freesound.org](https://freesound.org)
- [Zapsplat.com](https://www.zapsplat.com)
- macOS: Record using QuickTime Player
- Linux: Record using `arecord` or Audacity
- Windows: Record using Voice Recorder app

Keep sounds short (< 2 seconds) for better UX.