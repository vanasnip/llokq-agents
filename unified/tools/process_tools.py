"""
Process execution tools with safety controls
"""
import subprocess
import shlex
import os
import signal
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from unified.tools.base import Tool, AsyncTool, ToolContext, ToolCategory
import psutil
import asyncio
import re
from datetime import datetime


class CommandExecutionTool(Tool[Dict[str, Any]]):
    """Safe command execution with validation"""
    
    def __init__(self):
        super().__init__(
            name="execute_command",
            category=ToolCategory.PROCESS,
            description="Execute system commands with safety controls"
        )
        # Whitelist of allowed commands
        self.allowed_commands = {
            'ls', 'cat', 'grep', 'find', 'echo', 'pwd', 'date',
            'git', 'npm', 'yarn', 'python', 'pip', 'node',
            'curl', 'wget', 'tar', 'unzip', 'gzip'
        }
        # Blacklist of dangerous patterns
        self.dangerous_patterns = [
            r'rm\s+-rf',
            r'dd\s+',
            r'format\s+',
            r'mkfs',
            r'>\s*/dev/',
            r'sudo\s+',
            r'su\s+',
            r'chmod\s+777',
            r'eval\s*\(',
            r'\$\(',  # Command substitution
            r'`',     # Backticks
        ]
    
    def validate_input(self, command: str, cwd: Optional[str] = None, 
                      env: Optional[Dict[str, str]] = None, shell: bool = False) -> List[str]:
        """Validate command for safety"""
        errors = []
        
        if not command:
            errors.append("Command is required")
            return errors
        
        # Parse command
        try:
            if shell:
                # Shell commands are more dangerous
                errors.append("Shell execution is not allowed for safety")
                return errors
            
            parts = shlex.split(command)
            if not parts:
                errors.append("Empty command")
                return errors
            
            base_cmd = parts[0]
            
            # Check if command is in whitelist
            if base_cmd not in self.allowed_commands:
                errors.append(f"Command '{base_cmd}' is not in allowed list")
            
            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    errors.append(f"Dangerous pattern detected: {pattern}")
            
            # Validate working directory
            if cwd:
                cwd_path = Path(cwd)
                if not cwd_path.exists():
                    errors.append(f"Working directory does not exist: {cwd}")
                elif not cwd_path.is_dir():
                    errors.append(f"Working directory is not a directory: {cwd}")
            
            # Check for path traversal attempts
            if '..' in command:
                errors.append("Path traversal (..) not allowed in commands")
            
        except ValueError as e:
            errors.append(f"Invalid command format: {e}")
        
        return errors
    
    def dry_run(self, context: ToolContext, command: str, cwd: Optional[str] = None,
                env: Optional[Dict[str, str]] = None, shell: bool = False) -> str:
        """Preview command execution"""
        working_dir = cwd or context.working_directory or os.getcwd()
        env_str = f" with {len(env)} env vars" if env else ""
        return f"Would execute: '{command}' in {working_dir}{env_str}"
    
    def _execute_impl(self, context: ToolContext, command: str, cwd: Optional[str] = None,
                     env: Optional[Dict[str, str]] = None, shell: bool = False) -> Dict[str, Any]:
        """Execute command safely"""
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        if context.environment:
            exec_env.update(context.environment)
        
        # Set working directory
        working_dir = cwd or str(context.working_directory) if context.working_directory else None
        
        # Execute command
        start_time = datetime.now()
        
        try:
            # Use shlex to properly parse command
            cmd_list = shlex.split(command)
            
            result = subprocess.run(
                cmd_list,
                cwd=working_dir,
                env=exec_env,
                capture_output=True,
                text=True,
                timeout=context.timeout or 30,  # Default 30s timeout
                check=False  # Don't raise on non-zero exit
            )
            
            end_time = datetime.now()
            
            return {
                'command': command,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0,
                'duration': (end_time - start_time).total_seconds()
            }
            
        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'exit_code': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False,
                'duration': context.timeout or 30
            }


class ProcessMonitorTool(AsyncTool[Dict[str, Any]]):
    """Monitor running processes"""
    
    def __init__(self):
        super().__init__(
            name="process_monitor",
            category=ToolCategory.PROCESS,
            description="Monitor system processes and resource usage"
        )
    
    def validate_input(self, process_name: Optional[str] = None, 
                      pid: Optional[int] = None, duration: float = 5.0) -> List[str]:
        """Validate monitoring parameters"""
        errors = []
        
        if not process_name and not pid:
            errors.append("Either process_name or pid must be provided")
        
        if pid is not None and pid <= 0:
            errors.append("PID must be positive")
        
        if duration < 0.1 or duration > 300:
            errors.append("Duration must be between 0.1 and 300 seconds")
        
        return errors
    
    def dry_run(self, context: ToolContext, process_name: Optional[str] = None,
                pid: Optional[int] = None, duration: float = 5.0) -> str:
        """Preview monitoring"""
        target = f"process '{process_name}'" if process_name else f"PID {pid}"
        return f"Would monitor {target} for {duration} seconds"
    
    async def _execute_async_impl(self, context: ToolContext, process_name: Optional[str] = None,
                                 pid: Optional[int] = None, duration: float = 5.0) -> Dict[str, Any]:
        """Monitor process asynchronously"""
        # Find process
        process = None
        
        if pid:
            try:
                process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                return {'error': f'Process with PID {pid} not found'}
        else:
            # Find by name
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    process = proc
                    break
            
            if not process:
                return {'error': f'Process "{process_name}" not found'}
        
        # Monitor process
        samples = []
        start_time = asyncio.get_event_loop().time()
        sample_interval = min(0.1, duration / 10)  # At least 10 samples
        
        while asyncio.get_event_loop().time() - start_time < duration:
            try:
                with process.oneshot():
                    sample = {
                        'timestamp': datetime.now().isoformat(),
                        'cpu_percent': process.cpu_percent(),
                        'memory_percent': process.memory_percent(),
                        'memory_rss': process.memory_info().rss,
                        'memory_vms': process.memory_info().vms,
                        'num_threads': process.num_threads(),
                        'status': process.status()
                    }
                    samples.append(sample)
            except psutil.NoSuchProcess:
                break
            
            await asyncio.sleep(sample_interval)
        
        # Calculate statistics
        if samples:
            cpu_values = [s['cpu_percent'] for s in samples if s['cpu_percent'] is not None]
            memory_values = [s['memory_percent'] for s in samples]
            
            stats = {
                'process_name': process.name(),
                'pid': process.pid,
                'samples': len(samples),
                'duration': duration,
                'cpu_avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'cpu_max': max(cpu_values) if cpu_values else 0,
                'memory_avg': sum(memory_values) / len(memory_values),
                'memory_max': max(memory_values),
                'samples_data': samples
            }
        else:
            stats = {'error': 'No samples collected'}
        
        return stats


class ProcessKillTool(Tool[bool]):
    """Safely terminate processes"""
    
    def __init__(self):
        super().__init__(
            name="process_kill",
            category=ToolCategory.PROCESS,
            description="Safely terminate processes with graceful shutdown"
        )
        # Processes that should never be killed
        self.protected_processes = {
            'init', 'systemd', 'kernel', 'launchd',
            'WindowServer', 'loginwindow', 'csrss.exe', 'smss.exe'
        }
    
    def validate_input(self, pid: int, signal_type: str = "TERM", force: bool = False) -> List[str]:
        """Validate kill parameters"""
        errors = []
        
        if pid <= 0:
            errors.append("PID must be positive")
        
        valid_signals = ['TERM', 'INT', 'HUP', 'QUIT']
        if force:
            valid_signals.append('KILL')
        
        if signal_type not in valid_signals:
            errors.append(f"Invalid signal: {signal_type}. Must be one of {valid_signals}")
        
        # Check if process exists and is not protected
        try:
            process = psutil.Process(pid)
            if process.name() in self.protected_processes:
                errors.append(f"Cannot kill protected process: {process.name()}")
            
            # Don't kill our own process
            if pid == os.getpid():
                errors.append("Cannot kill own process")
            
        except psutil.NoSuchProcess:
            errors.append(f"Process with PID {pid} not found")
        
        return errors
    
    def dry_run(self, context: ToolContext, pid: int, signal_type: str = "TERM", force: bool = False) -> str:
        """Preview process termination"""
        try:
            process = psutil.Process(pid)
            return f"Would send {signal_type} signal to {process.name()} (PID: {pid})"
        except psutil.NoSuchProcess:
            return f"Process with PID {pid} not found"
    
    def _execute_impl(self, context: ToolContext, pid: int, signal_type: str = "TERM", force: bool = False) -> bool:
        """Terminate process"""
        try:
            process = psutil.Process(pid)
            
            # Map signal names to signal numbers
            signal_map = {
                'TERM': signal.SIGTERM,
                'INT': signal.SIGINT,
                'HUP': signal.SIGHUP,
                'QUIT': signal.SIGQUIT,
                'KILL': signal.SIGKILL
            }
            
            sig = signal_map.get(signal_type, signal.SIGTERM)
            
            # Send signal
            process.send_signal(sig)
            
            # Wait for process to terminate (up to 5 seconds)
            try:
                process.wait(timeout=5)
                return True
            except psutil.TimeoutExpired:
                if force and signal_type != 'KILL':
                    # Escalate to SIGKILL
                    process.kill()
                    process.wait(timeout=2)
                    return True
                return False
                
        except psutil.NoSuchProcess:
            # Process already gone
            return True
        except Exception:
            return False