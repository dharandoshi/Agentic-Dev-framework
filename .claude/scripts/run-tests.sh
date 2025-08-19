#!/bin/bash
"""
Agent Army Test Runner
Convenient script for running different types of tests
"""

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/.claude/scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🧪 Agent Army Test Runner${NC}"
echo -e "${CYAN}========================${NC}"
echo ""

show_help() {
    echo "Usage: $0 [TEST_TYPE]"
    echo ""
    echo "Available test types:"
    echo "  environment    - Validate environment setup and dependencies"
    echo "  integration    - Run complete integration test suite"
    echo "  mcp           - Test MCP server functionality"
    echo "  agents        - Validate agent definitions and configurations" 
    echo "  workflow      - Test agent workflows and handoffs"
    echo "  all           - Run all test types (default)"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 environment    # Quick environment check"
    echo "  $0 integration    # Full integration tests"
    echo "  $0 all           # Complete test suite"
    echo ""
}

run_environment_tests() {
    echo -e "${BLUE}🔍 Running Environment Validation Tests...${NC}"
    echo "================================================"
    
    if [ -f "$SCRIPTS_DIR/validate-environment.py" ]; then
        python3 "$SCRIPTS_DIR/validate-environment.py"
        env_result=$?
        
        if [ $env_result -eq 0 ]; then
            echo -e "${GREEN}✅ Environment tests passed${NC}"
            return 0
        else
            echo -e "${RED}❌ Environment tests failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Environment validation script not found${NC}"
        return 1
    fi
}

run_mcp_tests() {
    echo -e "${BLUE}🔧 Running MCP Server Tests...${NC}"
    echo "=============================="
    
    # Check if Claude CLI is available
    if ! command -v claude &> /dev/null; then
        echo -e "${RED}❌ Claude Code CLI not found${NC}"
        return 1
    fi
    
    # Test MCP server status
    echo "📡 Checking MCP server status..."
    claude mcp list > /tmp/mcp_status.txt 2>&1
    mcp_result=$?
    
    if [ $mcp_result -eq 0 ]; then
        echo -e "${GREEN}✅ MCP servers accessible${NC}"
        
        # Count registered servers
        server_count=$(grep -E "(workspace|docs|execution|coord|validation)" /tmp/mcp_status.txt | wc -l)
        echo "📊 Registered servers: $server_count/5"
        
        if [ $server_count -ge 4 ]; then
            echo -e "${GREEN}✅ MCP tests passed${NC}"
            rm -f /tmp/mcp_status.txt
            return 0
        else
            echo -e "${YELLOW}⚠️  Some MCP servers missing${NC}"
            rm -f /tmp/mcp_status.txt
            return 1
        fi
    else
        echo -e "${RED}❌ MCP server tests failed${NC}"
        cat /tmp/mcp_status.txt
        rm -f /tmp/mcp_status.txt
        return 1
    fi
}

run_agent_tests() {
    echo -e "${BLUE}🤖 Running Agent Definition Tests...${NC}"
    echo "=================================="
    
    agents_dir="$PROJECT_ROOT/.claude/agents"
    if [ ! -d "$agents_dir" ]; then
        echo -e "${RED}❌ Agents directory not found${NC}"
        return 1
    fi
    
    # Check for agent registry
    if [ -f "$agents_dir/agent-registry.json" ]; then
        echo -e "${GREEN}✅ Agent registry found${NC}"
        
        # Validate JSON syntax
        if python3 -m json.tool "$agents_dir/agent-registry.json" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Agent registry JSON valid${NC}"
        else
            echo -e "${RED}❌ Agent registry JSON invalid${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Agent registry not found${NC}"
        return 1
    fi
    
    # Count agent definition files
    agent_count=$(find "$agents_dir" -name "*.md" -type f | wc -l)
    echo "📊 Agent definitions found: $agent_count"
    
    # Check for key agents
    key_agents=("scrum-master.md" "tech-lead.md" "senior-backend-engineer.md" "senior-frontend-engineer.md")
    missing_agents=()
    
    for agent in "${key_agents[@]}"; do
        if [ ! -f "$agents_dir/$agent" ]; then
            missing_agents+=("$agent")
        fi
    done
    
    if [ ${#missing_agents[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All key agents found${NC}"
        echo -e "${GREEN}✅ Agent tests passed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Missing agents: ${missing_agents[*]}${NC}"
        return 1
    fi
}

run_workflow_tests() {
    echo -e "${BLUE}🔄 Running Workflow Tests...${NC}"
    echo "==========================="
    
    # Check hook system
    hooks_dir="$PROJECT_ROOT/.claude/hooks"
    if [ ! -d "$hooks_dir" ]; then
        echo -e "${RED}❌ Hooks directory not found${NC}"
        return 1
    fi
    
    # Check for orchestrator
    if [ -f "$hooks_dir/orchestrator.py" ]; then
        echo -e "${GREEN}✅ Orchestrator hook found${NC}"
    else
        echo -e "${RED}❌ Orchestrator hook missing${NC}"
        return 1
    fi
    
    # Check for communication tracker
    if [ -f "$hooks_dir/communication-tracker.py" ]; then
        echo -e "${GREEN}✅ Communication tracker found${NC}"
    else
        echo -e "${RED}❌ Communication tracker missing${NC}"
        return 1
    fi
    
    # Check hook configuration
    settings_files=("$PROJECT_ROOT/.claude/settings.json" "$PROJECT_ROOT/.claude/settings.local.json")
    hook_config_found=false
    
    for settings_file in "${settings_files[@]}"; do
        if [ -f "$settings_file" ] && grep -q "hooks" "$settings_file"; then
            echo -e "${GREEN}✅ Hook configuration found in $(basename "$settings_file")${NC}"
            hook_config_found=true
            break
        fi
    done
    
    if [ "$hook_config_found" = false ]; then
        echo -e "${RED}❌ Hook configuration not found${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Workflow tests passed${NC}"
    return 0
}

run_integration_tests() {
    echo -e "${BLUE}🧪 Running Integration Test Suite...${NC}"
    echo "=================================="
    
    if [ -f "$SCRIPTS_DIR/integration-tests.py" ]; then
        python3 "$SCRIPTS_DIR/integration-tests.py"
        integration_result=$?
        
        if [ $integration_result -eq 0 ]; then
            echo -e "${GREEN}✅ Integration tests passed${NC}"
            return 0
        elif [ $integration_result -eq 1 ]; then
            echo -e "${YELLOW}⚠️  Integration tests passed with warnings${NC}"
            return 1
        else
            echo -e "${RED}❌ Integration tests failed${NC}"
            return 2
        fi
    else
        echo -e "${RED}❌ Integration test script not found${NC}"
        return 1
    fi
}

run_all_tests() {
    echo -e "${PURPLE}🚀 Running Complete Test Suite...${NC}"
    echo "================================"
    
    total_tests=0
    passed_tests=0
    
    # Environment tests
    echo ""
    run_environment_tests
    env_result=$?
    total_tests=$((total_tests + 1))
    [ $env_result -eq 0 ] && passed_tests=$((passed_tests + 1))
    
    # MCP tests
    echo ""
    run_mcp_tests  
    mcp_result=$?
    total_tests=$((total_tests + 1))
    [ $mcp_result -eq 0 ] && passed_tests=$((passed_tests + 1))
    
    # Agent tests
    echo ""
    run_agent_tests
    agent_result=$?
    total_tests=$((total_tests + 1))
    [ $agent_result -eq 0 ] && passed_tests=$((passed_tests + 1))
    
    # Workflow tests
    echo ""
    run_workflow_tests
    workflow_result=$?
    total_tests=$((total_tests + 1))
    [ $workflow_result -eq 0 ] && passed_tests=$((passed_tests + 1))
    
    # Integration tests
    echo ""
    run_integration_tests
    integration_result=$?
    total_tests=$((total_tests + 1))
    [ $integration_result -eq 0 ] && passed_tests=$((passed_tests + 1))
    
    # Final summary
    echo ""
    echo -e "${CYAN}📊 Complete Test Suite Summary${NC}"
    echo "=============================="
    echo "Total test categories: $total_tests"
    echo "Passed categories: $passed_tests"
    
    success_rate=$((passed_tests * 100 / total_tests))
    echo "Success rate: $success_rate%"
    
    if [ $success_rate -eq 100 ]; then
        echo -e "${GREEN}🎉 All tests passed! Agent Army is ready for production.${NC}"
        return 0
    elif [ $success_rate -ge 80 ]; then
        echo -e "${YELLOW}⚠️  Most tests passed. Review warnings before production use.${NC}"
        return 1
    else
        echo -e "${RED}❌ Multiple test failures. Address issues before proceeding.${NC}"
        return 2
    fi
}

# Main execution
case "${1:-all}" in
    "environment")
        run_environment_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "mcp")
        run_mcp_tests
        ;;
    "agents")
        run_agent_tests
        ;;
    "workflow")
        run_workflow_tests
        ;;
    "all")
        run_all_tests
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown test type: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

exit $?