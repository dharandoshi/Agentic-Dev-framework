#!/usr/bin/env python3
"""
Agent Army Hook Orchestrator
Central hook system for coordinating all agent communications
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add integration with new monitoring system
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
try:
    from monitoring_system import AgentArmyMonitor, MonitoringEvent, EventType, AlertSeverity
    monitor = AgentArmyMonitor()
except ImportError:
    monitor = None

class AgentArmyOrchestrator:
    """Main orchestrator for agent army hooks"""
    
    def __init__(self):
        self.project_root = Path(os.environ.get('CLAUDE_PROJECT_ROOT', '.'))
        self.logs_dir = self.project_root / '.claude' / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load agent hierarchy and rules
        self.hierarchy = self._load_hierarchy()
        self.current_context = self._detect_context()
        
    def _load_hierarchy(self) -> Dict:
        """Load agent hierarchy and coordination rules"""
        return {
            "levels": {
                1: ["scrum-master"],
                2: ["system-architect", "tech-lead"],
                3: ["requirements-analyst", "senior-backend-engineer", 
                    "senior-frontend-engineer", "integration-engineer", "data-engineer"],
                4: ["qa-engineer", "security-engineer", "devops-engineer", 
                    "sre-engineer", "cloud-architect"],
                5: ["technical-writer"]
            },
            "permissions": {
                "task_create": ["scrum-master"],
                "task_assign": ["scrum-master", "tech-lead"],
                "workflow_start": ["scrum-master"],
                "workflow_status": ["scrum-master", "tech-lead"],
                "message_broadcast": ["scrum-master"],
                "agent_workload": ["scrum-master", "tech-lead"],
                "escalation_create": [
                    "tech-lead", "senior-backend-engineer", "senior-frontend-engineer",
                    "qa-engineer", "security-engineer", "sre-engineer"
                ],
                "checkpoint_create": [
                    "system-architect", "requirements-analyst", 
                    "senior-backend-engineer", "senior-frontend-engineer",
                    "devops-engineer"
                ]
            },
            "handoff_chains": [
                ["requirements-analyst", "system-architect"],
                ["system-architect", "tech-lead"],
                ["tech-lead", "senior-backend-engineer"],
                ["tech-lead", "senior-frontend-engineer"],
                ["senior-backend-engineer", "qa-engineer"],
                ["senior-frontend-engineer", "qa-engineer"],
                ["qa-engineer", "devops-engineer"],
                ["devops-engineer", "sre-engineer"]
            ]
        }
    
    def _detect_context(self) -> Dict:
        """Detect current session context"""
        return {
            "session_id": os.environ.get('CLAUDE_SESSION_ID', 'unknown'),
            "timestamp": datetime.now().isoformat(),
            "current_file": os.environ.get('CLAUDE_CURRENT_FILE', None),
            "hook_type": os.environ.get('CLAUDE_HOOK_TYPE', 'unknown')
        }
    
    def _extract_agent_context(self, input_data: Dict) -> Optional[str]:
        """Extract which agent is being simulated from the input"""
        prompt = input_data.get('prompt', '')
        tool_params = input_data.get('tool', {}).get('parameters', {})
        
        # Check tool parameters for agent names
        if 'from_agent' in tool_params:
            return tool_params['from_agent']
        if 'agent' in tool_params:
            return tool_params['agent']
        
        # Search in prompt for agent context
        agent_pattern = r'\b(scrum-master|system-architect|tech-lead|requirements-analyst|senior-backend-engineer|senior-frontend-engineer|integration-engineer|data-engineer|qa-engineer|security-engineer|devops-engineer|sre-engineer|cloud-architect|technical-writer)\b'
        
        # Look for "as <agent>" pattern
        as_pattern = r'as\s+(' + '|'.join([
            'scrum-master', 'system-architect', 'tech-lead', 'requirements-analyst',
            'senior-backend-engineer', 'senior-frontend-engineer', 'integration-engineer',
            'data-engineer', 'qa-engineer', 'security-engineer', 'devops-engineer',
            'sre-engineer', 'cloud-architect', 'technical-writer'
        ]) + r')'
        
        as_match = re.search(as_pattern, prompt.lower())
        if as_match:
            return as_match.group(1)
        
        # General agent mention
        matches = re.findall(agent_pattern, prompt.lower())
        return matches[0] if matches else None
    
    def _log_event(self, event_type: str, data: Dict):
        """Log events to file"""
        log_file = self.logs_dir / f"orchestrator-{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        log_entry = {
            **self.current_context,
            "event_type": event_type,
            "data": data
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def validate_communication_tool(self, tool_name: str, parameters: Dict, 
                                   current_agent: Optional[str] = None) -> Dict:
        """Validate communication tool usage"""
        if not tool_name.startswith('mcp__communication__'):
            return {"action": "allow"}
        
        action = tool_name.replace('mcp__communication__', '')
        
        # Log the communication attempt
        self._log_event("communication_attempt", {
            "tool": action,
            "parameters": parameters,
            "agent": current_agent
        })
        
        # Check permissions
        if action in self.hierarchy["permissions"]:
            allowed_agents = self.hierarchy["permissions"][action]
            
            if current_agent and current_agent not in allowed_agents:
                return {
                    "action": "block",
                    "message": f"❌ {current_agent} cannot use {action}. Only {', '.join(allowed_agents)} are authorized.",
                    "suggestion": "Use an authorized agent or escalate through proper channels."
                }
        
        # Validate handoff chains
        if action == "task_handoff":
            from_agent = parameters.get('from_agent')
            to_agent = parameters.get('to_agent')
            
            if from_agent and to_agent:
                valid_handoff = any(
                    chain[0] == from_agent and chain[1] == to_agent
                    for chain in self.hierarchy["handoff_chains"]
                )
                
                if not valid_handoff:
                    return {
                        "action": "warn",
                        "message": f"⚠️ Unusual handoff: {from_agent} → {to_agent}. This is not in the standard chain.",
                        "metadata": {"standard_chains": self.hierarchy["handoff_chains"]}
                    }
        
        return {"action": "allow"}
    
    def suggest_coordination(self, prompt: str) -> Optional[Dict]:
        """Suggest coordination improvements based on prompt"""
        suggestions = []
        
        # Check for task mentions
        if re.search(r'\b(task|feature|bug|issue|implement|create|build)\b', prompt.lower()):
            if 'todowrite' not in prompt.lower():
                suggestions.append({
                    "type": "todo",
                    "message": "💡 Consider using TodoWrite to track this task"
                })
        
        # Check for coordination keywords
        if re.search(r'\b(coordinate|handoff|assign|delegate|escalate)\b', prompt.lower()):
            suggestions.append({
                "type": "coordination",
                "message": "🔄 Use Communication MCP tools for proper coordination"
            })
        
        # Check for status updates
        if re.search(r'\b(status|progress|update|report)\b', prompt.lower()):
            suggestions.append({
                "type": "status",
                "message": "📊 Use task_status to report progress"
            })
        
        return suggestions if suggestions else None
    
    def process_hook(self, hook_type: str, input_data: Dict) -> Dict:
        """Main hook processing logic"""
        response = {"action": "allow"}
        
        if hook_type == "user-prompt-submit":
            # Process user prompt
            prompt = input_data.get('prompt', '')
            
            # Add suggestions
            suggestions = self.suggest_coordination(prompt)
            if suggestions:
                response["metadata"] = {"suggestions": suggestions}
                response["message"] = suggestions[0]["message"]
        
        elif hook_type == "agent-prompt-submit":
            # Process tool usage
            tool = input_data.get('tool', {})
            tool_name = tool.get('name', '')
            parameters = tool.get('parameters', {})
            
            # Detect current agent
            current_agent = self._extract_agent_context(input_data)
            
            # Validate communication tools
            validation = self.validate_communication_tool(tool_name, parameters, current_agent)
            response.update(validation)
        
        elif hook_type == "tool-result":
            # Process tool results
            tool_name = input_data.get('tool', {}).get('name', '')
            result = input_data.get('result', {})
            
            # Log successful communications
            if tool_name.startswith('mcp__communication__'):
                self._log_event("communication_success", {
                    "tool": tool_name.replace('mcp__communication__', ''),
                    "result_summary": str(result)[:200] if result else None
                })
        
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