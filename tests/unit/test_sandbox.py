"""
Unit tests for sandbox framework
"""
import pytest
from pathlib import Path
import tempfile
import time
from unittest.mock import Mock, patch
from unified.sandbox import (
    SandboxConfig, SandboxStatus, SandboxResult,
    ProcessSandbox, DockerSandbox, SandboxManager,
    get_sandbox_manager
)
from unified.tools import ToolContext
from unified.tools.sandboxed_tools import (
    SandboxedCommandTool, SandboxedPythonTool,
    SandboxedFileTool, SandboxedNetworkTool
)


class TestSandboxConfig:
    """Test SandboxConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SandboxConfig()
        
        assert config.max_memory_mb == 512
        assert config.max_cpu_seconds == 30
        assert config.timeout_seconds == 60
        assert config.allow_network is False
        assert config.drop_privileges is True
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = SandboxConfig(
            max_memory_mb=256,
            timeout_seconds=10,
            allow_network=True,
            allowed_hosts=['example.com']
        )
        
        assert config.max_memory_mb == 256
        assert config.timeout_seconds == 10
        assert config.allow_network is True
        assert 'example.com' in config.allowed_hosts


class TestSandboxResult:
    """Test SandboxResult"""
    
    def test_result_success(self):
        """Test successful result"""
        result = SandboxResult(
            status=SandboxStatus.COMPLETED,
            exit_code=0,
            output={'stdout': 'hello', 'stderr': ''}
        )
        
        assert result.success is True
        assert result.status == SandboxStatus.COMPLETED
    
    def test_result_failure(self):
        """Test failed result"""
        result = SandboxResult(
            status=SandboxStatus.FAILED,
            exit_code=1,
            error="Command failed"
        )
        
        assert result.success is False
        assert result.error == "Command failed"
    
    def test_result_duration(self):
        """Test duration calculation"""
        from datetime import datetime, timedelta
        
        start = datetime.now()
        end = start + timedelta(seconds=5)
        
        result = SandboxResult(
            status=SandboxStatus.COMPLETED,
            start_time=start,
            end_time=end
        )
        
        assert abs(result.duration - 5.0) < 0.01


class TestProcessSandbox:
    """Test ProcessSandbox"""
    
    @pytest.fixture
    def sandbox(self):
        config = SandboxConfig(timeout_seconds=5)
        return ProcessSandbox(config)
    
    def test_setup(self, sandbox):
        """Test sandbox setup"""
        sandbox.setup()
        
        assert sandbox.temp_dir is not None
        assert sandbox.temp_dir.exists()
        
        # Cleanup
        sandbox.cleanup()
    
    def test_execute_success(self, sandbox):
        """Test successful command execution"""
        sandbox.setup()
        
        result = sandbox.execute("echo hello")
        
        assert result.success is True
        assert result.exit_code == 0
        assert 'hello' in result.output['stdout']
        
        sandbox.cleanup()
    
    def test_execute_failure(self, sandbox):
        """Test failed command execution"""
        sandbox.setup()
        
        result = sandbox.execute("false")
        
        assert result.success is False
        assert result.exit_code != 0
        assert result.status == SandboxStatus.FAILED
        
        sandbox.cleanup()
    
    def test_execute_timeout(self):
        """Test command timeout"""
        config = SandboxConfig(timeout_seconds=1)
        sandbox = ProcessSandbox(config)
        sandbox.setup()
        
        result = sandbox.execute("sleep 5")
        
        assert result.status == SandboxStatus.TIMEOUT
        assert result.success is False
        
        sandbox.cleanup()
    
    def test_command_validation(self):
        """Test command validation with allowed commands"""
        config = SandboxConfig(allowed_commands=['echo', 'ls'])
        sandbox = ProcessSandbox(config)
        sandbox.setup()
        
        # Allowed command
        result = sandbox.execute("echo test")
        assert result.success is True
        
        # Disallowed command
        result = sandbox.execute("rm -rf /")
        assert result.success is False
        assert "not allowed" in result.error
        
        sandbox.cleanup()
    
    @pytest.mark.skipif(
        not hasattr(__import__('resource'), 'setrlimit'),
        reason="Resource limits not available on this platform"
    )
    def test_resource_limits(self):
        """Test resource limits"""
        config = SandboxConfig(
            max_memory_mb=64,
            max_cpu_seconds=1
        )
        sandbox = ProcessSandbox(config)
        sandbox.setup()
        
        # This might not actually hit limits in test environment
        # but tests that limits are set without errors
        result = sandbox.execute("echo test")
        assert result.exit_code is not None
        
        sandbox.cleanup()


class TestDockerSandbox:
    """Test DockerSandbox"""
    
    @pytest.fixture
    def docker_available(self):
        """Check if Docker is available"""
        import subprocess
        try:
            result = subprocess.run(["docker", "version"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    @pytest.mark.skipif(
        not pytest.fixture('docker_available'),
        reason="Docker not available"
    )
    def test_docker_setup(self, docker_available):
        """Test Docker sandbox setup"""
        if not docker_available:
            pytest.skip("Docker not available")
        
        config = SandboxConfig()
        sandbox = DockerSandbox(config)
        
        try:
            sandbox.setup()
            assert sandbox.container_id is not None
        finally:
            sandbox.cleanup()
    
    @pytest.mark.skipif(
        not pytest.fixture('docker_available'),
        reason="Docker not available"
    )
    def test_docker_execute(self, docker_available):
        """Test Docker command execution"""
        if not docker_available:
            pytest.skip("Docker not available")
        
        config = SandboxConfig()
        sandbox = DockerSandbox(config)
        
        try:
            sandbox.setup()
            result = sandbox.execute("echo hello from docker")
            
            assert result.success is True
            assert "hello from docker" in result.output['stdout']
        finally:
            sandbox.cleanup()


class TestSandboxManager:
    """Test SandboxManager"""
    
    def test_create_process_sandbox(self):
        """Test creating process sandbox"""
        manager = SandboxManager()
        config = SandboxConfig()
        
        sandbox = manager.create_sandbox("test", config, prefer_docker=False)
        
        assert isinstance(sandbox, ProcessSandbox)
        assert "test" in manager.sandboxes
        
        manager.cleanup_sandbox("test")
        assert "test" not in manager.sandboxes
    
    def test_cleanup_all(self):
        """Test cleaning up all sandboxes"""
        manager = SandboxManager()
        config = SandboxConfig()
        
        # Create multiple sandboxes
        manager.create_sandbox("test1", config, prefer_docker=False)
        manager.create_sandbox("test2", config, prefer_docker=False)
        
        assert len(manager.sandboxes) == 2
        
        manager.cleanup_all()
        
        assert len(manager.sandboxes) == 0


class TestSandboxedTools:
    """Test sandboxed tool implementations"""
    
    @pytest.fixture
    def tool_context(self):
        return ToolContext(
            working_directory=Path.cwd(),
            session_id="test_session"
        )
    
    def test_sandboxed_command_tool(self, tool_context):
        """Test sandboxed command execution"""
        tool = SandboxedCommandTool()
        
        # Test validation
        errors = tool.validate_input("")
        assert len(errors) > 0
        
        errors = tool.validate_input("echo test")
        assert len(errors) == 0
        
        # Test dry run
        preview = tool.dry_run(tool_context, "echo test")
        assert "Would execute in sandbox" in preview
        
        # Test execution
        result = tool.execute(tool_context, "echo hello sandbox")
        assert result.success
        assert 'hello sandbox' in result.output['stdout']
    
    def test_sandboxed_python_tool(self, tool_context):
        """Test sandboxed Python execution"""
        tool = SandboxedPythonTool()
        
        # Test validation
        errors = tool.validate_input("import os")
        assert len(errors) > 0  # Dangerous import
        
        errors = tool.validate_input("print(2 + 2)")
        assert len(errors) == 0
        
        # Test syntax error detection
        errors = tool.validate_input("print(")
        assert any("Syntax error" in e for e in errors)
        
        # Test execution
        result = tool.execute(tool_context, "result = 2 + 2")
        assert result.success
        assert result.output == 4
    
    def test_sandboxed_file_tool(self, tool_context):
        """Test sandboxed file operations"""
        tool = SandboxedFileTool()
        
        # Test validation
        errors = tool.validate_input("invalid_op", "test.txt")
        assert len(errors) > 0
        
        errors = tool.validate_input("write", "test.txt", "content")
        assert len(errors) == 0
        
        # Test dry run
        preview = tool.dry_run(tool_context, "read", "test.txt")
        assert "Would read file" in preview
        
        # Test write and read
        with tempfile.TemporaryDirectory() as tmpdir:
            context = ToolContext(
                working_directory=Path(tmpdir),
                session_id="test"
            )
            
            # Write file
            result = tool.execute(context, "write", "test.txt", "Hello, World!")
            assert result.success
            
            # Read file
            result = tool.execute(context, "read", "test.txt")
            assert result.success
            assert "Hello, World!" in result.output
    
    def test_sandboxed_network_tool(self, tool_context):
        """Test sandboxed network operations"""
        tool = SandboxedNetworkTool(allowed_hosts=["example.com"])
        
        # Test validation
        errors = tool.validate_input("")
        assert len(errors) > 0
        
        errors = tool.validate_input("http://example.com")
        assert len(errors) == 0
        
        errors = tool.validate_input("http://evil.com")
        assert any("not in allowed list" in e for e in errors)
        
        # Test dry run
        preview = tool.dry_run(tool_context, "http://example.com")
        assert "Would send GET request" in preview


def test_global_sandbox_manager():
    """Test global sandbox manager instance"""
    manager = get_sandbox_manager()
    assert isinstance(manager, SandboxManager)
    
    # Should return same instance
    assert manager is get_sandbox_manager()