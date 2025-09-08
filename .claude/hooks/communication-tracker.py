#!/usr/bin/env python3
"""
Communication Tracker Hook
Tracks all agent communications and generates analytics
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class CommunicationTracker:
    def __init__(self):
        # Get project root from environment or use script location
        project_root = Path(os.environ.get('CLAUDE_PROJECT_ROOT', Path(__file__).parent.parent))
        self.logs_dir = project_root / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.logs_dir / 'communication-stats.json'
        self.load_stats()
    
    def load_stats(self):
        """Load existing statistics"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "total_communications": 0,
                "by_tool": defaultdict(int),
                "by_agent": defaultdict(int),
                "by_day": defaultdict(int),
                "handoff_chains": [],
                "escalations": [],
                "checkpoints": []
            }
    
    def save_stats(self):
        """Save statistics"""
        # Convert defaultdicts to regular dicts for JSON serialization
        stats_to_save = {
            "total_communications": self.stats["total_communications"],
            "by_tool": dict(self.stats["by_tool"]),
            "by_agent": dict(self.stats["by_agent"]),
            "by_day": dict(self.stats["by_day"]),
            "handoff_chains": self.stats["handoff_chains"][-100:],  # Keep last 100
            "escalations": self.stats["escalations"][-50:],  # Keep last 50
            "checkpoints": self.stats["checkpoints"][-50:]  # Keep last 50
        }
        
        with open(self.stats_file, 'w') as f:
            json.dump(stats_to_save, f, indent=2)
    
    def track_communication(self, tool_name: str, parameters: dict):
        """Track a communication event"""
        if not tool_name.startswith('mcp__communication__'):
            return
        
        action = tool_name.replace('mcp__communication__', '')
        timestamp = datetime.now()
        
        # Update statistics
        self.stats["total_communications"] += 1
        self.stats["by_tool"][action] += 1
        
        # Track by agent
        from_agent = parameters.get('from_agent') or parameters.get('agent', 'unknown')
        self.stats["by_agent"][from_agent] += 1
        
        # Track by day
        day_key = timestamp.strftime('%Y-%m-%d')
        self.stats["by_day"][day_key] += 1
        
        # Track specific events
        if action == 'task_handoff':
            self.stats["handoff_chains"].append({
                "timestamp": timestamp.isoformat(),
                "from": parameters.get('from_agent'),
                "to": parameters.get('to_agent'),
                "task_id": parameters.get('task_id')
            })
        
        elif action == 'escalation_create':
            self.stats["escalations"].append({
                "timestamp": timestamp.isoformat(),
                "from": parameters.get('from_agent'),
                "reason": parameters.get('reason'),
                "severity": parameters.get('severity')
            })
        
        elif action == 'checkpoint_create':
            self.stats["checkpoints"].append({
                "timestamp": timestamp.isoformat(),
                "name": parameters.get('name'),
                "created_by": from_agent
            })
        
        # Log detailed event
        log_file = self.logs_dir / f"communications-{timestamp.strftime('%Y%m%d')}.jsonl"
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "tool": action,
            "parameters": parameters,
            "session": os.environ.get('CLAUDE_SESSION_ID', 'unknown')
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Save updated stats
        self.save_stats()
    
    def get_summary(self):
        """Get communication summary"""
        return {
            "total": self.stats["total_communications"],
            "most_used_tool": max(self.stats["by_tool"].items(), key=lambda x: x[1])[0] 
                              if self.stats["by_tool"] else None,
            "most_active_agent": max(self.stats["by_agent"].items(), key=lambda x: x[1])[0]
                                if self.stats["by_agent"] else None,
            "recent_escalations": len(self.stats["escalations"]),
            "recent_handoffs": len(self.stats["handoff_chains"])
        }

def main():
    """Main hook entry point"""
    try:
        hook_input = json.loads(os.environ.get('CLAUDE_HOOK_INPUT', '{}'))
        
        # Only track tool usage
        tool = hook_input.get('tool', {})
        if tool:
            tracker = CommunicationTracker()
            tracker.track_communication(
                tool.get('name', ''),
                tool.get('parameters', {})
            )
            
            # Get summary for metadata
            summary = tracker.get_summary()
            
            response = {
                "action": "allow",
                "metadata": {
                    "tracked": True,
                    "communication_stats": summary
                }
            }
        else:
            response = {"action": "allow"}
        
        print(json.dumps(response))
        
    except Exception as e:
        # Always allow on error
        print(json.dumps({"action": "allow", "error": str(e)}))

if __name__ == "__main__":
    main()