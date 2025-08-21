#!/usr/bin/env python3
"""
Complete Agent Army Data Reset Utility
Clears all persistent data across the entire system
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse

class CompleteSystemReset:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_root = self.base_path / "backups" / f"system_backup_{self.timestamp}"
        
        # Define all data locations
        self.data_locations = {
            "communication": {
                "path": self.base_path / "mcp" / "data" / "communication",
                "files": ["tasks.json", "messages.json", "agents.json", "workflows.json"],
                "default": {}
            },
            "registry": {
                "path": self.base_path / "mcp" / "data" / "registry",
                "files": ["documents.json", "document-index.json"],
                "default": {}
            },
            "logs": {
                "path": self.base_path / "logs",
                "files": "all",  # Clear all log files
                "default": None
            },
            "agent_registry": {
                "path": self.base_path / "agents",
                "files": ["agent-registry.json"],
                "default": None  # Don't reset, just backup
            }
        }
    
    def create_backup(self, component: str = None) -> Path:
        """Create comprehensive backup of specified component or all"""
        print(f"\n💾 Creating backup at: {self.backup_root}")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        components = [component] if component else self.data_locations.keys()
        
        for comp in components:
            if comp not in self.data_locations:
                continue
                
            config = self.data_locations[comp]
            source_path = config["path"]
            
            if not source_path.exists():
                continue
            
            backup_path = self.backup_root / comp
            backup_path.mkdir(exist_ok=True)
            
            if config["files"] == "all":
                # Backup all files in directory
                for file in source_path.iterdir():
                    if file.is_file():
                        shutil.copy2(file, backup_path / file.name)
                        print(f"  📁 Backed up: {comp}/{file.name}")
            else:
                # Backup specific files
                for filename in config["files"]:
                    file_path = source_path / filename
                    if file_path.exists():
                        shutil.copy2(file_path, backup_path / filename)
                        print(f"  📁 Backed up: {comp}/{filename}")
        
        return self.backup_root
    
    def reset_component(self, component: str):
        """Reset a specific component"""
        if component not in self.data_locations:
            print(f"❌ Unknown component: {component}")
            return False
        
        config = self.data_locations[component]
        path = config["path"]
        
        if not path.exists():
            print(f"⚠️  Path doesn't exist: {path}")
            return False
        
        if config["files"] == "all":
            # Clear all files in directory
            cleared = 0
            for file in path.iterdir():
                if file.is_file() and not file.name.startswith('.'):
                    if file.suffix in ['.log', '.jsonl', '.pid']:
                        file.unlink()
                        cleared += 1
                    elif file.suffix == '.json':
                        with open(file, 'w') as f:
                            json.dump({}, f)
                        cleared += 1
            print(f"  ✅ Cleared {cleared} files in {component}")
        else:
            # Reset specific files
            for filename in config["files"]:
                file_path = path / filename
                if config["default"] is not None:
                    # Reset to default value
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'w') as f:
                        json.dump(config["default"], f, indent=2)
                    print(f"  ✅ Reset: {component}/{filename}")
                elif file_path.exists() and component == "agent_registry":
                    # Skip agent registry (backup only, don't reset)
                    print(f"  ⏭️  Skipped: {component}/{filename} (backup only)")
        
        return True
    
    def reset_all(self, skip_backup: bool = False):
        """Complete system reset"""
        print("\n" + "=" * 60)
        print("🔄 COMPLETE AGENT ARMY SYSTEM RESET")
        print("=" * 60)
        
        if not skip_backup:
            self.create_backup()
        
        print("\n🧹 Resetting components...")
        
        # Reset communication data
        self.reset_component("communication")
        
        # Reset document registry
        self.reset_component("registry")
        
        # Clear logs
        self.reset_component("logs")
        
        print("\n✅ System reset complete!")
        if not skip_backup:
            print(f"📁 Backup saved to: {self.backup_root.relative_to(self.base_path.parent)}")
    
    def get_statistics(self) -> dict:
        """Get current data statistics"""
        stats = {}
        
        for name, config in self.data_locations.items():
            path = config["path"]
            if not path.exists():
                stats[name] = {"exists": False}
                continue
            
            component_stats = {"exists": True, "files": {}}
            
            if config["files"] == "all":
                # Count all files
                file_count = 0
                total_size = 0
                for file in path.iterdir():
                    if file.is_file():
                        file_count += 1
                        total_size += file.stat().st_size
                component_stats["total_files"] = file_count
                component_stats["total_size_kb"] = total_size / 1024
            else:
                # Check specific files
                for filename in config["files"]:
                    file_path = path / filename
                    if file_path.exists():
                        size = file_path.stat().st_size
                        component_stats["files"][filename] = {
                            "exists": True,
                            "size_kb": size / 1024
                        }
                        
                        # Try to count items if JSON
                        if filename.endswith('.json'):
                            try:
                                with open(file_path, 'r') as f:
                                    data = json.load(f)
                                    if isinstance(data, dict):
                                        component_stats["files"][filename]["items"] = len(data)
                            except:
                                pass
            
            stats[name] = component_stats
        
        return stats
    
    def restore_backup(self, backup_path: str):
        """Restore from a backup"""
        backup_dir = Path(backup_path)
        if not backup_dir.exists():
            print(f"❌ Backup not found: {backup_path}")
            return False
        
        print(f"\n🔄 Restoring from backup: {backup_dir}")
        
        for component_dir in backup_dir.iterdir():
            if not component_dir.is_dir():
                continue
            
            component = component_dir.name
            if component not in self.data_locations:
                continue
            
            config = self.data_locations[component]
            target_path = config["path"]
            target_path.mkdir(parents=True, exist_ok=True)
            
            for file in component_dir.iterdir():
                if file.is_file():
                    shutil.copy2(file, target_path / file.name)
                    print(f"  ✅ Restored: {component}/{file.name}")
        
        print("\n✅ Restore complete!")
        return True

def main():
    parser = argparse.ArgumentParser(description="Reset Agent Army System Data")
    parser.add_argument("action", 
                       choices=["reset", "stats", "backup", "restore", "list-backups"],
                       help="Action to perform")
    parser.add_argument("--component", 
                       choices=["all", "communication", "registry", "logs"],
                       default="all",
                       help="Component to reset (default: all)")
    parser.add_argument("--skip-backup", action="store_true",
                       help="Skip creating backup before reset")
    parser.add_argument("--confirm", action="store_true",
                       help="Skip confirmation prompt")
    parser.add_argument("--backup-path", help="Path to backup for restore")
    
    args = parser.parse_args()
    
    resetter = CompleteSystemReset()
    
    if args.action == "stats":
        stats = resetter.get_statistics()
        print("\n📊 System Data Statistics:")
        print("=" * 60)
        for component, data in stats.items():
            print(f"\n{component.upper()}:")
            if not data.get("exists"):
                print("  ⚠️  Component path doesn't exist")
            elif "total_files" in data:
                print(f"  Files: {data['total_files']}")
                print(f"  Size: {data['total_size_kb']:.1f} KB")
            else:
                for filename, info in data.get("files", {}).items():
                    if info.get("exists"):
                        items = f" ({info.get('items', 0)} items)" if 'items' in info else ""
                        print(f"  {filename}: {info['size_kb']:.1f} KB{items}")
    
    elif args.action == "backup":
        backup_path = resetter.create_backup(
            None if args.component == "all" else args.component
        )
        print(f"\n✅ Backup created at: {backup_path}")
    
    elif args.action == "list-backups":
        backups_dir = resetter.base_path / "backups"
        if backups_dir.exists():
            backups = sorted([d for d in backups_dir.iterdir() if d.is_dir()])
            if backups:
                print("\n📁 Available backups:")
                for backup in backups:
                    print(f"  • {backup.name}")
            else:
                print("\n⚠️  No backups found")
        else:
            print("\n⚠️  No backups directory")
    
    elif args.action == "restore":
        if not args.backup_path:
            print("❌ Please specify --backup-path")
            return
        resetter.restore_backup(args.backup_path)
    
    elif args.action == "reset":
        # Show warning and get confirmation
        if not args.confirm:
            stats = resetter.get_statistics()
            
            print("\n⚠️  WARNING: This will reset system data")
            print("Components to reset:")
            for component in ["communication", "registry", "logs"]:
                if args.component == "all" or args.component == component:
                    print(f"  • {component}")
            
            response = input("\nAre you sure? (yes/no): ").lower()
            if response != "yes":
                print("❌ Reset cancelled")
                return
        
        if args.component == "all":
            resetter.reset_all(skip_backup=args.skip_backup)
        else:
            if not args.skip_backup:
                resetter.create_backup(args.component)
            resetter.reset_component(args.component)
            print(f"\n✅ {args.component} reset complete!")

if __name__ == "__main__":
    main()