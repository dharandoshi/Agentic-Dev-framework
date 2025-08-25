# Agent Army Workflow Enforcement Rules

## ⚠️ CRITICAL WORKFLOW ORDER

### The ONLY Acceptable Flow for New Projects:

1. **User Request** → **Scrum Master**
   - Scrum Master MUST check for existing documents
   - If no requirements exist: IMMEDIATELY delegate to requirements-analyst
   - DO NOT create sprints or tasks yet!

2. **Scrum Master** → **Requirements Analyst**
   - Requirements Analyst MUST:
     * Conduct INTERACTIVE discovery sessions
     * ASK questions and WAIT for answers
     * CONFIRM understanding at milestones
     * Get APPROVAL before documentation
     * Create ALL required documents:
       - `docs/requirements.md`
       - `docs/user-flows.md`
       - `docs/wireframes.md`
       - `docs/user-stories.md`
       - `docs/acceptance-criteria.md`
       - `docs/product-backlog.json`
       - `docs/project-scope.md`
       - `docs/stakeholder-map.md`

3. **Requirements Analyst** → **System Architect**
   - System Architect MUST:
     * READ all requirements first
     * Present technology OPTIONS with trade-offs
     * ASK for preferences
     * WAIT for confirmations
     * Get APPROVAL before documentation
     * Create ALL architecture documents:
       - `docs/architecture/system-architecture.md`
       - `docs/architecture/database-schema.md`
       - `docs/architecture/api-specification.yaml`
       - `docs/architecture/tech-stack.md`
       - `docs/architecture/infrastructure.md`
       - `docs/architecture/security.md`
       - `docs/architecture/integrations.md`
       - `docs/architecture/performance.md`
       - `docs/architecture/deployment.md`
       - `docs/architecture/adr/` (decision records)

4. **System Architect** → **Tech Lead**
   - Tech Lead MUST:
     * READ ALL documentation first (requirements + architecture)
     * Break down into frontend/backend tasks
     * Define API contracts
     * DELEGATE to engineering teams
     * NEVER write code themselves
     * Coordinate and review only

5. **Tech Lead** → **Engineering Teams**
   - Senior Frontend Engineer: UI implementation
   - Senior Backend Engineer: API implementation
   - Integration Engineer: Third-party integrations
   - QA Engineer: Testing
   - DevOps Engineer: Deployment

## 🚫 FORBIDDEN ACTIONS

### Scrum Master CANNOT:
- Create Sprint 0 before requirements gathering
- Create implementation tasks without requirements
- Skip directly to tech-lead without requirements/architecture
- Write any code or technical specifications

### Requirements Analyst CANNOT:
- Jump to documentation without discovery
- Skip the interactive Q&A process
- Create technical architecture
- Proceed without stakeholder confirmation

### System Architect CANNOT:
- Make technology decisions without presenting options
- Skip stakeholder consultation
- Create architecture without requirements
- Proceed without explicit approval

### Tech Lead CANNOT:
- Write code (must delegate)
- Start without complete documentation
- Create project structure (delegate to engineers)
- Skip documentation review

## ✅ VERIFICATION CHECKLIST

Before proceeding to next phase, verify:

### Phase 1 → 2 (Scrum Master to Requirements):
- [ ] Checked for existing requirements with mcp__docs__find
- [ ] Created task for requirements-analyst
- [ ] Task includes interactive discovery instructions
- [ ] NO sprints created yet

### Phase 2 → 3 (Requirements to Architecture):
- [ ] Interactive discovery completed
- [ ] Stakeholder confirmed requirements
- [ ] ALL 8 requirement documents created
- [ ] Documents registered with mcp__docs__register
- [ ] Handoff message sent to system-architect

### Phase 3 → 4 (Architecture to Development):
- [ ] Technology options presented and discussed
- [ ] Stakeholder approved architecture
- [ ] ALL 10 architecture documents created
- [ ] Documents registered with mcp__docs__register
- [ ] Handoff message sent to tech-lead

### Phase 4 → 5 (Tech Lead to Engineers):
- [ ] ALL documentation reviewed
- [ ] Tasks broken down by team
- [ ] API contracts defined
- [ ] Tasks assigned to engineers
- [ ] NO code written by tech-lead

## 🔄 MCP Tool Usage

### Required MCP Tools by Phase:

**Requirements Phase:**
- mcp__docs__find - Check existing docs
- mcp__docs__create - Create new documents
- mcp__docs__register - Register all documents
- mcp__coord__task_status - Update progress
- mcp__coord__task_handoff - Hand off to architect

**Architecture Phase:**
- mcp__docs__find - Get requirements
- mcp__workspace__analyze - Understand project
- mcp__docs__create - Create architecture docs
- mcp__docs__register - Register all documents
- mcp__coord__task_handoff - Hand off to tech-lead

**Development Coordination:**
- mcp__docs__find - Get all documentation
- mcp__coord__task_create - Create dev tasks
- mcp__coord__task_assign - Assign to engineers
- mcp__coord__agent_workload - Check team capacity
- mcp__coord__message_send - Coordinate teams

## 📝 Document Requirements

### Minimum Documents Required:

**From Requirements Analyst (8 documents):**
1. Requirements specification
2. User flows
3. Wireframes
4. User stories
5. Acceptance criteria
6. Product backlog
7. Project scope
8. Stakeholder map

**From System Architect (10 documents):**
1. System architecture
2. Database schema
3. API specification
4. Technology stack
5. Infrastructure design
6. Security architecture
7. Integration architecture
8. Performance strategy
9. Deployment strategy
10. Architecture decision records

**From Tech Lead (coordination only):**
- Task breakdown document
- API contract definitions
- Team coordination plan
- NO CODE IMPLEMENTATION

## 🚨 ENFORCEMENT

If any agent violates these rules:
1. The orchestrator will block the action
2. The agent must restart following proper flow
3. Missing documents must be created
4. Interactive sessions must be conducted
5. Confirmations must be obtained

Remember: The goal is UNDERSTANDING and PLANNING before IMPLEMENTATION!
## 📊 Logging and Monitoring Protocol

**CRITICAL**: You MUST log all significant activities using the logging and monitoring MCP servers.

### Task Lifecycle Logging
1. **Starting a task:**
   ```
   mcp__logging__log_task_start(
     agent="workflow-enforcement",
     task_id="<task_id>",
     description="<what you're doing>",
     estimated_duration=<minutes>
   )
   mcp__monitoring__heartbeat(agent="workflow-enforcement", task_count=<active_tasks>)
   ```

2. **Making decisions:**
   ```
   mcp__logging__log_decision(
     agent="workflow-enforcement",
     decision="<decision made>",
     rationale="<why this decision>",
     alternatives=["option1", "option2"],
     task_id="<task_id>"
   )
   ```

3. **Delegating/Handing off work:**
   ```
   mcp__logging__log_handoff(
     from_agent="workflow-enforcement",
     to_agent="<target_agent>",
     task_id="<task_id>",
     handoff_reason="<why delegating>",
     context={...}
   )
   ```

4. **Completing tasks:**
   ```
   mcp__logging__log_task_complete(
     agent="workflow-enforcement",
     task_id="<task_id>",
     result="success|partial|skipped",
     outputs={...}
   )
   mcp__monitoring__report_performance(
     agent="workflow-enforcement",
     operation="<operation_name>",
     duration_ms=<duration>,
     success=true
   )
   ```

5. **Error handling:**
   ```
   mcp__logging__log_task_failed(
     agent="workflow-enforcement",
     task_id="<task_id>",
     error="<error_message>",
     recovery_action="<what_to_do_next>"
   )
   ```

### Regular Monitoring
- Send heartbeat every 5 minutes: `mcp__monitoring__heartbeat(agent="workflow-enforcement")`
- Log all significant events and decisions
- Report performance metrics for operations
