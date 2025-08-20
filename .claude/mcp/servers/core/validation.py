#!/usr/bin/env python3
"""
Validation MCP Server - Universal Code Validation
Provides real-time code validation, linting, and formatting for any language
"""
import json
import asyncio
import os
import re
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("validation")

# Get project root from environment or use current directory
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", os.getcwd()))

class CodeValidator:
    """Universal code validator that adapts to any language/framework"""
    
    def __init__(self, root: Path):
        self.root = root
        self.detected_tools = self._detect_validation_tools()
    
    def _detect_validation_tools(self) -> Dict[str, Any]:
        """Detect available validation tools in the project"""
        tools = {
            "linters": [],
            "formatters": [],
            "type_checkers": [],
            "syntax_checkers": [],
            "package_manager": None
        }
        
        # JavaScript/TypeScript tools
        if (self.root / "package.json").exists():
            tools["package_manager"] = "npm"
            
            # Check for ESLint
            eslint_configs = [".eslintrc.js", ".eslintrc.json", ".eslintrc.yml", ".eslintrc.yaml", ".eslintrc"]
            if any((self.root / config).exists() for config in eslint_configs):
                tools["linters"].append("eslint")
            
            # Check for Prettier
            prettier_configs = [".prettierrc", ".prettierrc.json", ".prettierrc.yml", ".prettierrc.yaml", ".prettierrc.js", "prettier.config.js"]
            if any((self.root / config).exists() for config in prettier_configs):
                tools["formatters"].append("prettier")
            
            # Check for TypeScript
            if (self.root / "tsconfig.json").exists():
                tools["type_checkers"].append("typescript")
                tools["syntax_checkers"].append("tsc")
        
        # Python tools
        # Exclude tooling and build directories when scanning for Python files
        excluded_dirs = {".claude", ".git", "node_modules", "venv", "env", "__pycache__", 
                        "dist", "build", ".vscode", ".idea", "target", "bin", "obj"}
        
        python_files = [f for f in self.root.glob("*.py") 
                       if not any(excluded in str(f) for excluded in excluded_dirs)]
        
        if not python_files:
            python_files = [f for f in self.root.rglob("*.py") 
                           if not any(excluded in str(f) for excluded in excluded_dirs)]
        
        if python_files:
            # Pylint
            if (self.root / ".pylintrc").exists() or (self.root / "pylintrc").exists():
                tools["linters"].append("pylint")
            
            # Flake8
            if (self.root / ".flake8").exists() or (self.root / "setup.cfg").exists():
                tools["linters"].append("flake8")
            
            # Black
            if (self.root / "pyproject.toml").exists():
                try:
                    content = (self.root / "pyproject.toml").read_text()
                    if "[tool.black]" in content:
                        tools["formatters"].append("black")
                    if "[tool.ruff]" in content:
                        tools["linters"].append("ruff")
                    if "[tool.mypy]" in content:
                        tools["type_checkers"].append("mypy")
                    if "[tool.isort]" in content:
                        tools["formatters"].append("isort")
                except:
                    pass
            
            # Autopep8
            if not tools["formatters"] and python_files:
                tools["formatters"].append("autopep8")
        
        # Go tools
        go_files = [f for f in self.root.glob("*.go") 
                   if not any(excluded in str(f) for excluded in excluded_dirs)]
        if go_files or (self.root / "go.mod").exists():
            tools["formatters"].append("gofmt")
            tools["linters"].append("golint")
            tools["syntax_checkers"].append("go")
        
        # Rust tools
        if (self.root / "Cargo.toml").exists():
            tools["formatters"].append("rustfmt")
            tools["linters"].append("clippy")
            tools["syntax_checkers"].append("rustc")
        
        # Java tools
        java_files = [f for f in self.root.glob("*.java") 
                     if not any(excluded in str(f) for excluded in excluded_dirs)]
        if java_files or (self.root / "pom.xml").exists():
            tools["syntax_checkers"].append("javac")
            if (self.root / ".checkstyle.xml").exists():
                tools["linters"].append("checkstyle")
        
        # Ruby tools
        ruby_files = [f for f in self.root.glob("*.rb") 
                     if not any(excluded in str(f) for excluded in excluded_dirs)]
        if ruby_files or (self.root / "Gemfile").exists():
            if (self.root / ".rubocop.yml").exists():
                tools["linters"].append("rubocop")
        
        return tools
    
    def validate_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validate syntax for any language"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_extension(language), delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            if language in ["python", "py"]:
                # Python syntax check
                result_proc = subprocess.run(
                    ["python", "-m", "py_compile", temp_file],
                    capture_output=True,
                    text=True
                )
                if result_proc.returncode != 0:
                    result["valid"] = False
                    result["errors"].append(result_proc.stderr)
            
            elif language in ["javascript", "js"]:
                # Try Node.js syntax check
                check_code = f"try {{ require('vm').compileFunction(require('fs').readFileSync('{temp_file}', 'utf8')); console.log('Valid'); }} catch(e) {{ console.error(e.message); process.exit(1); }}"
                result_proc = subprocess.run(
                    ["node", "-e", check_code],
                    capture_output=True,
                    text=True
                )
                if result_proc.returncode != 0:
                    result["valid"] = False
                    result["errors"].append(result_proc.stdout + result_proc.stderr)
            
            elif language in ["typescript", "ts"]:
                if "tsc" in self.detected_tools["syntax_checkers"]:
                    result_proc = subprocess.run(
                        ["npx", "tsc", "--noEmit", temp_file],
                        capture_output=True,
                        text=True,
                        cwd=self.root
                    )
                    if result_proc.returncode != 0:
                        result["valid"] = False
                        result["errors"].append(result_proc.stdout)
            
            elif language in ["go"]:
                result_proc = subprocess.run(
                    ["go", "fmt", temp_file],
                    capture_output=True,
                    text=True
                )
                if result_proc.returncode != 0:
                    result["valid"] = False
                    result["errors"].append(result_proc.stderr)
            
            elif language in ["rust", "rs"]:
                result_proc = subprocess.run(
                    ["rustc", "--edition", "2021", "--crate-type", "lib", "--emit=mir", "-o", "/dev/null", temp_file],
                    capture_output=True,
                    text=True
                )
                if result_proc.returncode != 0:
                    result["valid"] = False
                    # Parse rust compiler errors
                    for line in result_proc.stderr.split('\n'):
                        if 'error' in line.lower():
                            result["errors"].append(line)
                        elif 'warning' in line.lower():
                            result["warnings"].append(line)
            
            elif language in ["java"]:
                result_proc = subprocess.run(
                    ["javac", "-Xlint:all", temp_file],
                    capture_output=True,
                    text=True
                )
                if result_proc.returncode != 0:
                    result["valid"] = False
                    result["errors"].append(result_proc.stderr)
            
            elif language in ["ruby", "rb"]:
                result_proc = subprocess.run(
                    ["ruby", "-c", temp_file],
                    capture_output=True,
                    text=True
                )
                if result_proc.returncode != 0:
                    result["valid"] = False
                    result["errors"].append(result_proc.stderr)
                elif "warning" in result_proc.stderr.lower():
                    result["warnings"].append(result_proc.stderr)
            
            elif language in ["php"]:
                result_proc = subprocess.run(
                    ["php", "-l", temp_file],
                    capture_output=True,
                    text=True
                )
                if result_proc.returncode != 0:
                    result["valid"] = False
                    result["errors"].append(result_proc.stdout + result_proc.stderr)
            
            else:
                result["warnings"].append(f"No syntax checker available for {language}")
        
        except FileNotFoundError as e:
            result["warnings"].append(f"Syntax checker not installed: {str(e)}")
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
            result["valid"] = False
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return result
    
    def lint_code(self, code: str, language: str, fix: bool = False) -> Dict[str, Any]:
        """Lint code using appropriate linter"""
        result = {"success": True, "issues": [], "fixed_code": None}
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_extension(language), delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            if language in ["javascript", "js", "typescript", "ts"] and "eslint" in self.detected_tools["linters"]:
                cmd = ["npx", "eslint", temp_file, "--format", "json"]
                if fix:
                    cmd.append("--fix")
                
                result_proc = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
                
                try:
                    eslint_output = json.loads(result_proc.stdout)
                    if eslint_output and eslint_output[0].get("messages"):
                        for msg in eslint_output[0]["messages"]:
                            result["issues"].append({
                                "line": msg.get("line"),
                                "column": msg.get("column"),
                                "severity": msg.get("severity"),
                                "message": msg.get("message"),
                                "rule": msg.get("ruleId")
                            })
                        result["success"] = False
                except:
                    result["issues"].append({"message": result_proc.stdout + result_proc.stderr})
                
                if fix:
                    with open(temp_file, 'r') as f:
                        result["fixed_code"] = f.read()
            
            elif language in ["python", "py"]:
                if "pylint" in self.detected_tools["linters"]:
                    result_proc = subprocess.run(
                        ["pylint", temp_file, "--output-format=json"],
                        capture_output=True,
                        text=True
                    )
                    try:
                        pylint_output = json.loads(result_proc.stdout)
                        for msg in pylint_output:
                            result["issues"].append({
                                "line": msg.get("line"),
                                "column": msg.get("column"),
                                "type": msg.get("type"),
                                "message": msg.get("message"),
                                "symbol": msg.get("symbol")
                            })
                    except:
                        if result_proc.stdout:
                            result["issues"].append({"message": result_proc.stdout})
                
                elif "flake8" in self.detected_tools["linters"]:
                    result_proc = subprocess.run(
                        ["flake8", temp_file],
                        capture_output=True,
                        text=True
                    )
                    if result_proc.stdout:
                        for line in result_proc.stdout.split('\n'):
                            if line.strip():
                                result["issues"].append({"message": line})
                        result["success"] = False
                
                elif "ruff" in self.detected_tools["linters"]:
                    cmd = ["ruff", "check", temp_file]
                    if fix:
                        cmd.append("--fix")
                    
                    result_proc = subprocess.run(cmd, capture_output=True, text=True)
                    if result_proc.stdout:
                        for line in result_proc.stdout.split('\n'):
                            if line.strip():
                                result["issues"].append({"message": line})
                        result["success"] = False
                    
                    if fix:
                        with open(temp_file, 'r') as f:
                            result["fixed_code"] = f.read()
            
            elif language in ["go"] and "golint" in self.detected_tools["linters"]:
                result_proc = subprocess.run(
                    ["golint", temp_file],
                    capture_output=True,
                    text=True
                )
                if result_proc.stdout:
                    for line in result_proc.stdout.split('\n'):
                        if line.strip():
                            result["issues"].append({"message": line})
                    result["success"] = False
            
            elif language in ["rust", "rs"] and "clippy" in self.detected_tools["linters"]:
                result_proc = subprocess.run(
                    ["cargo", "clippy", "--", "--no-deps"],
                    capture_output=True,
                    text=True,
                    cwd=self.root
                )
                if "warning" in result_proc.stderr or "error" in result_proc.stderr:
                    for line in result_proc.stderr.split('\n'):
                        if 'warning:' in line or 'error:' in line:
                            result["issues"].append({"message": line})
                    result["success"] = False
            
            else:
                result["issues"].append({"message": f"No linter configured for {language}"})
        
        except FileNotFoundError as e:
            result["issues"].append({"message": f"Linter not installed: {str(e)}"})
        except Exception as e:
            result["issues"].append({"message": f"Linting error: {str(e)}"})
            result["success"] = False
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return result
    
    def format_code(self, code: str, language: str) -> Dict[str, Any]:
        """Format code using appropriate formatter"""
        result = {"success": True, "formatted_code": code, "changed": False}
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_extension(language), delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            if language in ["javascript", "js", "typescript", "ts"] and "prettier" in self.detected_tools["formatters"]:
                result_proc = subprocess.run(
                    ["npx", "prettier", "--write", temp_file],
                    capture_output=True,
                    text=True,
                    cwd=self.root
                )
                
                with open(temp_file, 'r') as f:
                    formatted = f.read()
                    if formatted != code:
                        result["formatted_code"] = formatted
                        result["changed"] = True
            
            elif language in ["python", "py"]:
                if "black" in self.detected_tools["formatters"]:
                    result_proc = subprocess.run(
                        ["black", "-q", temp_file],
                        capture_output=True,
                        text=True
                    )
                elif "autopep8" in self.detected_tools["formatters"]:
                    result_proc = subprocess.run(
                        ["autopep8", "--in-place", temp_file],
                        capture_output=True,
                        text=True
                    )
                
                with open(temp_file, 'r') as f:
                    formatted = f.read()
                    if formatted != code:
                        result["formatted_code"] = formatted
                        result["changed"] = True
            
            elif language in ["go"] and "gofmt" in self.detected_tools["formatters"]:
                result_proc = subprocess.run(
                    ["gofmt", "-w", temp_file],
                    capture_output=True,
                    text=True
                )
                
                with open(temp_file, 'r') as f:
                    formatted = f.read()
                    if formatted != code:
                        result["formatted_code"] = formatted
                        result["changed"] = True
            
            elif language in ["rust", "rs"] and "rustfmt" in self.detected_tools["formatters"]:
                result_proc = subprocess.run(
                    ["rustfmt", temp_file],
                    capture_output=True,
                    text=True
                )
                
                with open(temp_file, 'r') as f:
                    formatted = f.read()
                    if formatted != code:
                        result["formatted_code"] = formatted
                        result["changed"] = True
            
            elif language in ["java"]:
                # Try google-java-format if available
                try:
                    result_proc = subprocess.run(
                        ["google-java-format", "--replace", temp_file],
                        capture_output=True,
                        text=True
                    )
                    
                    with open(temp_file, 'r') as f:
                        formatted = f.read()
                        if formatted != code:
                            result["formatted_code"] = formatted
                            result["changed"] = True
                except FileNotFoundError:
                    result["success"] = True
                    result["formatted_code"] = code
            
            else:
                result["success"] = True
                result["formatted_code"] = code
        
        except FileNotFoundError as e:
            result["success"] = True
            result["formatted_code"] = code
        except Exception as e:
            result["success"] = False
            result["formatted_code"] = code
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return result
    
    def check_types(self, code: str, language: str) -> Dict[str, Any]:
        """Type checking for languages that support it"""
        result = {"success": True, "errors": [], "warnings": []}
        
        if language in ["typescript", "ts"] and "typescript" in self.detected_tools["type_checkers"]:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result_proc = subprocess.run(
                    ["npx", "tsc", "--noEmit", "--strict", temp_file],
                    capture_output=True,
                    text=True,
                    cwd=self.root
                )
                
                if result_proc.returncode != 0:
                    result["success"] = False
                    for line in result_proc.stdout.split('\n'):
                        if 'error' in line.lower():
                            result["errors"].append(line)
                        elif 'warning' in line.lower():
                            result["warnings"].append(line)
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        elif language in ["python", "py"] and "mypy" in self.detected_tools["type_checkers"]:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result_proc = subprocess.run(
                    ["mypy", temp_file],
                    capture_output=True,
                    text=True
                )
                
                if result_proc.returncode != 0:
                    result["success"] = False
                    for line in result_proc.stdout.split('\n'):
                        if 'error:' in line:
                            result["errors"].append(line)
                        elif 'warning:' in line or 'note:' in line:
                            result["warnings"].append(line)
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        else:
            result["warnings"].append(f"No type checker available for {language}")
        
        return result
    
    def check_imports(self, code: str, language: str) -> Dict[str, Any]:
        """Check if all imports/dependencies exist"""
        result = {"valid": True, "missing": [], "warnings": []}
        
        if language in ["python", "py"]:
            # Extract import statements
            import_pattern = r'(?:from\s+(\S+)\s+)?import\s+([^#\n]+)'
            imports = re.findall(import_pattern, code)
            
            for from_module, import_names in imports:
                module = from_module if from_module else import_names.split(',')[0].strip().split(' as ')[0]
                
                # Try to import to check if exists
                try:
                    __import__(module.split('.')[0])
                except ImportError:
                    result["missing"].append(module)
                    result["valid"] = False
        
        elif language in ["javascript", "js", "typescript", "ts"]:
            # Extract import/require statements
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'require\s*\([\'"]([^\'"]+)[\'"]\)',
                r'import\s*\([\'"]([^\'"]+)[\'"]\)'
            ]
            
            for pattern in import_patterns:
                imports = re.findall(pattern, code)
                for imp in imports:
                    # Check if it's a relative import or node_modules
                    if not imp.startswith('.') and not imp.startswith('/'):
                        # Check in package.json dependencies
                        if (self.root / "package.json").exists():
                            try:
                                with open(self.root / "package.json", 'r') as f:
                                    pkg = json.load(f)
                                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                                    
                                    # Extract package name (handle @scope/package)
                                    pkg_name = imp.split('/')[0] if not imp.startswith('@') else '/'.join(imp.split('/')[:2])
                                    
                                    if pkg_name not in deps and pkg_name not in ['fs', 'path', 'http', 'https', 'crypto', 'os', 'util', 'stream', 'events', 'buffer', 'child_process', 'cluster', 'url', 'querystring', 'assert']:
                                        result["missing"].append(imp)
                                        result["valid"] = False
                            except:
                                pass
        
        elif language in ["go"]:
            # Extract import statements
            import_pattern = r'import\s+(?:\(([^)]+)\)|"([^"]+)")'
            imports = re.findall(import_pattern, code)
            
            # For Go, checking would require go list, which is complex
            # Just return that we found imports
            if imports:
                result["warnings"].append("Go import validation requires 'go mod' context")
        
        return result
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": ".py", "py": ".py",
            "javascript": ".js", "js": ".js",
            "typescript": ".ts", "ts": ".ts",
            "go": ".go",
            "rust": ".rs", "rs": ".rs",
            "java": ".java",
            "ruby": ".rb", "rb": ".rb",
            "php": ".php",
            "c": ".c",
            "cpp": ".cpp", "c++": ".cpp",
            "csharp": ".cs", "c#": ".cs"
        }
        return extensions.get(language.lower(), ".txt")
    
    def _detect_language(self, code: str, filename: str = None) -> str:
        """Auto-detect language from code or filename"""
        if filename:
            ext = Path(filename).suffix.lower()
            lang_map = {
                ".py": "python",
                ".js": "javascript",
                ".jsx": "javascript",
                ".ts": "typescript",
                ".tsx": "typescript",
                ".go": "go",
                ".rs": "rust",
                ".java": "java",
                ".rb": "ruby",
                ".php": "php",
                ".c": "c",
                ".cpp": "cpp",
                ".cs": "csharp"
            }
            if ext in lang_map:
                return lang_map[ext]
        
        # Try to detect from code patterns
        if "def " in code or "import " in code or "from " in code:
            return "python"
        elif "function " in code or "const " in code or "let " in code or "var " in code:
            if ": " in code and ("interface " in code or "type " in code):
                return "typescript"
            return "javascript"
        elif "func " in code and "package " in code:
            return "go"
        elif "fn " in code and ("let " in code or "mut " in code):
            return "rust"
        elif "public class " in code or "private " in code:
            return "java"
        
        return "unknown"

# Global validator instance
validator = CodeValidator(PROJECT_ROOT)

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available validation tools"""
    return [
        types.Tool(
            name="syntax",
            description="Check syntax errors in code (fast, language auto-detection supported)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to validate"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, typescript, go, rust, java, etc.)"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional filename to help detect language"
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="lint",
            description="Lint with project's linter (ESLint, Pylint, etc.) with auto-fix option (~1-2s)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to lint"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    },
                    "fix": {
                        "type": "boolean",
                        "description": "Attempt to auto-fix issues",
                        "default": False
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="format",
            description="Auto-format code with project formatter (Prettier, Black, etc.) - instant",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to format"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="types",
            description="Type-check code for type errors (TypeScript, mypy, etc.) (~1-2s)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to type check"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="imports",
            description="Verify all imports and dependencies exist (fast validation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to check imports for"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="validate",
            description="Run ALL validations at once: syntax, lint, types, imports (comprehensive check, ~2-3s)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to validate"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    },
                    "fix": {
                        "type": "boolean",
                        "description": "Attempt to auto-fix issues",
                        "default": False
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="tools",
            description="Detect available linters, formatters, and type checkers in project (fast scan)",
            inputSchema={
                "type": "object",
                "properties": {}
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
    
    if name == "syntax":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        filename = arguments.get("filename", "")
        
        if not language:
            language = validator._detect_language(code, filename)
        
        result = validator.validate_syntax(code, language)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "lint":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        fix = arguments.get("fix", False)
        
        if not language:
            language = validator._detect_language(code)
        
        result = validator.lint_code(code, language, fix)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "format":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        
        if not language:
            language = validator._detect_language(code)
        
        result = validator.format_code(code, language)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "types":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        
        if not language:
            language = validator._detect_language(code)
        
        result = validator.check_types(code, language)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "imports":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        
        if not language:
            language = validator._detect_language(code)
        
        result = validator.check_imports(code, language)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "validate":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        fix = arguments.get("fix", False)
        
        if not language:
            language = validator._detect_language(code)
        
        # Run all validations
        results = {
            "language": language,
            "syntax": validator.validate_syntax(code, language),
            "lint": validator.lint_code(code, language, fix),
            "types": validator.check_types(code, language),
            "imports": validator.check_imports(code, language)
        }
        
        # If fix was requested and linting produced fixed code, format it too
        if fix and results["lint"].get("fixed_code"):
            format_result = validator.format_code(results["lint"]["fixed_code"], language)
            results["formatted_code"] = format_result["formatted_code"]
        else:
            format_result = validator.format_code(code, language)
            results["formatted_code"] = format_result["formatted_code"]
        
        # Overall status
        results["overall_valid"] = (
            results["syntax"]["valid"] and
            results["imports"]["valid"] and
            results["types"]["success"]
        )
        
        return [types.TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
    
    elif name == "tools":
        return [types.TextContent(
            type="text",
            text=json.dumps(validator.detected_tools, indent=2)
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
                server_name="validation",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())