#!/usr/bin/env python3
"""
Project Management MCP Server
Provides comprehensive project management tools for Agile/Scrum workflows
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

class ProjectPhase(Enum):
    """Project lifecycle phases"""
    INCEPTION = "inception"  # Nothing exists yet
    DISCOVERY = "discovery"  # Requirements gathering
    ARCHITECTURE = "architecture"  # Technical design
    PLANNING = "planning"  # Sprint planning
    EXECUTION = "execution"  # Active development
    TESTING = "testing"  # QA phase
    DEPLOYMENT = "deployment"  # Release phase
    MAINTENANCE = "maintenance"  # Post-release

class SprintStatus(Enum):
    """Sprint statuses"""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectManagementServer:
    """MCP Server for Project Management"""
    
    def __init__(self):
        self.data_dir = Path("/home/dhara/PensionID/agent-army-trial/.claude/mcp/data/project-management")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data files
        self.project_state_file = self.data_dir / "project-state.json"
        self.sprints_file = self.data_dir / "sprints.json"
        self.backlog_file = self.data_dir / "backlog.json"
        self.ceremonies_file = self.data_dir / "ceremonies.json"
        self.metrics_file = self.data_dir / "metrics.json"
        
        # Load or initialize data
        self.project_state = self._load_or_init_project_state()
        self.sprints = self._load_or_init_sprints()
        self.backlog = self._load_or_init_backlog()
        self.ceremonies = self._load_or_init_ceremonies()
        self.metrics = self._load_or_init_metrics()
    
    def _load_or_init_project_state(self) -> Dict:
        """Load or initialize project state"""
        if self.project_state_file.exists():
            with open(self.project_state_file, 'r') as f:
                return json.load(f)
        return {
            "phase": ProjectPhase.INCEPTION.value,
            "current_sprint": None,
            "project_name": None,
            "created_at": datetime.now().isoformat(),
            "inception_complete": False,
            "requirements_complete": False,
            "architecture_complete": False,
            "backlog_initialized": False,
            "sprints_completed": 0,
            "active_agents": [],
            "blockers": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_or_init_sprints(self) -> List[Dict]:
        """Load or initialize sprints"""
        if self.sprints_file.exists():
            with open(self.sprints_file, 'r') as f:
                return json.load(f)
        return []
    
    def _load_or_init_backlog(self) -> List[Dict]:
        """Load or initialize backlog"""
        if self.backlog_file.exists():
            with open(self.backlog_file, 'r') as f:
                return json.load(f)
        return []
    
    def _load_or_init_ceremonies(self) -> List[Dict]:
        """Load or initialize ceremonies"""
        if self.ceremonies_file.exists():
            with open(self.ceremonies_file, 'r') as f:
                return json.load(f)
        return []
    
    def _load_or_init_metrics(self) -> Dict:
        """Load or initialize metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            "velocity": [],
            "burndown": [],
            "cycle_time": [],
            "defect_rate": 0,
            "team_happiness": 0
        }
    
    def _save_data(self):
        """Save all data to files"""
        with open(self.project_state_file, 'w') as f:
            json.dump(self.project_state, f, indent=2)
        with open(self.sprints_file, 'w') as f:
            json.dump(self.sprints, f, indent=2)
        with open(self.backlog_file, 'w') as f:
            json.dump(self.backlog, f, indent=2)
        with open(self.ceremonies_file, 'w') as f:
            json.dump(self.ceremonies, f, indent=2)
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    # Phase Management Tools
    
    async def detect_phase(self) -> Dict:
        """Automatically detect current project phase"""
        # Check for requirements
        docs_dir = Path("/home/dhara/PensionID/agent-army-trial/docs")
        has_requirements = any(docs_dir.glob("*requirements*.md"))
        has_architecture = any(docs_dir.glob("*architecture*.md"))
        
        # Update phase based on artifacts
        if not has_requirements:
            self.project_state["phase"] = ProjectPhase.INCEPTION.value
        elif not has_architecture:
            self.project_state["phase"] = ProjectPhase.DISCOVERY.value
        elif not self.project_state["backlog_initialized"]:
            self.project_state["phase"] = ProjectPhase.ARCHITECTURE.value
        elif self.project_state["current_sprint"] is None:
            self.project_state["phase"] = ProjectPhase.PLANNING.value
        elif self.project_state["sprints_completed"] > 0:
            self.project_state["phase"] = ProjectPhase.EXECUTION.value
        
        self._save_data()
        
        return {
            "phase": self.project_state["phase"],
            "requirements_found": has_requirements,
            "architecture_found": has_architecture,
            "backlog_ready": self.project_state["backlog_initialized"],
            "active_sprint": self.project_state["current_sprint"],
            "recommendation": self._get_phase_recommendation()
        }
    
    def _get_phase_recommendation(self) -> str:
        """Get recommendation based on current phase"""
        phase = self.project_state["phase"]
        
        recommendations = {
            ProjectPhase.INCEPTION.value: "Start with requirements gathering. Delegate to requirements-analyst.",
            ProjectPhase.DISCOVERY.value: "Requirements found. Now create system architecture. Delegate to system-architect.",
            ProjectPhase.ARCHITECTURE.value: "Architecture ready. Initialize backlog and prepare for sprint planning.",
            ProjectPhase.PLANNING.value: "Ready for Sprint 1 planning. Review backlog and assign to engineering-manager.",
            ProjectPhase.EXECUTION.value: "Sprint active. Monitor progress and facilitate ceremonies.",
            ProjectPhase.TESTING.value: "Development complete. Focus on QA and bug fixes.",
            ProjectPhase.DEPLOYMENT.value: "Ready for release. Coordinate with DevOps.",
            ProjectPhase.MAINTENANCE.value: "Project in maintenance mode. Handle bugs and minor enhancements."
        }
        
        return recommendations.get(phase, "Unknown phase. Review project state.")
    
    async def transition_phase(self, from_phase: str, to_phase: str, checklist: List[str]) -> Dict:
        """Transition between project phases"""
        # Validate transition
        valid_transitions = {
            ProjectPhase.INCEPTION.value: [ProjectPhase.DISCOVERY.value],
            ProjectPhase.DISCOVERY.value: [ProjectPhase.ARCHITECTURE.value],
            ProjectPhase.ARCHITECTURE.value: [ProjectPhase.PLANNING.value],
            ProjectPhase.PLANNING.value: [ProjectPhase.EXECUTION.value],
            ProjectPhase.EXECUTION.value: [ProjectPhase.TESTING.value, ProjectPhase.PLANNING.value],
            ProjectPhase.TESTING.value: [ProjectPhase.DEPLOYMENT.value, ProjectPhase.EXECUTION.value],
            ProjectPhase.DEPLOYMENT.value: [ProjectPhase.MAINTENANCE.value],
            ProjectPhase.MAINTENANCE.value: [ProjectPhase.PLANNING.value]  # New features
        }
        
        if to_phase not in valid_transitions.get(from_phase, []):
            return {
                "success": False,
                "error": f"Invalid transition from {from_phase} to {to_phase}"
            }
        
        # Update phase
        self.project_state["phase"] = to_phase
        self.project_state["last_updated"] = datetime.now().isoformat()
        
        # Update completion flags
        if to_phase == ProjectPhase.DISCOVERY.value:
            self.project_state["inception_complete"] = True
        elif to_phase == ProjectPhase.ARCHITECTURE.value:
            self.project_state["requirements_complete"] = True
        elif to_phase == ProjectPhase.PLANNING.value:
            self.project_state["architecture_complete"] = True
        
        self._save_data()
        
        return {
            "success": True,
            "new_phase": to_phase,
            "checklist_items": checklist,
            "next_actions": self._get_phase_recommendation()
        }
    
    # Sprint Management Tools
    
    async def sprint_create(self, sprint_number: int, goals: List[str], 
                          capacity: int, start_date: str, end_date: str) -> Dict:
        """Create a new sprint"""
        sprint = {
            "id": f"sprint-{sprint_number}",
            "number": sprint_number,
            "goals": goals,
            "capacity": capacity,  # Story points
            "committed_points": 0,
            "completed_points": 0,
            "start_date": start_date,
            "end_date": end_date,
            "status": SprintStatus.PLANNED.value,
            "backlog_items": [],
            "created_at": datetime.now().isoformat()
        }
        
        self.sprints.append(sprint)
        
        # If this is Sprint 0, it's special
        if sprint_number == 0:
            sprint["goals"] = ["Complete requirements gathering", "Define system architecture", "Initialize project"]
            sprint["status"] = SprintStatus.ACTIVE.value
            self.project_state["current_sprint"] = sprint["id"]
        
        self._save_data()
        
        return {
            "success": True,
            "sprint_id": sprint["id"],
            "message": f"Sprint {sprint_number} created successfully"
        }
    
    async def sprint_current(self) -> Dict:
        """Get current active sprint information"""
        if not self.project_state["current_sprint"]:
            return {
                "active_sprint": None,
                "message": "No active sprint. Create Sprint 0 to begin."
            }
        
        current = next((s for s in self.sprints if s["id"] == self.project_state["current_sprint"]), None)
        
        if current:
            # Calculate sprint progress
            total_days = (datetime.fromisoformat(current["end_date"]) - 
                         datetime.fromisoformat(current["start_date"])).days
            elapsed_days = (datetime.now() - datetime.fromisoformat(current["start_date"])).days
            progress_percentage = min(100, (elapsed_days / total_days) * 100) if total_days > 0 else 0
            
            return {
                "sprint": current,
                "progress_percentage": progress_percentage,
                "days_remaining": max(0, total_days - elapsed_days),
                "velocity": current["completed_points"] / max(1, elapsed_days)
            }
        
        return {"active_sprint": None, "message": "Sprint data not found"}
    
    async def sprint_close(self, sprint_number: int, completed_items: List[str], 
                          carry_over_items: List[str]) -> Dict:
        """Close a sprint and calculate metrics"""
        sprint = next((s for s in self.sprints if s["number"] == sprint_number), None)
        
        if not sprint:
            return {"success": False, "error": f"Sprint {sprint_number} not found"}
        
        sprint["status"] = SprintStatus.COMPLETED.value
        sprint["completed_items"] = completed_items
        sprint["carry_over_items"] = carry_over_items
        
        # Update metrics
        velocity = sprint["completed_points"]
        self.metrics["velocity"].append(velocity)
        
        # Clear current sprint
        if self.project_state["current_sprint"] == sprint["id"]:
            self.project_state["current_sprint"] = None
            self.project_state["sprints_completed"] += 1
        
        self._save_data()
        
        return {
            "success": True,
            "sprint_velocity": velocity,
            "carry_over_count": len(carry_over_items),
            "message": f"Sprint {sprint_number} closed successfully"
        }
    
    # Backlog Management Tools
    
    async def backlog_add(self, user_story: str, priority: int, 
                         story_points: int, acceptance_criteria: List[str]) -> Dict:
        """Add item to product backlog"""
        item = {
            "id": f"PBI-{len(self.backlog) + 1:03d}",
            "user_story": user_story,
            "priority": priority,
            "story_points": story_points,
            "acceptance_criteria": acceptance_criteria,
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "sprint_id": None
        }
        
        self.backlog.append(item)
        self.project_state["backlog_initialized"] = True
        self._save_data()
        
        return {
            "success": True,
            "item_id": item["id"],
            "message": "Backlog item added successfully"
        }
    
    async def backlog_prioritize(self, criteria: str = "business_value") -> Dict:
        """Prioritize backlog items"""
        # Sort backlog based on criteria
        if criteria == "priority":
            self.backlog.sort(key=lambda x: x["priority"])
        elif criteria == "story_points":
            self.backlog.sort(key=lambda x: x["story_points"])
        elif criteria == "business_value":
            # Complex calculation based on priority and effort
            self.backlog.sort(key=lambda x: x["priority"] / max(1, x["story_points"]))
        
        self._save_data()
        
        return {
            "success": True,
            "criteria_used": criteria,
            "top_items": self.backlog[:5] if self.backlog else [],
            "total_items": len(self.backlog)
        }
    
    # Intelligence Tools
    
    async def recommend_next_action(self) -> Dict:
        """AI-powered recommendation for next action"""
        phase = self.project_state["phase"]
        recommendations = []
        
        if phase == ProjectPhase.INCEPTION.value:
            recommendations.append({
                "action": "delegate_to_requirements_analyst",
                "reason": "No requirements documentation found",
                "priority": "critical"
            })
        elif phase == ProjectPhase.DISCOVERY.value:
            recommendations.append({
                "action": "delegate_to_system_architect",
                "reason": "Requirements complete, need technical design",
                "priority": "high"
            })
        elif phase == ProjectPhase.PLANNING.value:
            if not self.project_state["current_sprint"]:
                recommendations.append({
                    "action": "create_sprint_1",
                    "reason": "No active sprint, ready to begin development",
                    "priority": "high"
                })
        elif phase == ProjectPhase.EXECUTION.value:
            # Check for blockers
            if self.project_state["blockers"]:
                recommendations.append({
                    "action": "resolve_blockers",
                    "reason": f"{len(self.project_state['blockers'])} blockers preventing progress",
                    "priority": "critical"
                })
        
        return {
            "phase": phase,
            "recommendations": recommendations,
            "confidence": 0.95
        }
    
    async def project_health(self) -> Dict:
        """Get overall project health metrics"""
        health_score = 100
        issues = []
        
        # Check for blockers
        if self.project_state["blockers"]:
            health_score -= 20
            issues.append(f"{len(self.project_state['blockers'])} blockers present")
        
        # Check velocity trend
        if len(self.metrics["velocity"]) >= 3:
            recent_velocity = self.metrics["velocity"][-3:]
            if recent_velocity[-1] < recent_velocity[0]:
                health_score -= 15
                issues.append("Velocity decreasing")
        
        # Check sprint progress
        if self.project_state["current_sprint"]:
            current = await self.sprint_current()
            if current.get("progress_percentage", 0) < 30 and current.get("days_remaining", 10) < 3:
                health_score -= 25
                issues.append("Sprint at risk")
        
        return {
            "health_score": max(0, health_score),
            "status": "healthy" if health_score >= 70 else "at_risk" if health_score >= 40 else "critical",
            "issues": issues,
            "phase": self.project_state["phase"],
            "active_sprint": self.project_state["current_sprint"],
            "sprints_completed": self.project_state["sprints_completed"]
        }

# MCP Server Interface
async def handle_request(request: Dict) -> Dict:
    """Handle incoming MCP requests"""
    server = ProjectManagementServer()
    
    tool = request.get("tool")
    params = request.get("params", {})
    
    # Route to appropriate handler
    handlers = {
        "detect_phase": server.detect_phase,
        "transition_phase": lambda: server.transition_phase(**params),
        "sprint_create": lambda: server.sprint_create(**params),
        "sprint_current": server.sprint_current,
        "sprint_close": lambda: server.sprint_close(**params),
        "backlog_add": lambda: server.backlog_add(**params),
        "backlog_prioritize": lambda: server.backlog_prioritize(**params),
        "recommend_next_action": server.recommend_next_action,
        "project_health": server.project_health
    }
    
    handler = handlers.get(tool)
    if handler:
        result = await handler()
        return {"success": True, "result": result}
    
    return {"success": False, "error": f"Unknown tool: {tool}"}

if __name__ == "__main__":
    # Test the server
    import sys
    
    async def test():
        server = ProjectManagementServer()
        
        # Test phase detection
        phase = await server.detect_phase()
        print(f"Current phase: {phase}")
        
        # Test recommendations
        rec = await server.recommend_next_action()
        print(f"Recommendations: {rec}")
        
        # Test project health
        health = await server.project_health()
        print(f"Project health: {health}")
    
    asyncio.run(test())