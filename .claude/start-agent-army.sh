#!/bin/bash
#
# Agent Army Startup Script
# Launches all components in the correct order with health checks
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

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$PROJECT_ROOT/.claude"
SCRIPTS_DIR="$CLAUDE_DIR/scripts"
LOGS_DIR="$CLAUDE_DIR/logs"

echo -e "${CYAN}🚀 Agent Army Startup Sequence${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local service_name=$1
    local check_command=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "Waiting for $service_name to be ready"
    while [ $attempt -lt $max_attempts ]; do
        if eval "$check_command" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e " ${RED}✗${NC}"
    return 1
}

# Step 1: Environment Validation
echo -e "${BLUE}📋 Step 1: Validating Environment${NC}"
echo "----------------------------------------"

if python3 "$SCRIPTS_DIR/validate-environment.py" > "$LOGS_DIR/startup-validation.log" 2>&1; then
    echo -e "${GREEN}✅ Environment validation passed${NC}"
else
    echo -e "${RED}❌ Environment validation failed${NC}"
    echo "Check logs at: $LOGS_DIR/startup-validation.log"
    exit 1
fi

# Step 2: MCP Server Registration
echo ""
echo -e "${BLUE}🔧 Step 2: Initializing MCP Servers${NC}"
echo "----------------------------------------"

# Check if MCP servers are already registered
mcp_status=$(claude mcp list 2>/dev/null | grep -c "workspace\|docs\|execution\|coord\|validation" || echo "0")

if [ "$mcp_status" -ge 5 ]; then
    echo -e "${GREEN}✅ MCP servers already registered${NC}"
else
    echo "Registering MCP servers..."
    if "$SCRIPTS_DIR/register-mcp-servers.sh" > "$LOGS_DIR/mcp-registration.log" 2>&1; then
        echo -e "${GREEN}✅ MCP servers registered successfully${NC}"
    else
        echo -e "${RED}❌ MCP server registration failed${NC}"
        echo "Check logs at: $LOGS_DIR/mcp-registration.log"
        exit 1
    fi
fi

# Verify MCP servers are connected
if wait_for_service "MCP servers" "claude mcp list | grep -q Connected"; then
    echo -e "${GREEN}✅ MCP servers connected${NC}"
else
    echo -e "${YELLOW}⚠️  Some MCP servers may not be fully connected${NC}"
fi

# Step 3: Start Monitoring System
echo ""
echo -e "${BLUE}📊 Step 3: Starting Monitoring System${NC}"
echo "----------------------------------------"

if is_running "monitoring-system.py"; then
    echo -e "${YELLOW}ℹ️  Monitoring system already running${NC}"
else
    echo "Starting monitoring daemon..."
    nohup python3 "$SCRIPTS_DIR/monitoring-system.py" --start --daemon \
        > "$LOGS_DIR/monitoring.log" 2>&1 &
    MONITOR_PID=$!
    
    sleep 2
    
    if kill -0 $MONITOR_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Monitoring system started (PID: $MONITOR_PID)${NC}"
        echo $MONITOR_PID > "$LOGS_DIR/monitoring.pid"
    else
        echo -e "${RED}❌ Failed to start monitoring system${NC}"
        exit 1
    fi
fi

# Step 4: Verify Hook System
echo ""
echo -e "${BLUE}🪝 Step 4: Verifying Hook System${NC}"
echo "----------------------------------------"

# Check hook configuration
if [ -f "$CLAUDE_DIR/settings.json" ] && grep -q "hooks" "$CLAUDE_DIR/settings.json"; then
    echo -e "${GREEN}✅ Hook system configured${NC}"
    
    # Test hook scripts
    hook_errors=0
    for hook in orchestrator.py communication-tracker.py smart-suggestions.py; do
        if [ -f "$CLAUDE_DIR/hooks/$hook" ]; then
            if [ -x "$CLAUDE_DIR/hooks/$hook" ]; then
                echo -e "  ${GREEN}✓${NC} $hook is executable"
            else
                echo -e "  ${YELLOW}⚠${NC} $hook is not executable, fixing..."
                chmod +x "$CLAUDE_DIR/hooks/$hook"
            fi
        else
            echo -e "  ${RED}✗${NC} $hook not found"
            hook_errors=$((hook_errors + 1))
        fi
    done
    
    if [ $hook_errors -eq 0 ]; then
        echo -e "${GREEN}✅ All hooks verified${NC}"
    else
        echo -e "${YELLOW}⚠️  Some hooks are missing${NC}"
    fi
else
    echo -e "${RED}❌ Hook system not configured${NC}"
    echo "Please check .claude/settings.json"
fi

# Step 5: Start Master Orchestrator
echo ""
echo -e "${BLUE}🎯 Step 5: Starting Master Orchestrator${NC}"
echo "----------------------------------------"

if is_running "agent-army-orchestrator.py"; then
    echo -e "${YELLOW}ℹ️  Orchestrator already running${NC}"
else
    echo "Starting orchestrator..."
    nohup python3 "$SCRIPTS_DIR/agent-army-orchestrator.py" --start --daemon \
        > "$LOGS_DIR/orchestrator.log" 2>&1 &
    ORCHESTRATOR_PID=$!
    
    sleep 3
    
    if kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Orchestrator started (PID: $ORCHESTRATOR_PID)${NC}"
        echo $ORCHESTRATOR_PID > "$LOGS_DIR/orchestrator.pid"
    else
        echo -e "${YELLOW}⚠️  Orchestrator may not have started properly${NC}"
    fi
fi

# Step 6: Run Integration Tests
echo ""
echo -e "${BLUE}🧪 Step 6: Running System Tests${NC}"
echo "----------------------------------------"

echo "Running quick system tests..."
if "$SCRIPTS_DIR/run-tests.sh" environment > "$LOGS_DIR/startup-tests.log" 2>&1; then
    echo -e "${GREEN}✅ Environment tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some tests failed, check logs${NC}"
fi

if "$SCRIPTS_DIR/run-tests.sh" mcp >> "$LOGS_DIR/startup-tests.log" 2>&1; then
    echo -e "${GREEN}✅ MCP tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  MCP tests had issues${NC}"
fi

# Step 7: Display System Status
echo ""
echo -e "${PURPLE}📊 System Status${NC}"
echo "----------------------------------------"

# Get orchestrator status
if [ -f "$LOGS_DIR/orchestrator.pid" ]; then
    ORCHESTRATOR_PID=$(cat "$LOGS_DIR/orchestrator.pid")
    if kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
        echo -e "Orchestrator:    ${GREEN}● Running${NC} (PID: $ORCHESTRATOR_PID)"
    else
        echo -e "Orchestrator:    ${RED}○ Stopped${NC}"
    fi
else
    echo -e "Orchestrator:    ${YELLOW}? Unknown${NC}"
fi

# Get monitoring status
if [ -f "$LOGS_DIR/monitoring.pid" ]; then
    MONITOR_PID=$(cat "$LOGS_DIR/monitoring.pid")
    if kill -0 $MONITOR_PID 2>/dev/null; then
        echo -e "Monitoring:      ${GREEN}● Running${NC} (PID: $MONITOR_PID)"
    else
        echo -e "Monitoring:      ${RED}○ Stopped${NC}"
    fi
else
    echo -e "Monitoring:      ${YELLOW}? Unknown${NC}"
fi

# MCP server status
mcp_count=$(claude mcp list 2>/dev/null | grep -c "workspace\|docs\|execution\|coord\|validation" || echo "0")
echo -e "MCP Servers:     ${GREEN}$mcp_count/5 registered${NC}"

# Agent status
agent_count=$(find "$CLAUDE_DIR/agents" -name "*.md" -type f 2>/dev/null | wc -l)
echo -e "Agents:          ${GREEN}$agent_count agents available${NC}"

# Hook status
if [ -f "$CLAUDE_DIR/settings.json" ] && grep -q "hooks" "$CLAUDE_DIR/settings.json"; then
    echo -e "Hooks:           ${GREEN}● Configured${NC}"
else
    echo -e "Hooks:           ${YELLOW}○ Not configured${NC}"
fi

echo ""
echo -e "${CYAN}🎉 Agent Army Startup Complete!${NC}"
echo ""
echo "Available Commands:"
echo "  • View Dashboard:     python3 $SCRIPTS_DIR/monitoring-dashboard.py"
echo "  • Check Status:       python3 $SCRIPTS_DIR/monitoring-system.py --status"
echo "  • Run Tests:          $SCRIPTS_DIR/run-tests.sh all"
echo "  • View Logs:          tail -f $LOGS_DIR/*.log"
echo "  • Stop Services:      $PROJECT_ROOT/stop-agent-army.sh"
echo ""
echo "Documentation:"
echo "  • Integration Guide:  $CLAUDE_DIR/docs/integration-guide.md"
echo "  • Backup Guide:       $CLAUDE_DIR/docs/backup-recovery.md"
echo ""

# Optional: Start dashboard in background
read -p "Would you like to open the monitoring dashboard? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting dashboard (press 'q' to exit)..."
    python3 "$SCRIPTS_DIR/monitoring-dashboard.py"
fi