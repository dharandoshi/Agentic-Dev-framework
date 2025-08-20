#!/usr/bin/env python3
"""
Agent Army Hook Orchestrator - SIMPLIFIED VERSION
Fixed coordination system that actually triggers agents to work
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class AgentArmyOrchestrator:
    """Simplified orchestrator that actually coordinates agents"""
    
    def __init__(self):
        self.project_root = Path(os.environ.get('CLAUDE_PROJECT_ROOT', '.'))
        self.logs_dir = self.project_root / '.claude' / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Core agent coordination rules
        self.coordination_rules = {
            'task_handoff_chains': [
                ('scrum-master', 'tech-lead'),
                ('tech-lead', 'senior-backend-engineer'),
                ('tech-lead', 'senior-frontend-engineer'),
                ('senior-backend-engineer', 'qa-engineer'),
                ('senior-frontend-engineer', 'qa-engineer'),
                ('qa-engineer', 'devops-engineer')
            ],
            'auto_start_agents': {
                'tech-lead': ['senior-backend-engineer', 'senior-frontend-engineer'],
                'scrum-master': ['tech-lead']
            }
        }
        
    def _trigger_agent_work(self, agent_name: str, task_id: str, context: Dict = None) -> bool:
        """Actually trigger an agent to start working on a task"""
        try:
            # Use the workflow engine to trigger agent
            scripts_dir = self.project_root / '.claude' / 'scripts'
            workflow_engine = scripts_dir / 'agent_workflow_engine.py'
            
            if workflow_engine.exists():
                # Call the workflow engine
                context_json = json.dumps(context or {})
                cmd = [
                    'python3', 
                    str(workflow_engine), 
                    agent_name, 
                    task_id, 
                    context_json
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self._log_event("agent_triggered", {
                        "agent": agent_name,
                        "task_id": task_id,
                        "timestamp": datetime.now().isoformat()
                    })
                    return True
                else:
                    self._log_event("agent_trigger_failed", {
                        "agent": agent_name,
                        "task_id": task_id,
                        "error": result.stderr
                    })
                    return False
            else:
                # Fallback: just log the trigger
                self._log_event("agent_triggered_fallback", {
                    "agent": agent_name,
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat()
                })
                return True
                
        except Exception as e:
            self._log_event("agent_trigger_failed", {
                "agent": agent_name,
                "task_id": task_id,
                "error": str(e)
            })
            return False
    
    def _check_task_dependencies(self, task_id: str) -> bool:
        """Check if task dependencies are met"""
        try:
            tasks_file = self.project_root / '.claude' / 'mcp' / 'data' / 'communication' / 'tasks.json'
            if not tasks_file.exists():
                return True
            
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
            
            if task_id not in tasks:
                return True
            
            task = tasks[task_id]
            dependencies = task.get('dependencies', [])
            
            for dep_id in dependencies:
                if dep_id in tasks:
                    dep_status = tasks[dep_id].get('status', 'pending')
                    if dep_status not in ['completed']:
                        return False
            
            return True
        except Exception:
            return True
    
    def _handle_task_assignment(self, task_data: Dict) -> Dict:
        """Handle task assignment and trigger agent work"""
        task_id = task_data.get('task_id')
        assigned_to = task_data.get('assigned_to')
        
        if not task_id or not assigned_to:
            return {"action": "allow"}
        
        # Check if dependencies are met
        if not self._check_task_dependencies(task_id):
            return {
                "action": "warn",
                "message": f"⏳ Task {task_id} dependencies not met yet"
            }
        
        # Trigger the assigned agent to start work
        success = self._trigger_agent_work(assigned_to, task_id, task_data)
        
        if success:
            # Also trigger any downstream agents if this is a coordinating agent
            if assigned_to in self.coordination_rules['auto_start_agents']:
                downstream_agents = self.coordination_rules['auto_start_agents'][assigned_to]
                for agent in downstream_agents:
                    self._trigger_agent_work(agent, task_id, {
                        'role': 'supporting',
                        'coordinator': assigned_to
                    })
            
            return {
                "action": "allow",
                "message": f"✅ Triggered {assigned_to} to start working on task {task_id}"
            }
        else:
            return {
                "action": "warn",
                "message": f"⚠️ Failed to trigger {assigned_to} for task {task_id}"
            }
    
    def _log_event(self, event_type: str, data: Dict):
        """Log events to file"""
        log_file = self.logs_dir / f"coordination-{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _validate_coordination_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Validate and handle coordination tools"""
        if not tool_name.startswith('mcp__coord__'):
            return {"action": "allow"}
        
        action = tool_name.replace('mcp__coord__', '')
        
        # Log the coordination attempt
        self._log_event("coordination_attempt", {
            "tool": action,
            "parameters": parameters
        })
        
        # Handle task assignment - this is where coordination happens!
        if action == "task_assign":
            return self._handle_task_assignment(parameters)
        
        # Handle task status updates
        elif action == "task_status":
            status = parameters.get('status')
            task_id = parameters.get('task_id')
            
            if status == 'completed' and task_id:
                # Trigger dependent tasks when this one completes
                self._trigger_dependent_tasks(task_id)
        
        return {"action": "allow"}
    
    def _trigger_dependent_tasks(self, completed_task_id: str):
        """Trigger tasks that depend on the completed task"""
        try:
            tasks_file = self.project_root / '.claude' / 'mcp' / 'data' / 'communication' / 'tasks.json'
            if not tasks_file.exists():
                return
            
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
            
            # Find tasks that depend on the completed task
            for task_id, task_data in tasks.items():
                dependencies = task_data.get('dependencies', [])
                if completed_task_id in dependencies:
                    # Check if all dependencies are now met
                    if self._check_task_dependencies(task_id):
                        assigned_to = task_data.get('assigned_to')
                        if assigned_to:
                            self._trigger_agent_work(assigned_to, task_id, task_data)
                            self._log_event("dependent_task_triggered", {
                                "task_id": task_id,
                                "assigned_to": assigned_to,
                                "completed_dependency": completed_task_id
                            })
        except Exception as e:
            self._log_event("dependent_task_trigger_failed", {
                "completed_task_id": completed_task_id,
                "error": str(e)
            })
    
    def process_hook(self, hook_type: str, input_data: Dict) -> Dict:
        """Main hook processing logic - SIMPLIFIED"""
        response = {"action": "allow"}
        
        try:
            if hook_type == "pre-tool-use":
                # Process coordination tools before they execute
                tool = input_data.get('tool', {})
                tool_name = tool.get('name', '')
                parameters = tool.get('parameters', {})
                
                # Handle coordination tools
                validation = self._validate_coordination_tool(tool_name, parameters)
                response.update(validation)
            
            elif hook_type == "post-tool-use":
                # Process results after tool execution
                tool_name = input_data.get('tool', {}).get('name', '')
                result = input_data.get('result', {})
                
                # Log successful coordinations
                if tool_name.startswith('mcp__coord__'):
                    self._log_event("coordination_success", {
                        "tool": tool_name.replace('mcp__coord__', ''),
                        "success": True
                    })
        
        except Exception as e:
            self._log_event("hook_error", {
                "hook_type": hook_type,
                "error": str(e)
            })
            # Always allow on error to prevent blocking
        
        return response

def main():
    """Main entry point for the hook"""
    try:
        # Get hook input
        hook_input = json.loads(os.environ.get('CLAUDE_HOOK_INPUT', '{}'))
        hook_type = os.environ.get('CLAUDE_HOOK_TYPE', 'unknown')
        
        # Initialize orchestrator
        orchestrator = AgentArmyOrchestrator()
        
        # Process the hook
        response = orchestrator.process_hook(hook_type, hook_input)
        
        # Output response
        print(json.dumps(response))
        
    except Exception as e:
        # Always allow on error to prevent blocking
        error_response = {
            "action": "allow",
            "error": str(e)
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()