#!/usr/bin/env python3
"""
Test Delegation Chain Script
Demonstrates how tech-lead delegates to developers and reports back to scrum-master
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def simulate_delegation_chain():
    """Simulate the delegation chain: scrum-master -> tech-lead -> devs -> tech-lead -> scrum-master"""
    
    print("🚀 DELEGATION CHAIN TEST")
    print("=" * 50)
    
    # Setup paths
    project_root = Path('/home/dhara/PensionID/agent-army-trial/.claude')
    tasks_file = project_root / 'mcp' / 'data' / 'communication' / 'tasks.json'
    messages_file = project_root / 'mcp' / 'data' / 'communication' / 'messages.json'
    
    # Ensure directories exist
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Scrum Master creates a feature task
    print("\n1️⃣ SCRUM MASTER creates feature task...")
    
    tasks = {}
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    tasks[task_id] = {
        "id": task_id,
        "title": "Implement User Authentication",
        "description": "Add login/logout functionality with JWT tokens",
        "created_by": "scrum-master",
        "assigned_to": "tech-lead",
        "status": "assigned",
        "priority": "high",
        "created_at": datetime.now().isoformat()
    }
    
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    print(f"   ✅ Task {task_id} created and assigned to tech-lead")
    
    # Step 2: Tech Lead receives task and delegates
    print("\n2️⃣ TECH LEAD receives task and delegates to developers...")
    
    # Create subtasks for developers
    backend_task_id = f"{task_id}_backend"
    frontend_task_id = f"{task_id}_frontend"
    
    tasks[backend_task_id] = {
        "id": backend_task_id,
        "title": "Implement JWT authentication API",
        "description": "Create /auth/login and /auth/logout endpoints",
        "created_by": "tech-lead",
        "assigned_to": "senior-backend-engineer",
        "status": "assigned",
        "priority": "high",
        "parent_task": task_id,
        "created_at": datetime.now().isoformat()
    }
    
    tasks[frontend_task_id] = {
        "id": frontend_task_id,
        "title": "Create login UI components",
        "description": "Build login form and auth state management",
        "created_by": "tech-lead",
        "assigned_to": "senior-frontend-engineer",
        "status": "assigned",
        "priority": "high",
        "parent_task": task_id,
        "created_at": datetime.now().isoformat()
    }
    
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    print(f"   ✅ Subtask {backend_task_id} delegated to senior-backend-engineer")
    print(f"   ✅ Subtask {frontend_task_id} delegated to senior-frontend-engineer")
    
    # Step 3: Create delegation messages
    print("\n3️⃣ Creating delegation messages...")
    
    messages = {}
    
    # Message from tech-lead to backend dev
    msg_backend = f"msg_backend_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    messages[msg_backend] = {
        "id": msg_backend,
        "from_agent": "tech-lead",
        "to_agent": "senior-backend-engineer",
        "subject": f"Task Assignment: {backend_task_id}",
        "content": "Please implement JWT authentication endpoints. Coordinate with frontend for API spec.",
        "type": "task",
        "priority": "high",
        "task_id": backend_task_id,
        "timestamp": datetime.now().isoformat(),
        "status": "unread"
    }
    
    # Message from tech-lead to frontend dev
    msg_frontend = f"msg_frontend_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    messages[msg_frontend] = {
        "id": msg_frontend,
        "from_agent": "tech-lead",
        "to_agent": "senior-frontend-engineer",
        "subject": f"Task Assignment: {frontend_task_id}",
        "content": "Please create login UI components. Coordinate with backend for API integration.",
        "type": "task",
        "priority": "high",
        "task_id": frontend_task_id,
        "timestamp": datetime.now().isoformat(),
        "status": "unread"
    }
    
    with open(messages_file, 'w') as f:
        json.dump(messages, f, indent=2)
    
    print("   ✅ Delegation messages sent to developers")
    
    # Step 4: Simulate developers completing tasks
    print("\n4️⃣ Simulating developers completing tasks...")
    
    # Backend completes
    tasks[backend_task_id]["status"] = "completed"
    tasks[backend_task_id]["completed_at"] = datetime.now().isoformat()
    
    # Frontend completes
    tasks[frontend_task_id]["status"] = "completed"
    tasks[frontend_task_id]["completed_at"] = datetime.now().isoformat()
    
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    print(f"   ✅ Backend task {backend_task_id} completed")
    print(f"   ✅ Frontend task {frontend_task_id} completed")
    
    # Step 5: Developers report back to tech-lead
    print("\n5️⃣ Developers report completion to tech-lead...")
    
    # Backend reports to tech-lead
    msg_backend_report = f"msg_backend_report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    messages[msg_backend_report] = {
        "id": msg_backend_report,
        "from_agent": "senior-backend-engineer",
        "to_agent": "tech-lead",
        "subject": f"Task {backend_task_id} Completed",
        "content": "JWT authentication endpoints implemented. Tests passing. API docs updated.",
        "type": "status",
        "priority": "medium",
        "task_id": backend_task_id,
        "timestamp": datetime.now().isoformat(),
        "status": "unread"
    }
    
    # Frontend reports to tech-lead
    msg_frontend_report = f"msg_frontend_report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    messages[msg_frontend_report] = {
        "id": msg_frontend_report,
        "from_agent": "senior-frontend-engineer",
        "to_agent": "tech-lead",
        "subject": f"Task {frontend_task_id} Completed",
        "content": "Login UI components created. Integration with auth API tested.",
        "type": "status",
        "priority": "medium",
        "task_id": frontend_task_id,
        "timestamp": datetime.now().isoformat(),
        "status": "unread"
    }
    
    with open(messages_file, 'w') as f:
        json.dump(messages, f, indent=2)
    
    print("   ✅ Backend engineer reported to tech-lead")
    print("   ✅ Frontend engineer reported to tech-lead")
    
    # Step 6: Tech-lead reports to scrum-master
    print("\n6️⃣ Tech-lead reports feature completion to scrum-master...")
    
    # Update main task
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["completed_at"] = datetime.now().isoformat()
    
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    # Tech-lead reports to scrum-master
    msg_tech_report = f"msg_tech_report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    messages[msg_tech_report] = {
        "id": msg_tech_report,
        "from_agent": "tech-lead",
        "to_agent": "scrum-master",
        "subject": f"Feature {task_id} Completed",
        "content": "User authentication feature completed. Both backend API and frontend UI implemented and tested. Ready for deployment.",
        "type": "status",
        "priority": "high",
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "status": "unread"
    }
    
    with open(messages_file, 'w') as f:
        json.dump(messages, f, indent=2)
    
    print(f"   ✅ Tech-lead reported to scrum-master")
    
    # Summary
    print("\n" + "=" * 50)
    print("✨ DELEGATION CHAIN COMPLETE!")
    print("\nFlow executed:")
    print("  1. Scrum Master → Tech Lead (feature task)")
    print("  2. Tech Lead → Backend Dev (API task)")
    print("  3. Tech Lead → Frontend Dev (UI task)")
    print("  4. Backend Dev → Tech Lead (completion report)")
    print("  5. Frontend Dev → Tech Lead (completion report)")
    print("  6. Tech Lead → Scrum Master (feature complete)")
    
    print(f"\n📁 Tasks stored in: {tasks_file}")
    print(f"📬 Messages stored in: {messages_file}")
    
    return True

if __name__ == "__main__":
    try:
        success = simulate_delegation_chain()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)