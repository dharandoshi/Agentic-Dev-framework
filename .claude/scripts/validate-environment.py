#!/usr/bin/env python3
"""
Environment Validation Script for Agent Army
Validates that all required components are properly set up and functional
"""

import os
import sys
import json
import subprocess
import pathlib
from typing import List, Dict, Tuple, Optional

class AgentArmyValidator:
    """Comprehensive environment validation for Agent Army setup"""
    
    def __init__(self):
        self.project_root = pathlib.Path.cwd()
        self.claude_dir = self.project_root / ".claude"
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
        
    def log_success(self, message: str):
        """Log a successful check"""
        print(f"✅ {message}")
        self.success_count += 1
        self.total_checks += 1
        
    def log_error(self, message: str):
        """Log an error"""
        print(f"❌ {message}")
        self.errors.append(message)
        self.total_checks += 1
        
    def log_warning(self, message: str):
        """Log a warning"""
        print(f"⚠️  {message}")
        self.warnings.append(message)
        
    def log_info(self, message: str):
        """Log informational message"""
        print(f"ℹ️  {message}")
        
    def check_python_environment(self) -> bool:
        """Validate Python environment and dependencies"""
        self.log_info("Checking Python Environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.log_error(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
            return False
        else:
            self.log_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        # Check virtual environment
        venv_path = self.claude_dir / "mcp" / "venv"
        if not venv_path.exists():
            self.log_error("MCP virtual environment not found at .claude/mcp/venv/")
            return False
        else:
            self.log_success("MCP virtual environment found")
            
        # Check MCP installation
        try:
            result = subprocess.run([
                str(venv_path / "bin" / "python"), 
                "-c", "import mcp; print('MCP installed successfully')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_success("MCP Python package installed")
            else:
                self.log_error(f"MCP package not installed or broken: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_error(f"Failed to check MCP installation: {e}")
            return False
            
        return True
        
    def check_mcp_servers(self) -> bool:
        """Validate MCP server files and configuration"""
        self.log_info("Checking MCP Servers...")
        
        required_servers = [
            "workspace.py", "docs.py", "execution.py", 
            "coord.py", "validation.py"
        ]
        
        servers_dir = self.claude_dir / "mcp" / "servers" / "core"
        if not servers_dir.exists():
            self.log_error("MCP servers directory not found")
            return False
            
        all_servers_exist = True
        for server in required_servers:
            server_path = servers_dir / server
            if server_path.exists():
                self.log_success(f"MCP server found: {server}")
            else:
                self.log_error(f"MCP server missing: {server}")
                all_servers_exist = False
                
        return all_servers_exist
        
    def check_claude_code_integration(self) -> bool:
        """Check Claude Code MCP integration"""
        self.log_info("Checking Claude Code Integration...")
        
        try:
            # Check if claude command is available
            result = subprocess.run(["claude", "--version"], 
                                 capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_success("Claude Code CLI available")
            else:
                self.log_error("Claude Code CLI not found or not working")
                return False
                
        except FileNotFoundError:
            self.log_error("Claude Code CLI not installed")
            return False
        except Exception as e:
            self.log_error(f"Error checking Claude Code CLI: {e}")
            return False
            
        # Check MCP server registration
        try:
            result = subprocess.run(["claude", "mcp", "list"], 
                                 capture_output=True, text=True, timeout=15)
            
            if "workspace" in result.stdout and "docs" in result.stdout:
                self.log_success("MCP servers registered with Claude Code")
            else:
                self.log_error("MCP servers not properly registered")
                self.log_info("Run setup script to register MCP servers")
                return False
                
        except Exception as e:
            self.log_error(f"Error checking MCP registration: {e}")
            return False
            
        return True
        
    def check_hook_system(self) -> bool:
        """Validate hook system configuration and scripts"""
        self.log_info("Checking Hook System...")
        
        # Check hook scripts
        hooks_dir = self.claude_dir / "hooks"
        required_hooks = [
            "orchestrator.py", 
            "communication-tracker.py", 
            "smart-suggestions.py"
        ]
        
        if not hooks_dir.exists():
            self.log_error("Hooks directory not found")
            return False
            
        all_hooks_exist = True
        for hook in required_hooks:
            hook_path = hooks_dir / hook
            if hook_path.exists():
                self.log_success(f"Hook script found: {hook}")
                
                # Check if executable
                if os.access(hook_path, os.X_OK):
                    self.log_success(f"Hook script executable: {hook}")
                else:
                    self.log_warning(f"Hook script not executable: {hook}")
            else:
                self.log_error(f"Hook script missing: {hook}")
                all_hooks_exist = False
                
        # Check hook configuration
        settings_files = [
            self.claude_dir / "settings.json",
            self.claude_dir / "settings.local.json"
        ]
        
        hook_config_found = False
        for settings_file in settings_files:
            if settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        config = json.load(f)
                        
                    if "hooks" in config:
                        hook_config_found = True
                        self.log_success(f"Hook configuration found in {settings_file.name}")
                        break
                        
                except Exception as e:
                    self.log_error(f"Error reading {settings_file.name}: {e}")
                    
        if not hook_config_found:
            self.log_error("No hook configuration found in settings files")
            return False
            
        return all_hooks_exist
        
    def check_agent_definitions(self) -> bool:
        """Validate agent definition files"""
        self.log_info("Checking Agent Definitions...")
        
        agents_dir = self.claude_dir / "agents"
        if not agents_dir.exists():
            self.log_error("Agents directory not found")
            return False
            
        # Check agent registry
        registry_file = agents_dir / "agent-registry.json"
        if registry_file.exists():
            self.log_success("Agent registry found")
            
            try:
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                    
                total_agents = registry.get("total_agents", 0)
                self.log_success(f"Agent registry contains {total_agents} agents")
                
            except Exception as e:
                self.log_error(f"Error reading agent registry: {e}")
                return False
        else:
            self.log_error("Agent registry file not found")
            return False
            
        # Check some key agent definitions
        key_agents = [
            "scrum-master.md", "tech-lead.md", 
            "senior-backend-engineer.md", "senior-frontend-engineer.md"
        ]
        
        agents_found = 0
        for agent in key_agents:
            agent_path = agents_dir / agent
            if agent_path.exists():
                agents_found += 1
                self.log_success(f"Agent definition found: {agent}")
            else:
                self.log_warning(f"Agent definition missing: {agent}")
                
        if agents_found >= len(key_agents) // 2:
            return True
        else:
            self.log_error("Too many agent definitions missing")
            return False
            
    def check_project_structure(self) -> bool:
        """Validate overall project structure"""
        self.log_info("Checking Project Structure...")
        
        required_paths = [
            ".claude",
            ".claude/agents", 
            ".claude/hooks",
            ".claude/mcp",
            ".claude/mcp/servers",
            ".claude/mcp/servers/core",
            ".claude/scripts"
        ]
        
        all_paths_exist = True
        for path in required_paths:
            full_path = self.project_root / path
            if full_path.exists():
                self.log_success(f"Directory exists: {path}")
            else:
                self.log_error(f"Directory missing: {path}")
                all_paths_exist = False
                
        # Check README
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            self.log_success("README.md found")
        else:
            self.log_warning("README.md not found")
            
        return all_paths_exist
        
    def check_git_repository(self) -> bool:
        """Check Git repository status"""
        self.log_info("Checking Git Repository...")
        
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            self.log_success("Git repository initialized")
            
            # Check for uncommitted changes
            try:
                result = subprocess.run(["git", "status", "--porcelain"], 
                                     capture_output=True, text=True, timeout=10)
                
                if result.stdout.strip():
                    self.log_warning("Uncommitted changes in repository")
                else:
                    self.log_success("Repository is clean")
                    
            except Exception as e:
                self.log_warning(f"Error checking git status: {e}")
                
        else:
            self.log_warning("Not a git repository")
            
        return True
        
    def run_comprehensive_validation(self) -> bool:
        """Run all validation checks"""
        print("🔍 Agent Army Environment Validation")
        print("=" * 50)
        
        checks = [
            ("Python Environment", self.check_python_environment),
            ("MCP Servers", self.check_mcp_servers),
            ("Claude Code Integration", self.check_claude_code_integration),
            ("Hook System", self.check_hook_system),
            ("Agent Definitions", self.check_agent_definitions),
            ("Project Structure", self.check_project_structure),
            ("Git Repository", self.check_git_repository)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"\n📋 {check_name}")
            print("-" * 30)
            
            try:
                result = check_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_error(f"Validation check failed: {e}")
                all_passed = False
                
        # Summary
        print(f"\n📊 Validation Summary")
        print("=" * 50)
        print(f"✅ Successful checks: {self.success_count}/{self.total_checks}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n🚨 Critical Issues:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if all_passed and len(self.errors) == 0:
            print(f"\n🎉 Agent Army environment is properly configured!")
            return True
        else:
            print(f"\n🔧 Please fix the issues above before using Agent Army")
            return False

def main():
    """Main validation entry point"""
    validator = AgentArmyValidator()
    success = validator.run_comprehensive_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()