"""
Sandboxed execution environment for safe tool execution
"""
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
import subprocess
import tempfile
import shutil
import json
import os
import signal
import threading
import time
from datetime import datetime
import resource


class SandboxStatus(Enum):
    """Status of sandbox execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    KILLED = "killed"


@dataclass
class SandboxConfig:
    """Configuration for sandbox environment"""
    # Resource limits
    max_memory_mb: int = 512
    max_cpu_seconds: int = 30
    max_file_size_mb: int = 100
    max_process_count: int = 10
    max_open_files: int = 100
    
    # Network
    allow_network: bool = False
    allowed_hosts: List[str] = field(default_factory=list)
    
    # Filesystem
    readonly_paths: List[Path] = field(default_factory=list)
    writable_paths: List[Path] = field(default_factory=list)
    temp_dir: Optional[Path] = None
    
    # Execution
    timeout_seconds: int = 60
    allowed_commands: List[str] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    
    # Security
    drop_privileges: bool = True
    user: Optional[str] = None
    group: Optional[str] = None


@dataclass 
class SandboxResult:
    """Result of sandboxed execution"""
    status: SandboxStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> float:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success(self) -> bool:
        """Check if execution was successful"""
        return self.status == SandboxStatus.COMPLETED and self.exit_code == 0


class SandboxEnvironment(ABC):
    """Abstract base class for sandbox environments"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.status = SandboxStatus.PENDING
        self._cleanup_handlers: List[Callable] = []
    
    @abstractmethod
    def setup(self) -> None:
        """Set up the sandbox environment"""
        pass
    
    @abstractmethod
    def execute(self, command: Union[str, List[str]], **kwargs) -> SandboxResult:
        """Execute command in sandbox"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up sandbox environment"""
        pass
    
    def add_cleanup_handler(self, handler: Callable) -> None:
        """Add cleanup handler to be called on cleanup"""
        self._cleanup_handlers.append(handler)
    
    def _run_cleanup_handlers(self) -> None:
        """Run all cleanup handlers"""
        for handler in self._cleanup_handlers:
            try:
                handler()
            except Exception as e:
                # Log but don't fail cleanup
                print(f"Cleanup handler failed: {e}")


class ProcessSandbox(SandboxEnvironment):
    """Process-based sandbox using resource limits and isolation"""
    
    def __init__(self, config: SandboxConfig):
        super().__init__(config)
        self.temp_dir: Optional[Path] = None
        self._process: Optional[subprocess.Popen] = None
    
    def setup(self) -> None:
        """Set up process sandbox environment"""
        # Create temporary directory
        if self.config.temp_dir:
            self.temp_dir = self.config.temp_dir
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="sandbox_"))
            self.add_cleanup_handler(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
    
    def execute(self, command: Union[str, List[str]], **kwargs) -> SandboxResult:
        """Execute command with resource limits"""
        result = SandboxResult(
            status=SandboxStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # Prepare command
            if isinstance(command, str):
                cmd_list = command.split()
            else:
                cmd_list = command
            
            # Validate command
            if self.config.allowed_commands:
                base_cmd = cmd_list[0]
                if base_cmd not in self.config.allowed_commands:
                    result.status = SandboxStatus.FAILED
                    result.error = f"Command '{base_cmd}' not allowed"
                    return result
            
            # Set up environment
            env = os.environ.copy()
            env.update(self.config.environment_vars)
            
            # Remove dangerous environment variables
            for var in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'PYTHONPATH']:
                env.pop(var, None)
            
            # Set resource limits
            def set_limits():
                if hasattr(resource, 'RLIMIT_AS'):
                    # Memory limit
                    memory_limit = self.config.max_memory_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
                
                if hasattr(resource, 'RLIMIT_CPU'):
                    # CPU time limit  
                    resource.setrlimit(resource.RLIMIT_CPU, 
                                     (self.config.max_cpu_seconds, self.config.max_cpu_seconds))
                
                if hasattr(resource, 'RLIMIT_FSIZE'):
                    # File size limit
                    file_limit = self.config.max_file_size_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
                
                if hasattr(resource, 'RLIMIT_NPROC'):
                    # Process count limit
                    resource.setrlimit(resource.RLIMIT_NPROC, 
                                     (self.config.max_process_count, self.config.max_process_count))
                
                if hasattr(resource, 'RLIMIT_NOFILE'):
                    # Open files limit
                    resource.setrlimit(resource.RLIMIT_NOFILE,
                                     (self.config.max_open_files, self.config.max_open_files))
            
            # Execute with timeout
            self._process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(self.temp_dir),
                preexec_fn=set_limits if os.name != 'nt' else None,
                text=True
            )
            
            # Set up timeout
            timer = None
            if self.config.timeout_seconds:
                def timeout_handler():
                    if self._process and self._process.poll() is None:
                        self._process.terminate()
                        time.sleep(1)
                        if self._process.poll() is None:
                            self._process.kill()
                        result.status = SandboxStatus.TIMEOUT
                
                timer = threading.Timer(self.config.timeout_seconds, timeout_handler)
                timer.start()
            
            # Wait for completion
            stdout, stderr = self._process.communicate()
            
            if timer:
                timer.cancel()
            
            # Set result
            result.exit_code = self._process.returncode
            result.output = {
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': self._process.returncode
            }
            
            if result.status != SandboxStatus.TIMEOUT:
                if self._process.returncode == 0:
                    result.status = SandboxStatus.COMPLETED
                else:
                    result.status = SandboxStatus.FAILED
                    result.error = stderr or f"Process exited with code {self._process.returncode}"
            
            # Get resource usage if available
            if hasattr(resource, 'getrusage') and hasattr(resource, 'RUSAGE_CHILDREN'):
                usage = resource.getrusage(resource.RUSAGE_CHILDREN)
                result.resource_usage = {
                    'user_time': usage.ru_utime,
                    'system_time': usage.ru_stime,
                    'max_memory_kb': usage.ru_maxrss
                }
            
        except Exception as e:
            result.status = SandboxStatus.FAILED
            result.error = str(e)
        finally:
            result.end_time = datetime.now()
            self._process = None
        
        return result
    
    def cleanup(self) -> None:
        """Clean up process sandbox"""
        # Kill process if still running
        if self._process and self._process.poll() is None:
            self._process.terminate()
            time.sleep(1)
            if self._process.poll() is None:
                self._process.kill()
        
        # Run cleanup handlers
        self._run_cleanup_handlers()


class DockerSandbox(SandboxEnvironment):
    """Docker-based sandbox for stronger isolation"""
    
    def __init__(self, config: SandboxConfig, image: str = "python:3.9-slim"):
        super().__init__(config)
        self.image = image
        self.container_id: Optional[str] = None
        self.temp_dir: Optional[Path] = None
    
    def setup(self) -> None:
        """Set up Docker container"""
        # Create temporary directory for bind mount
        self.temp_dir = Path(tempfile.mkdtemp(prefix="docker_sandbox_"))
        self.add_cleanup_handler(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        
        # Build docker run command
        docker_cmd = [
            "docker", "run", "-d",
            "--rm",  # Auto-remove on stop
            f"--memory={self.config.max_memory_mb}m",
            f"--cpus=1",
            "--pids-limit", str(self.config.max_process_count),
            "--read-only",  # Read-only root filesystem
            "--security-opt", "no-new-privileges",
            "-v", f"{self.temp_dir}:/workspace:rw",
            "-w", "/workspace"
        ]
        
        # Add network restrictions
        if not self.config.allow_network:
            docker_cmd.extend(["--network", "none"])
        
        # Add environment variables
        for key, value in self.config.environment_vars.items():
            docker_cmd.extend(["-e", f"{key}={value}"])
        
        # Start container
        docker_cmd.extend([self.image, "sleep", "infinity"])
        
        try:
            result = subprocess.run(docker_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Failed to start container: {result.stderr}")
            
            self.container_id = result.stdout.strip()
            self.add_cleanup_handler(self._stop_container)
            
        except Exception as e:
            raise RuntimeError(f"Docker setup failed: {e}")
    
    def execute(self, command: Union[str, List[str]], **kwargs) -> SandboxResult:
        """Execute command in Docker container"""
        if not self.container_id:
            raise RuntimeError("Container not set up")
        
        result = SandboxResult(
            status=SandboxStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # Prepare command
            if isinstance(command, list):
                command = " ".join(command)
            
            # Execute in container
            docker_exec = [
                "docker", "exec",
                "-i",  # Interactive for stdin
                self.container_id,
                "/bin/sh", "-c", command
            ]
            
            # Run with timeout
            process = subprocess.Popen(
                docker_exec,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Set up timeout
            timer = None
            if self.config.timeout_seconds:
                def timeout_handler():
                    if process.poll() is None:
                        subprocess.run(["docker", "kill", self.container_id], 
                                     capture_output=True)
                        result.status = SandboxStatus.TIMEOUT
                
                timer = threading.Timer(self.config.timeout_seconds, timeout_handler)
                timer.start()
            
            # Wait for completion
            stdout, stderr = process.communicate()
            
            if timer:
                timer.cancel()
            
            # Set result
            result.exit_code = process.returncode
            result.output = {
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': process.returncode
            }
            
            if result.status != SandboxStatus.TIMEOUT:
                if process.returncode == 0:
                    result.status = SandboxStatus.COMPLETED
                else:
                    result.status = SandboxStatus.FAILED
                    result.error = stderr or f"Process exited with code {process.returncode}"
            
            # Get container stats
            stats_result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "{{json .}}", self.container_id],
                capture_output=True,
                text=True
            )
            if stats_result.returncode == 0 and stats_result.stdout:
                try:
                    stats = json.loads(stats_result.stdout)
                    result.resource_usage = {
                        'memory_usage': stats.get('MemUsage', 'unknown'),
                        'cpu_usage': stats.get('CPUPerc', 'unknown')
                    }
                except:
                    pass
            
        except Exception as e:
            result.status = SandboxStatus.FAILED
            result.error = str(e)
        finally:
            result.end_time = datetime.now()
        
        return result
    
    def _stop_container(self) -> None:
        """Stop and remove Docker container"""
        if self.container_id:
            subprocess.run(["docker", "stop", self.container_id], 
                         capture_output=True)
            self.container_id = None
    
    def cleanup(self) -> None:
        """Clean up Docker sandbox"""
        self._run_cleanup_handlers()


class SandboxManager:
    """Manager for sandbox environments"""
    
    def __init__(self):
        self.sandboxes: Dict[str, SandboxEnvironment] = {}
        self.docker_available = self._check_docker()
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(["docker", "version"], 
                                  capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def create_sandbox(self, name: str, config: SandboxConfig, 
                      prefer_docker: bool = True) -> SandboxEnvironment:
        """Create a new sandbox environment"""
        # Choose sandbox type
        if prefer_docker and self.docker_available:
            sandbox = DockerSandbox(config)
        else:
            sandbox = ProcessSandbox(config)
        
        # Set up sandbox
        sandbox.setup()
        
        # Store reference
        self.sandboxes[name] = sandbox
        
        return sandbox
    
    def get_sandbox(self, name: str) -> Optional[SandboxEnvironment]:
        """Get existing sandbox by name"""
        return self.sandboxes.get(name)
    
    def cleanup_sandbox(self, name: str) -> None:
        """Clean up and remove a sandbox"""
        sandbox = self.sandboxes.get(name)
        if sandbox:
            sandbox.cleanup()
            del self.sandboxes[name]
    
    def cleanup_all(self) -> None:
        """Clean up all sandboxes"""
        for name in list(self.sandboxes.keys()):
            self.cleanup_sandbox(name)


# Global sandbox manager instance
_sandbox_manager = SandboxManager()


def get_sandbox_manager() -> SandboxManager:
    """Get global sandbox manager instance"""
    return _sandbox_manager