#!/usr/bin/env python3
"""
Agent Army Master Orchestrator
Central orchestration system that integrates all components
"""

import os
import sys
import json
import time
import logging
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import Agent Army components
try:
    from monitoring_system import AgentArmyMonitor, MonitoringEvent, EventType, AlertSeverity
except ImportError:
    print("Warning: Monitoring system not available")
    AgentArmyMonitor = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AgentArmyOrchestrator')

class ComponentStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"

@dataclass
class SystemComponent:
    """Represents a system component"""
    name: str
    type: str  # "mcp", "agent", "hook", "service"
    status: ComponentStatus
    last_check: datetime
    details: Dict[str, Any]

class AgentArmyOrchestrator:
    """Master orchestrator for Agent Army system"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.claude_dir = self.project_root / ".claude"
        
        # Component tracking
        self.components: Dict[str, SystemComponent] = {}
        self.workflows: Dict[str, Any] = {}
        
        # Monitoring integration
        self.monitor = AgentArmyMonitor() if AgentArmyMonitor else None
        
        # Thread management
        self.running = False
        self.threads: List[threading.Thread] = []
        
        # Load configurations
        self.load_configurations()
        
    def load_configurations(self):
        """Load all system configurations"""
        # Load agent registry
        self.agent_registry = self._load_json(
            self.claude_dir / "agents" / "agent-registry.json"
        )
        
        # Load alerting config
        self.alert_config = self._load_json(
            self.claude_dir / "config" / "alerting-config.json"
        )
        
        # Load test scenarios
        self.test_scenarios = self._load_json(
            self.claude_dir / "scripts" / "test-scenarios.json"
        )
        
        # Load hook configuration from settings
        self.hook_config = self._load_hook_config()
        
    def _load_json(self, path: Path) -> Dict:
        """Load JSON file safely"""
        if path.exists():
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {path}: {e}")
        return {}
        
    def _load_hook_config(self) -> Dict:
        """Load hook configuration from settings"""
        settings_path = self.claude_dir / "settings.json"
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get("hooks", {})
            except Exception as e:
                logger.error(f"Failed to load hook config: {e}")
        return {}
        
    def initialize_system(self) -> bool:
        """Initialize all system components"""
        logger.info("Initializing Agent Army system...")
        
        # 1. Validate environment
        if not self.validate_environment():
            logger.error("Environment validation failed")
            return False
            
        # 2. Initialize MCP servers
        if not self.initialize_mcp_servers():
            logger.error("MCP server initialization failed")
            return False
            
        # 3. Validate agents
        if not self.validate_agents():
            logger.error("Agent validation failed")
            return False
            
        # 4. Initialize hooks
        if not self.initialize_hooks():
            logger.error("Hook initialization failed")
            return False
            
        # 5. Start monitoring
        if self.monitor:
            self.monitor.start_monitoring()
            logger.info("Monitoring system started")
            
        logger.info("✅ Agent Army system initialized successfully")
        return True
        
    def validate_environment(self) -> bool:
        """Validate system environment"""
        logger.info("Validating environment...")
        
        try:
            result = subprocess.run(
                ["python3", str(self.claude_dir / "scripts" / "validate-environment.py")],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.components["environment"] = SystemComponent(
                    name="environment",
                    type="service",
                    status=ComponentStatus.HEALTHY,
                    last_check=datetime.now(),
                    details={"validation": "passed"}
                )
                return True
            else:
                self.components["environment"] = SystemComponent(
                    name="environment",
                    type="service",
                    status=ComponentStatus.FAILED,
                    last_check=datetime.now(),
                    details={"error": result.stderr}
                )
                return False
                
        except Exception as e:
            logger.error(f"Environment validation error: {e}")
            return False
            
    def initialize_mcp_servers(self) -> bool:
        """Initialize and verify MCP servers"""
        logger.info("Initializing MCP servers...")
        
        try:
            # Check current MCP status
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            servers = ["workspace", "docs", "execution", "coord", "validation"]
            all_connected = True
            
            for server in servers:
                if server in result.stdout:
                    self.components[f"mcp_{server}"] = SystemComponent(
                        name=f"mcp_{server}",
                        type="mcp",
                        status=ComponentStatus.HEALTHY,
                        last_check=datetime.now(),
                        details={"connected": True}
                    )
                else:
                    all_connected = False
                    self.components[f"mcp_{server}"] = SystemComponent(
                        name=f"mcp_{server}",
                        type="mcp",
                        status=ComponentStatus.FAILED,
                        last_check=datetime.now(),
                        details={"connected": False}
                    )
                    
            if not all_connected:
                logger.warning("Some MCP servers not connected, attempting registration...")
                
                # Try to register servers
                register_result = subprocess.run(
                    [str(self.claude_dir / "scripts" / "register-mcp-servers.sh")],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if register_result.returncode == 0:
                    logger.info("MCP servers registered successfully")
                    return True
                else:
                    logger.error("Failed to register MCP servers")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"MCP initialization error: {e}")
            return False
            
    def validate_agents(self) -> bool:
        """Validate agent definitions"""
        logger.info("Validating agents...")
        
        agents_dir = self.claude_dir / "agents"
        
        if not agents_dir.exists():
            logger.error("Agents directory not found")
            return False
            
        # Check agent registry
        if not self.agent_registry:
            logger.error("Agent registry not loaded")
            return False
            
        total_agents = self.agent_registry.get("total_agents", 0)
        
        if total_agents > 0:
            self.components["agents"] = SystemComponent(
                name="agents",
                type="agent",
                status=ComponentStatus.HEALTHY,
                last_check=datetime.now(),
                details={
                    "total_agents": total_agents,
                    "hierarchy_levels": len(self.agent_registry.get("hierarchy", {}))
                }
            )
            return True
        else:
            self.components["agents"] = SystemComponent(
                name="agents",
                type="agent",
                status=ComponentStatus.FAILED,
                last_check=datetime.now(),
                details={"error": "No agents found"}
            )
            return False
            
    def initialize_hooks(self) -> bool:
        """Initialize hook system"""
        logger.info("Initializing hooks...")
        
        hooks_dir = self.claude_dir / "hooks"
        
        if not hooks_dir.exists():
            logger.error("Hooks directory not found")
            return False
            
        # Check for key hook scripts
        required_hooks = ["orchestrator.py", "communication-tracker.py"]
        all_hooks_exist = True
        
        for hook in required_hooks:
            hook_path = hooks_dir / hook
            if not hook_path.exists():
                all_hooks_exist = False
                logger.error(f"Required hook missing: {hook}")
                
        if all_hooks_exist and self.hook_config:
            self.components["hooks"] = SystemComponent(
                name="hooks",
                type="hook",
                status=ComponentStatus.HEALTHY,
                last_check=datetime.now(),
                details={"hooks_configured": len(self.hook_config)}
            )
            return True
        else:
            self.components["hooks"] = SystemComponent(
                name="hooks",
                type="hook",
                status=ComponentStatus.DEGRADED if all_hooks_exist else ComponentStatus.FAILED,
                last_check=datetime.now(),
                details={"error": "Hooks not properly configured"}
            )
            return False
            
    def execute_workflow(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a predefined workflow"""
        logger.info(f"Executing workflow: {workflow_name}")
        
        # Log workflow start
        if self.monitor:
            self.monitor.add_event(MonitoringEvent(
                timestamp=datetime.now(),
                event_type=EventType.SYSTEM_HEALTH,
                severity=AlertSeverity.INFO,
                component="Orchestrator",
                message=f"Starting workflow: {workflow_name}",
                details=params
            ))
            
        # Get workflow definition
        workflow = self.test_scenarios.get("test_scenarios", {}).get(workflow_name)
        
        if not workflow:
            logger.error(f"Workflow not found: {workflow_name}")
            return {"success": False, "error": "Workflow not found"}
            
        # Execute workflow steps
        results = []
        for step in workflow.get("workflow_steps", []):
            step_result = self.execute_workflow_step(step, params)
            results.append(step_result)
            
            if not step_result.get("success"):
                logger.error(f"Workflow step failed: {step.get('step')}")
                break
                
        return {
            "workflow": workflow_name,
            "success": all(r.get("success") for r in results),
            "steps_completed": len([r for r in results if r.get("success")]),
            "total_steps": len(workflow.get("workflow_steps", [])),
            "results": results
        }
        
    def execute_workflow_step(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        step_name = step.get("step", "unknown")
        responsible_agent = step.get("responsible_agent", "unknown")
        
        logger.info(f"Executing step: {step_name} (Agent: {responsible_agent})")
        
        # Simulate step execution
        # In production, this would actually invoke the agent
        time.sleep(0.5)  # Simulate work
        
        return {
            "step": step_name,
            "agent": responsible_agent,
            "success": True,
            "duration": 0.5,
            "deliverables": step.get("deliverables", [])
        }
        
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": ComponentStatus.HEALTHY.value,
            "components": {}
        }
        
        # Check each component
        for name, component in self.components.items():
            health_status["components"][name] = {
                "type": component.type,
                "status": component.status.value,
                "last_check": component.last_check.isoformat(),
                "details": component.details
            }
            
            # Update overall status
            if component.status == ComponentStatus.FAILED:
                health_status["overall_status"] = ComponentStatus.FAILED.value
            elif component.status == ComponentStatus.DEGRADED and health_status["overall_status"] != ComponentStatus.FAILED.value:
                health_status["overall_status"] = ComponentStatus.DEGRADED.value
                
        return health_status
        
    def monitor_system(self):
        """Continuous system monitoring"""
        while self.running:
            try:
                # Perform health checks
                health = self.health_check()
                
                # Log health status
                if self.monitor and health["overall_status"] != ComponentStatus.HEALTHY.value:
                    self.monitor.add_event(MonitoringEvent(
                        timestamp=datetime.now(),
                        event_type=EventType.SYSTEM_HEALTH,
                        severity=AlertSeverity.HIGH if health["overall_status"] == ComponentStatus.FAILED.value else AlertSeverity.MEDIUM,
                        component="System",
                        message=f"System health: {health['overall_status']}",
                        details=health
                    ))
                    
                # Re-check failed components
                for name, component in self.components.items():
                    if component.status == ComponentStatus.FAILED:
                        self.attempt_component_recovery(name)
                        
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                
            time.sleep(60)  # Check every minute
            
    def attempt_component_recovery(self, component_name: str):
        """Attempt to recover a failed component"""
        logger.info(f"Attempting recovery for: {component_name}")
        
        component = self.components.get(component_name)
        if not component:
            return
            
        if component.type == "mcp":
            # Try to restart MCP server
            server_name = component_name.replace("mcp_", "")
            self.initialize_mcp_servers()
            
        elif component.type == "agent":
            # Re-validate agents
            self.validate_agents()
            
        elif component.type == "hook":
            # Re-initialize hooks
            self.initialize_hooks()
            
    def start(self):
        """Start the orchestrator"""
        if self.running:
            logger.warning("Orchestrator already running")
            return
            
        logger.info("Starting Agent Army Orchestrator...")
        
        # Initialize system
        if not self.initialize_system():
            logger.error("System initialization failed")
            return
            
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self.monitor_system,
            name="SystemMonitor",
            daemon=True
        )
        monitor_thread.start()
        self.threads.append(monitor_thread)
        
        logger.info("✅ Agent Army Orchestrator started successfully")
        
    def stop(self):
        """Stop the orchestrator"""
        logger.info("Stopping Agent Army Orchestrator...")
        
        self.running = False
        
        # Stop monitoring
        if self.monitor:
            self.monitor.stop_monitoring()
            
        # Wait for threads
        for thread in self.threads:
            thread.join(timeout=5)
            
        logger.info("Agent Army Orchestrator stopped")
        
    def status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "running": self.running,
            "health": self.health_check(),
            "active_workflows": len(self.workflows),
            "component_count": len(self.components),
            "monitor_active": self.monitor.monitoring_active if self.monitor else False
        }

def main():
    """Main orchestrator execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Army Master Orchestrator")
    parser.add_argument("--start", action="store_true", help="Start orchestrator")
    parser.add_argument("--stop", action="store_true", help="Stop orchestrator")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--health", action="store_true", help="Perform health check")
    parser.add_argument("--workflow", help="Execute workflow")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    orchestrator = AgentArmyOrchestrator()
    
    if args.start or args.daemon:
        orchestrator.start()
        
        if args.daemon:
            print("🔄 Agent Army Orchestrator running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(60)
                    # Print status every minute
                    status = orchestrator.status()
                    print(f"Status: {status['health']['overall_status']}")
            except KeyboardInterrupt:
                print("\n⏹️  Stopping orchestrator...")
                orchestrator.stop()
        else:
            print("✅ Orchestrator started")
            
    elif args.stop:
        orchestrator.stop()
        
    elif args.status:
        status = orchestrator.status()
        print(json.dumps(status, indent=2))
        
    elif args.health:
        health = orchestrator.health_check()
        print(json.dumps(health, indent=2))
        
    elif args.workflow:
        # Execute workflow
        result = orchestrator.execute_workflow(args.workflow, {})
        print(json.dumps(result, indent=2))
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()