#!/usr/bin/env python3
"""
Agent Boundary Validator
Prevents role boundary violations and enforces proper agent responsibilities
"""

import json
import re
from typing import Dict, List, Tuple, Optional

# Define what each agent CANNOT do
BOUNDARY_RULES = {
    "scrum-master": {
        "forbidden_actions": [
            "writing code",
            "implementing features",
            "creating database schemas",
            "designing APIs",
            "fixing bugs",
            "deploying applications"
        ],
        "forbidden_patterns": [
            r"def\s+\w+\s*\(",  # Python functions
            r"function\s+\w+\s*\(",  # JavaScript functions
            r"CREATE\s+TABLE",  # SQL
            r"app\.get\(",  # Express routes
            r"<[A-Z][\w]*.*>",  # React components
            r"git\s+push",  # Git deployment
        ],
        "must_delegate_to": {
            "code_writing": "tech-lead",
            "requirements": "requirements-analyst",
            "architecture": "system-architect"
        }
    },
    "requirements-analyst": {
        "forbidden_actions": [
            "system architecture design",
            "database schema creation",
            "API specification",
            "code implementation",
            "deployment configuration",
            "performance optimization"
        ],
        "forbidden_patterns": [
            r"class\s+\w+Model",  # Database models
            r"router\.\w+\(",  # API routes
            r"SELECT\s+.*\s+FROM",  # SQL queries
            r"docker",  # Docker commands
            r"kubectl",  # Kubernetes
        ],
        "must_delegate_to": {
            "technical_design": "system-architect",
            "implementation": "tech-lead"
        }
    },
    "tech-lead": {
        "forbidden_actions": [
            "business requirements gathering",
            "sprint planning",
            "stakeholder communication",
            "deployment to production"
        ],
        "forbidden_patterns": [
            r"As\s+a\s+user",  # User stories
            r"sprint\s+goal",  # Sprint planning
            r"kubectl\s+apply.*prod",  # Production deployment
        ],
        "must_delegate_to": {
            "requirements": "requirements-analyst",
            "sprint_planning": "scrum-master",
            "deployment": "devops-engineer"
        }
    },
    "senior-frontend-engineer": {
        "forbidden_actions": [
            "database design",
            "backend API implementation",
            "infrastructure setup",
            "production deployment"
        ],
        "forbidden_patterns": [
            r"CREATE\s+DATABASE",  # Database creation
            r"app\.listen\(",  # Server setup
            r"docker-compose",  # Infrastructure
            r"terraform",  # Infrastructure as code
        ],
        "must_delegate_to": {
            "backend_work": "senior-backend-engineer",
            "deployment": "devops-engineer"
        }
    },
    "senior-backend-engineer": {
        "forbidden_actions": [
            "UI component design",
            "frontend styling",
            "UX decisions",
            "production deployment"
        ],
        "forbidden_patterns": [
            r"<div.*className",  # React/JSX
            r"\.css\s*{",  # CSS
            r"useState\(",  # React hooks
            r"kubectl.*production",  # Production deployment
        ],
        "must_delegate_to": {
            "frontend_work": "senior-frontend-engineer",
            "deployment": "devops-engineer"
        }
    },
    "qa-engineer": {
        "forbidden_actions": [
            "fixing bugs in code",
            "implementing features",
            "deploying to production",
            "modifying architecture"
        ],
        "forbidden_patterns": [
            r"git\s+commit.*fix",  # Fixing code
            r"function\s+implement",  # Implementation
            r"helm\s+upgrade.*prod",  # Production deployment
        ],
        "must_delegate_to": {
            "bug_fixes": "tech-lead",
            "deployment": "devops-engineer"
        }
    }
}

class BoundaryValidator:
    """Validates agent actions against role boundaries"""
    
    def __init__(self):
        self.violations_log = []
    
    def validate_action(self, agent: str, action: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if an agent's action is within their boundaries
        Returns: (is_valid, error_message)
        """
        if agent not in BOUNDARY_RULES:
            return True, None  # No rules defined, allow
        
        rules = BOUNDARY_RULES[agent]
        
        # Check forbidden patterns in content
        for pattern in rules.get("forbidden_patterns", []):
            if re.search(pattern, content, re.IGNORECASE):
                violation = f"Agent '{agent}' attempted forbidden action: pattern '{pattern}' detected"
                self.log_violation(agent, action, violation)
                return False, self.suggest_delegation(agent, action)
        
        # Check forbidden actions
        action_lower = action.lower()
        for forbidden in rules.get("forbidden_actions", []):
            if forbidden.lower() in action_lower:
                violation = f"Agent '{agent}' attempted forbidden action: '{forbidden}'"
                self.log_violation(agent, action, violation)
                return False, self.suggest_delegation(agent, action)
        
        return True, None
    
    def suggest_delegation(self, agent: str, action: str) -> str:
        """Suggest who should handle this action instead"""
        rules = BOUNDARY_RULES.get(agent, {})
        delegations = rules.get("must_delegate_to", {})
        
        # Find best match for delegation
        for key, delegate in delegations.items():
            if key in action.lower():
                return f"This action should be delegated to '{delegate}'. Agent '{agent}' is not authorized for: {action}"
        
        return f"Agent '{agent}' is not authorized for this action: {action}"
    
    def log_violation(self, agent: str, action: str, violation: str):
        """Log boundary violations for monitoring"""
        self.violations_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "violation": violation
        })
    
    def validate_handoff(self, from_agent: str, to_agent: str, task: str) -> Tuple[bool, Optional[str]]:
        """Validate if a handoff is allowed"""
        # Define valid handoff patterns
        VALID_HANDOFFS = {
            "scrum-master": ["requirements-analyst", "system-architect", "tech-lead"],
            "requirements-analyst": ["system-architect", "scrum-master"],
            "system-architect": ["tech-lead", "scrum-master"],
            "tech-lead": ["senior-frontend-engineer", "senior-backend-engineer", "qa-engineer"],
            "senior-frontend-engineer": ["qa-engineer", "tech-lead"],
            "senior-backend-engineer": ["qa-engineer", "tech-lead"],
            "qa-engineer": ["devops-engineer", "tech-lead"],
            "devops-engineer": ["sre-engineer", "scrum-master"],
        }
        
        valid_targets = VALID_HANDOFFS.get(from_agent, [])
        
        if to_agent not in valid_targets:
            return False, f"Invalid handoff: '{from_agent}' cannot hand off to '{to_agent}'. Valid targets: {valid_targets}"
        
        return True, None
    
    def enforce_phase_requirements(self, current_phase: str, requested_action: str) -> Tuple[bool, Optional[str]]:
        """Ensure actions are appropriate for current project phase"""
        PHASE_REQUIREMENTS = {
            "inception": {
                "allowed": ["requirements_gathering", "user_stories", "scope_definition"],
                "forbidden": ["coding", "deployment", "testing"]
            },
            "architecture": {
                "allowed": ["system_design", "api_design", "database_design"],
                "forbidden": ["implementation", "deployment"]
            },
            "execution": {
                "allowed": ["coding", "testing", "code_review"],
                "forbidden": ["requirements_change", "architecture_change"]
            },
            "deployment": {
                "allowed": ["deploy", "monitor", "rollback"],
                "forbidden": ["new_features", "architecture_change"]
            }
        }
        
        phase_rules = PHASE_REQUIREMENTS.get(current_phase, {})
        
        # Check if action is forbidden in current phase
        for forbidden in phase_rules.get("forbidden", []):
            if forbidden in requested_action.lower():
                return False, f"Action '{requested_action}' is not allowed in {current_phase} phase"
        
        return True, None

# Hook integration
def validate_agent_action(agent: str, action: str, content: str = "") -> Dict:
    """Main validation function for hook integration"""
    validator = BoundaryValidator()
    
    # Validate action boundaries
    is_valid, error = validator.validate_action(agent, action, content)
    
    if not is_valid:
        return {
            "action": "block",
            "message": error,
            "suggestion": "Please delegate this task to the appropriate agent"
        }
    
    return {"action": "allow"}

def validate_handoff(from_agent: str, to_agent: str, task: str) -> Dict:
    """Validate agent handoffs"""
    validator = BoundaryValidator()
    
    is_valid, error = validator.validate_handoff(from_agent, to_agent, task)
    
    if not is_valid:
        return {
            "action": "block",
            "message": error,
            "suggestion": "Please follow the correct handoff chain"
        }
    
    return {"action": "allow"}

if __name__ == "__main__":
    # Test validation
    validator = BoundaryValidator()
    
    # Test cases
    tests = [
        ("scrum-master", "write code", "def hello_world():"),
        ("requirements-analyst", "create database", "CREATE TABLE users"),
        ("tech-lead", "coordinate development", "assign tasks to team"),
        ("qa-engineer", "test feature", "run test suite"),
    ]
    
    for agent, action, content in tests:
        is_valid, error = validator.validate_action(agent, action, content)
        print(f"{agent} - {action}: {'✅ Valid' if is_valid else f'❌ {error}'}")
    
    # Test handoffs
    handoffs = [
        ("scrum-master", "tech-lead"),
        ("scrum-master", "qa-engineer"),  # Invalid
        ("tech-lead", "senior-frontend-engineer"),
    ]
    
    for from_agent, to_agent in handoffs:
        is_valid, error = validator.validate_handoff(from_agent, to_agent, "task")
        print(f"{from_agent} → {to_agent}: {'✅ Valid' if is_valid else f'❌ {error}'}")