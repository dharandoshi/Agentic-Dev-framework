#!/usr/bin/env python3
"""
Quick script to add boundaries to remaining agent files
"""

import os

agent_boundaries = {
    "data-engineer": {
        "can": [
            "Design data pipelines and ETL processes",
            "Set up data warehouses and lakes",
            "Implement real-time streaming (Kafka, Spark)",
            "Create data models and schemas",
            "Build data integration workflows",
            "Optimize data processing performance",
            "Implement data quality checks",
            "Set up analytics infrastructure"
        ],
        "cannot": [
            "Build application features",
            "Create UI components",
            "Make project management decisions",
            "Deploy infrastructure directly",
            "Write application business logic"
        ],
        "coordinate": {
            "senior-backend-engineer": "for data API needs",
            "devops-engineer": "for pipeline deployment",
            "integration-engineer": "for external data sources"
        }
    },
    "security-engineer": {
        "can": [
            "Perform security audits and assessments",
            "Implement security controls",
            "Configure authentication/authorization",
            "Set up vulnerability scanning",
            "Create security policies",
            "Implement encryption",
            "Handle compliance requirements",
            "Perform penetration testing"
        ],
        "cannot": [
            "Implement features directly",
            "Fix non-security bugs",
            "Make architectural decisions",
            "Deploy applications",
            "Write business logic"
        ],
        "coordinate": {
            "senior-backend-engineer": "for security implementations",
            "devops-engineer": "for security configurations",
            "sre-engineer": "for security monitoring"
        }
    },
    "sre-engineer": {
        "can": [
            "Set up monitoring and alerting",
            "Implement SLIs/SLOs/SLAs",
            "Handle incident response",
            "Create runbooks and playbooks",
            "Optimize system reliability",
            "Implement chaos engineering",
            "Set up observability",
            "Manage on-call rotations"
        ],
        "cannot": [
            "Write application code",
            "Implement features",
            "Make product decisions",
            "Design UI/UX",
            "Create business logic"
        ],
        "coordinate": {
            "devops-engineer": "for infrastructure issues",
            "senior-backend-engineer": "for performance issues",
            "security-engineer": "for security incidents"
        }
    },
    "requirements-analyst": {
        "can": [
            "Gather business requirements",
            "Create user stories and acceptance criteria",
            "Define feature specifications",
            "Conduct stakeholder interviews",
            "Create wireframes and mockups",
            "Prioritize features by business value",
            "Define success metrics",
            "Document requirements"
        ],
        "cannot": [
            "Implement any code",
            "Make technical decisions",
            "Design system architecture",
            "Deploy applications",
            "Assign development tasks"
        ],
        "coordinate": {
            "scrum-master": "for sprint planning",
            "system-architect": "for technical feasibility",
            "tech-lead": "for implementation approach"
        }
    },
    "system-architect": {
        "can": [
            "Design system architecture",
            "Create technical specifications",
            "Define API contracts",
            "Design database schemas",
            "Select technology stack",
            "Create architecture diagrams",
            "Define integration patterns",
            "Establish technical standards"
        ],
        "cannot": [
            "Implement code directly",
            "Manage sprints",
            "Make business decisions",
            "Deploy applications",
            "Write actual code"
        ],
        "coordinate": {
            "tech-lead": "for implementation",
            "requirements-analyst": "for requirements",
            "cloud-architect": "for cloud design"
        }
    },
    "technical-writer": {
        "can": [
            "Create API documentation",
            "Write user guides",
            "Create developer documentation",
            "Write deployment guides",
            "Create technical tutorials",
            "Document system architecture",
            "Write error messages",
            "Create help content"
        ],
        "cannot": [
            "Write code",
            "Implement features",
            "Make technical decisions",
            "Deploy applications",
            "Design architecture"
        ],
        "coordinate": {
            "senior-backend-engineer": "for API docs",
            "senior-frontend-engineer": "for UI docs",
            "devops-engineer": "for deployment docs"
        }
    },
    "cloud-architect": {
        "can": [
            "Design cloud infrastructure",
            "Create multi-cloud strategies",
            "Design serverless architectures",
            "Optimize cloud costs",
            "Plan disaster recovery",
            "Design scalable solutions",
            "Select cloud services",
            "Create cloud migration plans"
        ],
        "cannot": [
            "Write application code",
            "Implement features",
            "Make business decisions",
            "Manage projects",
            "Deploy without DevOps"
        ],
        "coordinate": {
            "devops-engineer": "for implementation",
            "system-architect": "for system design",
            "sre-engineer": "for reliability"
        }
    },
    "project-initializer": {
        "can": [
            "Set up project structure",
            "Initialize repositories",
            "Configure development environment",
            "Set up basic tooling",
            "Create initial documentation",
            "Configure linting and formatting",
            "Set up testing framework",
            "Create starter templates"
        ],
        "cannot": [
            "Implement features",
            "Make architectural decisions",
            "Manage sprints",
            "Deploy to production",
            "Make business decisions"
        ],
        "coordinate": {
            "tech-lead": "for technical setup",
            "devops-engineer": "for CI/CD setup",
            "system-architect": "for structure approval"
        }
    }
}

def format_boundaries(agent_name, boundaries):
    """Format boundaries for an agent"""
    can_list = "\n".join([f"- {item}" for item in boundaries["can"]])
    cannot_list = "\n".join([f"- {item}" for item in boundaries["cannot"]])
    
    coordinate_list = "\n".join([
        f"- **{agent}** {reason}"
        for agent, reason in boundaries["coordinate"].items()
    ])
    
    return f"""
## ⚠️ CRITICAL: Role Boundaries

### ✅ YOU CAN:
{can_list}

### ❌ YOU ABSOLUTELY CANNOT:
{cannot_list}

### 🔄 YOU MUST COORDINATE WITH:
{coordinate_list}

### 📋 REQUIRED OUTPUT FORMAT:
```json
{{
  "role": "{agent_name}",
  "action_type": "describe_your_action",
  "work_completed": ["item1", "item2"],
  "deliverables": ["deliverable1", "deliverable2"],
  "next_steps": ["step1", "step2"]
}}
```"""

# Print the boundaries for each agent
for agent_name, boundaries in agent_boundaries.items():
    print(f"\n{'='*60}")
    print(f"AGENT: {agent_name}")
    print('='*60)
    print(format_boundaries(agent_name, boundaries))