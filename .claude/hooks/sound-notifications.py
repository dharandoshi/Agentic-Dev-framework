#!/usr/bin/env python3
"""
Sound Notification System for Claude Code Agent Army
Plays different sounds for various agent and conversation events
"""

import json
import sys
import os
import subprocess
import platform
from pathlib import Path
import threading

# Define sound file paths (you can customize these)
SOUNDS_DIR = Path(__file__).parent / "sounds"
SOUNDS = {
    "agent_start": "agent-start.mp3",      # When an agent/subagent starts
    "agent_complete": "agent-complete.mp3", # When an agent completes successfully
    "agent_error": "agent-error.mp3",      # When an agent fails
    "permission": "permission-required.mp3", # When waiting for user permission
    "session_end": "session-end.mp3",      # When conversation ends
    "notification": "notification.mp3",     # General notification
    "task_start": "task-start.mp3",        # When a new task begins
    "tool_blocked": "tool-blocked.mp3"     # When a tool is blocked
}

def get_system_platform():
    """Detect the operating system."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    return "unknown"

def play_sound_macos(sound_file):
    """Play sound on macOS using afplay."""
    try:
        subprocess.run(["afplay", sound_file], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try with osascript as fallback
        try:
            script = f'do shell script "afplay {sound_file}"'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
            return True
        except:
            return False

def play_sound_linux(sound_file):
    """Play sound on Linux using various methods."""
    # Try different audio players in order of preference
    players = [
        ["mpg123", "-q", sound_file],     # mpg123 - best for MP3
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", sound_file],  # FFmpeg
        ["play", "-q", sound_file],       # SoX  
        ["paplay", sound_file],           # PulseAudio
        ["aplay", sound_file],            # ALSA
        ["pw-play", sound_file],          # PipeWire
        ["cvlc", "--play-and-exit", "--intf", "dummy", sound_file],  # VLC
        ["mplayer", "-really-quiet", sound_file]  # MPlayer
    ]
    
    for player_cmd in players:
        try:
            subprocess.run(player_cmd, check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Try Python-based playback as fallback
    try:
        # Try using pygame if available
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        return True
    except ImportError:
        pass
    
    # Try using playsound if available
    try:
        from playsound import playsound
        playsound(sound_file)
        return True
    except ImportError:
        pass
    
    # Try speaker-test as last resort (beep)
    try:
        subprocess.run(["speaker-test", "-t", "sine", "-f", "1000", "-l", "1"], 
                      timeout=0.2, capture_output=True)
        return True
    except:
        return False

def play_sound_windows(sound_file):
    """Play sound on Windows using PowerShell."""
    try:
        # Use PowerShell to play sound
        ps_command = f'(New-Object Media.SoundPlayer "{sound_file}").PlaySync()'
        subprocess.run(["powershell", "-Command", ps_command], 
                      check=True, capture_output=True)
        return True
    except:
        # Try with Windows Media Player as fallback
        try:
            subprocess.run(["start", "/min", sound_file], 
                          shell=True, check=True, capture_output=True)
            return True
        except:
            return False

def play_system_sound(sound_type="notification"):
    """Play a system sound based on the event type."""
    platform_name = get_system_platform()
    
    # Use system sounds if custom sounds not available
    if platform_name == "macos":
        # macOS system sounds
        system_sounds = {
            "agent_start": "/System/Library/Sounds/Hero.aiff",
            "agent_complete": "/System/Library/Sounds/Glass.aiff",
            "agent_error": "/System/Library/Sounds/Basso.aiff",
            "permission": "/System/Library/Sounds/Ping.aiff",
            "session_end": "/System/Library/Sounds/Submarine.aiff",
            "notification": "/System/Library/Sounds/Pop.aiff",
            "task_start": "/System/Library/Sounds/Morse.aiff",
            "tool_blocked": "/System/Library/Sounds/Funk.aiff"
        }
        sound_file = system_sounds.get(sound_type, "/System/Library/Sounds/Pop.aiff")
        return play_sound_macos(sound_file)
    
    elif platform_name == "linux":
        # Try to play a beep using various methods
        beep_commands = [
            ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
            ["paplay", "/usr/share/sounds/ubuntu/stereo/message.ogg"],
            ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"],
            ["beep"],  # System beep
            ["tput", "bel"],  # Terminal bell
            ["printf", "\\a"]  # ASCII bell
        ]
        
        for cmd in beep_commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                return True
            except:
                continue
        return False
    
    elif platform_name == "windows":
        # Windows system sounds
        import winsound
        try:
            sound_map = {
                "agent_start": winsound.MB_OK,
                "agent_complete": winsound.MB_ICONASTERISK,
                "agent_error": winsound.MB_ICONHAND,
                "permission": winsound.MB_ICONQUESTION,
                "session_end": winsound.MB_ICONEXCLAMATION,
                "notification": winsound.MB_OK,
                "task_start": winsound.MB_OK,
                "tool_blocked": winsound.MB_ICONHAND
            }
            winsound.MessageBeep(sound_map.get(sound_type, winsound.MB_OK))
            return True
        except:
            return False
    
    return False

def get_sound_for_event(hook_event, tool_name=None, additional_context=None):
    """Determine which sound to play based on the event."""
    
    # Map hook events to sound types
    if hook_event == "SessionStart":
        return "agent_start"
    elif hook_event == "SessionEnd":
        return "session_end"
    elif hook_event == "Stop" or hook_event == "SubagentStop":
        return "agent_complete"
    elif hook_event == "Notification":
        # Check notification message for context
        if additional_context and "error" in additional_context.lower():
            return "agent_error"
        elif additional_context and "permission" in additional_context.lower():
            return "permission"
        return "notification"
    elif hook_event == "PreToolUse":
        # Special sound for subagent/task tools
        if tool_name and "Task" in tool_name:
            return "task_start"
        return None  # No sound for regular tool use
    elif hook_event == "PostToolUse":
        # Check for errors in tool response
        if additional_context and "error" in str(additional_context).lower():
            return "agent_error"
        elif tool_name and "Task" in tool_name:
            return "agent_complete"
        return None
    elif hook_event == "UserPromptSubmit":
        return None  # No sound for prompt submission
    
    # Check for permission/approval contexts
    if additional_context:
        context_str = str(additional_context).lower()
        if "permission" in context_str or "approve" in context_str or "confirm" in context_str:
            return "permission"
        elif "block" in context_str or "deny" in context_str:
            return "tool_blocked"
    
    return "notification"  # Default sound

def main():
    """Main function to handle hook input and play appropriate sound."""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        # Extract relevant information
        hook_event = input_data.get("hook_event_name", "")
        tool_name = input_data.get("tool_name", "")
        tool_response = input_data.get("tool_response", {})
        message = input_data.get("message", "")
        prompt = input_data.get("prompt", "")
        
        # Determine additional context
        additional_context = message or prompt or tool_response
        
        # Get the appropriate sound type
        sound_type = get_sound_for_event(hook_event, tool_name, additional_context)
        
        if sound_type:
            # Try to play custom sound first, then system sound
            custom_sound = SOUNDS_DIR / SOUNDS.get(sound_type, "notification.wav")
            
            if custom_sound.exists():
                platform_name = get_system_platform()
                if platform_name == "macos":
                    success = play_sound_macos(str(custom_sound))
                elif platform_name == "linux":
                    success = play_sound_linux(str(custom_sound))
                elif platform_name == "windows":
                    success = play_sound_windows(str(custom_sound))
                else:
                    success = False
                
                if not success:
                    # Fall back to system sounds
                    play_system_sound(sound_type)
            else:
                # Use system sounds if custom not available
                play_system_sound(sound_type)
        
        # Always allow the operation to continue
        sys.exit(0)
        
    except Exception as e:
        # Log error but don't block operations
        print(f"Sound notification error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()