"""
Sandboxed versions of tools for secure execution
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
from unified.tools.base import Tool, ToolContext, ToolResult, ToolStatus, ToolCategory
from unified.sandbox import (
    SandboxEnvironment, SandboxConfig, SandboxStatus,
    get_sandbox_manager
)


class SandboxedCommandTool(Tool[Dict[str, Any]]):
    """Execute commands in a sandboxed environment"""
    
    def __init__(self, sandbox_config: Optional[SandboxConfig] = None):
        super().__init__(
            "sandboxed_command",
            ToolCategory.PROCESS,
            "Execute commands in a secure sandbox"
        )
        self.sandbox_config = sandbox_config or SandboxConfig(
            max_memory_mb=256,
            max_cpu_seconds=10,
            timeout_seconds=30,
            allow_network=False
        )
    
    def validate_input(self, command: str) -> List[str]:
        """Validate command input"""
        errors = []
        if not command:
            errors.append("Command cannot be empty")
        if len(command) > 1000:
            errors.append("Command too long (max 1000 characters)")
        return errors
    
    def dry_run(self, context: ToolContext, command: str) -> str:
        """Preview sandboxed execution"""
        return f"Would execute in sandbox: '{command}' with limits: memory={self.sandbox_config.max_memory_mb}MB, timeout={self.sandbox_config.timeout_seconds}s"
    
    def _execute_impl(self, context: ToolContext, command: str) -> Dict[str, Any]:
        """Execute command in sandbox"""
        # Get or create sandbox
        manager = get_sandbox_manager()
        sandbox_name = f"cmd_sandbox_{context.session_id}"
        
        try:
            # Create sandbox
            sandbox = manager.create_sandbox(sandbox_name, self.sandbox_config)
            
            # Execute command
            result = sandbox.execute(command)
            
            # Convert result
            output = {
                'success': result.success,
                'exit_code': result.exit_code,
                'status': result.status.value,
                'duration': result.duration,
                'resource_usage': result.resource_usage
            }
            
            if result.output and isinstance(result.output, dict):
                output['stdout'] = result.output.get('stdout', '')
                output['stderr'] = result.output.get('stderr', '')
            
            if not result.success:
                raise RuntimeError(result.error or f"Command failed with status: {result.status.value}")
            
            return output
            
        finally:
            # Always cleanup
            manager.cleanup_sandbox(sandbox_name)


class SandboxedPythonTool(Tool[Any]):
    """Execute Python code in a sandboxed environment"""
    
    def __init__(self, sandbox_config: Optional[SandboxConfig] = None):
        super().__init__(
            "sandboxed_python",
            ToolCategory.CODE_EXECUTION,
            "Execute Python code in a secure sandbox"
        )
        self.sandbox_config = sandbox_config or SandboxConfig(
            max_memory_mb=128,
            max_cpu_seconds=5,
            timeout_seconds=10,
            allow_network=False
        )
    
    def validate_input(self, code: str) -> List[str]:
        """Validate Python code input"""
        errors = []
        if not code:
            errors.append("Code cannot be empty")
        if len(code) > 10000:
            errors.append("Code too long (max 10000 characters)")
        
        # Basic syntax check
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
        
        # Check for dangerous imports
        dangerous_imports = ['os', 'subprocess', 'sys', '__builtins__']
        for imp in dangerous_imports:
            if f'import {imp}' in code or f'from {imp}' in code:
                errors.append(f"Import of '{imp}' not allowed in sandbox")
        
        return errors
    
    def dry_run(self, context: ToolContext, code: str) -> str:
        """Preview Python execution"""
        lines = code.strip().split('\n')
        preview = lines[0] if lines else ""
        if len(lines) > 1:
            preview += f" ... ({len(lines)} lines total)"
        return f"Would execute Python code: {preview}"
    
    def _execute_impl(self, context: ToolContext, code: str) -> Any:
        """Execute Python code in sandbox"""
        # Wrap code for execution
        wrapped_code = f"""
import json
import sys

# Capture output
output = []
error = None
result = None

class OutputCapture:
    def write(self, text):
        output.append(text)
    def flush(self):
        pass

sys.stdout = OutputCapture()
sys.stderr = OutputCapture()

try:
    # User code
    {code}
    
    # Try to capture last expression result
    if 'result' in locals():
        result = locals()['result']
except Exception as e:
    error = str(e)

# Output results
print(json.dumps({{
    'output': ''.join(output),
    'error': error,
    'result': result
}}))
"""
        
        # Create Python command
        python_cmd = ["python3", "-c", wrapped_code]
        
        # Get or create sandbox
        manager = get_sandbox_manager()
        sandbox_name = f"python_sandbox_{context.session_id}"
        
        try:
            # Create sandbox
            sandbox = manager.create_sandbox(sandbox_name, self.sandbox_config)
            
            # Execute code
            result = sandbox.execute(python_cmd)
            
            if not result.success:
                raise RuntimeError(result.error or f"Python execution failed: {result.status.value}")
            
            # Parse output
            if result.output and isinstance(result.output, dict):
                stdout = result.output.get('stdout', '')
                try:
                    # Try to parse JSON output
                    output_data = json.loads(stdout.strip())
                    if output_data.get('error'):
                        raise RuntimeError(f"Python error: {output_data['error']}")
                    return output_data.get('result', output_data.get('output', ''))
                except json.JSONDecodeError:
                    # Return raw output if not JSON
                    return stdout
            
            return None
            
        finally:
            # Always cleanup
            manager.cleanup_sandbox(sandbox_name)


class SandboxedFileTool(Tool[str]):
    """File operations in a sandboxed environment"""
    
    def __init__(self, sandbox_config: Optional[SandboxConfig] = None):
        super().__init__(
            "sandboxed_file_ops",
            ToolCategory.FILE,
            "Perform file operations in a sandbox"
        )
        self.sandbox_config = sandbox_config or SandboxConfig(
            max_memory_mb=64,
            max_file_size_mb=10,
            timeout_seconds=5,
            allow_network=False
        )
    
    def validate_input(self, operation: str, path: str, content: Optional[str] = None) -> List[str]:
        """Validate file operation input"""
        errors = []
        
        if operation not in ['read', 'write', 'append', 'delete', 'list']:
            errors.append(f"Invalid operation: {operation}")
        
        if not path:
            errors.append("Path cannot be empty")
        
        if operation in ['write', 'append'] and content is None:
            errors.append(f"Content required for {operation} operation")
        
        if content and len(content) > self.sandbox_config.max_file_size_mb * 1024 * 1024:
            errors.append(f"Content too large (max {self.sandbox_config.max_file_size_mb}MB)")
        
        return errors
    
    def dry_run(self, context: ToolContext, operation: str, path: str, 
                content: Optional[str] = None) -> str:
        """Preview file operation"""
        if operation == 'read':
            return f"Would read file: {path}"
        elif operation == 'write':
            return f"Would write {len(content or '')} bytes to: {path}"
        elif operation == 'append':
            return f"Would append {len(content or '')} bytes to: {path}"
        elif operation == 'delete':
            return f"Would delete file: {path}"
        elif operation == 'list':
            return f"Would list directory: {path}"
        return f"Would perform {operation} on: {path}"
    
    def _execute_impl(self, context: ToolContext, operation: str, path: str,
                     content: Optional[str] = None) -> str:
        """Execute file operation in sandbox"""
        # Build command based on operation
        if operation == 'read':
            command = f"cat {path}"
        elif operation == 'write':
            # Use echo with proper escaping
            escaped_content = content.replace("'", "'\"'\"'")
            command = f"echo '{escaped_content}' > {path}"
        elif operation == 'append':
            escaped_content = content.replace("'", "'\"'\"'")
            command = f"echo '{escaped_content}' >> {path}"
        elif operation == 'delete':
            command = f"rm -f {path}"
        elif operation == 'list':
            command = f"ls -la {path}"
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        # Get or create sandbox
        manager = get_sandbox_manager()
        sandbox_name = f"file_sandbox_{context.session_id}"
        
        try:
            # Create sandbox with temp directory
            config = self.sandbox_config
            config.temp_dir = context.working_directory / ".sandbox"
            sandbox = manager.create_sandbox(sandbox_name, config)
            
            # Execute command
            result = sandbox.execute(command)
            
            if not result.success:
                raise RuntimeError(result.error or f"File operation failed: {result.status.value}")
            
            # Return output
            if result.output and isinstance(result.output, dict):
                return result.output.get('stdout', '')
            
            return ""
            
        finally:
            # Always cleanup
            manager.cleanup_sandbox(sandbox_name)


class SandboxedNetworkTool(Tool[Dict[str, Any]]):
    """Network operations in a sandboxed environment"""
    
    def __init__(self, allowed_hosts: List[str], sandbox_config: Optional[SandboxConfig] = None):
        super().__init__(
            "sandboxed_network",
            ToolCategory.PROCESS,
            "Perform network operations in a sandbox"
        )
        self.allowed_hosts = allowed_hosts
        self.sandbox_config = sandbox_config or SandboxConfig(
            max_memory_mb=128,
            timeout_seconds=30,
            allow_network=True,
            allowed_hosts=allowed_hosts
        )
    
    def validate_input(self, url: str, method: str = "GET", 
                      headers: Optional[Dict[str, str]] = None,
                      data: Optional[str] = None) -> List[str]:
        """Validate network request input"""
        errors = []
        
        if not url:
            errors.append("URL cannot be empty")
        
        # Validate URL format
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                errors.append("Invalid URL format")
            
            # Check allowed hosts
            if self.allowed_hosts and parsed.netloc not in self.allowed_hosts:
                errors.append(f"Host {parsed.netloc} not in allowed list")
        except:
            errors.append("Invalid URL")
        
        if method not in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD']:
            errors.append(f"Invalid HTTP method: {method}")
        
        return errors
    
    def dry_run(self, context: ToolContext, url: str, method: str = "GET",
                headers: Optional[Dict[str, str]] = None,
                data: Optional[str] = None) -> str:
        """Preview network request"""
        return f"Would send {method} request to: {url}"
    
    def _execute_impl(self, context: ToolContext, url: str, method: str = "GET",
                     headers: Optional[Dict[str, str]] = None,
                     data: Optional[str] = None) -> Dict[str, Any]:
        """Execute network request in sandbox"""
        # Build curl command
        cmd_parts = ["curl", "-s", "-X", method]
        
        # Add headers
        if headers:
            for key, value in headers.items():
                cmd_parts.extend(["-H", f"{key}: {value}"])
        
        # Add data
        if data:
            cmd_parts.extend(["-d", data])
        
        # Add URL
        cmd_parts.append(url)
        
        # Also get headers
        cmd_parts.extend(["-w", "\\n\\n__STATUS_CODE__:%{http_code}"])
        
        # Get or create sandbox
        manager = get_sandbox_manager()
        sandbox_name = f"network_sandbox_{context.session_id}"
        
        try:
            # Create sandbox
            sandbox = manager.create_sandbox(sandbox_name, self.sandbox_config)
            
            # Execute request
            result = sandbox.execute(cmd_parts)
            
            if not result.success:
                raise RuntimeError(result.error or f"Network request failed: {result.status.value}")
            
            # Parse output
            if result.output and isinstance(result.output, dict):
                output = result.output.get('stdout', '')
                
                # Extract status code
                status_code = 0
                body = output
                if "__STATUS_CODE__:" in output:
                    parts = output.split("__STATUS_CODE__:")
                    body = parts[0].strip()
                    try:
                        status_code = int(parts[1].strip())
                    except:
                        pass
                
                return {
                    'status_code': status_code,
                    'body': body,
                    'success': 200 <= status_code < 300
                }
            
            return {'status_code': 0, 'body': '', 'success': False}
            
        finally:
            # Always cleanup
            manager.cleanup_sandbox(sandbox_name)