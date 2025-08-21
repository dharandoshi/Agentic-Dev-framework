#!/usr/bin/env python3
"""
Agent Army Flow Test Scenarios
Tests the complete agent orchestration flow
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import unittest

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from hooks.orchestrator import AgentArmyOrchestrator
from hooks.boundary_validator import BoundaryValidator
from mcp.servers.project_management.server import ProjectManagementServer

class TestAgentFlow(unittest.TestCase):
    """Test complete agent flow scenarios"""
    
    def setUp(self):
        """Setup test environment"""
        self.orchestrator = AgentArmyOrchestrator()
        self.validator = BoundaryValidator()
        self.pm_server = ProjectManagementServer()
        
        # Clean test data
        self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Clean up test data files"""
        test_files = [
            self.orchestrator.project_root / 'mcp' / 'data' / 'communication' / 'test_tasks.json',
            self.orchestrator.project_root / 'mcp' / 'data' / 'project-management' / 'test_project-state.json'
        ]
        for file in test_files:
            if file.exists():
                file.unlink()
    
    def test_project_intent_detection(self):
        """Test that project keywords trigger Scrum Master"""
        test_cases = [
            ("Build a todo app", True),
            ("Create an API service", True),
            ("Develop a dashboard", True),
            ("How does Python work?", False),
            ("Explain REST APIs", False),
        ]
        
        for user_input, should_trigger in test_cases:
            result = self.orchestrator.detect_project_intent(user_input)
            self.assertEqual(result, should_trigger, 
                           f"Failed for: {user_input}")
    
    def test_auto_trigger_scrum_master(self):
        """Test automatic Scrum Master triggering"""
        user_input = "Build a task management application"
        result = self.orchestrator.auto_trigger_scrum_master(user_input)
        
        self.assertEqual(result["action"], "inject")
        self.assertIn("Scrum Master", result["message"])
        self.assertEqual(result["trigger_agent"], "scrum-master")
        self.assertEqual(result["context"]["phase"], "inception")
    
    def test_phase_detection(self):
        """Test project phase detection"""
        # Test inception phase (nothing exists)
        phase_result = self.pm_server.detect_phase()
        # Should detect inception when no docs exist
        self.assertIn(phase_result["phase"], ["inception", "discovery", "architecture"])
    
    def test_sprint_0_creation(self):
        """Test Sprint 0 creation for new projects"""
        result = self.pm_server.sprint_create(
            sprint_number=0,
            goals=["Requirements gathering", "Architecture design"],
            capacity=0,
            start_date=datetime.now().isoformat(),
            end_date=datetime.now().isoformat()
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["sprint_id"], "sprint-0")
    
    def test_requirements_to_architect_handoff(self):
        """Test valid handoff from Requirements Analyst to System Architect"""
        is_valid, error = self.validator.validate_handoff(
            "requirements-analyst", 
            "system-architect", 
            "Architecture design needed"
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_invalid_handoff_blocked(self):
        """Test that invalid handoffs are blocked"""
        is_valid, error = self.validator.validate_handoff(
            "scrum-master", 
            "qa-engineer",  # Can't skip to QA
            "Test the app"
        )
        self.assertFalse(is_valid)
        self.assertIn("cannot hand off to", error)
    
    def test_boundary_violation_detection(self):
        """Test role boundary violation detection"""
        # Scrum Master trying to write code
        is_valid, error = self.validator.validate_action(
            "scrum-master",
            "implement feature",
            "def calculate_total(): return sum(items)"
        )
        self.assertFalse(is_valid)
        self.assertIn("tech-lead", error)  # Should suggest tech-lead
        
        # Requirements Analyst trying to design database
        is_valid, error = self.validator.validate_action(
            "requirements-analyst",
            "create database schema",
            "CREATE TABLE users (id INT PRIMARY KEY)"
        )
        self.assertFalse(is_valid)
        self.assertIn("system-architect", error)
    
    def test_valid_agent_actions(self):
        """Test that valid actions are allowed"""
        # Tech Lead coordinating development
        is_valid, error = self.validator.validate_action(
            "tech-lead",
            "assign tasks",
            "Frontend: implement login form, Backend: create auth API"
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # QA Engineer testing
        is_valid, error = self.validator.validate_action(
            "qa-engineer",
            "run test suite",
            "pytest tests/ --cov"
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_complete_flow_simulation(self):
        """Test complete project flow from inception to execution"""
        # Step 1: User request triggers Scrum Master
        user_input = "Build a todo application"
        trigger_result = self.orchestrator.auto_trigger_scrum_master(user_input)
        self.assertEqual(trigger_result["action"], "inject")
        
        # Step 2: Scrum Master detects inception phase
        phase = self.pm_server.detect_phase()
        self.assertIn(phase["phase"], ["inception", "discovery"])
        
        # Step 3: Create Sprint 0
        sprint_result = self.pm_server.sprint_create(
            sprint_number=0,
            goals=["Requirements", "Architecture"],
            capacity=0,
            start_date=datetime.now().isoformat(),
            end_date=datetime.now().isoformat()
        )
        self.assertTrue(sprint_result["success"])
        
        # Step 4: Requirements Analyst creates backlog
        backlog_result = self.pm_server.backlog_add(
            user_story="As a user, I want to create todos",
            priority=1,
            story_points=3,
            acceptance_criteria=["User can enter todo", "Todo is saved"]
        )
        self.assertTrue(backlog_result["success"])
        
        # Step 5: Transition to architecture phase
        transition_result = self.pm_server.transition_phase(
            from_phase="inception",
            to_phase="discovery",
            checklist=["Requirements complete"]
        )
        self.assertTrue(transition_result["success"])
        
        # Step 6: System Architect completes design
        # (Simulated by transitioning to planning)
        transition_result = self.pm_server.transition_phase(
            from_phase="discovery",
            to_phase="architecture",
            checklist=["Architecture complete"]
        )
        self.assertTrue(transition_result["success"])
        
        # Step 7: Sprint 1 planning
        sprint1_result = self.pm_server.sprint_create(
            sprint_number=1,
            goals=["Implement core features"],
            capacity=20,
            start_date=datetime.now().isoformat(),
            end_date=datetime.now().isoformat()
        )
        self.assertTrue(sprint1_result["success"])
        
        # Step 8: Validate handoff to Tech Lead
        is_valid, _ = self.validator.validate_handoff(
            "scrum-master",
            "tech-lead",
            "Sprint backlog for implementation"
        )
        self.assertTrue(is_valid)
        
        print("✅ Complete flow test passed!")
    
    def test_parallel_work_validation(self):
        """Test that parallel work is allowed"""
        # Frontend and Backend can work in parallel
        fe_valid, _ = self.validator.validate_handoff(
            "tech-lead",
            "senior-frontend-engineer",
            "Implement UI components"
        )
        be_valid, _ = self.validator.validate_handoff(
            "tech-lead",
            "senior-backend-engineer",
            "Implement API endpoints"
        )
        
        self.assertTrue(fe_valid)
        self.assertTrue(be_valid)
    
    def test_workflow_template_selection(self):
        """Test workflow template selection based on project type"""
        # Load workflow templates
        templates_file = Path("/home/dhara/PensionID/agent-army-trial/.claude/mcp/data/project-management/workflow-templates.json")
        
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
            
            # Test keyword matching
            keywords_map = templates["template_selection_rules"]["keywords_to_template"]
            
            test_cases = [
                ("web app", "web-application"),
                ("api", "api-service"),
                ("mobile", "mobile-app"),
                ("etl", "data-pipeline"),
                ("microservices", "microservices")
            ]
            
            for keyword, expected_template in test_cases:
                selected = keywords_map.get(keyword)
                self.assertEqual(selected, expected_template)

class TestCeremonyAutomation(unittest.TestCase):
    """Test ceremony automation tools"""
    
    def test_standup_creation(self):
        """Test daily standup creation"""
        from mcp.servers.project_management.ceremonies import CeremonyAutomation
        
        automation = CeremonyAutomation()
        result = automation.daily_standup_create(
            sprint_id="sprint-1",
            attendees=["dev1", "dev2", "qa1"]
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["attendees"]), 3)
        self.assertEqual(len(result["questions"]), 3)
    
    def test_retrospective_creation(self):
        """Test sprint retrospective creation"""
        from mcp.servers.project_management.ceremonies import CeremonyAutomation
        
        automation = CeremonyAutomation()
        result = automation.retrospective_create(
            sprint_id="sprint-1",
            sprint_number=1
        )
        
        self.assertTrue(result["success"])
        self.assertIn("went_well", result["prompts"])
        self.assertIn("could_improve", result["prompts"])

if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)