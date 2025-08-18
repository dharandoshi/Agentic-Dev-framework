#!/usr/bin/env python3
"""Git utilities for workspace MCP server"""

import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

class GitManager:
    """Manages git operations for the workspace"""
    
    def __init__(self, root: Path):
        self.root = root
        self.is_git_repo = (root / ".git").exists()
    
    def get_status(self) -> Dict[str, Any]:
        """Get git status information"""
        if not self.is_git_repo:
            return {"error": "Not a git repository"}
        
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.root
            )
            current_branch = branch_result.stdout.strip()
            
            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.root
            )
            
            # Parse status
            modified = []
            untracked = []
            staged = []
            
            for line in status_result.stdout.splitlines():
                if line.startswith("??"):
                    untracked.append(line[3:])
                elif line.startswith("M ") or line.startswith(" M"):
                    modified.append(line[3:])
                elif line.startswith("A "):
                    staged.append(line[3:])
            
            # Get commit info
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-n", "5"],
                capture_output=True,
                text=True,
                cwd=self.root
            )
            recent_commits = log_result.stdout.splitlines()
            
            # Get remote info
            remote_result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                cwd=self.root
            )
            remotes = []
            for line in remote_result.stdout.splitlines():
                if "fetch" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes.append({"name": parts[0], "url": parts[1]})
            
            return {
                "is_git_repo": True,
                "current_branch": current_branch,
                "modified_files": modified,
                "untracked_files": untracked,
                "staged_files": staged,
                "recent_commits": recent_commits,
                "remotes": remotes,
                "has_changes": bool(modified or untracked or staged)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_file_history(self, file_path: str, limit: int = 10) -> List[Dict[str, str]]:
        """Get commit history for a specific file"""
        if not self.is_git_repo:
            return []
        
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%an|%ae|%at|%s", "--", file_path],
                capture_output=True,
                text=True,
                cwd=self.root
            )
            
            commits = []
            for line in result.stdout.splitlines():
                parts = line.split("|")
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0][:7],
                        "author": parts[1],
                        "email": parts[2],
                        "timestamp": parts[3],
                        "message": parts[4]
                    })
            
            return commits
            
        except:
            return []
    
    def get_blame(self, file_path: str) -> Dict[str, Any]:
        """Get blame information for a file"""
        if not self.is_git_repo:
            return {"error": "Not a git repository"}
        
        try:
            result = subprocess.run(
                ["git", "blame", "--line-porcelain", file_path],
                capture_output=True,
                text=True,
                cwd=self.root
            )
            
            # Parse blame output
            blame_data = []
            current_block = {}
            
            for line in result.stdout.splitlines():
                if line.startswith("author "):
                    current_block["author"] = line[7:]
                elif line.startswith("author-time "):
                    current_block["timestamp"] = line[12:]
                elif line.startswith("\t"):
                    current_block["code"] = line[1:]
                    blame_data.append(current_block)
                    current_block = {}
            
            return {
                "file": file_path,
                "blame": blame_data[:50]  # Limit to first 50 lines
            }
            
        except Exception as e:
            return {"error": str(e)}