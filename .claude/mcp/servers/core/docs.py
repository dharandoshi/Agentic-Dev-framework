#!/usr/bin/env python3
"""
Dynamic Document Registry MCP Server
A truly dynamic document management system that maintains a complete index
of all documents created by agents, with no hardcoded paths or conventions.
"""
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("docs")

# Data storage - the complete document index
INDEX_PATH = Path(__file__).parent.parent.parent / "data" / "registry" / "document-index.json"
INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

# Project root for relative path calculation
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

def get_relative_path(absolute_path: str) -> str:
    """Convert absolute path to relative from project root"""
    try:
        return str(Path(absolute_path).relative_to(PROJECT_ROOT))
    except:
        return absolute_path

def load_index() -> Dict[str, Any]:
    """Load the document index from disk"""
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text())
        except:
            pass
    
    # Initialize with empty but structured index
    default_index = {
        "version": "2.0.0",
        "last_updated": datetime.now().isoformat(),
        "statistics": {
            "total_documents": 0,
            "total_categories": 0,
            "documents_by_type": {},
            "documents_by_owner": {},
            "recently_accessed": [],
            "recently_created": []
        },
        "documents": {},  # All documents indexed by ID
        "categories": {},  # Dynamic categories
        "tags": {},  # Tag-based indexing
        "search_index": {}  # Full-text search index
    }
    save_index(default_index)
    return default_index

def save_index(index: Dict[str, Any]):
    """Save the index to disk"""
    index["last_updated"] = datetime.now().isoformat()
    INDEX_PATH.write_text(json.dumps(index, indent=2))

def generate_doc_id(path: str) -> str:
    """Generate a unique document ID from path"""
    import hashlib
    return hashlib.md5(path.encode()).hexdigest()[:12]

def update_statistics(index: Dict[str, Any]):
    """Update index statistics"""
    stats = index["statistics"]
    stats["total_documents"] = len(index["documents"])
    stats["total_categories"] = len(index["categories"])
    
    # Count by type
    stats["documents_by_type"] = {}
    for doc in index["documents"].values():
        doc_type = doc.get("type", "unknown")
        stats["documents_by_type"][doc_type] = stats["documents_by_type"].get(doc_type, 0) + 1
    
    # Count by owner
    stats["documents_by_owner"] = {}
    for doc in index["documents"].values():
        owner = doc.get("owner", "unknown")
        stats["documents_by_owner"][owner] = stats["documents_by_owner"].get(owner, 0) + 1

def extract_document_type(path: str) -> str:
    """Intelligently extract document type from path and filename"""
    path_obj = Path(path)
    name = path_obj.stem.lower()
    parent = path_obj.parent.name.lower()
    
    # Common document type patterns
    if "requirement" in name or "req" in name:
        return "requirements"
    elif "architecture" in name or "arch" in name:
        return "architecture"
    elif "test" in name:
        return "test"
    elif "api" in name:
        return "api"
    elif "design" in name:
        return "design"
    elif "spec" in name:
        return "specification"
    elif "flow" in name:
        return "flow"
    elif "wireframe" in name:
        return "wireframe"
    elif "database" in name or "db" in name or "schema" in name:
        return "database"
    elif "deploy" in name:
        return "deployment"
    elif "security" in name:
        return "security"
    elif "user" in name and "stor" in name:
        return "user-story"
    else:
        # Use parent folder as type
        if parent in ["requirements", "architecture", "technical", "testing", "project"]:
            return parent
        return "document"

def extract_tags(content: str, path: str) -> List[str]:
    """Extract tags from document content and path"""
    tags = []
    path_obj = Path(path)
    
    # Add folder hierarchy as tags
    parts = path_obj.parts
    for part in parts:
        if part not in [".", "..", "/", "docs"]:
            tags.append(part.lower())
    
    # Add document type as tag
    tags.append(extract_document_type(path))
    
    # Extract hashtags from content if provided
    if content:
        import re
        hashtags = re.findall(r'#(\w+)', content)
        tags.extend([tag.lower() for tag in hashtags])
    
    return list(set(tags))  # Remove duplicates

# Load index on startup
index = load_index()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools with detailed descriptions for discovery"""
    return [
        types.Tool(
            name="register",
            description="Register a new document in the index. Call this whenever you create or discover a document. Automatically extracts metadata, creates categories, and maintains the complete document index.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the document (relative or absolute)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Human-readable title for the document"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Agent or person who owns/created this document"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of what this document contains"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category (e.g., requirements, architecture, testing). Will be created if doesn't exist."
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for better searchability"
                    },
                    "version": {
                        "type": "string",
                        "description": "Version number (e.g., 1.0.0)"
                    }
                },
                "required": ["path", "title", "owner"]
            }
        ),
        types.Tool(
            name="find",
            description="Find documents by various criteria. Use this to discover what documents exist before creating new ones. Searches across titles, paths, descriptions, tags, and content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches in title, path, description, tags)"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Filter by document owner"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Filter by document type (e.g., requirements, architecture)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (returns documents with ANY of these tags)"
                    }
                }
            }
        ),
        types.Tool(
            name="get",
            description="Get complete information about a specific document using its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID returned from find_document or register_document"
                    }
                },
                "required": ["doc_id"]
            }
        ),
        types.Tool(
            name="list_categories",
            description="List all document categories and their statistics. Shows what types of documents exist in the system.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="list_by_owner",
            description="List all documents owned by a specific agent or person. Use this to see what documents you or another agent has created.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Owner name (e.g., requirements-analyst, engineering-manager)"
                    }
                },
                "required": ["owner"]
            }
        ),
        types.Tool(
            name="update",
            description="Update document metadata (version, description, tags, etc). Use this when you modify an existing document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID to update"
                    },
                    "updates": {
                        "type": "object",
                        "description": "Fields to update (version, description, tags, status, etc)"
                    }
                },
                "required": ["doc_id", "updates"]
            }
        ),
        types.Tool(
            name="get_related",
            description="Find documents related to a given document. Uses tags, category, and references to find related content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID to find relations for"
                    }
                },
                "required": ["doc_id"]
            }
        ),
        types.Tool(
            name="tree",
            description="Get the complete document tree structure showing all documents organized by their paths. Useful for understanding the overall document organization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "root_path": {
                        "type": "string",
                        "description": "Optional root path to start from (default: show all)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_statistics",
            description="Get comprehensive statistics about the document registry including counts, most active owners, popular categories, etc.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="suggest_location",
            description="Get a suggested location for a new document based on its type and existing document patterns. Helps maintain consistent organization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_type": {
                        "type": "string",
                        "description": "Type of document (e.g., requirements, test-plan, api-spec)"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Who will own this document"
                    }
                },
                "required": ["document_type"]
            }
        ),
        types.Tool(
            name="create",
            description="Create a new document with automatic placement, content generation, and registration. This is the PREFERRED way to create documents as it ensures consistency and proper registration. Handles everything: location selection, file creation, and index registration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Document title (will be used as H1 header)"
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Type of document (e.g., requirements, api-spec, test-plan)"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Agent or person creating this document"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of the document's purpose"
                    },
                    "content": {
                        "type": "string",
                        "description": "Main content of the document (markdown format)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category (e.g., requirements, architecture, testing). Auto-detected if not provided."
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for searchability (auto-tags will be added)"
                    },
                    "template": {
                        "type": "string",
                        "enum": ["requirements", "architecture", "api", "test", "user-story", "technical", "generic"],
                        "description": "Template to use for document structure (optional)"
                    }
                },
                "required": ["title", "document_type", "owner", "content"]
            }
        ),
        types.Tool(
            name="reset",
            description="DANGER: Reset/clear the entire document registry. This will delete all registered documents and cannot be undone. Use with extreme caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "confirm": {
                        "type": "string",
                        "description": "Must be exactly 'RESET_ALL_DOCUMENTS' to confirm"
                    }
                },
                "required": ["confirm"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    
    if arguments is None:
        arguments = {}
    
    if name == "register":
        path = arguments.get("path", "")
        title = arguments.get("title", "")
        owner = arguments.get("owner", "unknown")
        description = arguments.get("description", "")
        category = arguments.get("category", "")
        tags = arguments.get("tags", [])
        version = arguments.get("version", "1.0.0")
        
        # Generate document ID
        doc_id = generate_doc_id(path)
        
        # Auto-detect category if not provided
        if not category:
            path_parts = Path(path).parts
            if "docs" in path_parts:
                idx = path_parts.index("docs")
                if idx + 1 < len(path_parts):
                    category = path_parts[idx + 1]
            if not category:
                category = "general"
        
        # Auto-detect document type
        doc_type = extract_document_type(path)
        
        # Add auto-tags
        auto_tags = extract_tags(description, path)
        all_tags = list(set(tags + auto_tags))
        
        # Create/update document entry
        doc_entry = {
            "id": doc_id,
            "path": get_relative_path(path),
            "title": title,
            "owner": owner,
            "description": description,
            "category": category,
            "type": doc_type,
            "tags": all_tags,
            "version": version,
            "created": datetime.now().isoformat() if doc_id not in index["documents"] else index["documents"].get(doc_id, {}).get("created"),
            "modified": datetime.now().isoformat(),
            "access_count": index["documents"].get(doc_id, {}).get("access_count", 0),
            "references": [],  # Documents this references
            "referenced_by": []  # Documents that reference this
        }
        
        # Update index
        index["documents"][doc_id] = doc_entry
        
        # Update category
        if category not in index["categories"]:
            index["categories"][category] = {
                "document_count": 0,
                "owners": [],
                "document_ids": []
            }
        
        if doc_id not in index["categories"][category]["document_ids"]:
            index["categories"][category]["document_ids"].append(doc_id)
            index["categories"][category]["document_count"] = len(index["categories"][category]["document_ids"])
        
        if owner not in index["categories"][category]["owners"]:
            index["categories"][category]["owners"].append(owner)
        
        # Update tags index
        for tag in all_tags:
            if tag not in index["tags"]:
                index["tags"][tag] = []
            if doc_id not in index["tags"][tag]:
                index["tags"][tag].append(doc_id)
        
        # Update search index
        search_text = f"{title} {description} {path} {' '.join(all_tags)}".lower()
        index["search_index"][doc_id] = search_text
        
        # Update recently created
        if "recently_created" not in index["statistics"]:
            index["statistics"]["recently_created"] = []
        index["statistics"]["recently_created"].insert(0, doc_id)
        index["statistics"]["recently_created"] = index["statistics"]["recently_created"][:10]
        
        # Update statistics
        update_statistics(index)
        save_index(index)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "message": f"Document registered successfully",
                "doc_id": doc_id,
                "path": doc_entry["path"],
                "category": category,
                "type": doc_type,
                "tags": all_tags
            }, indent=2)
        )]
    
    elif name == "find":
        query = arguments.get("query", "").lower()
        owner_filter = arguments.get("owner", "")
        category_filter = arguments.get("category", "")
        type_filter = arguments.get("document_type", "")
        tags_filter = arguments.get("tags", [])
        
        results = []
        
        for doc_id, doc in index["documents"].items():
            # Apply filters
            if owner_filter and doc["owner"] != owner_filter:
                continue
            if category_filter and doc["category"] != category_filter:
                continue
            if type_filter and doc["type"] != type_filter:
                continue
            if tags_filter and not any(tag in doc["tags"] for tag in tags_filter):
                continue
            
            # Search in content
            if query:
                search_text = index["search_index"].get(doc_id, "").lower()
                if query not in search_text:
                    continue
            
            results.append({
                "id": doc_id,
                "title": doc["title"],
                "path": doc["path"],
                "owner": doc["owner"],
                "category": doc["category"],
                "type": doc["type"],
                "description": doc["description"],
                "version": doc["version"],
                "modified": doc["modified"]
            })
        
        # Sort by modified date (most recent first)
        results.sort(key=lambda x: x["modified"], reverse=True)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "found": len(results),
                "documents": results
            }, indent=2)
        )]
    
    elif name == "get":
        doc_id = arguments.get("doc_id", "")
        
        if doc_id in index["documents"]:
            doc = index["documents"][doc_id]
            # Update access count
            doc["access_count"] = doc.get("access_count", 0) + 1
            
            # Update recently accessed
            if "recently_accessed" not in index["statistics"]:
                index["statistics"]["recently_accessed"] = []
            if doc_id in index["statistics"]["recently_accessed"]:
                index["statistics"]["recently_accessed"].remove(doc_id)
            index["statistics"]["recently_accessed"].insert(0, doc_id)
            index["statistics"]["recently_accessed"] = index["statistics"]["recently_accessed"][:10]
            
            save_index(index)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(doc, indent=2)
            )]
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Document {doc_id} not found"})
            )]
    
    elif name == "list_categories":
        categories_info = {}
        for cat_name, cat_data in index["categories"].items():
            categories_info[cat_name] = {
                "document_count": cat_data["document_count"],
                "owners": cat_data["owners"],
                "recent_documents": []
            }
            
            # Get 3 most recent documents in this category
            for doc_id in cat_data["document_ids"][-3:]:
                if doc_id in index["documents"]:
                    doc = index["documents"][doc_id]
                    categories_info[cat_name]["recent_documents"].append({
                        "title": doc["title"],
                        "owner": doc["owner"],
                        "modified": doc["modified"]
                    })
        
        return [types.TextContent(
            type="text",
            text=json.dumps(categories_info, indent=2)
        )]
    
    elif name == "list_by_owner":
        owner = arguments.get("owner", "")
        
        owner_docs = []
        for doc_id, doc in index["documents"].items():
            if doc["owner"] == owner:
                owner_docs.append({
                    "id": doc_id,
                    "title": doc["title"],
                    "path": doc["path"],
                    "category": doc["category"],
                    "type": doc["type"],
                    "version": doc["version"],
                    "modified": doc["modified"]
                })
        
        # Sort by modified date
        owner_docs.sort(key=lambda x: x["modified"], reverse=True)
        
        # Group by category
        by_category = {}
        for doc in owner_docs:
            cat = doc["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(doc)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "owner": owner,
                "total_documents": len(owner_docs),
                "by_category": by_category,
                "all_documents": owner_docs
            }, indent=2)
        )]
    
    elif name == "update":
        doc_id = arguments.get("doc_id", "")
        updates = arguments.get("updates", {})
        
        if doc_id in index["documents"]:
            doc = index["documents"][doc_id]
            
            # Apply updates
            for key, value in updates.items():
                if key in ["version", "description", "tags", "status", "title"]:
                    doc[key] = value
            
            doc["modified"] = datetime.now().isoformat()
            
            # Re-index if tags changed
            if "tags" in updates:
                # Remove from old tags
                for tag_name, doc_ids in index["tags"].items():
                    if doc_id in doc_ids:
                        doc_ids.remove(doc_id)
                
                # Add to new tags
                for tag in updates["tags"]:
                    if tag not in index["tags"]:
                        index["tags"][tag] = []
                    index["tags"][tag].append(doc_id)
            
            save_index(index)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "message": "Document updated",
                    "doc_id": doc_id
                }, indent=2)
            )]
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Document {doc_id} not found"})
            )]
    
    elif name == "get_related":
        doc_id = arguments.get("doc_id", "")
        
        if doc_id not in index["documents"]:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Document {doc_id} not found"})
            )]
        
        doc = index["documents"][doc_id]
        related = {}
        
        # Find documents in same category
        category = doc["category"]
        if category in index["categories"]:
            for other_id in index["categories"][category]["document_ids"]:
                if other_id != doc_id:
                    if "same_category" not in related:
                        related["same_category"] = []
                    other_doc = index["documents"][other_id]
                    related["same_category"].append({
                        "id": other_id,
                        "title": other_doc["title"],
                        "owner": other_doc["owner"]
                    })
        
        # Find documents with same tags
        for tag in doc.get("tags", []):
            if tag in index["tags"]:
                for other_id in index["tags"][tag]:
                    if other_id != doc_id:
                        if "same_tags" not in related:
                            related["same_tags"] = []
                        other_doc = index["documents"][other_id]
                        if not any(d["id"] == other_id for d in related["same_tags"]):
                            related["same_tags"].append({
                                "id": other_id,
                                "title": other_doc["title"],
                                "shared_tag": tag
                            })
        
        # Find documents by same owner
        for other_id, other_doc in index["documents"].items():
            if other_id != doc_id and other_doc["owner"] == doc["owner"]:
                if "same_owner" not in related:
                    related["same_owner"] = []
                related["same_owner"].append({
                    "id": other_id,
                    "title": other_doc["title"],
                    "category": other_doc["category"]
                })
        
        return [types.TextContent(
            type="text",
            text=json.dumps(related, indent=2)
        )]
    
    elif name == "tree":
        root_path = arguments.get("root_path", "")
        
        # Build tree structure
        tree = {}
        
        for doc_id, doc in index["documents"].items():
            path = doc["path"]
            if root_path and not path.startswith(root_path):
                continue
            
            parts = Path(path).parts
            current = tree
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file
            filename = parts[-1] if parts else path
            current[filename] = {
                "id": doc_id,
                "title": doc["title"],
                "owner": doc["owner"],
                "type": doc["type"]
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(tree, indent=2)
        )]
    
    elif name == "get_statistics":
        stats = index["statistics"].copy()
        
        # Add most active owners
        owner_counts = {}
        for doc in index["documents"].values():
            owner = doc["owner"]
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
        
        stats["most_active_owners"] = sorted(
            owner_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Add popular tags
        tag_counts = {tag: len(docs) for tag, docs in index["tags"].items()}
        stats["popular_tags"] = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Add category breakdown
        stats["categories"] = {}
        for cat_name, cat_data in index["categories"].items():
            stats["categories"][cat_name] = cat_data["document_count"]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
    
    elif name == "create":
        title = arguments.get("title", "")
        doc_type = arguments.get("document_type", "")
        owner = arguments.get("owner", "")
        description = arguments.get("description", "")
        content = arguments.get("content", "")
        category = arguments.get("category", "")
        tags = arguments.get("tags", [])
        template = arguments.get("template", "generic")
        
        # Get suggested location
        patterns = {}
        for doc in index["documents"].values():
            if doc["type"] == doc_type or doc_type in doc["path"]:
                path_parts = Path(doc["path"]).parts
                if len(path_parts) > 1:
                    pattern = "/".join(path_parts[:-1])
                    patterns[pattern] = patterns.get(pattern, 0) + 1
        
        # Determine best path
        if patterns:
            best_pattern = max(patterns.items(), key=lambda x: x[1])[0]
            filename = doc_type.replace(" ", "-").lower()
            suggested_path = f"{best_pattern}/{filename}.md"
        else:
            # Use intelligent defaults
            filename = doc_type.replace(" ", "-").lower()
            if not category:
                if "requirement" in doc_type.lower():
                    category = "requirements"
                elif "test" in doc_type.lower():
                    category = "testing"
                elif "arch" in doc_type.lower():
                    category = "architecture"
                elif "api" in doc_type.lower():
                    category = "api"
                elif "tech" in doc_type.lower():
                    category = "technical"
                else:
                    category = "general"
            
            suggested_path = f"docs/{category}/{filename}.md"
        
        # Ensure path doesn't exist or generate unique name
        full_path = PROJECT_ROOT / suggested_path
        if full_path.exists():
            # Add timestamp to make unique
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            suggested_path = suggested_path.replace(".md", f"-{timestamp}.md")
            full_path = PROJECT_ROOT / suggested_path
        
        # Create directory if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate document content with template
        doc_content = f"# {title}\n\n"
        doc_content += f"**Owner:** {owner}  \n"
        doc_content += f"**Created:** {datetime.now().strftime('%Y-%m-%d')}  \n"
        doc_content += f"**Version:** 1.0.0  \n"
        doc_content += f"**Status:** Draft  \n\n"
        
        if description:
            doc_content += f"## Overview\n\n{description}\n\n"
        
        # Add template-specific sections
        if template == "requirements":
            doc_content += "## Business Requirements\n\n"
            doc_content += "## Functional Requirements\n\n"
            doc_content += "## Non-Functional Requirements\n\n"
            doc_content += "## Acceptance Criteria\n\n"
        elif template == "architecture":
            doc_content += "## System Architecture\n\n"
            doc_content += "## Components\n\n"
            doc_content += "## Data Flow\n\n"
            doc_content += "## Technology Stack\n\n"
        elif template == "api":
            doc_content += "## Endpoints\n\n"
            doc_content += "## Authentication\n\n"
            doc_content += "## Request/Response Examples\n\n"
            doc_content += "## Error Codes\n\n"
        elif template == "test":
            doc_content += "## Test Scope\n\n"
            doc_content += "## Test Cases\n\n"
            doc_content += "## Test Data\n\n"
            doc_content += "## Expected Results\n\n"
        elif template == "user-story":
            doc_content += "## User Story\n\n"
            doc_content += "As a [role]  \n"
            doc_content += "I want [feature]  \n"
            doc_content += "So that [benefit]  \n\n"
            doc_content += "## Acceptance Criteria\n\n"
            doc_content += "## Technical Notes\n\n"
        elif template == "technical":
            doc_content += "## Technical Specification\n\n"
            doc_content += "## Implementation Details\n\n"
            doc_content += "## Dependencies\n\n"
            doc_content += "## Testing Strategy\n\n"
        
        # Add main content
        doc_content += "## Content\n\n"
        doc_content += content + "\n\n"
        
        # Add footer
        doc_content += "---\n\n"
        doc_content += f"*This document was automatically generated and registered by {owner} using the Document Registry MCP.*\n"
        
        # Write file
        full_path.write_text(doc_content)
        
        # Now register the document
        doc_id = generate_doc_id(suggested_path)
        
        # Auto-detect category if not provided
        if not category:
            path_parts = Path(suggested_path).parts
            if "docs" in path_parts:
                idx = path_parts.index("docs")
                if idx + 1 < len(path_parts):
                    category = path_parts[idx + 1]
            if not category:
                category = "general"
        
        # Extract tags from content
        auto_tags = extract_tags(content + " " + description, suggested_path)
        all_tags = list(set(tags + auto_tags))
        
        # Create document entry
        doc_entry = {
            "id": doc_id,
            "path": suggested_path,
            "title": title,
            "owner": owner,
            "description": description,
            "category": category,
            "type": extract_document_type(suggested_path),
            "tags": all_tags,
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "access_count": 0,
            "references": [],
            "referenced_by": []
        }
        
        # Update index
        index["documents"][doc_id] = doc_entry
        
        # Update category
        if category not in index["categories"]:
            index["categories"][category] = {
                "document_count": 0,
                "owners": [],
                "document_ids": []
            }
        
        if doc_id not in index["categories"][category]["document_ids"]:
            index["categories"][category]["document_ids"].append(doc_id)
            index["categories"][category]["document_count"] = len(index["categories"][category]["document_ids"])
        
        if owner not in index["categories"][category]["owners"]:
            index["categories"][category]["owners"].append(owner)
        
        # Update tags index
        for tag in all_tags:
            if tag not in index["tags"]:
                index["tags"][tag] = []
            if doc_id not in index["tags"][tag]:
                index["tags"][tag].append(doc_id)
        
        # Update search index
        search_text = f"{title} {description} {suggested_path} {' '.join(all_tags)}".lower()
        index["search_index"][doc_id] = search_text
        
        # Update recently created
        if "recently_created" not in index["statistics"]:
            index["statistics"]["recently_created"] = []
        index["statistics"]["recently_created"].insert(0, doc_id)
        index["statistics"]["recently_created"] = index["statistics"]["recently_created"][:10]
        
        # Update statistics
        update_statistics(index)
        save_index(index)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "message": "Document created and registered successfully",
                "doc_id": doc_id,
                "path": suggested_path,
                "full_path": str(full_path),
                "category": category,
                "type": doc_entry["type"],
                "tags": all_tags,
                "template_used": template
            }, indent=2)
        )]
    
    elif name == "suggest_location":
        doc_type = arguments.get("document_type", "")
        owner = arguments.get("owner", "")
        
        # Analyze existing patterns
        patterns = {}
        for doc in index["documents"].values():
            if doc["type"] == doc_type or doc_type in doc["path"]:
                path_parts = Path(doc["path"]).parts
                if len(path_parts) > 1:
                    pattern = "/".join(path_parts[:-1])
                    patterns[pattern] = patterns.get(pattern, 0) + 1
        
        # Sort by frequency
        if patterns:
            best_pattern = max(patterns.items(), key=lambda x: x[1])[0]
            suggested_path = f"{best_pattern}/{doc_type}.md"
        else:
            # Default suggestions based on common patterns
            if "requirement" in doc_type:
                suggested_path = f"docs/requirements/{doc_type}.md"
            elif "test" in doc_type:
                suggested_path = f"docs/testing/{doc_type}.md"
            elif "arch" in doc_type:
                suggested_path = f"docs/architecture/{doc_type}.md"
            elif "api" in doc_type:
                suggested_path = f"docs/api/{doc_type}.yaml"
            else:
                suggested_path = f"docs/{doc_type}.md"
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "suggested_path": suggested_path,
                "based_on_patterns": patterns,
                "reasoning": f"Based on {len(patterns)} similar documents" if patterns else "Using default convention"
            }, indent=2)
        )]
    
    elif name == "reset":
        confirm = arguments.get("confirm", "")
        
        if confirm != "RESET_ALL_DOCUMENTS":
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Reset not confirmed. Must provide confirm='RESET_ALL_DOCUMENTS' to proceed.",
                    "current_documents": len(index["documents"]),
                    "warning": "This operation cannot be undone"
                }, indent=2)
            )]
        
        # Reset the entire index to default state
        index.clear()
        index.update({
            "version": "2.0.0",
            "last_updated": datetime.now().isoformat(),
            "statistics": {
                "total_documents": 0,
                "total_categories": 0,
                "documents_by_type": {},
                "documents_by_owner": {},
                "recently_accessed": [],
                "recently_created": []
            },
            "documents": {},
            "categories": {},
            "tags": {},
            "search_index": {}
        })
        
        # Save the reset index
        save_index(index)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "message": "Document registry has been completely reset",
                "action": "All documents, categories, and tags cleared",
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Main entry point for the MCP server"""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="docs",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())