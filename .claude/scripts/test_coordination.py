#!/usr/bin/env python3
"""
Test Script for Agent Army Coordination
Verifies that the coordination system is working properly
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

def run_mcp_command(tool: str, params: dict) -> dict:
    """Simulate running an MCP command"""
    print(f"\n🔧 Running {tool} with params: {json.dumps(params, indent=2)}")
    return {"status": "simulated", "tool": tool, "params": params}

def test_coordination_flow():
    """Test the complete coordination flow"""
    print("=" * 60)
    print("AGENT ARMY COORDINATION TEST")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    # Test 1: Check if hooks are configured
    print("\n✅ Test 1: Checking hook configuration...")
    settings_file = Path(__file__).parent.parent / "settings.json"
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        has_hooks = bool(settings.get('hooks', {}))
        test_result = {
            "test": "Hook Configuration",
            "passed": has_hooks,
            "details": "Hooks configured" if has_hooks else "No hooks configured"
        }
        results["tests"].append(test_result)
        print(f"   Result: {'✅ PASS' if has_hooks else '❌ FAIL'} - {test_result['details']}")
    
    # Test 2: Check if orchestrator is accessible
    print("\n✅ Test 2: Testing orchestrator hook...")
    orchestrator_path = Path(__file__).parent.parent / "hooks" / "orchestrator.py"
    if orchestrator_path.exists():
        test_cmd = [
            'python3', str(orchestrator_path)
        ]
        env = {
            'CLAUDE_HOOK_INPUT': '{"tool":{"name":"test","parameters":{}}}',
            'CLAUDE_HOOK_TYPE': 'pre-tool-use',
            'CLAUDE_PROJECT_ROOT': str(Path(__file__).parent.parent)
        }
        
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, env={**env}, timeout=5)
            response = json.loads(result.stdout) if result.stdout else {}
            test_result = {
                "test": "Orchestrator Hook",
                "passed": result.returncode == 0 and response.get('action') == 'allow',
                "details": f"Hook responded with: {response.get('action', 'no response')}"
            }
            results["tests"].append(test_result)
            print(f"   Result: {'✅ PASS' if test_result['passed'] else '❌ FAIL'} - {test_result['details']}")
        except Exception as e:
            test_result = {
                "test": "Orchestrator Hook",
                "passed": False,
                "details": f"Error: {str(e)}"
            }
            results["tests"].append(test_result)
            print(f"   Result: ❌ FAIL - {test_result['details']}")
    
    # Test 3: Check workflow engine
    print("\n✅ Test 3: Testing workflow engine...")
    workflow_engine_path = Path(__file__).parent / "agent_workflow_engine.py"
    if workflow_engine_path.exists():
        test_cmd = [
            'python3', str(workflow_engine_path),
            'tech-lead', 'test-task-id', '{}'
        ]
        
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
            response = json.loads(result.stdout) if result.stdout else {}
            test_result = {
                "test": "Workflow Engine",
                "passed": 'success' in response,
                "details": f"Engine response: {response}"
            }
            results["tests"].append(test_result)
            print(f"   Result: {'✅ PASS' if test_result['passed'] else '❌ FAIL'} - {test_result['details']}")
        except Exception as e:
            test_result = {
                "test": "Workflow Engine",
                "passed": False,
                "details": f"Error: {str(e)}"
            }
            results["tests"].append(test_result)
            print(f"   Result: ❌ FAIL - {test_result['details']}")
    
    # Test 4: Check task files
    print("\n✅ Test 4: Checking task data structure...")
    tasks_file = Path(__file__).parent.parent / "mcp" / "data" / "communication" / "tasks.json"
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        task_count = len(tasks)
        in_progress = sum(1 for t in tasks.values() if t.get('status') == 'in_progress')
        test_result = {
            "test": "Task Data Structure",
            "passed": task_count > 0,
            "details": f"Found {task_count} tasks, {in_progress} in progress"
        }
        results["tests"].append(test_result)
        print(f"   Result: {'✅ PASS' if test_result['passed'] else '❌ FAIL'} - {test_result['details']}")
    
    # Test 5: Check agent registry
    print("\n✅ Test 5: Checking agent registry...")
    registry_file = Path(__file__).parent.parent / "agents" / "agent-registry.json"
    if registry_file.exists():
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        agent_count = registry.get('total_agents', 0)
        test_result = {
            "test": "Agent Registry",
            "passed": agent_count > 0,
            "details": f"Registry contains {agent_count} agents"
        }
        results["tests"].append(test_result)
        print(f"   Result: {'✅ PASS' if test_result['passed'] else '❌ FAIL'} - {test_result['details']}")
    
    # Test 6: Check response templates
    print("\n✅ Test 6: Checking response templates...")
    templates_file = Path(__file__).parent.parent / "templates" / "agent_response_templates.json"
    if templates_file.exists():
        with open(templates_file, 'r') as f:
            templates = json.load(f)
        
        template_count = len(templates.get('templates', {}))
        test_result = {
            "test": "Response Templates",
            "passed": template_count > 0,
            "details": f"Found {template_count} response templates"
        }
        results["tests"].append(test_result)
        print(f"   Result: {'✅ PASS' if test_result['passed'] else '❌ FAIL'} - {test_result['details']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results["tests"])
    passed_tests = sum(1 for t in results["tests"] if t["passed"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    # Overall status
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Agent Army coordination is working properly.")
    elif passed_tests >= total_tests * 0.7:
        print("\n⚠️ PARTIAL SUCCESS: Most components working but some issues remain.")
    else:
        print("\n❌ COORDINATION ISSUES: Multiple components are not working properly.")
    
    # Save results
    results_file = Path(__file__).parent.parent / "logs" / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    test_coordination_flow()