#!/usr/bin/env python3
"""
Agent Consistency Enforcer
Ensures agents follow proper responsibility areas and provide consistent outputs
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

class AgentConsistencyEnforcer:
    """Enforces agent responsibility boundaries and output consistency"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.claude_dir = self.project_root / '.claude'
        self.agents_dir = self.claude_dir / 'agents'
        
        # Load agent specifications
        self.agent_specs = self._load_agent_specifications()
        
        # Define responsibility boundaries
        self.responsibility_matrix = self._build_responsibility_matrix()
        
        # Output standards
        self.output_standards = self._define_output_standards()
    
    def _load_agent_specifications(self) -> Dict[str, Dict]:
        """Load agent specifications from registry"""
        try:
            registry_file = self.agents_dir / 'agent-registry.json'
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                return registry.get('hierarchy', {})
            return {}
        except Exception:
            return {}
    
    def _build_responsibility_matrix(self) -> Dict[str, Dict]:
        """Build responsibility matrix defining what each agent can/cannot do"""
        return {
            'scrum-master': {
                'primary_responsibilities': [
                    'sprint_planning', 'backlog_management', 'ceremony_facilitation',
                    'stakeholder_communication', 'project_timeline_management'
                ],
                'can_create': ['tasks', 'workflows', 'sprint_plans'],
                'can_assign': ['tasks_to_tech_lead', 'ceremonies'],
                'cannot_do': ['technical_implementation', 'code_review', 'deployment'],
                'coordinates_with': ['tech-lead', 'requirements-analyst', 'system-architect']
            },
            'tech-lead': {
                'primary_responsibilities': [
                    'technical_direction', 'task_assignment', 'code_quality',
                    'architecture_implementation', 'developer_coordination'
                ],
                'can_create': ['technical_tasks', 'implementation_plans'],
                'can_assign': ['development_tasks', 'code_reviews'],
                'cannot_do': ['sprint_planning', 'stakeholder_communication'],
                'coordinates_with': ['senior-backend-engineer', 'senior-frontend-engineer', 'qa-engineer']
            },
            'senior-frontend-engineer': {
                'primary_responsibilities': [
                    'ui_implementation', 'frontend_architecture', 'user_experience',
                    'responsive_design', 'frontend_testing'
                ],
                'can_create': ['components', 'pages', 'styles'],
                'can_assign': ['frontend_subtasks'],
                'cannot_do': ['backend_apis', 'database_design', 'deployment_config'],
                'coordinates_with': ['senior-backend-engineer', 'qa-engineer', 'tech-lead']
            },
            'senior-backend-engineer': {
                'primary_responsibilities': [
                    'api_development', 'database_design', 'server_logic',
                    'data_modeling', 'backend_testing'
                ],
                'can_create': ['apis', 'database_schemas', 'services'],
                'can_assign': ['backend_subtasks'],
                'cannot_do': ['ui_design', 'frontend_components', 'deployment_config'],
                'coordinates_with': ['senior-frontend-engineer', 'qa-engineer', 'tech-lead']
            },
            'qa-engineer': {
                'primary_responsibilities': [
                    'test_planning', 'test_execution', 'quality_assurance',
                    'bug_tracking', 'acceptance_testing'
                ],
                'can_create': ['test_plans', 'test_cases', 'bug_reports'],
                'can_assign': ['testing_tasks'],
                'cannot_do': ['feature_implementation', 'deployment'],
                'coordinates_with': ['tech-lead', 'senior-backend-engineer', 'senior-frontend-engineer']
            }
        }
    
    def _define_output_standards(self) -> Dict[str, Dict]:
        """Define output format standards for each agent type"""
        return {
            'task_creation': {
                'required_fields': ['title', 'description', 'acceptance_criteria', 'priority'],
                'format': 'structured',
                'must_include': ['clear_objectives', 'success_metrics']
            },
            'status_updates': {
                'required_fields': ['task_id', 'status', 'progress', 'next_steps'],
                'format': 'structured',
                'must_include': ['blockers_if_any', 'timeline_estimate']
            },
            'handoffs': {
                'required_fields': ['from_agent', 'to_agent', 'task_context', 'expectations'],
                'format': 'structured',
                'must_include': ['deliverables', 'success_criteria']
            },
            'communications': {
                'tone': 'professional',
                'structure': 'clear_and_concise',
                'must_include': ['action_items', 'next_steps']
            }
        }
    
    def validate_agent_action(self, agent_name: str, action: str, context: Dict) -> Dict:
        """Validate if an agent action is within their responsibility boundaries"""
        if agent_name not in self.responsibility_matrix:
            return {
                'valid': False,
                'reason': f'Unknown agent: {agent_name}',
                'suggestion': 'Check agent registry'
            }
        
        agent_spec = self.responsibility_matrix[agent_name]
        
        # Check if action is within primary responsibilities
        primary_responsibilities = agent_spec.get('primary_responsibilities', [])
        cannot_do = agent_spec.get('cannot_do', [])
        
        # Simple action validation (can be extended)
        if any(forbidden in action.lower() for forbidden in cannot_do):
            suggested_agents = self._suggest_appropriate_agent(action)
            return {
                'valid': False,
                'reason': f'{agent_name} cannot perform: {action}',
                'suggestion': f'This should be handled by: {suggested_agents}',
                'redirect_to': suggested_agents[0] if suggested_agents else None
            }
        
        return {
            'valid': True,
            'reason': 'Action within agent responsibilities'
        }
    
    def _suggest_appropriate_agent(self, action: str) -> List[str]:
        """Suggest appropriate agents for a given action"""
        action_lower = action.lower()
        suggestions = []
        
        # Simple keyword matching (can be improved with ML)
        if any(word in action_lower for word in ['frontend', 'ui', 'component', 'design']):
            suggestions.append('senior-frontend-engineer')
        elif any(word in action_lower for word in ['backend', 'api', 'database', 'server']):
            suggestions.append('senior-backend-engineer')
        elif any(word in action_lower for word in ['test', 'quality', 'bug', 'validation']):
            suggestions.append('qa-engineer')
        elif any(word in action_lower for word in ['deploy', 'ci', 'cd', 'infrastructure']):
            suggestions.append('devops-engineer')
        elif any(word in action_lower for word in ['sprint', 'project', 'ceremony', 'stakeholder']):
            suggestions.append('scrum-master')
        elif any(word in action_lower for word in ['technical', 'architecture', 'coordinate']):
            suggestions.append('tech-lead')
        
        return suggestions
    
    def enforce_output_consistency(self, agent_name: str, output_type: str, content: Dict) -> Dict:
        """Enforce output consistency standards"""
        if output_type not in self.output_standards:
            return {
                'valid': True,
                'reason': 'No standards defined for this output type'
            }
        
        standards = self.output_standards[output_type]
        issues = []
        
        # Check required fields
        required_fields = standards.get('required_fields', [])
        for field in required_fields:
            if field not in content:
                issues.append(f'Missing required field: {field}')
        
        # Check must_include items
        must_include = standards.get('must_include', [])
        content_str = json.dumps(content).lower()
        for item in must_include:
            if item.replace('_', ' ') not in content_str:
                issues.append(f'Must include: {item}')
        
        if issues:
            return {
                'valid': False,
                'issues': issues,
                'suggestion': 'Please address the missing requirements'
            }
        
        return {
            'valid': True,
            'reason': 'Output meets consistency standards'
        }
    
    def suggest_coordination_improvements(self, agent_name: str, task_context: Dict) -> List[str]:
        """Suggest coordination improvements based on task context"""
        suggestions = []
        
        if agent_name not in self.responsibility_matrix:
            return suggestions
        
        agent_spec = self.responsibility_matrix[agent_name]
        coordinates_with = agent_spec.get('coordinates_with', [])
        
        # Check if coordination is needed
        task_type = task_context.get('type', '')
        task_description = task_context.get('description', '').lower()
        
        # Suggest coordination based on task complexity
        if any(keyword in task_description for keyword in ['frontend', 'backend', 'fullstack']):
            if 'senior-frontend-engineer' in coordinates_with and 'senior-backend-engineer' in coordinates_with:
                suggestions.append('Consider coordinating with both frontend and backend engineers')
        
        if 'testing' in task_description or 'quality' in task_description:
            if 'qa-engineer' in coordinates_with:
                suggestions.append('Include QA engineer for testing strategy')
        
        if agent_name == 'tech-lead' and task_context.get('priority') == 'critical':
            suggestions.append('Consider parallel development with multiple engineers')
        
        return suggestions
    
    def generate_consistency_report(self) -> Dict:
        """Generate a report on agent consistency"""
        return {
            'timestamp': datetime.now().isoformat(),
            'agents_monitored': list(self.responsibility_matrix.keys()),
            'responsibility_boundaries': self.responsibility_matrix,
            'output_standards': self.output_standards,
            'status': 'active'
        }

def main():
    """CLI interface for consistency enforcer"""
    enforcer = AgentConsistencyEnforcer()
    report = enforcer.generate_consistency_report()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()