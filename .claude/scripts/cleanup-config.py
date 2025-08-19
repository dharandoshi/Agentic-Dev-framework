#!/usr/bin/env python3
"""
Configuration Cleanup Script
Safely removes redundant MCP server configurations while preserving functionality
"""

import json
import os
import shutil
from pathlib import Path

def backup_config(config_path: Path) -> Path:
    """Create timestamped backup of configuration"""
    timestamp = os.popen('date +%Y%m%d_%H%M%S').read().strip()
    backup_path = config_path.parent / f"{config_path.name}.backup.{timestamp}"
    shutil.copy2(config_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path

def clean_claude_config():
    """Clean up redundant MCP server configurations in ~/.claude.json"""
    config_path = Path.home() / ".claude.json"
    
    if not config_path.exists():
        print("⚠️  No ~/.claude.json found")
        return
    
    # Create backup
    backup_path = backup_config(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Remove global MCP server configurations that are project-specific
        agent_army_servers = ["workspace", "docs", "execution", "coord", "validation"]
        
        if "mcpServers" in config:
            original_count = len(config["mcpServers"])
            
            # Remove agent army servers from global config
            for server_name in agent_army_servers:
                if server_name in config["mcpServers"]:
                    server_config = config["mcpServers"][server_name]
                    # Only remove if it's pointing to our agent army project
                    if "agent-army-trial" in str(server_config.get("command", "")):
                        del config["mcpServers"][server_name]
                        print(f"🗑️  Removed global config for: {server_name}")
            
            new_count = len(config["mcpServers"])
            print(f"📊 Reduced global MCP servers from {original_count} to {new_count}")
        
        # Clean up project-specific configurations
        if "projects" in config:
            for project_path in config["projects"]:
                project_config = config["projects"][project_path]
                
                if "mcpServers" in project_config:
                    original_count = len(project_config["mcpServers"])
                    
                    # Remove agent army servers from non-agent-army projects
                    if "agent-army-trial" not in project_path:
                        for server_name in agent_army_servers:
                            if server_name in project_config["mcpServers"]:
                                server_config = project_config["mcpServers"][server_name]
                                if "agent-army-trial" in str(server_config.get("command", "")):
                                    del project_config["mcpServers"][server_name]
                                    print(f"🗑️  Removed {server_name} from project: {project_path}")
                    
                    # For the agent-army-trial project, clear mcpServers (will use .claude/mcp.json)
                    elif "agent-army-trial" in project_path:
                        if project_config.get("mcpServers"):
                            project_config["mcpServers"] = {}
                            print(f"🧹 Cleared project-level MCP config for: {project_path}")
                            print("   (Will now use .claude/mcp.json)")
        
        # Write cleaned configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration cleaned successfully!")
        print(f"📁 Backup available at: {backup_path}")
        
    except Exception as e:
        print(f"❌ Error cleaning configuration: {e}")
        print(f"🔄 Restoring from backup: {backup_path}")
        shutil.copy2(backup_path, config_path)

def validate_project_config():
    """Validate that project-level MCP configuration is working"""
    project_mcp_path = Path(".claude/mcp.json")
    
    if not project_mcp_path.exists():
        print("❌ Project MCP configuration not found!")
        return False
    
    try:
        with open(project_mcp_path, 'r') as f:
            config = json.load(f)
        
        expected_servers = ["workspace", "docs", "execution", "coord", "validation"]
        actual_servers = list(config.get("mcpServers", {}).keys())
        
        missing = set(expected_servers) - set(actual_servers)
        if missing:
            print(f"❌ Missing MCP servers in project config: {missing}")
            return False
        
        # Validate server paths exist
        for server_name, server_config in config["mcpServers"].items():
            server_script = Path(server_config["args"][0])
            if not server_script.exists():
                print(f"❌ MCP server script not found: {server_script}")
                return False
        
        print("✅ Project MCP configuration is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating project configuration: {e}")
        return False

def main():
    """Main cleanup process"""
    print("🧹 Agent Army Configuration Cleanup")
    print("=" * 40)
    
    # Change to project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent.parent
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Validate project configuration exists
    if not validate_project_config():
        print("❌ Project configuration validation failed!")
        return
    
    # Clean up Claude configuration
    clean_claude_config()
    
    print("\n🎉 Configuration cleanup completed!")
    print("\n📋 Next steps:")
    print("1. Restart Claude Code")
    print("2. Run: claude mcp list")
    print("3. Verify all 5 MCP servers are loaded")
    print("4. Test agent functionality")

if __name__ == "__main__":
    main()