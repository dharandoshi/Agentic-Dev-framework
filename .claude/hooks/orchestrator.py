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

# Agent expertise mapping for intelligent task routing
AGENT_EXPERTISE = {
    'senior-frontend-engineer': ['ui', 'component', 'frontend', 'react', 'vue', 'angular', 'css', 'html'],
    'senior-backend-engineer': ['api', 'backend', 'database', 'server', 'endpoint', 'migration', 'model'],
    'qa-engineer': ['test', 'quality', 'bug', 'validation', 'e2e', 'integration', 'unit'],
    'devops-engineer': ['deploy', 'ci/cd', 'pipeline', 'docker', 'kubernetes', 'infrastructure'],
    'security-engineer': ['security', 'vulnerability', 'authentication', 'authorization', 'encryption'],
    'data-engineer': ['etl', 'pipeline', 'data', 'warehouse', 'analytics', 'stream'],
    'system-architect': ['architecture', 'design', 'system', 'schema', 'structure'],
    'requirements-analyst': ['requirements', 'user story', 'acceptance', 'criteria', 'specification'],
    'technical-writer': ['documentation', 'readme', 'guide', 'tutorial', 'api docs'],
    'scrum-master': ['sprint', 'backlog', 'agile', 'planning', 'retrospective'],
    'project-initializer': ['setup', 'initialize', 'bootstrap', 'scaffold', 'structure']
}

# Agent names that can be explicitly mentioned
AGENT_NAMES = [
    'senior-frontend-engineer', 'senior-backend-engineer', 'qa-engineer',
    'devops-engineer', 'security-engineer', 'data-engineer',
    'system-architect', 'requirements-analyst', 'technical-writer',
    'scrum-master', 'project-initializer', 'engineering-manager'
]

class AgentArmyOrchestrator:
    """Simplified orchestrator that actually coordinates agents"""
    
    def __init__(self):
        self.project_root = Path(os.environ.get('CLAUDE_PROJECT_ROOT', '.'))
        self.logs_dir = self.project_root / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.auto_trigger_enabled = False  # Disabled auto agent selection
        
        # Comprehensive agent coordination rules
        self.coordination_rules = {
            # Who can hand off to whom
            'handoff_patterns': {
                'scrum-master': ['engineering-manager', 'requirements-analyst', 'project-initializer'],
                'engineering-manager': ['senior-backend-engineer', 'senior-frontend-engineer', 'system-architect', 
                             'security-engineer', 'data-engineer'],
                'requirements-analyst': ['system-architect', 'technical-writer', 'engineering-manager'],
                'system-architect': ['engineering-manager', 'senior-backend-engineer', 'senior-frontend-engineer'],
                'senior-backend-engineer': ['qa-engineer', 'security-engineer', 'data-engineer'],
                'senior-frontend-engineer': ['qa-engineer', 'technical-writer'],
                'data-engineer': ['qa-engineer'],
                'qa-engineer': ['devops-engineer', 'engineering-manager'],
                'devops-engineer': ['engineering-manager'],
                'security-engineer': ['devops-engineer', 'engineering-manager'],
                'technical-writer': ['engineering-manager'],
                'project-initializer': ['engineering-manager', 'system-architect']
            },
            
            # Automatic coordination triggers
            'auto_coordinate': {
                'requirements_complete': ['system-architect', 'engineering-manager'],
                'architecture_complete': ['engineering-manager'],
                'backend_complete': ['qa-engineer'],
                'frontend_complete': ['qa-engineer'],
                'testing_complete': ['devops-engineer'],
                'deployment_ready': ['devops-engineer']
            },
            
            # Reporting hierarchy
            'reporting_chain': {
                'senior-backend-engineer': 'engineering-manager',
                'senior-frontend-engineer': 'engineering-manager',
                'qa-engineer': 'engineering-manager',
                'devops-engineer': 'engineering-manager',
                'security-engineer': 'engineering-manager',
                'data-engineer': 'engineering-manager',
                'system-architect': 'engineering-manager',
                'technical-writer': 'engineering-manager',
                'engineering-manager': 'scrum-master',
                'requirements-analyst': 'scrum-master',
                'project-initializer': 'scrum-master'
            },
            
            # Collaboration patterns
            'collaboration_required': {
                'api_design': ['senior-backend-engineer', 'senior-frontend-engineer'],
                'security_review': ['security-engineer', 'senior-backend-engineer'],
                'deployment': ['devops-engineer', 'sre-engineer'],
                'data_pipeline': ['data-engineer', 'integration-engineer'],
                'performance': ['senior-backend-engineer', 'sre-engineer']
            }
        }
        
    def _trigger_agent_work(self, agent_name: str, task_id: str, context: Dict = None) -> bool:
        """Actually trigger an agent to start working on a task"""
        try:
            # Get current working directory for consistency
            import os
            current_dir = os.getcwd()
            
            # Enhanced content with working directory context
            task_content = (
                f"Please begin work on task {task_id}.\n"
                f"CRITICAL: Working Directory = {current_dir}\n"
                f"DO NOT create project subfolders. Use the current directory structure.\n"
                f"Read .claude/shared-context.md for directory rules.\n"
                f"Report progress back when complete."
            )
            
            # Create a delegation message with working directory context
            message_data = {
                "from_agent": context.get('coordinator', 'engineering-manager') if context else 'engineering-manager',
                "to_agent": agent_name,
                "subject": f"Task Assignment: {task_id}",
                "content": task_content,
                "type": "task",
                "priority": "high",
                "requires_response": True,
                "task_id": task_id,
                "working_directory": current_dir,
                "context": {
                    "cwd": current_dir,
                    "shared_context": ".claude/shared-context.md",
                    **(context or {})
                }
            }
            
            # Store delegation message for agent to pick up
            self._store_delegation_message(message_data)
            
            # Log the delegation
            self._log_event("delegation_initiated", {
                "from": message_data['from_agent'],
                "to": agent_name,
                "task_id": task_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Create automatic status update reminder
            self._schedule_status_check(agent_name, task_id)
            
            return True
                
        except Exception as e:
            self._log_event("delegation_failed", {
                "agent": agent_name,
                "task_id": task_id,
                "error": str(e)
            })
            return False
    
    def _store_delegation_message(self, message_data: Dict):
        """Store delegation message for agent coordination"""
        try:
            messages_file = self.project_root / 'mcp' / 'data' / 'communication' / 'messages.json'
            messages_file.parent.mkdir(parents=True, exist_ok=True)
            
            messages = {}
            if messages_file.exists():
                with open(messages_file, 'r') as f:
                    messages = json.load(f)
            
            message_id = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}_{message_data['to_agent']}"
            messages[message_id] = {
                **message_data,
                "id": message_id,
                "timestamp": datetime.now().isoformat(),
                "status": "unread"
            }
            
            with open(messages_file, 'w') as f:
                json.dump(messages, f, indent=2)
                
        except Exception as e:
            self._log_event("message_store_failed", {"error": str(e)})
    
    def _schedule_status_check(self, agent_name: str, task_id: str):
        """Schedule a status check for delegated task"""
        try:
            reminders_file = self.project_root / 'mcp' / 'data' / 'communication' / 'reminders.json'
            reminders_file.parent.mkdir(parents=True, exist_ok=True)
            
            reminders = {}
            if reminders_file.exists():
                with open(reminders_file, 'r') as f:
                    reminders = json.load(f)
            
            reminder_id = f"reminder_{task_id}_{agent_name}"
            reminders[reminder_id] = {
                "agent": agent_name,
                "task_id": task_id,
                "check_after": datetime.now().isoformat(),
                "status": "pending"
            }
            
            with open(reminders_file, 'w') as f:
                json.dump(reminders, f, indent=2)
                
        except Exception as e:
            self._log_event("reminder_schedule_failed", {"error": str(e)})
    
    def _check_task_dependencies(self, task_id: str) -> bool:
        """Check if task dependencies are met"""
        try:
            tasks_file = self.project_root / 'mcp' / 'data' / 'communication' / 'tasks.json'
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
        
        # Simple validation: check if right agent for the task
        task_details = self._load_task_details(task_id)
        if task_details:
            task_title = task_details.get('title', '').lower()
            task_desc = task_details.get('description', '').lower()
            
            # Find best agent based on expertise matching
            suggested_agents = self._find_best_agents_for_task(task_title + ' ' + task_desc)
            suggested_agent = suggested_agents[0] if suggested_agents else None
            
            # Warn if potentially wrong assignment
            if suggested_agent and suggested_agent != assigned_to:
                self._log_event("assignment_mismatch_warning", {
                    "task_id": task_id,
                    "assigned_to": assigned_to,
                    "suggested": suggested_agent
                })
        
        # Check if dependencies are met
        if not self._check_task_dependencies(task_id):
            return {
                "action": "warn",
                "message": f"⏳ Task {task_id} dependencies not met yet"
            }
        
        # Trigger the assigned agent to start work
        success = self._trigger_agent_work(assigned_to, task_id, task_data)
        
        if success:
            # Check if collaboration is needed
            collaborators = self._find_collaborators(task_details) if task_details else []
            for collaborator in collaborators:
                if collaborator != assigned_to:
                    self._trigger_agent_work(collaborator, task_id, {
                        'role': 'collaborator',
                        'lead': assigned_to
                    })
            
            return {
                "action": "allow",
                "message": f"✅ Triggered {assigned_to} to work on task {task_id}" + 
                          (f" with {', '.join(collaborators)}" if collaborators else "")
            }
        else:
            return {
                "action": "warn",
                "message": f"⚠️ Failed to trigger {assigned_to} for task {task_id}"
            }
    
    def _log_event(self, event_type: str, data: Dict):
        """Log events using MCP logging server (fallback to file if MCP unavailable)"""
        # For now, still log to file as backup
        # In production, this would call the MCP logging server
        log_file = self.logs_dir / f"coordination-{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
            "logged_via": "file"  # Will be "mcp" when integrated
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # TODO: When MCP servers are running, use:
        # mcp__logging__log_event(
        #     agent="orchestrator",
        #     level="info",
        #     message=f"Event: {event_type}",
        #     context=data
        # )
    
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
                # Report completion back up the chain
                self._report_task_completion(task_id, parameters)
                # Trigger dependent tasks when this one completes
                self._trigger_dependent_tasks(task_id)
        
        # Handle message sends for reporting
        elif action == "message_send":
            return self._handle_message_send(parameters)
        
        # Handle task handoffs
        elif action == "task_handoff":
            return self._handle_task_handoff(parameters)
        
        return {"action": "allow"}
    
    def _load_task_details(self, task_id: str) -> Optional[Dict]:
        """Load full task details from JSON"""
        try:
            tasks_file = self.project_root / 'mcp' / 'data' / 'communication' / 'tasks.json'
            if not tasks_file.exists():
                return None
            
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
            
            return tasks.get(task_id)
        except Exception:
            return None
    
    def _report_task_completion(self, task_id: str, parameters: Dict):
        """Report task completion up the reporting chain"""
        try:
            # Get the agent who completed the task
            task_details = self._load_task_details(task_id)
            if not task_details:
                return
            
            assigned_to = task_details.get('assigned_to')
            if not assigned_to:
                return
            
            # Find who to report to
            report_to = self.coordination_rules['reporting_chain'].get(assigned_to)
            if not report_to:
                return
            
            # Create completion report
            report_message = {
                "from_agent": assigned_to,
                "to_agent": report_to,
                "subject": f"Task {task_id} Completed",
                "content": f"Task {task_id} has been completed successfully. Status: {parameters.get('status')}\nProgress: {parameters.get('progress', 100)}%",
                "type": "status",
                "priority": "medium",
                "task_id": task_id
            }
            
            self._store_delegation_message(report_message)
            
            self._log_event("completion_reported", {
                "task_id": task_id,
                "from": assigned_to,
                "to": report_to,
                "timestamp": datetime.now().isoformat()
            })
            
            # If reporting to scrum-master, create a summary
            if report_to == 'scrum-master':
                self._create_sprint_summary(task_id, assigned_to)
                
        except Exception as e:
            self._log_event("report_failed", {
                "task_id": task_id,
                "error": str(e)
            })
    
    def _create_sprint_summary(self, task_id: str, completed_by: str):
        """Create sprint summary for scrum master"""
        try:
            summary_file = self.project_root / 'mcp' / 'data' / 'communication' / 'sprint_summary.json'
            summary_file.parent.mkdir(parents=True, exist_ok=True)
            
            summary = {}
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
            
            if 'completed_tasks' not in summary:
                summary['completed_tasks'] = []
            
            summary['completed_tasks'].append({
                "task_id": task_id,
                "completed_by": completed_by,
                "completed_at": datetime.now().isoformat()
            })
            
            summary['last_updated'] = datetime.now().isoformat()
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
                
        except Exception as e:
            self._log_event("summary_failed", {"error": str(e)})
    
    def _handle_message_send(self, parameters: Dict) -> Dict:
        """Handle message sends between agents"""
        from_agent = parameters.get('from_agent', '')
        to_agent = parameters.get('to_agent', '')
        message_type = parameters.get('type', '')
        
        # Validate reporting chain
        if message_type in ['status', 'response']:
            expected_recipient = self.coordination_rules['reporting_chain'].get(from_agent)
            if expected_recipient and to_agent != expected_recipient:
                self._log_event("reporting_chain_violation", {
                    "from": from_agent,
                    "to": to_agent,
                    "expected": expected_recipient
                })
                return {
                    "action": "warn",
                    "message": f"⚠️ {from_agent} should report to {expected_recipient}, not {to_agent}"
                }
        
        # Store the message for coordination
        self._store_delegation_message(parameters)
        
        return {"action": "allow"}
    
    def _trigger_dependent_tasks(self, completed_task_id: str):
        """Trigger tasks that depend on the completed task"""
        try:
            tasks_file = self.project_root / 'mcp' / 'data' / 'communication' / 'tasks.json'
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
    
    def _find_best_agents_for_task(self, task_text: str) -> List[str]:
        """Find best agents based on task keywords and expertise"""
        task_lower = task_text.lower()
        scores = {}
        
        for agent, keywords in AGENT_EXPERTISE.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                scores[agent] = score
        
        # Sort by score and return top matches
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [agent for agent, _ in sorted_agents[:3]]
    
    def _find_collaborators(self, task_details: Dict) -> List[str]:
        """Find agents that should collaborate on this task"""
        task_text = (task_details.get('title', '') + ' ' + task_details.get('description', '')).lower()
        collaborators = []
        
        for pattern, agents in self.coordination_rules['collaboration_required'].items():
            if pattern.replace('_', ' ') in task_text:
                collaborators.extend(agents)
        
        return list(set(collaborators))  # Remove duplicates
    
    def _handle_task_handoff(self, parameters: Dict) -> Dict:
        """Handle task handoffs between agents"""
        from_agent = parameters.get('from_agent', '')
        to_agent = parameters.get('to_agent', '')
        task_id = parameters.get('task_id', '')
        
        # Check if handoff is allowed
        allowed_handoffs = self.coordination_rules['handoff_patterns'].get(from_agent, [])
        
        if to_agent not in allowed_handoffs:
            # Check if it's a valid reverse handoff (reporting back)
            if self.coordination_rules['reporting_chain'].get(from_agent) == to_agent:
                # This is a report back, allow it
                pass
            else:
                self._log_event("invalid_handoff", {
                    "from": from_agent,
                    "to": to_agent,
                    "allowed": allowed_handoffs
                })
                return {
                    "action": "warn",
                    "message": f"⚠️ {from_agent} cannot hand off to {to_agent}. Allowed: {', '.join(allowed_handoffs)}"
                }
        
        # Create handoff message
        handoff_message = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "subject": f"Task Handoff: {task_id}",
            "content": parameters.get('context', {}).get('message', f"Taking over task {task_id} from {from_agent}"),
            "type": "handoff",
            "priority": "high",
            "task_id": task_id,
            "artifacts": parameters.get('artifacts', [])
        }
        
        self._store_delegation_message(handoff_message)
        
        # Trigger the receiving agent
        self._trigger_agent_work(to_agent, task_id, {
            'handoff_from': from_agent,
            'context': parameters.get('context', {})
        })
        
        self._log_event("handoff_executed", {
            "from": from_agent,
            "to": to_agent,
            "task_id": task_id
        })
        
        return {
            "action": "allow",
            "message": f"✅ Handed off task {task_id} from {from_agent} to {to_agent}"
        }
    
    def detect_explicit_agent(self, text: str) -> Optional[str]:
        """Detect if user explicitly mentioned an agent"""
        if not text:
            return None
        text_lower = text.lower()
        
        # Check for explicit agent mentions
        for agent_name in AGENT_NAMES:
            # Check various formats: "use qa-engineer", "qa engineer", "QA engineer"
            agent_variations = [
                agent_name,
                agent_name.replace('-', ' '),
                agent_name.replace('-', '_'),
            ]
            
            for variation in agent_variations:
                if variation in text_lower:
                    self._log_event("explicit_agent_detected", {
                        "agent": agent_name,
                        "user_input": text
                    })
                    return agent_name
        
        return None
    
    def trigger_explicit_agent(self, agent_name: str, user_input: str) -> Dict:
        """Trigger an explicitly mentioned agent"""
        # Create task for the explicitly mentioned agent
        task_data = {
            "title": f"Task for {agent_name}",
            "description": f"User request: {user_input}",
            "created_by": "orchestrator",
            "priority": "high",
            "explicit_request": True
        }
        
        # Store task for scrum-master
        tasks_file = self.project_root / 'mcp' / 'data' / 'communication' / 'tasks.json'
        tasks_file.parent.mkdir(parents=True, exist_ok=True)
        
        tasks = {}
        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        
        task_id = f"task_{agent_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        tasks[task_id] = {
            **task_data,
            "id": task_id,
            "status": "pending",
            "assigned_to": agent_name,
            "created_at": datetime.now().isoformat()
        }
        
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        # Trigger the explicitly mentioned agent
        self._trigger_agent_work(agent_name, task_id, {
            "explicit_request": True,
            "user_input": user_input
        })
        
        self._log_event("explicit_agent_triggered", {
            "agent": agent_name,
            "user_input": user_input,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create instruction to trigger the explicitly mentioned agent
        additional_context = f"""

🎯 **AGENT EXPLICITLY REQUESTED: {agent_name}**

The user has explicitly requested the {agent_name} agent.

**YOU MUST NOW:**
1. Immediately use the Task tool
2. Set subagent_type to '{agent_name}'
3. Pass this exact prompt to the {agent_name}:

```
User request: {user_input}

You have been explicitly requested to handle this task.
Working Directory: {os.getcwd()}
DO NOT create project subfolders unless specifically requested.
```

**Let the {agent_name} handle this task as requested by the user.**

Task ID: {task_id}
Working Directory: {os.getcwd()}"""
        
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit", 
                "additionalContext": additional_context
            }
        }
    
    def process_hook(self, hook_type: str, input_data: Dict) -> Dict:
        """Main hook processing logic - SIMPLIFIED"""
        response = {}
        
        try:
            # Handle user prompt submission - only trigger if agent explicitly mentioned
            if hook_type == "UserPromptSubmit" or hook_type == "user-prompt-submit":
                user_input = input_data.get('prompt', '')
                
                # Check if user explicitly mentioned an agent
                explicit_agent = self.detect_explicit_agent(user_input)
                
                if explicit_agent:
                    # User explicitly mentioned an agent, trigger it
                    return self.trigger_explicit_agent(explicit_agent, user_input)
                
                # No explicit agent mentioned, let Claude handle normally
                self._log_event("no_explicit_agent", {
                    "user_input": user_input,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif hook_type == "pre-tool-use":
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
        # Read hook input from stdin (Claude Code passes input via stdin)
        import sys
        stdin_input = sys.stdin.read()
        
        # Parse the input
        if stdin_input:
            hook_input = json.loads(stdin_input)
        else:
            # Fallback to environment variable for testing
            hook_input = json.loads(os.environ.get('CLAUDE_HOOK_INPUT', '{}'))
        
        # Determine hook type from input
        hook_type = hook_input.get('hook_event_name', 'UserPromptSubmit')
        
        # Debug logging
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n--- {datetime.now().isoformat()} ---\n")
            f.write(f"Hook Type: {hook_type}\n")
            f.write(f"Hook Input: {json.dumps(hook_input)}\n")
            f.write(f"Stdin received: {len(stdin_input)} bytes\n")
        
        # Initialize orchestrator
        orchestrator = AgentArmyOrchestrator()
        
        # Process the hook
        response = orchestrator.process_hook(hook_type, hook_input)
        
        # Debug log the response
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"Response: {json.dumps(response)}\n")
        
        # Output response
        print(json.dumps(response))
        
    except Exception as e:
        # Log errors
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"ERROR: {str(e)}\n")
        
        # Always allow on error to prevent blocking
        error_response = {
            "action": "allow",
            "error": str(e)
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()