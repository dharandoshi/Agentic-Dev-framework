#!/bin/bash
"""
Agent Army Shutdown Script
Gracefully stops all Agent Army components
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$PROJECT_ROOT/.claude"
LOGS_DIR="$CLAUDE_DIR/logs"

echo -e "${CYAN}⏹️  Agent Army Shutdown Sequence${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if kill -0 $PID 2>/dev/null; then
            echo -n "Stopping $service_name (PID: $PID)..."
            kill $PID 2>/dev/null || true
            
            # Wait for process to stop
            local count=0
            while kill -0 $PID 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if kill -0 $PID 2>/dev/null; then
                echo -e " ${YELLOW}Force killing${NC}"
                kill -9 $PID 2>/dev/null || true
            else
                echo -e " ${GREEN}✓${NC}"
            fi
            
            rm -f "$pid_file"
        else
            echo -e "$service_name: ${YELLOW}Not running${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "$service_name: ${YELLOW}No PID file found${NC}"
    fi
}

# Stop Orchestrator
echo -e "${CYAN}Stopping Orchestrator...${NC}"
stop_service "Orchestrator" "$LOGS_DIR/orchestrator.pid"

# Also try to stop by process name
pkill -f "agent-army-orchestrator.py" 2>/dev/null || true

# Stop Monitoring System
echo -e "${CYAN}Stopping Monitoring System...${NC}"
stop_service "Monitoring" "$LOGS_DIR/monitoring.pid"

# Also try to stop by process name
pkill -f "monitoring-system.py" 2>/dev/null || true

# Stop any dashboard instances
echo -e "${CYAN}Stopping Dashboard instances...${NC}"
pkill -f "monitoring-dashboard.py" 2>/dev/null || {
    echo -e "Dashboard: ${YELLOW}Not running${NC}"
}

# Optional: Clean up background processes
echo ""
echo -e "${CYAN}Cleaning up background processes...${NC}"

# Kill any remaining Python processes from our scripts
for script in "integration-tests.py" "validate-environment.py" "backup-system.py"; do
    if pgrep -f "$script" > /dev/null; then
        echo "Stopping $script..."
        pkill -f "$script" 2>/dev/null || true
    fi
done

# Create shutdown timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$LOGS_DIR/last_shutdown.txt"

echo ""
echo -e "${GREEN}✅ Agent Army shutdown complete${NC}"
echo ""
echo "To restart the system, run:"
echo "  $PROJECT_ROOT/start-agent-army.sh"
echo ""