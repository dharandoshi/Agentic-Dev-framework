#!/usr/bin/env python3
"""
Agent Army Automated Backup System
Creates comprehensive backups of the entire Agent Army infrastructure
"""

import os
import sys
import shutil
import tarfile
import datetime
import argparse
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

class AgentArmyBackup:
    """Comprehensive backup system for Agent Army"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.claude_dir = self.project_root / ".claude"
        self.backup_dir = self.project_root / "backups"
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
    def get_critical_files(self) -> Dict[str, List[str]]:
        """Define critical files and directories for backup"""
        return {
            "agents": [
                ".claude/agents/",
                ".claude/agents/agent-registry.json"
            ],
            "mcp": [
                ".claude/mcp/servers/core/",
                ".claude/mcp/data/",
                ".claude/mcp/logs/"
            ],
            "hooks": [
                ".claude/hooks/",
                ".claude/settings.json",
                ".claude/settings.local.json",
                ".claude/example-hooks-config.json"
            ],
            "scripts": [
                ".claude/scripts/"
            ],
            "docs": [
                ".claude/docs/",
                "README.md"
            ],
            "logs": [
                ".claude/logs/"
            ],
            "config": [
                ".claude/config-backup.json"
            ]
        }
        
    def create_component_backup(self, component: str) -> Optional[Path]:
        """Create backup for specific component"""
        critical_files = self.get_critical_files()
        
        if component not in critical_files:
            print(f"❌ Unknown component: {component}")
            return None
            
        backup_name = f"agent-army-{component}-{self.timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Creating {component} backup...")
        
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in critical_files[component]:
                    full_path = self.project_root / file_path
                    
                    if full_path.exists():
                        if full_path.is_dir():
                            # Add directory recursively, excluding certain files
                            for item in full_path.rglob("*"):
                                if self._should_include_file(item):
                                    arcname = item.relative_to(self.project_root)
                                    tar.add(item, arcname=arcname)
                        else:
                            # Add individual file
                            arcname = full_path.relative_to(self.project_root)
                            tar.add(full_path, arcname=arcname)
                        
                        print(f"  ✅ Added: {file_path}")
                    else:
                        print(f"  ⚠️  Skipped (not found): {file_path}")
                        
        except Exception as e:
            print(f"❌ Error creating {component} backup: {e}")
            return None
            
        print(f"✅ {component} backup created: {backup_path}")
        return backup_path
        
    def create_full_backup(self) -> Optional[Path]:
        """Create complete system backup"""
        backup_name = f"agent-army-full-{self.timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Creating full system backup...")
        
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                critical_files = self.get_critical_files()
                
                # Add all components
                for component, file_paths in critical_files.items():
                    print(f"  📂 Processing {component}...")
                    
                    for file_path in file_paths:
                        full_path = self.project_root / file_path
                        
                        if full_path.exists():
                            if full_path.is_dir():
                                # Add directory recursively
                                for item in full_path.rglob("*"):
                                    if self._should_include_file(item):
                                        arcname = item.relative_to(self.project_root)
                                        tar.add(item, arcname=arcname)
                            else:
                                # Add individual file
                                arcname = full_path.relative_to(self.project_root)
                                tar.add(full_path, arcname=arcname)
                                
                            print(f"    ✅ {file_path}")
                        else:
                            print(f"    ⚠️  {file_path} (not found)")
                            
        except Exception as e:
            print(f"❌ Error creating full backup: {e}")
            return None
            
        # Create backup manifest
        self._create_backup_manifest(backup_path)
        
        print(f"✅ Full backup created: {backup_path}")
        return backup_path
        
    def create_incremental_backup(self) -> Optional[Path]:
        """Create incremental backup of changed files"""
        backup_name = f"agent-army-incremental-{self.timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Creating incremental backup...")
        
        # Get changed files using git
        try:
            result = subprocess.run([
                "git", "diff", "--name-only", "HEAD~1", "HEAD"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                print("⚠️  Git not available or no changes, creating modified files backup")
                return self._create_modified_files_backup()
                
            changed_files = result.stdout.strip().split('\n')
            changed_files = [f for f in changed_files if f.strip()]
            
            if not changed_files:
                print("ℹ️  No changes detected")
                return None
                
        except Exception as e:
            print(f"⚠️  Error detecting changes: {e}")
            return self._create_modified_files_backup()
            
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in changed_files:
                    full_path = self.project_root / file_path
                    
                    if full_path.exists() and self._should_include_file(full_path):
                        tar.add(full_path, arcname=file_path)
                        print(f"  ✅ {file_path}")
                        
        except Exception as e:
            print(f"❌ Error creating incremental backup: {e}")
            return None
            
        print(f"✅ Incremental backup created: {backup_path}")
        return backup_path
        
    def _create_modified_files_backup(self) -> Optional[Path]:
        """Create backup of recently modified files"""
        backup_name = f"agent-army-modified-{self.timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        # Find files modified in last 24 hours
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=24)
        modified_files = []
        
        for root, dirs, files in os.walk(self.claude_dir):
            for file in files:
                file_path = Path(root) / file
                
                if file_path.stat().st_mtime > cutoff_time.timestamp():
                    if self._should_include_file(file_path):
                        modified_files.append(file_path)
                        
        if not modified_files:
            print("ℹ️  No recently modified files found")
            return None
            
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in modified_files:
                    arcname = file_path.relative_to(self.project_root)
                    tar.add(file_path, arcname=arcname)
                    print(f"  ✅ {arcname}")
                    
        except Exception as e:
            print(f"❌ Error creating modified files backup: {e}")
            return None
            
        return backup_path
        
    def _should_include_file(self, file_path: Path) -> bool:
        """Determine if file should be included in backup"""
        exclude_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "Thumbs.db",
            "venv",
            "node_modules",
            "*.tmp",
            "*.temp"
        ]
        
        file_str = str(file_path)
        
        for pattern in exclude_patterns:
            if pattern in file_str:
                return False
                
        return True
        
    def _create_backup_manifest(self, backup_path: Path):
        """Create manifest file with backup details"""
        manifest = {
            "backup_name": backup_path.name,
            "created_at": self.timestamp,
            "type": "full",
            "project_root": str(self.project_root),
            "components": list(self.get_critical_files().keys()),
            "file_count": 0,
            "size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2)
        }
        
        # Count files in backup
        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                manifest["file_count"] = len(tar.getnames())
        except:
            pass
            
        manifest_path = backup_path.with_suffix('.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
    def list_backups(self):
        """List all available backups"""
        backups = list(self.backup_dir.glob("*.tar.gz"))
        
        if not backups:
            print("ℹ️  No backups found")
            return
            
        print(f"📁 Available backups ({len(backups)}):")
        print("-" * 50)
        
        for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True):
            size_mb = round(backup.stat().st_size / (1024 * 1024), 2)
            modified = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
            
            print(f"  📦 {backup.name}")
            print(f"     Size: {size_mb} MB")
            print(f"     Created: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backup files, keeping the most recent ones"""
        backups = list(self.backup_dir.glob("*.tar.gz"))
        
        if len(backups) <= keep_count:
            print(f"ℹ️  Only {len(backups)} backups found, no cleanup needed")
            return
            
        # Sort by modification time, oldest first
        sorted_backups = sorted(backups, key=lambda x: x.stat().st_mtime)
        old_backups = sorted_backups[:-keep_count]
        
        print(f"🗑️  Cleaning up {len(old_backups)} old backups...")
        
        for backup in old_backups:
            try:
                backup.unlink()
                # Also remove manifest if it exists
                manifest = backup.with_suffix('.json')
                if manifest.exists():
                    manifest.unlink()
                print(f"  ✅ Removed: {backup.name}")
            except Exception as e:
                print(f"  ❌ Failed to remove {backup.name}: {e}")
                
    def git_backup(self):
        """Create git-based backup"""
        print("📦 Creating git-based backup...")
        
        try:
            # Add all critical files to git
            result = subprocess.run([
                "git", "add", ".claude/", "README.md"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                print(f"❌ Git add failed: {result.stderr}")
                return False
                
            # Commit changes
            commit_msg = f"backup: Agent Army configuration {self.timestamp}"
            result = subprocess.run([
                "git", "commit", "-m", commit_msg
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("ℹ️  No changes to commit")
                    return True
                else:
                    print(f"❌ Git commit failed: {result.stderr}")
                    return False
                    
            print("✅ Git backup committed")
            
            # Push to remote if configured
            result = subprocess.run([
                "git", "push"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Git backup pushed to remote")
            else:
                print("⚠️  Git push failed (no remote configured?)")
                
            return True
            
        except Exception as e:
            print(f"❌ Git backup failed: {e}")
            return False

def main():
    """Main backup execution"""
    parser = argparse.ArgumentParser(description="Agent Army Backup System")
    parser.add_argument("--type", choices=["full", "incremental", "git"], 
                       default="full", help="Backup type")
    parser.add_argument("--components", 
                       help="Comma-separated list of components to backup")
    parser.add_argument("--list", action="store_true", 
                       help="List available backups")
    parser.add_argument("--cleanup", type=int, metavar="KEEP_COUNT", 
                       help="Clean up old backups, keeping specified number")
    
    args = parser.parse_args()
    
    backup = AgentArmyBackup()
    
    if args.list:
        backup.list_backups()
        return
        
    if args.cleanup:
        backup.cleanup_old_backups(args.cleanup)
        return
        
    print("🔄 Agent Army Backup System")
    print("=" * 40)
    
    if args.components:
        # Backup specific components
        components = [c.strip() for c in args.components.split(",")]
        for component in components:
            backup.create_component_backup(component)
    elif args.type == "full":
        backup.create_full_backup()
    elif args.type == "incremental":
        backup.create_incremental_backup()
    elif args.type == "git":
        backup.git_backup()
        
    print("\n✅ Backup operation completed!")

if __name__ == "__main__":
    main()