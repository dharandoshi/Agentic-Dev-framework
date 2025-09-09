#!/bin/bash
#
# Setup Script for Agent Army Sound Notifications
# Installs audio dependencies and configures sound system
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CLAUDE_DIR="$PROJECT_ROOT/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SOUNDS_DIR="$HOOKS_DIR/sounds"

echo -e "${CYAN}🔊 Agent Army Sound Notification Setup${NC}"
echo -e "${CYAN}======================================${NC}"
echo ""

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install audio players on Linux
install_linux_audio() {
    echo -e "${BLUE}📦 Installing audio players for Linux...${NC}"
    
    # Check if we can use sudo
    if command_exists sudo; then
        echo "Select audio player to install:"
        echo "1) mpg123 (lightweight, best for MP3)"
        echo "2) ffmpeg (full-featured, supports all formats)"
        echo "3) sox (command-line audio swiss-army knife)"
        echo "4) pygame (Python-based, no system install needed)"
        echo "5) Skip installation"
        
        read -p "Enter choice (1-5): " choice
        
        case $choice in
            1)
                echo "Installing mpg123..."
                sudo apt-get update && sudo apt-get install -y mpg123
                echo -e "${GREEN}✅ mpg123 installed${NC}"
                ;;
            2)
                echo "Installing ffmpeg..."
                sudo apt-get update && sudo apt-get install -y ffmpeg
                echo -e "${GREEN}✅ ffmpeg installed${NC}"
                ;;
            3)
                echo "Installing sox..."
                sudo apt-get update && sudo apt-get install -y sox libsox-fmt-mp3
                echo -e "${GREEN}✅ sox installed${NC}"
                ;;
            4)
                echo "Installing pygame via pip..."
                if command_exists pip3; then
                    pip3 install --user pygame
                    echo -e "${GREEN}✅ pygame installed${NC}"
                elif command_exists pip; then
                    pip install --user pygame
                    echo -e "${GREEN}✅ pygame installed${NC}"
                else
                    echo -e "${YELLOW}⚠️  pip not found. Install Python pip first${NC}"
                fi
                ;;
            5)
                echo -e "${YELLOW}⚠️  Skipping audio player installation${NC}"
                ;;
            *)
                echo -e "${YELLOW}⚠️  Invalid choice, skipping${NC}"
                ;;
        esac
    else
        echo -e "${YELLOW}⚠️  sudo not available. Please manually install one of:${NC}"
        echo "  - mpg123: apt-get install mpg123"
        echo "  - ffmpeg: apt-get install ffmpeg"
        echo "  - pygame: pip install pygame"
    fi
}

# Function to verify audio setup
verify_audio() {
    echo ""
    echo -e "${BLUE}🔍 Checking audio system...${NC}"
    
    local has_player=false
    
    # Check for various audio players
    if command_exists mpg123; then
        echo -e "${GREEN}  ✓ mpg123 found${NC}"
        has_player=true
    fi
    
    if command_exists ffplay; then
        echo -e "${GREEN}  ✓ ffplay (ffmpeg) found${NC}"
        has_player=true
    fi
    
    if command_exists play; then
        echo -e "${GREEN}  ✓ play (sox) found${NC}"
        has_player=true
    fi
    
    if command_exists paplay; then
        echo -e "${GREEN}  ✓ PulseAudio found${NC}"
        has_player=true
    fi
    
    if command_exists afplay; then
        echo -e "${GREEN}  ✓ afplay (macOS) found${NC}"
        has_player=true
    fi
    
    # Check for Python audio libraries
    if python3 -c "import pygame" 2>/dev/null; then
        echo -e "${GREEN}  ✓ pygame (Python) found${NC}"
        has_player=true
    fi
    
    if ! $has_player; then
        echo -e "${RED}  ✗ No audio players found${NC}"
        return 1
    fi
    
    return 0
}

# Function to check sound files
check_sound_files() {
    echo ""
    echo -e "${BLUE}📂 Checking sound files...${NC}"
    
    local sounds=(
        "agent-start"
        "agent-complete"
        "agent-error"
        "permission-required"
        "session-end"
        "task-start"
        "tool-blocked"
        "notification"
    )
    
    local missing=0
    for sound in "${sounds[@]}"; do
        if ls "$SOUNDS_DIR"/${sound}.* 2>/dev/null | grep -qE "\.(mp3|wav|ogg|aiff)$"; then
            echo -e "${GREEN}  ✓ ${sound} found${NC}"
        else
            echo -e "${YELLOW}  ⚠ ${sound} missing${NC}"
            ((missing++))
        fi
    done
    
    if [[ $missing -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}Missing $missing sound file(s).${NC}"
        echo "Add them to: $SOUNDS_DIR/"
        echo "Supported formats: MP3, WAV, OGG, AIFF"
        return 1
    fi
    
    return 0
}

# Function to verify hooks configuration
check_hooks_config() {
    echo ""
    echo -e "${BLUE}⚙️  Checking hooks configuration...${NC}"
    
    if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
        if grep -q "hooks" "$CLAUDE_DIR/settings.json"; then
            echo -e "${GREEN}  ✓ Hooks configured in settings.json${NC}"
            
            # Check specific hooks
            if grep -q "SessionStart" "$CLAUDE_DIR/settings.json"; then
                echo -e "${GREEN}    ✓ SessionStart hook${NC}"
            fi
            if grep -q "SessionEnd" "$CLAUDE_DIR/settings.json"; then
                echo -e "${GREEN}    ✓ SessionEnd hook${NC}"
            fi
            if grep -q "Notification" "$CLAUDE_DIR/settings.json"; then
                echo -e "${GREEN}    ✓ Notification hook${NC}"
            fi
            return 0
        else
            echo -e "${RED}  ✗ No hooks found in settings.json${NC}"
            return 1
        fi
    else
        echo -e "${RED}  ✗ settings.json not found${NC}"
        return 1
    fi
}

# Function to test sound playback
test_sounds() {
    echo ""
    echo -e "${BLUE}🎵 Testing sound playback...${NC}"
    
    read -p "Would you like to test sound playback? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ -x "$HOOKS_DIR/test-sounds.sh" ]]; then
            "$HOOKS_DIR/test-sounds.sh"
        else
            echo -e "${YELLOW}Test script not found or not executable${NC}"
        fi
    fi
}

# Main setup flow
main() {
    local os_type=$(detect_os)
    
    echo "Detected OS: $os_type"
    echo ""
    
    # Step 1: Check/Install audio players
    if [[ "$os_type" == "linux" ]]; then
        if ! verify_audio; then
            install_linux_audio
            verify_audio
        fi
    elif [[ "$os_type" == "macos" ]]; then
        echo -e "${GREEN}✅ macOS has built-in audio support (afplay)${NC}"
    elif [[ "$os_type" == "windows" ]]; then
        echo -e "${GREEN}✅ Windows has built-in audio support (PowerShell)${NC}"
    else
        echo -e "${YELLOW}⚠️  Unknown OS. Manual audio setup may be required${NC}"
    fi
    
    # Step 2: Check sound files
    check_sound_files
    
    # Step 3: Check hooks configuration
    if ! check_hooks_config; then
        echo ""
        echo -e "${YELLOW}Run the following to configure hooks:${NC}"
        echo "  claude settings hooks"
    fi
    
    # Step 4: Make scripts executable
    echo ""
    echo -e "${BLUE}🔧 Setting permissions...${NC}"
    if [[ -f "$HOOKS_DIR/sound-notifications.py" ]]; then
        chmod +x "$HOOKS_DIR/sound-notifications.py"
        echo -e "${GREEN}  ✓ sound-notifications.py executable${NC}"
    fi
    if [[ -f "$HOOKS_DIR/test-sounds.sh" ]]; then
        chmod +x "$HOOKS_DIR/test-sounds.sh"
        echo -e "${GREEN}  ✓ test-sounds.sh executable${NC}"
    fi
    
    # Step 5: Test sounds
    test_sounds
    
    # Summary
    echo ""
    echo -e "${PURPLE}📊 Setup Summary${NC}"
    echo "===================="
    
    if verify_audio >/dev/null 2>&1; then
        echo -e "Audio System:     ${GREEN}✅ Ready${NC}"
    else
        echo -e "Audio System:     ${RED}❌ Needs setup${NC}"
    fi
    
    if check_sound_files >/dev/null 2>&1; then
        echo -e "Sound Files:      ${GREEN}✅ All present${NC}"
    else
        echo -e "Sound Files:      ${YELLOW}⚠️  Some missing${NC}"
    fi
    
    if check_hooks_config >/dev/null 2>&1; then
        echo -e "Hooks Config:     ${GREEN}✅ Configured${NC}"
    else
        echo -e "Hooks Config:     ${YELLOW}⚠️  Needs configuration${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}🎉 Sound notification setup complete!${NC}"
    echo ""
    echo "The sound system will activate on the next Claude Code session."
    echo ""
    echo "Commands:"
    echo "  Test sounds:  $HOOKS_DIR/test-sounds.sh"
    echo "  View config:  cat $CLAUDE_DIR/settings.json"
    echo ""
}

# Run main function
main