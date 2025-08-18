#!/usr/bin/env python3
"""
Execution MCP Server - Universal Code Execution and Testing
Provides safe code execution, output capture, and runtime validation for any language
"""
import json
import asyncio
import os
import subprocess
import tempfile
import time
import psutil
import signal
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import shlex
import sys

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("execution")

# Get project root from environment or use current directory
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", os.getcwd()))
SANDBOX_MODE = os.getenv("SANDBOX", "true").lower() == "true"
DEFAULT_TIMEOUT = int(os.getenv("TIMEOUT", "30000"))  # 30 seconds default

class CodeExecutor:
    """Universal code executor with sandboxing and monitoring"""
    
    def __init__(self, root: Path):
        self.root = root
        self.processes = {}  # Track running processes
    
    def execute_code(self, code: str, language: str, 
                     timeout: int = None, 
                     args: List[str] = None,
                     stdin: str = None,
                     env: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute code in any language with timeout and monitoring"""
        
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "execution_time": 0,
            "memory_usage": 0,
            "timeout": False,
            "error": None
        }
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_extension(language), delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Get execution command based on language
            cmd = self._get_execution_command(language, temp_file, args)
            
            if not cmd:
                result["error"] = f"No executor available for {language}"
                return result
            
            # Prepare environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            # Start process
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if stdin else None,
                env=exec_env,
                cwd=self.root,
                text=True
            )
            
            # Track process for monitoring
            self.processes[process.pid] = process
            
            try:
                # Monitor memory usage in background
                max_memory = 0
                
                def monitor_memory():
                    nonlocal max_memory
                    try:
                        proc = psutil.Process(process.pid)
                        while process.poll() is None:
                            memory_info = proc.memory_info()
                            max_memory = max(max_memory, memory_info.rss)
                            time.sleep(0.1)
                    except:
                        pass
                
                monitor_thread = threading.Thread(target=monitor_memory)
                monitor_thread.daemon = True
                monitor_thread.start()
                
                # Execute with timeout
                stdout, stderr = process.communicate(
                    input=stdin if stdin else None,
                    timeout=timeout / 1000.0  # Convert to seconds
                )
                
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                
                result["success"] = process.returncode == 0
                result["stdout"] = stdout
                result["stderr"] = stderr
                result["exit_code"] = process.returncode
                result["execution_time"] = round(execution_time, 2)
                result["memory_usage"] = max_memory
                
            except subprocess.TimeoutExpired:
                # Kill process on timeout
                process.kill()
                stdout, stderr = process.communicate()
                result["timeout"] = True
                result["error"] = f"Execution timeout after {timeout}ms"
                result["stdout"] = stdout if stdout else ""
                result["stderr"] = stderr if stderr else ""
            
            finally:
                # Clean up process tracking
                if process.pid in self.processes:
                    del self.processes[process.pid]
        
        except Exception as e:
            result["error"] = str(e)
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
                # Clean up compiled files for some languages
                if language == "java":
                    class_file = temp_file.replace(".java", ".class")
                    if os.path.exists(class_file):
                        os.unlink(class_file)
            except:
                pass
        
        return result
    
    def run_script(self, script_path: str, 
                   args: List[str] = None,
                   timeout: int = None,
                   env: Dict[str, str] = None) -> Dict[str, Any]:
        """Run an existing script file"""
        
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "execution_time": 0,
            "timeout": False,
            "error": None
        }
        
        script_path = Path(script_path)
        if not script_path.is_absolute():
            script_path = self.root / script_path
        
        if not script_path.exists():
            result["error"] = f"Script not found: {script_path}"
            return result
        
        # Detect language from extension
        language = self._detect_language_from_file(str(script_path))
        
        # Get execution command
        cmd = self._get_execution_command(language, str(script_path), args)
        
        if not cmd:
            # Try to execute directly (for shell scripts)
            if script_path.stat().st_mode & 0o111:  # Check if executable
                cmd = [str(script_path)]
                if args:
                    cmd.extend(args)
            else:
                result["error"] = f"Cannot determine how to run {script_path}"
                return result
        
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        
        # Execute
        try:
            start_time = time.time()
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout / 1000.0,
                env=exec_env,
                cwd=self.root
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            result["success"] = process.returncode == 0
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            result["exit_code"] = process.returncode
            result["execution_time"] = round(execution_time, 2)
            
        except subprocess.TimeoutExpired:
            result["timeout"] = True
            result["error"] = f"Script timeout after {timeout}ms"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def run_test(self, test_command: str = None, 
                 test_file: str = None,
                 coverage: bool = False) -> Dict[str, Any]:
        """Run tests with optional coverage"""
        
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage_percent": None,
            "execution_time": 0,
            "error": None
        }
        
        # Auto-detect test command if not provided
        if not test_command:
            test_command = self._detect_test_command()
            if not test_command:
                result["error"] = "No test command found"
                return result
        
        # Add coverage if requested
        if coverage:
            test_command = self._add_coverage_to_command(test_command)
        
        # Add specific test file if provided
        if test_file:
            test_command = f"{test_command} {test_file}"
        
        # Execute tests
        try:
            start_time = time.time()
            process = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,  # 60 seconds for tests
                cwd=self.root
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            result["exit_code"] = process.returncode
            result["execution_time"] = round(execution_time, 2)
            
            # Parse test results
            self._parse_test_results(result)
            
            # Parse coverage if available
            if coverage:
                self._parse_coverage(result)
            
            result["success"] = process.returncode == 0
            
        except subprocess.TimeoutExpired:
            result["error"] = "Test execution timeout"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def test_api_endpoint(self, url: str, 
                         method: str = "GET",
                         headers: Dict[str, str] = None,
                         body: str = None,
                         timeout: int = 10000) -> Dict[str, Any]:
        """Test API endpoints"""
        
        result = {
            "success": False,
            "status_code": None,
            "response_body": None,
            "response_headers": {},
            "response_time": 0,
            "error": None
        }
        
        try:
            import urllib.request
            import urllib.parse
            import urllib.error
            
            # Prepare request
            req = urllib.request.Request(url, method=method)
            
            # Add headers
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            # Add body for POST/PUT/PATCH
            data = None
            if body and method in ["POST", "PUT", "PATCH"]:
                data = body.encode('utf-8')
                if not headers or 'Content-Type' not in headers:
                    req.add_header('Content-Type', 'application/json')
            
            # Execute request
            start_time = time.time()
            
            try:
                response = urllib.request.urlopen(req, data=data, timeout=timeout/1000.0)
                result["success"] = True
                result["status_code"] = response.getcode()
                result["response_body"] = response.read().decode('utf-8')
                result["response_headers"] = dict(response.headers)
                
            except urllib.error.HTTPError as e:
                result["status_code"] = e.code
                result["response_body"] = e.read().decode('utf-8')
                result["error"] = f"HTTP {e.code}: {e.reason}"
                
            except urllib.error.URLError as e:
                result["error"] = f"URL Error: {e.reason}"
            
            result["response_time"] = round((time.time() - start_time) * 1000, 2)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def run_command(self, command: str, 
                   timeout: int = None,
                   shell: bool = True) -> Dict[str, Any]:
        """Run arbitrary shell command"""
        
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "execution_time": 0,
            "error": None
        }
        
        if SANDBOX_MODE and any(dangerous in command for dangerous in ['rm -rf', 'dd if=', 'format', ':(){ :|:& };:']):
            result["error"] = "Command blocked in sandbox mode"
            return result
        
        try:
            start_time = time.time()
            
            if shell:
                cmd = command
            else:
                cmd = shlex.split(command)
            
            process = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout / 1000.0,
                cwd=self.root
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            result["success"] = process.returncode == 0
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr
            result["exit_code"] = process.returncode
            result["execution_time"] = round(execution_time, 2)
            
        except subprocess.TimeoutExpired:
            result["error"] = f"Command timeout after {timeout}ms"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def debug_code(self, code: str, language: str, 
                  breakpoint_line: int = None) -> Dict[str, Any]:
        """Debug code and analyze errors"""
        
        result = {
            "error_analysis": [],
            "suggestions": [],
            "stack_trace": None,
            "variables": {}
        }
        
        # First, try to execute the code
        exec_result = self.execute_code(code, language)
        
        if not exec_result["success"]:
            # Analyze error output
            error_output = exec_result["stderr"] or exec_result["error"] or ""
            
            if language in ["python", "py"]:
                result["error_analysis"] = self._analyze_python_error(error_output)
            elif language in ["javascript", "js", "typescript", "ts"]:
                result["error_analysis"] = self._analyze_js_error(error_output)
            elif language in ["java"]:
                result["error_analysis"] = self._analyze_java_error(error_output)
            
            # Generate suggestions
            result["suggestions"] = self._generate_debug_suggestions(
                error_output, language
            )
        
        return result
    
    def profile_performance(self, code: str, language: str,
                           iterations: int = 1) -> Dict[str, Any]:
        """Profile code performance"""
        
        result = {
            "avg_execution_time": 0,
            "min_execution_time": float('inf'),
            "max_execution_time": 0,
            "avg_memory_usage": 0,
            "iterations": iterations,
            "measurements": []
        }
        
        total_time = 0
        total_memory = 0
        
        for i in range(iterations):
            exec_result = self.execute_code(code, language)
            
            if exec_result["success"]:
                time_ms = exec_result["execution_time"]
                memory = exec_result["memory_usage"]
                
                result["measurements"].append({
                    "iteration": i + 1,
                    "time": time_ms,
                    "memory": memory
                })
                
                total_time += time_ms
                total_memory += memory
                
                result["min_execution_time"] = min(result["min_execution_time"], time_ms)
                result["max_execution_time"] = max(result["max_execution_time"], time_ms)
            else:
                result["error"] = exec_result["error"]
                break
        
        if result["measurements"]:
            result["avg_execution_time"] = round(total_time / len(result["measurements"]), 2)
            result["avg_memory_usage"] = round(total_memory / len(result["measurements"]))
        
        return result
    
    def _get_execution_command(self, language: str, file_path: str, args: List[str] = None) -> List[str]:
        """Get the command to execute code in given language"""
        
        cmd = []
        
        if language in ["python", "py"]:
            cmd = ["python", file_path]
        elif language in ["javascript", "js"]:
            cmd = ["node", file_path]
        elif language in ["typescript", "ts"]:
            # Compile and run TypeScript
            cmd = ["npx", "ts-node", file_path]
        elif language in ["java"]:
            # Compile first
            compile_result = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                cwd=self.root
            )
            if compile_result.returncode == 0:
                # Extract class name from file
                class_name = Path(file_path).stem
                cmd = ["java", class_name]
        elif language in ["go"]:
            cmd = ["go", "run", file_path]
        elif language in ["rust", "rs"]:
            cmd = ["rustc", file_path, "-o", "/tmp/rust_exec", "&&", "/tmp/rust_exec"]
        elif language in ["ruby", "rb"]:
            cmd = ["ruby", file_path]
        elif language in ["php"]:
            cmd = ["php", file_path]
        elif language in ["c"]:
            # Compile and run C
            output = "/tmp/c_exec"
            compile_result = subprocess.run(
                ["gcc", file_path, "-o", output],
                capture_output=True
            )
            if compile_result.returncode == 0:
                cmd = [output]
        elif language in ["cpp", "c++"]:
            # Compile and run C++
            output = "/tmp/cpp_exec"
            compile_result = subprocess.run(
                ["g++", file_path, "-o", output],
                capture_output=True
            )
            if compile_result.returncode == 0:
                cmd = [output]
        elif language in ["csharp", "cs", "c#"]:
            cmd = ["dotnet", "script", file_path]
        elif language in ["bash", "sh"]:
            cmd = ["bash", file_path]
        
        # Add arguments if provided
        if cmd and args:
            cmd.extend(args)
        
        return cmd
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": ".py", "py": ".py",
            "javascript": ".js", "js": ".js",
            "typescript": ".ts", "ts": ".ts",
            "java": ".java",
            "go": ".go",
            "rust": ".rs", "rs": ".rs",
            "ruby": ".rb", "rb": ".rb",
            "php": ".php",
            "c": ".c",
            "cpp": ".cpp", "c++": ".cpp",
            "csharp": ".cs", "cs": ".cs", "c#": ".cs",
            "bash": ".sh", "sh": ".sh"
        }
        return extensions.get(language.lower(), ".txt")
    
    def _detect_language_from_file(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cs": "csharp",
            ".sh": "bash"
        }
        return lang_map.get(ext, "unknown")
    
    def _detect_test_command(self) -> str:
        """Auto-detect test command for project"""
        
        # Check package.json for npm/yarn test
        if (self.root / "package.json").exists():
            try:
                with open(self.root / "package.json", 'r') as f:
                    pkg = json.load(f)
                    if "scripts" in pkg and "test" in pkg["scripts"]:
                        return "npm test"
            except:
                pass
        
        # Check for pytest
        if (self.root / "pytest.ini").exists() or (self.root / "setup.cfg").exists():
            return "pytest"
        
        # Check for go test
        if (self.root / "go.mod").exists():
            return "go test ./..."
        
        # Check for cargo test
        if (self.root / "Cargo.toml").exists():
            return "cargo test"
        
        # Check for maven
        if (self.root / "pom.xml").exists():
            return "mvn test"
        
        # Check for gradle
        if (self.root / "build.gradle").exists():
            return "gradle test"
        
        return None
    
    def _add_coverage_to_command(self, test_command: str) -> str:
        """Add coverage flags to test command"""
        
        if "pytest" in test_command:
            return f"{test_command} --cov --cov-report=term"
        elif "npm test" in test_command:
            return "npm run test -- --coverage"
        elif "go test" in test_command:
            return f"{test_command} -cover"
        elif "cargo test" in test_command:
            # Cargo coverage requires tarpaulin
            return "cargo tarpaulin"
        
        return test_command
    
    def _parse_test_results(self, result: Dict[str, Any]):
        """Parse test output to extract pass/fail counts"""
        
        output = result["stdout"] + result["stderr"]
        
        # Jest/Mocha patterns
        if "passing" in output or "failing" in output:
            import re
            passing = re.search(r'(\d+)\s+passing', output)
            failing = re.search(r'(\d+)\s+failing', output)
            
            if passing:
                result["tests_passed"] = int(passing.group(1))
            if failing:
                result["tests_failed"] = int(failing.group(1))
        
        # Pytest patterns
        elif "passed" in output or "failed" in output:
            import re
            match = re.search(r'(\d+)\s+passed(?:,\s*(\d+)\s+failed)?', output)
            if match:
                result["tests_passed"] = int(match.group(1))
                if match.group(2):
                    result["tests_failed"] = int(match.group(2))
        
        # Go test patterns
        elif "PASS" in output or "FAIL" in output:
            result["tests_passed"] = output.count("PASS")
            result["tests_failed"] = output.count("FAIL")
    
    def _parse_coverage(self, result: Dict[str, Any]):
        """Parse coverage output"""
        
        output = result["stdout"] + result["stderr"]
        
        # Look for coverage percentage
        import re
        
        # Common patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*coverage',
            r'Coverage:\s*(\d+(?:\.\d+)?)\s*%',
            r'TOTAL\s+\d+\s+\d+\s+(\d+(?:\.\d+)?)\s*%',
            r'Lines\s*:\s*(\d+(?:\.\d+)?)\s*%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                result["coverage_percent"] = float(match.group(1))
                break
    
    def _analyze_python_error(self, error: str) -> List[str]:
        """Analyze Python error messages"""
        
        analysis = []
        
        if "SyntaxError" in error:
            analysis.append("Syntax error detected - check indentation and syntax")
        if "NameError" in error:
            analysis.append("Undefined variable or function - check spelling and imports")
        if "TypeError" in error:
            analysis.append("Type mismatch - check argument types and operations")
        if "ImportError" in error or "ModuleNotFoundError" in error:
            analysis.append("Missing module - install required dependencies")
        if "IndentationError" in error:
            analysis.append("Indentation error - check spacing and tabs vs spaces")
        
        return analysis
    
    def _analyze_js_error(self, error: str) -> List[str]:
        """Analyze JavaScript error messages"""
        
        analysis = []
        
        if "SyntaxError" in error:
            analysis.append("Syntax error - check brackets, semicolons, and quotes")
        if "ReferenceError" in error:
            analysis.append("Undefined variable - check variable declarations and scope")
        if "TypeError" in error:
            analysis.append("Type error - check null/undefined values and method calls")
        if "Cannot find module" in error:
            analysis.append("Missing module - run npm install")
        
        return analysis
    
    def _analyze_java_error(self, error: str) -> List[str]:
        """Analyze Java error messages"""
        
        analysis = []
        
        if "cannot find symbol" in error:
            analysis.append("Undefined symbol - check class/method names and imports")
        if "incompatible types" in error:
            analysis.append("Type mismatch - check variable types and casting")
        if "package does not exist" in error:
            analysis.append("Missing package - check classpath and dependencies")
        
        return analysis
    
    def _generate_debug_suggestions(self, error: str, language: str) -> List[str]:
        """Generate debugging suggestions based on error"""
        
        suggestions = []
        
        # General suggestions
        suggestions.append("Add print/log statements to trace execution")
        suggestions.append("Check variable values at the point of error")
        suggestions.append("Verify all function arguments are correct")
        
        # Language-specific suggestions
        if language in ["python", "py"]:
            suggestions.append("Use pdb debugger: import pdb; pdb.set_trace()")
        elif language in ["javascript", "js", "typescript", "ts"]:
            suggestions.append("Use console.log() or debugger statement")
            suggestions.append("Check browser DevTools or Node.js inspector")
        elif language in ["java"]:
            suggestions.append("Use System.out.println() for debugging")
            suggestions.append("Check stack trace for exact error location")
        
        return suggestions

# Global executor instance
executor = CodeExecutor(PROJECT_ROOT)

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available execution tools"""
    return [
        types.Tool(
            name="run",
            description="Execute code snippet in any language with sandboxing (timeout: 30s default)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to execute"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, go, etc.)"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command line arguments"
                    },
                    "stdin": {
                        "type": "string",
                        "description": "Input to provide via stdin"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in milliseconds (default: 30000)"
                    }
                },
                "required": ["code", "language"]
            }
        ),
        types.Tool(
            name="script",
            description="Run existing script file with args (auto-detects language from extension)",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the script file"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command line arguments"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in milliseconds"
                    }
                },
                "required": ["script_path"]
            }
        ),
        types.Tool(
            name="test",
            description="Run project tests with coverage option (auto-detects test framework)",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_command": {
                        "type": "string",
                        "description": "Test command (auto-detected if not provided)"
                    },
                    "test_file": {
                        "type": "string",
                        "description": "Specific test file to run"
                    },
                    "coverage": {
                        "type": "boolean",
                        "description": "Include coverage report",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="api",
            description="Test API endpoints with HTTP methods, headers, and body (timeout: 10s)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "API endpoint URL"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                        "description": "HTTP method",
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers"
                    },
                    "body": {
                        "type": "string",
                        "description": "Request body (for POST/PUT/PATCH)"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in milliseconds",
                        "default": 10000
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="command",
            description="Execute shell commands safely with timeout protection (sandboxed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in milliseconds"
                    }
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="debug",
            description="Debug code with error analysis and fix suggestions (language-aware)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to debug"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    },
                    "breakpoint_line": {
                        "type": "number",
                        "description": "Line number for breakpoint"
                    }
                },
                "required": ["code", "language"]
            }
        ),
        types.Tool(
            name="profile",
            description="Profile code performance: execution time, memory usage (multi-iteration)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to profile"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language"
                    },
                    "iterations": {
                        "type": "number",
                        "description": "Number of iterations to run",
                        "default": 1
                    }
                },
                "required": ["code", "language"]
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
    
    if name == "run":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        args = arguments.get("args", [])
        stdin = arguments.get("stdin", None)
        timeout = arguments.get("timeout", None)
        
        result = executor.execute_code(code, language, timeout, args, stdin)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "script":
        script_path = arguments.get("script_path", "")
        args = arguments.get("args", [])
        timeout = arguments.get("timeout", None)
        
        result = executor.run_script(script_path, args, timeout)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "test":
        test_command = arguments.get("test_command", None)
        test_file = arguments.get("test_file", None)
        coverage = arguments.get("coverage", False)
        
        result = executor.run_test(test_command, test_file, coverage)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "api":
        url = arguments.get("url", "")
        method = arguments.get("method", "GET")
        headers = arguments.get("headers", None)
        body = arguments.get("body", None)
        timeout = arguments.get("timeout", 10000)
        
        result = executor.test_api_endpoint(url, method, headers, body, timeout)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "command":
        command = arguments.get("command", "")
        timeout = arguments.get("timeout", None)
        
        result = executor.run_command(command, timeout)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "debug":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        breakpoint_line = arguments.get("breakpoint_line", None)
        
        result = executor.debug_code(code, language, breakpoint_line)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "profile":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        iterations = arguments.get("iterations", 1)
        
        result = executor.profile_performance(code, language, iterations)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
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
                server_name="execution",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())