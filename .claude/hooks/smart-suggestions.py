#!/usr/bin/env python3
"""
Smart Suggestions Hook
Provides intelligent suggestions based on context
"""

import json
import os
import re
from typing import List, Dict, Optional

class SmartSuggestions:
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load suggestion patterns"""
        return {
            "task_patterns": [
                (r'\b(implement|create|build|develop|add|fix|update|refactor)\b.*\b(feature|function|component|module|system)\b', 
                 "📝 This looks like a development task. Consider:\n1. Use TodoWrite to track it\n2. Start with requirements-analyst\n3. Follow the development workflow"),
                
                (r'\b(bug|issue|error|problem|broken|failing)\b',
                 "🐛 This looks like a bug. Consider:\n1. Create an escalation if critical\n2. Assign to engineering-manager for triage\n3. Track with TodoWrite"),
                
                (r'\b(deploy|release|rollout|launch)\b',
                 "🚀 This looks like deployment. Consider:\n1. Ensure QA has completed testing\n2. Create checkpoint before deployment\n3. Coordinate with devops-engineer")
            ],
            
            "coordination_patterns": [
                (r'\b(coordinate|sync|align|collaborate)\b',
                 "🤝 For coordination, use:\n- message_send for direct communication\n- task_handoff for work transfer\n- workflow_start for multi-step processes"),
                
                (r'\b(assign|delegate|distribute)\b',
                 "📋 For task assignment:\n- Only scrum-master and engineering-manager can assign\n- Use task_assign with clear specifications\n- Check agent_workload first"),
                
                (r'\b(escalate|urgent|critical|blocker)\b',
                 "⚠️ For escalations:\n- Use escalation_create\n- Specify severity level\n- Include detailed reason")
            ],
            
            "workflow_patterns": [
                (r'\b(workflow|process|pipeline|flow)\b',
                 "🔄 For workflows:\n- Use workflow_start to begin\n- Create checkpoints at key stages\n- Track with workflow_status"),
                
                (r'\b(handoff|transfer|pass|continue)\b',
                 "➡️ For handoffs:\n- Use task_handoff\n- Include context and artifacts\n- Follow standard handoff chains"),
                
                (r'\b(checkpoint|milestone|save|backup)\b',
                 "💾 For checkpoints:\n- Use checkpoint_create\n- Name descriptively\n- Include current state")
            ]
        }
    
    def analyze_prompt(self, prompt: str) -> List[Dict]:
        """Analyze prompt and generate suggestions"""
        suggestions = []
        prompt_lower = prompt.lower()
        
        # Check task patterns
        for pattern, suggestion in self.patterns["task_patterns"]:
            if re.search(pattern, prompt_lower):
                suggestions.append({
                    "type": "task",
                    "confidence": "high",
                    "suggestion": suggestion
                })
                break
        
        # Check coordination patterns
        for pattern, suggestion in self.patterns["coordination_patterns"]:
            if re.search(pattern, prompt_lower):
                suggestions.append({
                    "type": "coordination",
                    "confidence": "high",
                    "suggestion": suggestion
                })
                break
        
        # Check workflow patterns
        for pattern, suggestion in self.patterns["workflow_patterns"]:
            if re.search(pattern, prompt_lower):
                suggestions.append({
                    "type": "workflow",
                    "confidence": "high",
                    "suggestion": suggestion
                })
                break
        
        # Check for agent mentions
        agents = self._extract_agents(prompt_lower)
        if agents:
            suggestions.append({
                "type": "agent",
                "confidence": "medium",
                "suggestion": f"🤖 Agents mentioned: {', '.join(agents)}\n" +
                            "Remember to specify 'as <agent>' for context"
            })
        
        # Check for missing TodoWrite
        if re.search(r'\b(task|feature|bug|implement|create)\b', prompt_lower):
            if 'todowrite' not in prompt_lower and 'todo' not in prompt_lower:
                suggestions.append({
                    "type": "todo",
                    "confidence": "high",
                    "suggestion": "💡 Remember to use TodoWrite to track this task!"
                })
        
        return suggestions
    
    def _extract_agents(self, text: str) -> List[str]:
        """Extract agent names from text"""
        agent_names = [
            'scrum-master', 'system-architect', 'engineering-manager', 
            'requirements-analyst', 'senior-backend-engineer',
            'data-engineer', 'qa-engineer', 'security-engineer',
            'technical-writer'
        ]
        
        found = []
        for agent in agent_names:
            if agent in text:
                found.append(agent)
        
        return found
    
    def suggest_next_action(self, current_context: Dict) -> Optional[str]:
        """Suggest next action based on current context"""
        tool = current_context.get('tool', {}).get('name', '')
        
        suggestions_map = {
            'mcp__communication__task_create': 
                "Next: Use task_assign to assign the created task",
            
            'mcp__communication__task_assign':
                "Next: Monitor progress with task_status",
            
            'mcp__communication__task_handoff':
                "Next: New agent should update task_status",
            
            'mcp__communication__workflow_start':
                "Next: Create tasks with task_create",
            
            'mcp__communication__escalation_create':
                "Next: Scrum-master or engineering-manager should respond",
            
            'mcp__communication__checkpoint_create':
                "Next: Safe to proceed with next phase"
        }
        
        return suggestions_map.get(tool)

def main():
    """Main hook entry point"""
    try:
        hook_input = json.loads(os.environ.get('CLAUDE_HOOK_INPUT', '{}'))
        hook_type = os.environ.get('CLAUDE_HOOK_TYPE', 'unknown')
        
        suggester = SmartSuggestions()
        
        if hook_type == 'user-prompt-submit':
            # Analyze user prompt
            prompt = hook_input.get('prompt', '')
            suggestions = suggester.analyze_prompt(prompt)
            
            if suggestions:
                # Format suggestions
                messages = []
                for s in suggestions[:2]:  # Show top 2 suggestions
                    messages.append(s['suggestion'])
                
                response = {
                    "action": "allow",
                    "message": "\n\n".join(messages),
                    "metadata": {
                        "suggestions": suggestions
                    }
                }
            else:
                response = {"action": "allow"}
        
        elif hook_type == 'agent-prompt-submit':
            # Suggest next action
            next_action = suggester.suggest_next_action(hook_input)
            
            if next_action:
                response = {
                    "action": "allow",
                    "metadata": {
                        "next_action": next_action
                    }
                }
            else:
                response = {"action": "allow"}
        
        else:
            response = {"action": "allow"}
        
        print(json.dumps(response))
        
    except Exception as e:
        print(json.dumps({"action": "allow", "error": str(e)}))

if __name__ == "__main__":
    main()