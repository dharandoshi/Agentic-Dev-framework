#!/usr/bin/env python3
"""
Scrum Ceremony Automation Tools
Automates standups, retrospectives, reviews, and planning
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import random

class CeremonyAutomation:
    """Automate Scrum ceremonies"""
    
    def __init__(self):
        # Find project root dynamically
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / '.claude').exists():
                project_root = current_dir
                break
            current_dir = current_dir.parent
        else:
            project_root = Path.cwd()
        
        self.data_dir = project_root / ".claude" / "mcp" / "data" / "project-management"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.ceremonies_file = self.data_dir / "ceremonies.json"
        self.standup_file = self.data_dir / "daily-standups.json"
        self.retro_file = self.data_dir / "retrospectives.json"
        
    async def daily_standup_create(self, sprint_id: str, attendees: List[str]) -> Dict:
        """Create daily standup record"""
        standup_template = {
            "id": f"standup-{datetime.now().strftime('%Y%m%d')}",
            "sprint_id": sprint_id,
            "date": datetime.now().isoformat(),
            "attendees": attendees,
            "updates": {},
            "blockers": [],
            "helps_needed": [],
            "duration_minutes": 15
        }
        
        # Generate standup questions for each attendee
        questions = [
            "What did you complete yesterday?",
            "What will you work on today?",
            "Are there any blockers?"
        ]
        
        for attendee in attendees:
            standup_template["updates"][attendee] = {
                "yesterday": None,
                "today": None,
                "blockers": None
            }
        
        # Save standup
        standups = []
        if self.standup_file.exists():
            with open(self.standup_file, 'r') as f:
                standups = json.load(f)
        
        standups.append(standup_template)
        
        with open(self.standup_file, 'w') as f:
            json.dump(standups, f, indent=2)
        
        return {
            "success": True,
            "standup_id": standup_template["id"],
            "questions": questions,
            "attendees": attendees
        }
    
    async def standup_update(self, standup_id: str, attendee: str, 
                            yesterday: str, today: str, blockers: Optional[str] = None) -> Dict:
        """Update standup with attendee's status"""
        if not self.standup_file.exists():
            return {"success": False, "error": "No standups found"}
        
        with open(self.standup_file, 'r') as f:
            standups = json.load(f)
        
        for standup in standups:
            if standup["id"] == standup_id:
                if attendee in standup["updates"]:
                    standup["updates"][attendee] = {
                        "yesterday": yesterday,
                        "today": today,
                        "blockers": blockers
                    }
                    
                    if blockers:
                        standup["blockers"].append({
                            "reporter": attendee,
                            "blocker": blockers,
                            "reported_at": datetime.now().isoformat()
                        })
                    
                    with open(self.standup_file, 'w') as f:
                        json.dump(standups, f, indent=2)
                    
                    return {"success": True, "message": "Standup updated"}
        
        return {"success": False, "error": "Standup not found"}
    
    async def retrospective_create(self, sprint_id: str, sprint_number: int) -> Dict:
        """Create sprint retrospective"""
        retro_template = {
            "id": f"retro-sprint-{sprint_number}",
            "sprint_id": sprint_id,
            "sprint_number": sprint_number,
            "date": datetime.now().isoformat(),
            "went_well": [],
            "could_improve": [],
            "action_items": [],
            "kudos": [],
            "metrics": {
                "team_happiness": None,
                "velocity_achieved": None,
                "goals_met": None
            }
        }
        
        # Retrospective prompts
        prompts = {
            "went_well": "What went well this sprint?",
            "could_improve": "What could be improved?",
            "action_items": "What specific actions should we take?",
            "kudos": "Who deserves recognition?"
        }
        
        # Save retrospective
        retros = []
        if self.retro_file.exists():
            with open(self.retro_file, 'r') as f:
                retros = json.load(f)
        
        retros.append(retro_template)
        
        with open(self.retro_file, 'w') as f:
            json.dump(retros, f, indent=2)
        
        return {
            "success": True,
            "retro_id": retro_template["id"],
            "prompts": prompts
        }
    
    async def retrospective_add_item(self, retro_id: str, category: str, 
                                    item: str, reporter: str) -> Dict:
        """Add item to retrospective"""
        if not self.retro_file.exists():
            return {"success": False, "error": "No retrospectives found"}
        
        with open(self.retro_file, 'r') as f:
            retros = json.load(f)
        
        for retro in retros:
            if retro["id"] == retro_id:
                if category in retro:
                    retro[category].append({
                        "item": item,
                        "reporter": reporter,
                        "votes": 0,
                        "added_at": datetime.now().isoformat()
                    })
                    
                    with open(self.retro_file, 'w') as f:
                        json.dump(retros, f, indent=2)
                    
                    return {"success": True, "message": f"Added to {category}"}
        
        return {"success": False, "error": "Retrospective not found"}
    
    async def sprint_review_prepare(self, sprint_id: str, completed_items: List[str]) -> Dict:
        """Prepare sprint review presentation"""
        review = {
            "id": f"review-{sprint_id}",
            "sprint_id": sprint_id,
            "date": datetime.now().isoformat(),
            "completed_items": completed_items,
            "demo_order": [],
            "stakeholder_feedback": [],
            "acceptance_status": {}
        }
        
        # Generate demo order
        for item in completed_items:
            review["demo_order"].append({
                "item": item,
                "presenter": None,
                "duration_minutes": 5,
                "demo_notes": None
            })
            review["acceptance_status"][item] = "pending"
        
        # Review agenda
        agenda = [
            "1. Sprint Goal Review (5 min)",
            "2. Completed Work Demo (20 min)",
            "3. Metrics Review (5 min)",
            "4. Stakeholder Feedback (10 min)",
            "5. Next Sprint Preview (5 min)"
        ]
        
        return {
            "success": True,
            "review_id": review["id"],
            "agenda": agenda,
            "demo_items": len(completed_items),
            "total_duration_minutes": 45
        }
    
    async def planning_poker_session(self, stories: List[Dict]) -> Dict:
        """Facilitate planning poker estimation"""
        poker_values = [1, 2, 3, 5, 8, 13, 21, 34]
        
        session = {
            "id": f"poker-{datetime.now().strftime('%Y%m%d%H%M')}",
            "date": datetime.now().isoformat(),
            "stories": [],
            "total_points": 0
        }
        
        for story in stories:
            # Simulate team estimation
            estimates = {
                "developer_1": random.choice(poker_values),
                "developer_2": random.choice(poker_values),
                "qa_engineer": random.choice(poker_values),
                "tech_lead": random.choice(poker_values)
            }
            
            # Calculate consensus (median)
            values = list(estimates.values())
            values.sort()
            consensus = values[len(values)//2]
            
            session["stories"].append({
                "story_id": story.get("id"),
                "title": story.get("title"),
                "estimates": estimates,
                "consensus": consensus,
                "discussion_notes": None
            })
            
            session["total_points"] += consensus
        
        return {
            "success": True,
            "session_id": session["id"],
            "estimated_stories": len(stories),
            "total_points": session["total_points"],
            "session_data": session
        }
    
    async def ceremony_schedule(self, sprint_number: int, start_date: str, 
                               duration_weeks: int = 2) -> Dict:
        """Generate ceremony schedule for sprint"""
        start = datetime.fromisoformat(start_date)
        
        schedule = {
            "sprint_number": sprint_number,
            "ceremonies": []
        }
        
        # Sprint Planning (Day 1)
        schedule["ceremonies"].append({
            "type": "sprint_planning",
            "date": start.isoformat(),
            "duration_hours": 4,
            "attendees": ["scrum-master", "engineering-manager", "team"],
            "location": "Main Conference Room"
        })
        
        # Daily Standups (Every weekday)
        for day in range(duration_weeks * 7):
            current_date = start + timedelta(days=day)
            if current_date.weekday() < 5:  # Monday to Friday
                schedule["ceremonies"].append({
                    "type": "daily_standup",
                    "date": current_date.replace(hour=9, minute=0).isoformat(),
                    "duration_minutes": 15,
                    "attendees": ["team"],
                    "location": "Team Area"
                })
        
        # Sprint Review (Last day - 1)
        review_date = start + timedelta(days=(duration_weeks * 7) - 1)
        schedule["ceremonies"].append({
            "type": "sprint_review",
            "date": review_date.replace(hour=14, minute=0).isoformat(),
            "duration_hours": 1,
            "attendees": ["team", "stakeholders"],
            "location": "Demo Room"
        })
        
        # Sprint Retrospective (Last day)
        retro_date = start + timedelta(days=(duration_weeks * 7) - 1)
        schedule["ceremonies"].append({
            "type": "sprint_retrospective",
            "date": retro_date.replace(hour=15, minute=30).isoformat(),
            "duration_hours": 1.5,
            "attendees": ["team"],
            "location": "Team Room"
        })
        
        return {
            "success": True,
            "sprint_number": sprint_number,
            "total_ceremonies": len(schedule["ceremonies"]),
            "schedule": schedule
        }

# Integration with PM Server
async def handle_ceremony_request(request: Dict) -> Dict:
    """Handle ceremony automation requests"""
    automation = CeremonyAutomation()
    
    tool = request.get("tool")
    params = request.get("params", {})
    
    handlers = {
        "daily_standup_create": lambda: automation.daily_standup_create(**params),
        "standup_update": lambda: automation.standup_update(**params),
        "retrospective_create": lambda: automation.retrospective_create(**params),
        "retrospective_add_item": lambda: automation.retrospective_add_item(**params),
        "sprint_review_prepare": lambda: automation.sprint_review_prepare(**params),
        "planning_poker_session": lambda: automation.planning_poker_session(**params),
        "ceremony_schedule": lambda: automation.ceremony_schedule(**params)
    }
    
    handler = handlers.get(tool)
    if handler:
        result = await handler()
        return {"success": True, "result": result}
    
    return {"success": False, "error": f"Unknown ceremony tool: {tool}"}