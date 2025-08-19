# Agent Army - Backup and Recovery Procedures

> Comprehensive backup strategies and disaster recovery procedures for the Agent Army infrastructure.

## 🛡️ Overview

This document outlines the backup and recovery procedures for maintaining the Agent Army system, ensuring business continuity and data protection.

## 📋 What to Backup

### Critical Components

#### 1. **Agent Configurations** (Priority: Critical)
- `.claude/agents/` - All agent definitions and specifications
- `.claude/agents/agent-registry.json` - Agent hierarchy and coordination rules
- Recovery Time: < 5 minutes
- Backup Frequency: After any agent modification

#### 2. **MCP Server Infrastructure** (Priority: Critical)
- `.claude/mcp/servers/core/` - All MCP server implementations
- MCP server registration configuration
- Python virtual environment dependencies
- Recovery Time: < 15 minutes
- Backup Frequency: After any server modification

#### 3. **Hook System** (Priority: High)
- `.claude/hooks/` - All hook scripts and automation
- `.claude/settings.json` and `.claude/settings.local.json` - Hook configurations
- Recovery Time: < 10 minutes
- Backup Frequency: After any hook modification

#### 4. **Project Documentation** (Priority: High)
- `README.md` and all documentation files
- `.claude/docs/` - Project documentation
- Recovery Time: < 5 minutes
- Backup Frequency: Daily or after documentation updates

#### 5. **Data and Logs** (Priority: Medium)
- `.claude/logs/` - Communication logs and analytics
- `.claude/mcp/data/` - MCP server data storage
- Recovery Time: < 30 minutes
- Backup Frequency: Daily

#### 6. **Configuration Files** (Priority: Critical)
- `.claude/scripts/` - Automation and utility scripts
- Project-level configurations
- Recovery Time: < 5 minutes
- Backup Frequency: After any configuration change

## 🔧 Backup Strategies

### 1. **Git-Based Version Control** (Recommended Primary)

```bash
# Add all critical files to git
git add .claude/agents/ .claude/hooks/ .claude/scripts/
git add .claude/mcp/servers/ .claude/settings*.json
git add README.md docs/ .claude/docs/

# Commit with descriptive message
git commit -m "backup: Agent Army configuration $(date '+%Y-%m-%d %H:%M:%S')"

# Push to remote repository
git push origin main
```

**Advantages:**
- Version history and change tracking
- Distributed backup across multiple locations
- Easy rollback to previous versions
- Collaborative development support

### 2. **Automated Backup Script**

Create automated backup using the provided script:

```bash
# Run daily backup
./.claude/scripts/backup-system.py --type full

# Run incremental backup
./.claude/scripts/backup-system.py --type incremental

# Backup specific components
./.claude/scripts/backup-system.py --components agents,mcp,hooks
```

### 3. **Cloud Storage Integration**

```bash
# Backup to cloud storage (example with AWS S3)
aws s3 sync .claude/ s3://your-bucket/agent-army-backup/$(date +%Y%m%d)/ \
  --exclude "*.pyc" --exclude "__pycache__/*" --exclude "venv/*"

# Backup to Google Drive (using gdrive CLI)
gdrive upload -r .claude/ --parent your-folder-id

# Backup to Dropbox
dropbox_uploader.sh upload .claude/ /AgentArmy/Backups/$(date +%Y%m%d)/
```

### 4. **Database Backup** (If using persistent storage)

```bash
# Backup MCP data storage
cd .claude/mcp/data/
tar -czf "mcp-data-backup-$(date +%Y%m%d).tar.gz" registry/ communication/

# Backup log files
cd .claude/logs/
tar -czf "logs-backup-$(date +%Y%m%d).tar.gz" *.log *.jsonl
```

## 🔄 Automated Backup Script

Create the automated backup system:

```python
#!/usr/bin/env python3
"""
Agent Army Automated Backup System
"""

import os
import sys
import shutil
import tarfile
import datetime
from pathlib import Path

class AgentArmyBackup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / "backups"
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def create_full_backup(self):
        """Create complete system backup"""
        backup_name = f"agent-army-full-{self.timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create tar archive
        with tarfile.open(backup_path, "w:gz") as tar:
            # Add critical directories
            critical_dirs = [
                ".claude/agents",
                ".claude/hooks", 
                ".claude/mcp/servers",
                ".claude/scripts",
                ".claude/docs"
            ]
            
            for dir_path in critical_dirs:
                if Path(dir_path).exists():
                    tar.add(dir_path, arcname=dir_path)
            
            # Add configuration files
            config_files = [
                ".claude/settings.json",
                ".claude/settings.local.json", 
                ".claude/example-hooks-config.json",
                "README.md"
            ]
            
            for file_path in config_files:
                if Path(file_path).exists():
                    tar.add(file_path, arcname=file_path)
        
        return backup_path
```

## 🚨 Disaster Recovery Procedures

### Recovery Scenarios

#### **Scenario 1: Agent Configuration Corruption**

**Symptoms:**
- Agents not responding correctly
- Invalid agent registry errors
- Missing agent definitions

**Recovery Steps:**
1. **Identify the issue:**
   ```bash
   python3 .claude/scripts/validate-environment.py
   ```

2. **Restore from git:**
   ```bash
   git checkout HEAD -- .claude/agents/
   git checkout HEAD -- .claude/agents/agent-registry.json
   ```

3. **Validate restoration:**
   ```bash
   python3 .claude/scripts/validate-environment.py
   ```

4. **Test agent functionality:**
   ```bash
   claude mcp list
   # Test with: "Act as scrum-master and validate system"
   ```

#### **Scenario 2: MCP Server Failure**

**Symptoms:**
- MCP tools not available
- Server connection errors
- Missing tool functions

**Recovery Steps:**
1. **Check server status:**
   ```bash
   claude mcp list
   ```

2. **Re-register MCP servers:**
   ```bash
   ./.claude/scripts/register-mcp-servers.sh
   ```

3. **Restore server files if corrupted:**
   ```bash
   git checkout HEAD -- .claude/mcp/servers/
   ```

4. **Rebuild virtual environment if needed:**
   ```bash
   cd .claude/mcp/
   rm -rf venv/
   python3 -m venv venv
   source venv/bin/activate
   pip install mcp anthropic uvicorn starlette
   ```

#### **Scenario 3: Hook System Malfunction**

**Symptoms:**
- Hooks not executing
- Permission errors
- Invalid hook responses

**Recovery Steps:**
1. **Restore hook scripts:**
   ```bash
   git checkout HEAD -- .claude/hooks/
   chmod +x .claude/hooks/*.py
   ```

2. **Restore hook configuration:**
   ```bash
   git checkout HEAD -- .claude/settings*.json
   ```

3. **Test hook functionality:**
   ```bash
   python3 .claude/hooks/orchestrator.py --test
   python3 .claude/hooks/communication-tracker.py --test
   ```

#### **Scenario 4: Complete System Failure**

**Recovery Steps:**
1. **Clone from backup repository:**
   ```bash
   git clone <your-backup-repo-url> agent-army-recovery
   cd agent-army-recovery
   ```

2. **Restore MCP environment:**
   ```bash
   cd .claude/mcp/
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # If available
   # Or manually install: pip install mcp anthropic uvicorn starlette
   ```

3. **Register MCP servers:**
   ```bash
   ./.claude/scripts/register-mcp-servers.sh
   ```

4. **Validate complete system:**
   ```bash
   python3 .claude/scripts/validate-environment.py
   ```

5. **Test end-to-end functionality:**
   ```bash
   claude mcp list
   # Test agent workflow
   ```

## 🔍 Recovery Validation

After any recovery procedure, run the comprehensive validation:

```bash
# Full system validation
python3 .claude/scripts/validate-environment.py

# Test MCP servers
claude mcp list

# Test hook system
python3 .claude/hooks/orchestrator.py --health-check

# Test agent definitions
ls -la .claude/agents/

# Test a complete workflow
# Example: "Act as scrum-master and create a sample task"
```

## 📅 Backup Schedule Recommendations

### **Daily Backups** (Automated)
- Configuration files
- Log files and analytics data
- Git commit and push

### **Weekly Backups** (Automated)
- Complete system archive
- Cloud storage sync
- Backup verification

### **Monthly Backups** (Manual Review)
- Full system export
- Backup retention cleanup
- Recovery procedure testing
- Documentation updates

## 🛠️ Tools and Scripts

### **Backup Scripts Location:**
```
.claude/scripts/
├── backup-system.py          # Automated backup creation
├── register-mcp-servers.sh   # MCP server registration
├── validate-environment.py   # System validation
└── restore-system.py         # Recovery assistance
```

### **Quick Commands:**
```bash
# Create full backup
.claude/scripts/backup-system.py --full

# Validate system
.claude/scripts/validate-environment.py

# Register MCP servers
.claude/scripts/register-mcp-servers.sh

# Git-based backup
git add . && git commit -m "backup: $(date)" && git push
```

## 🔒 Security Considerations

### **Backup Security:**
1. **Encrypt sensitive backups** before cloud storage
2. **Use secure git repositories** (private repos)
3. **Rotate backup access keys** regularly
4. **Test backup integrity** periodically

### **Access Control:**
1. **Limit backup access** to authorized personnel only
2. **Use service accounts** for automated backups
3. **Monitor backup access** logs
4. **Implement backup versioning** policies

## 📞 Emergency Contacts

### **System Administration:**
- **Primary Contact:** [Your Name] - [Email]
- **Secondary Contact:** [Backup Admin] - [Email]
- **Escalation:** [Manager/Team Lead] - [Email]

### **Recovery Checklist:**
- [ ] Identify failure scope and impact
- [ ] Notify stakeholders if necessary
- [ ] Execute appropriate recovery procedure
- [ ] Validate system functionality
- [ ] Document incident and lessons learned
- [ ] Update procedures if needed

---

**Remember:** Regular backups are useless without tested recovery procedures. Test your recovery processes quarterly to ensure they work when needed.

**Last Updated:** August 2025 | **Version:** 1.0 | **Owner:** Agent Army Team