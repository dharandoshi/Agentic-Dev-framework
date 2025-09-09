# Shared Logging Protocol for All Agents

## 📊 CRITICAL: Human-Readable Logging Requirements

**YOU MUST log all significant activities using the MCP logging server in a way that humans can easily understand.**

### When to Log File Operations

**ALWAYS log file operations BEFORE performing them:**

1. **Reading a file:**
   ```python
   mcp__logging__log_file_operation(
     agent="your-agent-name",
     operation="read",
     file_path="/path/to/file",
     task_id="current_task_id"
   )
   ```

2. **Writing a file:**
   ```python
   mcp__logging__log_file_operation(
     agent="your-agent-name",
     operation="write",
     file_path="/path/to/file",
     details="Created new component",
     task_id="current_task_id"
   )
   ```

3. **Editing a file:**
   ```python
   mcp__logging__log_file_operation(
     agent="your-agent-name",
     operation="edit",
     file_path="/path/to/file",
     details="Added authentication logic",
     task_id="current_task_id"
   )
   ```

### When to Log Tool Usage

**Log significant tool usage:**
```python
mcp__logging__log_tool_use(
  agent="your-agent-name",
  tool_name="mcp__workspace__analyze",
  success=True,
  duration_ms=1500,
  task_id="current_task_id"
)
```

### When to Log Decisions

**Log important technical or business decisions:**
```python
mcp__logging__log_decision(
  agent="your-agent-name",
  decision="Selected PostgreSQL over MongoDB",
  rationale="Need ACID compliance for financial transactions",
  alternatives=["MongoDB", "MySQL"],
  task_id="current_task_id"
)
```

### Task Lifecycle Logging

1. **Starting a task:**
   ```python
   # Get timestamp and estimate completion
   start_time = mcp__utilities__get_current_time(format="iso")
   estimated_completion = mcp__utilities__calculate_date(
     base_date="now",
     operation="add",
     minutes=30
   )
   
   mcp__logging__log_task_start(
     agent="your-agent-name",
     task_id="task_id",
     description="Brief description of what you're doing",
     estimated_duration=30
   )
   ```

2. **Completing a task:**
   ```python
   # Calculate actual duration
   duration = mcp__utilities__date_difference(
     start_date=start_time,
     end_date="now",
     unit="minutes"
   )
   
   mcp__logging__log_task_complete(
     agent="your-agent-name",
     task_id="task_id",
     result="success",
     outputs={"files_created": 3, "tests_passed": 10, "duration_minutes": duration}
   )
   ```

3. **Task failure:**
   ```python
   mcp__logging__log_task_failed(
     agent="your-agent-name",
     task_id="task_id",
     error="Connection timeout to database",
     recovery_action="Retry with increased timeout"
   )
   ```

### What Gets Logged (Human-Readable Format)

The logs appear in `.claude/logs/agents_YYYYMMDD.log` like this:

```
[2025-01-09 10:15:24] REQUIREMENTS     | FILE READ     | docs/existing-requirements.md
[2025-01-09 10:16:12] REQUIREMENTS     | FILE WRITE    | docs/project-brief.md
[2025-01-09 10:18:45] REQUIREMENTS     | FILE EDIT     | docs/prd.md - Added functional requirements
[2025-01-09 10:20:20] SYSTEM-ARCH      | DECISION      | Selected PostgreSQL for ACID compliance
[2025-01-09 10:21:20] SR-BACKEND       | FILE WRITE    | src/api/payment-controller.js
```

### Logging Best Practices

1. **Be Concise**: Keep messages under 80 characters
2. **Be Specific**: Include file paths, component names, decision outcomes
3. **Log Actions, Not Intentions**: Log when you DO something, not when you're about to
4. **Include Context**: Add task IDs to trace work across agents
5. **Log Failures**: Always log errors with recovery actions

### Example Logging Flow with Time Tracking

```python
# 0. Track start time
task_start_time = mcp__utilities__get_current_time(format="iso")
log_timestamp = mcp__utilities__format_timestamp(timestamp="now", purpose="log")

# 1. Start task with time estimate
mcp__logging__log_task_start(agent="senior-backend-engineer", task_id="BE-001", 
                             description=f"{log_timestamp} Implement payment API", 
                             estimated_duration=45)

# 2. Read specification
mcp__logging__log_file_operation(agent="senior-backend-engineer", operation="read",
                                 file_path="docs/api-spec.yaml", task_id="BE-001")

# 3. Make decision with timestamp
decision_time = mcp__utilities__get_current_time(format="readable")
mcp__logging__log_decision(agent="senior-backend-engineer", 
                          decision=f"Use Express.js for API (decided at {decision_time})",
                          rationale="Team familiarity and good ecosystem",
                          alternatives=["Fastify", "Koa"], task_id="BE-001")

# 4. Write code
mcp__logging__log_file_operation(agent="senior-backend-engineer", operation="write",
                                 file_path="src/api/payment.js", 
                                 details="Payment endpoints", task_id="BE-001")

# 5. Use validation tool
mcp__logging__log_tool_use(agent="senior-backend-engineer", 
                          tool_name="mcp__validation__lint",
                          success=True, duration_ms=500, task_id="BE-001")

# 6. Complete task with duration
task_duration = mcp__utilities__date_difference(
    start_date=task_start_time,
    end_date="now",
    unit="minutes"
)
mcp__logging__log_task_complete(agent="senior-backend-engineer", task_id="BE-001",
                               result="success", 
                               outputs={"endpoints": 5, "tests": 12, "duration": task_duration})
```

## IMPORTANT: This logging helps humans understand:
- What files each agent is working on
- What decisions were made and why
- How long tasks are taking
- Where problems occurred
- The flow of work between agents