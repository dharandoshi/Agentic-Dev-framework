# Document Management Utilities

## Overview
Shared utility functions for document management that all agents can use directly without spawning a separate agent.

## Core Functions

### 1. get_document_path(document_type)
Returns the current path for any document type.

**Usage:**
```python
# In any agent:
api_spec_path = get_document_path("api_specification")
# Returns: "docs/architecture/api-spec.yaml"
```

### 2. register_document(category, doc_type, path, version)
Registers or updates a document in the registry.

**Usage:**
```python
register_document(
    category="technical",
    doc_type="api_contracts", 
    path="docs/technical/api-contracts/user-api.yaml",
    version="1.0.0"
)
```

### 3. find_documents_by_owner(agent_name)
Returns all documents owned by a specific agent.

**Usage:**
```python
my_docs = find_documents_by_owner("tech-lead")
# Returns list of documents with paths
```

### 4. get_related_documents(document_type)
Returns related documents that might be useful.

**Usage:**
```python
related = get_related_documents("api_specification")
# Returns: ["api_contracts", "technical_specs", "database_schema"]
```

## Implementation Pattern - Safe & Restricted Approach

### Philosophy: Fail Gracefully, Never Break

Agents should:
1. **READ** the registry if it exists
2. **FALLBACK** to conventions if registry missing or incomplete  
3. **UPDATE** only existing entries (don't create new structure)
4. **ONLY** document owners can add new entries

```python
# Safe implementation with fallbacks
registry_path = "/.claude/agents/document-registry.json"

def get_document_path(doc_type):
    """
    Safely get document path - READ ONLY operation.
    Falls back to conventions if registry unavailable.
    """
    try:
        if file_exists(registry_path):
            registry = json.parse(Read(registry_path))
            # Search all categories for document
            for cat_name, cat_data in registry["document_categories"].items():
                docs = cat_data.get("documents", {})
                if doc_type in docs:
                    path = docs[doc_type].get("current_path")
                    if path:
                        return path
    except:
        pass  # Fallback to convention
    
    # Use conventional path as fallback
    return get_conventional_path(doc_type)

def get_conventional_path(doc_type):
    """
    Returns standard path based on document type.
    This ensures system works even without registry.
    """
    conventions = {
        "requirements": "docs/requirements/requirements.md",
        "user_flows": "docs/requirements/user-flows.md",
        "wireframes": "docs/requirements/wireframes.md",
        "architecture": "docs/architecture/architecture.md",
        "database_schema": "docs/architecture/database-schema.sql",
        "api_specification": "docs/architecture/api-spec.yaml",
        "technical_specs": "docs/technical/technical-specifications.md",
        "api_contracts": "docs/technical/api-contracts/",
        "test_plan": "docs/testing/test-plan.md",
        "bug_reports": "docs/testing/bugs/"
    }
    return conventions.get(doc_type, f"docs/general/{doc_type}.md")

def register_document(category, doc_type, path, version, owner_only=True):
    """
    Update existing document entry - RESTRICTED operation.
    Only updates if entry exists, unless you're the owner.
    """
    try:
        if not file_exists(registry_path):
            # Don't create registry - let system admin handle it
            return False
            
        registry = json.parse(Read(registry_path))
        
        # Check if structure exists
        if category not in registry["document_categories"]:
            return False  # Don't create new categories
            
        if doc_type not in registry["document_categories"][category]["documents"]:
            # Only owner can add new document types
            if owner_only:
                current_agent = get_current_agent_name()
                category_owner = registry["document_categories"][category].get("owner")
                if current_agent != category_owner:
                    return False  # Not authorized to add
        
        # Update existing entry (always allowed for existing docs)
        registry["document_categories"][category]["documents"][doc_type]["current_path"] = path
        registry["document_categories"][category]["documents"][doc_type]["version"] = version
        registry["document_categories"][category]["documents"][doc_type]["last_modified"] = current_timestamp()
        
        Write(registry_path, json.stringify(registry))
        return True
        
    except:
        return False  # Fail silently, continue with conventions
```

## Benefits Over Document-Manager Agent

1. **Zero Overhead** - Direct file operations, no agent spawning
2. **Instant Access** - No inter-agent communication delay
3. **Simpler** - Just function calls, not message passing
4. **Efficient** - No LLM tokens used for simple lookups
5. **Reliable** - No agent availability issues

## Usage in Agents

Instead of:
```json
// Query document-manager agent
{
  "to": "document-manager",
  "action": "query",
  "search_term": "api_specification"
}
// Wait for response...
```

Agents would simply:
```python
# Direct utility function call
api_path = get_document_path("api_specification")
# Instant result: "docs/architecture/api-spec.yaml"
```

## Migration Path

1. Keep document-registry.json as the source of truth
2. Remove document-manager agent
3. Each agent directly reads/writes the registry
4. Use utility functions for common operations
5. No inter-agent communication needed for documents

## Registry File Locking

To prevent conflicts when multiple agents write:
```python
def safe_update_registry(update_function):
    # Read current state
    registry = json.parse(Read(registry_path))
    
    # Apply update
    updated_registry = update_function(registry)
    
    # Write atomically
    Write(registry_path, json.stringify(updated_registry))
```

## Standard Document Paths

All agents should follow these conventions:
```
docs/
├── requirements/     # Owner: requirements-analyst
├── architecture/     # Owner: system-architect  
├── technical/        # Owner: tech-lead
├── testing/          # Owner: qa-engineer
├── project/          # Owner: scrum-master
├── security/         # Owner: security-engineer
├── deployment/       # Owner: devops-engineer
└── api/             # Owner: technical-writer
```

## Error Handling & Fallback Strategy

### Principle: System Should Never Break Due to Missing Registry

```python
def get_document_path_safe(doc_type, fallback=None):
    """
    Three-tier fallback strategy:
    1. Try registry
    2. Use conventions
    3. Use provided fallback
    """
    # Tier 1: Registry
    path = get_document_path(doc_type)
    if path and file_exists(path):
        return path
    
    # Tier 2: Conventional path
    conventional = get_conventional_path(doc_type)
    if file_exists(conventional):
        return conventional
        
    # Tier 3: Provided fallback or generic
    return fallback or f"docs/general/{doc_type}.md"
```

### Registry Permissions

| Action | Who Can Do It | When |
|--------|--------------|------|
| Read registry | All agents | Always |
| Update existing entry | Entry owner | When document moves/updates |
| Add new entry | Category owner only | When creating new doc type |
| Create registry | Tech-lead or system init | Project setup only |
| Delete entry | Never | Entries are only deprecated |

### Fallback Behavior Matrix

| Scenario | Agent Action | Result |
|----------|-------------|--------|
| Registry missing | get_document_path() | Returns conventional path |
| Registry corrupted | get_document_path() | Returns conventional path |
| Document not in registry | get_document_path() | Returns conventional path |
| Can't write to registry | register_document() | Fails silently, continues |
| Not authorized to add | register_document() | Returns false, continues |