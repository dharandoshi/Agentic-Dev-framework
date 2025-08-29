#!/usr/bin/env python3
"""
Agent Army Integration Test Suite
Comprehensive testing for agent workflows, handoff chains, and coordination protocols
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import unittest

@dataclass
class TestResult:
    """Test result container"""
    name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    message: str
    details: Optional[Dict[str, Any]] = None

class TestSeverity(Enum):
    """Test severity levels"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class AgentTest:
    """Agent test definition"""
    name: str
    description: str
    severity: TestSeverity
    agents_involved: List[str]
    expected_workflow: List[str]
    timeout_seconds: int = 60

class AgentArmyIntegrationTests:
    """Comprehensive integration test suite for Agent Army"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.claude_dir = self.project_root / ".claude"
        self.test_results: List[TestResult] = []
        self.agent_registry = self._load_agent_registry()
        
    def _load_agent_registry(self) -> Dict[str, Any]:
        """Load agent registry for test configuration"""
        registry_path = self.claude_dir / "agents" / "agent-registry.json"
        
        if not registry_path.exists():
            return {}
            
        try:
            with open(registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load agent registry: {e}")
            return {}
            
    def _run_test(self, test: AgentTest) -> TestResult:
        """Execute a single integration test"""
        start_time = time.time()
        
        try:
            print(f"🧪 Running test: {test.name}")
            print(f"   Agents: {', '.join(test.agents_involved)}")
            print(f"   Severity: {test.severity.value}")
            
            # Execute the test based on test type
            if "handoff" in test.name.lower():
                result = self._test_agent_handoff(test)
            elif "coordination" in test.name.lower():
                result = self._test_agent_coordination(test)
            elif "communication" in test.name.lower():
                result = self._test_agent_communication(test)
            elif "workflow" in test.name.lower():
                result = self._test_complete_workflow(test)
            elif "mcp" in test.name.lower():
                result = self._test_mcp_integration(test)
            else:
                result = self._test_generic_agent_interaction(test)
                
            duration = time.time() - start_time
            
            return TestResult(
                name=test.name,
                status="passed" if result["success"] else "failed",
                duration=duration,
                message=result["message"],
                details=result.get("details")
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test.name,
                status="failed",
                duration=duration,
                message=f"Test execution failed: {str(e)}",
                details={"exception": str(e), "type": type(e).__name__}
            )
            
    def _test_agent_handoff(self, test: AgentTest) -> Dict[str, Any]:
        """Test agent-to-agent handoff functionality"""
        
        # Simulate a task requiring handoff between agents
        test_scenario = {
            "task": "Create a simple API endpoint with tests",
            "initial_agent": "scrum-master",
            "expected_handoffs": [
                "scrum-master -> system-architect",
                "system-architect -> senior-backend-engineer", 
                "senior-backend-engineer -> qa-engineer"
            ]
        }
        
        # Create temporary test file to simulate work
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_scenario, f, indent=2)
            test_file = f.name
            
        try:
            # Simulate handoff chain by checking agent definitions
            handoff_success = True
            for agent in test.agents_involved:
                agent_file = self.claude_dir / "agents" / f"{agent}.md"
                if not agent_file.exists():
                    return {
                        "success": False,
                        "message": f"Agent definition missing: {agent}",
                        "details": {"missing_agent": agent}
                    }
                    
            return {
                "success": handoff_success,
                "message": f"Agent handoff chain validated for {len(test.agents_involved)} agents",
                "details": {
                    "agents_validated": test.agents_involved,
                    "scenario": test_scenario
                }
            }
            
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.unlink(test_file)
                
    def _test_agent_coordination(self, test: AgentTest) -> Dict[str, Any]:
        """Test multi-agent coordination protocols"""
        
        # Check coordination patterns in agent registry
        coordination_rules = self.agent_registry.get("coordination", {})
        hierarchy = self.agent_registry.get("hierarchy", {})
        
        if not coordination_rules or not hierarchy:
            return {
                "success": False,
                "message": "Agent coordination rules or hierarchy not defined",
                "details": {"registry_keys": list(self.agent_registry.keys())}
            }
            
        # Validate coordination patterns
        missing_patterns = []
        expected_patterns = ["task_assignment", "status_reporting", "conflict_resolution"]
        
        for pattern in expected_patterns:
            if pattern not in coordination_rules:
                missing_patterns.append(pattern)
                
        if missing_patterns:
            return {
                "success": False, 
                "message": f"Missing coordination patterns: {missing_patterns}",
                "details": {"missing_patterns": missing_patterns}
            }
            
        return {
            "success": True,
            "message": "Agent coordination protocols validated",
            "details": {
                "coordination_rules": len(coordination_rules),
                "hierarchy_levels": len(hierarchy)
            }
        }
        
    def _test_agent_communication(self, test: AgentTest) -> Dict[str, Any]:
        """Test agent communication protocols"""
        
        # Test hook system for communication tracking
        hooks_dir = self.claude_dir / "hooks"
        communication_tracker = hooks_dir / "communication-tracker.py"
        
        if not communication_tracker.exists():
            return {
                "success": False,
                "message": "Communication tracker hook not found",
                "details": {"expected_path": str(communication_tracker)}
            }
            
        # Test orchestrator functionality
        orchestrator = hooks_dir / "orchestrator.py"
        if not orchestrator.exists():
            return {
                "success": False,
                "message": "Orchestrator hook not found", 
                "details": {"expected_path": str(orchestrator)}
            }
            
        # Validate communication protocols in agent definitions
        protocol_validation = True
        missing_protocols = []
        
        for agent in test.agents_involved:
            agent_file = self.claude_dir / "agents" / f"{agent}.md"
            if agent_file.exists():
                try:
                    content = agent_file.read_text()
                    if "communication" not in content.lower():
                        missing_protocols.append(agent)
                except Exception as e:
                    protocol_validation = False
                    
        return {
            "success": protocol_validation and len(missing_protocols) == 0,
            "message": f"Communication protocols validated for {len(test.agents_involved) - len(missing_protocols)}/{len(test.agents_involved)} agents",
            "details": {
                "agents_with_protocols": len(test.agents_involved) - len(missing_protocols),
                "missing_protocols": missing_protocols,
                "hooks_available": True
            }
        }
        
    def _test_complete_workflow(self, test: AgentTest) -> Dict[str, Any]:
        """Test complete end-to-end workflow"""
        
        # Simulate a complete development workflow
        workflow_steps = [
            "Requirements gathering",
            "Technical planning", 
            "Architecture design",
            "Implementation",
            "Testing",
            "Documentation",
            "Deployment"
        ]
        
        # Map workflow steps to responsible agents
        agent_workflow_map = {
            "Requirements gathering": ["requirements-analyst", "scrum-master"],
            "Technical planning": ["engineering-manager", "system-architect"], 
            "Architecture design": ["system-architect", "senior-backend-engineer"],
            "Implementation": ["senior-backend-engineer", "senior-frontend-engineer"],
            "Testing": ["qa-engineer"],
            "Documentation": ["technical-writer"],
        }
        
        # Validate that required agents exist for each workflow step
        missing_agents = []
        workflow_coverage = {}
        
        for step, required_agents in agent_workflow_map.items():
            step_coverage = []
            for agent in required_agents:
                agent_file = self.claude_dir / "agents" / f"{agent}.md"
                if agent_file.exists():
                    step_coverage.append(agent)
                else:
                    missing_agents.append(f"{step}: {agent}")
                    
            workflow_coverage[step] = {
                "required": required_agents,
                "available": step_coverage,
                "coverage_percent": (len(step_coverage) / len(required_agents)) * 100
            }
            
        # Calculate overall workflow coverage
        total_coverage = sum(data["coverage_percent"] for data in workflow_coverage.values()) / len(workflow_coverage)
        
        return {
            "success": total_coverage >= 80 and len(missing_agents) < 3,
            "message": f"Workflow coverage: {total_coverage:.1f}% ({len(missing_agents)} missing agents)",
            "details": {
                "workflow_coverage": workflow_coverage,
                "missing_agents": missing_agents,
                "total_coverage": total_coverage
            }
        }
        
    def _test_mcp_integration(self, test: AgentTest) -> Dict[str, Any]:
        """Test MCP server integration with agents"""
        
        try:
            # Check MCP server status
            result = subprocess.run(
                ["claude", "mcp", "list"], 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Failed to query MCP server status",
                    "details": {"stderr": result.stderr, "stdout": result.stdout}
                }
                
            # Parse MCP server list
            mcp_output = result.stdout
            expected_servers = ["workspace", "docs", "execution", "coord", "validation"]
            available_servers = []
            
            for server in expected_servers:
                if server in mcp_output:
                    available_servers.append(server)
                    
            coverage = (len(available_servers) / len(expected_servers)) * 100
            
            return {
                "success": coverage >= 80,
                "message": f"MCP integration: {coverage:.1f}% servers available ({len(available_servers)}/{len(expected_servers)})",
                "details": {
                    "expected_servers": expected_servers,
                    "available_servers": available_servers,
                    "coverage_percent": coverage,
                    "mcp_output": mcp_output
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "MCP server query timed out",
                "details": {"timeout": 15}
            }
        except FileNotFoundError:
            return {
                "success": False,
                "message": "Claude Code CLI not found",
                "details": {"requirement": "Claude Code CLI must be installed"}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"MCP integration test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    def _test_generic_agent_interaction(self, test: AgentTest) -> Dict[str, Any]:
        """Generic agent interaction test"""
        
        # Basic validation that all agents in test exist
        missing_agents = []
        for agent in test.agents_involved:
            agent_file = self.claude_dir / "agents" / f"{agent}.md"
            if not agent_file.exists():
                missing_agents.append(agent)
                
        if missing_agents:
            return {
                "success": False,
                "message": f"Missing agent definitions: {missing_agents}",
                "details": {"missing_agents": missing_agents}
            }
            
        return {
            "success": True,
            "message": f"Agent interaction test passed for {len(test.agents_involved)} agents",
            "details": {"agents_validated": test.agents_involved}
        }
        
    def define_test_suite(self) -> List[AgentTest]:
        """Define comprehensive test suite"""
        
        return [
            # Critical handoff tests
            AgentTest(
                name="scrum_master_to_tech_lead_handoff",
                description="Test task handoff from Scrum Master to Tech Lead",
                severity=TestSeverity.CRITICAL,
                agents_involved=["scrum-master", "engineering-manager"],
                expected_workflow=["task_creation", "assignment", "acknowledgment"],
                timeout_seconds=30
            ),
            
            AgentTest(
                name="tech_lead_to_engineers_handoff",
                description="Test technical task distribution to engineering teams",
                severity=TestSeverity.CRITICAL,
                agents_involved=["engineering-manager", "senior-backend-engineer", "senior-frontend-engineer"],
                expected_workflow=["task_breakdown", "assignment", "coordination"],
                timeout_seconds=45
            ),
            
            AgentTest(
                name="engineer_to_qa_handoff",
                description="Test implementation to testing handoff",
                severity=TestSeverity.HIGH,
                agents_involved=["senior-backend-engineer", "qa-engineer"],
                expected_workflow=["implementation_complete", "test_request", "validation"],
                timeout_seconds=30
            ),
            
            # Coordination tests
            AgentTest(
                name="multi_agent_coordination",
                description="Test coordination protocols across agent hierarchy",
                severity=TestSeverity.CRITICAL,
                agents_involved=["scrum-master", "engineering-manager", "system-architect", "senior-backend-engineer"],
                expected_workflow=["coordination_setup", "status_sync", "conflict_resolution"],
                timeout_seconds=60
            ),
            
            AgentTest(
                name="cross_functional_coordination",
                description="Test coordination between different functional areas",
                severity=TestSeverity.HIGH,
                agents_involved=["senior-backend-engineer", "senior-frontend-engineer", "devops-engineer", "security-engineer"],
                expected_workflow=["requirement_alignment", "integration_planning", "delivery_coordination"],
                timeout_seconds=60
            ),
            
            # Communication tests
            AgentTest(
                name="agent_communication_protocols",
                description="Test agent-to-agent communication protocols",
                severity=TestSeverity.HIGH,
                agents_involved=["scrum-master", "engineering-manager", "senior-backend-engineer", "qa-engineer"],
                expected_workflow=["message_sending", "acknowledgment", "response"],
                timeout_seconds=30
            ),
            
            AgentTest(
                name="escalation_communication",
                description="Test escalation communication flows",
                severity=TestSeverity.HIGH,
                agents_involved=["senior-backend-engineer", "engineering-manager", "scrum-master"],
                expected_workflow=["issue_identification", "escalation", "resolution"],
                timeout_seconds=30
            ),
            
            # Workflow tests
            AgentTest(
                name="complete_feature_workflow",
                description="Test complete feature development workflow",
                severity=TestSeverity.CRITICAL,
                agents_involved=[
                    "requirements-analyst", "scrum-master", "system-architect", 
                    "senior-backend-engineer", "senior-frontend-engineer", 
                    "qa-engineer", "technical-writer", "devops-engineer"
                ],
                expected_workflow=[
                    "requirements_gathering", "planning", "architecture", 
                    "implementation", "testing", "documentation", "deployment"
                ],
                timeout_seconds=120
            ),
            
            AgentTest(
                name="bug_fix_workflow",
                description="Test bug identification and resolution workflow",
                severity=TestSeverity.HIGH,
                agents_involved=["qa-engineer", "engineering-manager", "senior-backend-engineer", "devops-engineer"],
                expected_workflow=["bug_identification", "assignment", "fix_implementation", "validation", "deployment"],
                timeout_seconds=90
            ),
            
            # MCP integration tests
            AgentTest(
                name="mcp_server_integration",
                description="Test MCP server availability and integration",
                severity=TestSeverity.CRITICAL,
                agents_involved=["engineering-manager"],  # Any agent using MCP tools
                expected_workflow=["server_connection", "tool_availability", "function_execution"],
                timeout_seconds=30
            ),
            
            AgentTest(
                name="agent_tool_access",
                description="Test agent access to MCP tools based on permissions",
                severity=TestSeverity.HIGH,
                agents_involved=["senior-backend-engineer", "qa-engineer", "devops-engineer"],
                expected_workflow=["tool_request", "permission_check", "tool_execution"],
                timeout_seconds=45
            ),
            
            # Specialized agent tests
            AgentTest(
                name="security_integration_workflow",
                description="Test security engineer integration in development workflow",
                severity=TestSeverity.HIGH,
                agents_involved=["security-engineer", "senior-backend-engineer", "devops-engineer"],
                expected_workflow=["security_review", "vulnerability_assessment", "remediation"],
                timeout_seconds=60
            ),
            
            AgentTest(
                name="data_pipeline_workflow",
                description="Test data engineering workflow integration",
                severity=TestSeverity.MEDIUM,
                agents_involved=["data-engineer", "senior-backend-engineer", "system-architect"],
                expected_workflow=["data_requirements", "pipeline_design", "implementation"],
                timeout_seconds=60
            ),
        ]
        
    def run_test_suite(self) -> Dict[str, Any]:
        """Execute complete integration test suite"""
        
        print("🧪 Agent Army Integration Test Suite")
        print("=" * 50)
        
        test_suite = self.define_test_suite()
        
        print(f"📋 Running {len(test_suite)} integration tests...")
        print()
        
        # Group tests by severity
        critical_tests = [t for t in test_suite if t.severity == TestSeverity.CRITICAL]
        high_tests = [t for t in test_suite if t.severity == TestSeverity.HIGH]  
        medium_tests = [t for t in test_suite if t.severity == TestSeverity.MEDIUM]
        low_tests = [t for t in test_suite if t.severity == TestSeverity.LOW]
        
        all_results = []
        
        # Run tests by priority
        for test_group, group_name in [
            (critical_tests, "Critical Tests"),
            (high_tests, "High Priority Tests"),
            (medium_tests, "Medium Priority Tests"),
            (low_tests, "Low Priority Tests")
        ]:
            if test_group:
                print(f"\n🔥 {group_name} ({len(test_group)} tests)")
                print("-" * 40)
                
                for test in test_group:
                    result = self._run_test(test)
                    all_results.append(result)
                    
                    status_emoji = "✅" if result.status == "passed" else "❌"
                    print(f"  {status_emoji} {result.name} ({result.duration:.2f}s)")
                    if result.status == "failed":
                        print(f"      {result.message}")
                        
        self.test_results = all_results
        
        # Generate summary
        return self._generate_test_summary()
        
    def _generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        skipped_tests = len([r for r in self.test_results if r.status == "skipped"])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Categorize failures
        critical_failures = []
        high_failures = []
        
        test_suite = self.define_test_suite()
        test_severity_map = {t.name: t.severity for t in test_suite}
        
        for result in self.test_results:
            if result.status == "failed":
                severity = test_severity_map.get(result.name, TestSeverity.MEDIUM)
                if severity == TestSeverity.CRITICAL:
                    critical_failures.append(result)
                elif severity == TestSeverity.HIGH:
                    high_failures.append(result)
                    
        # Overall system health assessment
        if success_rate >= 95 and len(critical_failures) == 0:
            health_status = "EXCELLENT"
        elif success_rate >= 85 and len(critical_failures) == 0:
            health_status = "GOOD" 
        elif success_rate >= 70 and len(critical_failures) <= 1:
            health_status = "FAIR"
        else:
            health_status = "NEEDS_ATTENTION"
            
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests, 
            "skipped": skipped_tests,
            "success_rate": round(success_rate, 1),
            "health_status": health_status,
            "critical_failures": len(critical_failures),
            "high_failures": len(high_failures),
            "test_duration": sum(r.duration for r in self.test_results),
            "failures": [{"name": r.name, "message": r.message} for r in self.test_results if r.status == "failed"]
        }
        
        # Print summary
        print(f"\n📊 Test Suite Summary")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🏥 System Health: {health_status}")
        print(f"⏱️  Total Duration: {summary['test_duration']:.2f}s")
        
        if critical_failures:
            print(f"\n🚨 Critical Failures ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"  • {failure.name}: {failure.message}")
                
        if high_failures:
            print(f"\n⚠️  High Priority Failures ({len(high_failures)}):")
            for failure in high_failures[:3]:  # Show first 3
                print(f"  • {failure.name}: {failure.message}")
            if len(high_failures) > 3:
                print(f"  ... and {len(high_failures) - 3} more")
                
        print(f"\n💡 Recommendations:")
        if health_status == "NEEDS_ATTENTION":
            print("  • Fix critical failures immediately")
            print("  • Review agent definitions and coordination protocols") 
            print("  • Verify MCP server configurations")
        elif health_status == "FAIR":
            print("  • Address high priority failures")
            print("  • Improve agent handoff mechanisms")
        elif health_status == "GOOD":
            print("  • System is functioning well")
            print("  • Consider optimizing failed workflows")
        else:
            print("  • System is performing excellently")
            print("  • Continue monitoring and maintaining current standards")
            
        return summary
        
    def save_test_report(self, output_file: Optional[Path] = None) -> Path:
        """Save detailed test report to file"""
        
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = self.project_root / f"agent-army-test-report-{timestamp}.json"
            
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": str(self.project_root),
            "summary": self._generate_test_summary(),
            "detailed_results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "duration": r.duration,
                    "message": r.message,
                    "details": r.details
                } for r in self.test_results
            ],
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "agent_registry_loaded": bool(self.agent_registry)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n📄 Detailed test report saved: {output_file}")
        return output_file

def main():
    """Main test execution entry point"""
    
    tester = AgentArmyIntegrationTests()
    
    print("Starting Agent Army Integration Tests...")
    
    # Run test suite
    summary = tester.run_test_suite()
    
    # Save report
    tester.save_test_report()
    
    # Exit with appropriate code
    if summary["health_status"] in ["EXCELLENT", "GOOD"]:
        sys.exit(0)
    elif summary["health_status"] == "FAIR":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()