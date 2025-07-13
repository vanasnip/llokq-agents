"""
Unit tests for Tool abstraction
"""
import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch
from unified.tools import (
    Tool, ToolContext, ToolResult, ToolStatus, ToolCategory,
    ReadFileTool, WriteFileTool, DeleteFileTool,
    CommandExecutionTool
)


class TestToolBase:
    """Test base Tool functionality"""
    
    class MockTool(Tool[str]):
        """Mock tool for testing"""
        
        def __init__(self):
            super().__init__("mock_tool", ToolCategory.DATA_TRANSFORM, "Mock tool for testing")
        
        def validate_input(self, value: str, required: bool = True) -> list:
            errors = []
            if required and not value:
                errors.append("Value is required")
            if value and len(value) > 10:
                errors.append("Value too long")
            return errors
        
        def dry_run(self, context: ToolContext, value: str, required: bool = True) -> str:
            return f"Would process: {value}"
        
        def _execute_impl(self, context: ToolContext, value: str, required: bool = True) -> str:
            return f"Processed: {value}"
    
    @pytest.fixture
    def mock_tool(self):
        return self.MockTool()
    
    @pytest.fixture
    def tool_context(self):
        return ToolContext(
            working_directory=Path.cwd(),
            user="test_user",
            session_id="test_session",
            dry_run=False
        )
    
    def test_tool_creation(self, mock_tool):
        """Test tool creation and properties"""
        assert mock_tool.name == "mock_tool"
        assert mock_tool.category == ToolCategory.DATA_TRANSFORM
        assert mock_tool.description == "Mock tool for testing"
        assert mock_tool.get_status() == ToolStatus.NOT_STARTED
    
    def test_tool_validation_success(self, mock_tool, tool_context):
        """Test successful validation"""
        result = mock_tool.execute(tool_context, "valid")
        assert result.success
        assert result.output == "Processed: valid"
        assert result.status == ToolStatus.COMPLETED
    
    def test_tool_validation_failure(self, mock_tool, tool_context):
        """Test validation failure"""
        result = mock_tool.execute(tool_context, "")
        assert result.failed
        assert result.error == "Validation failed: Value is required"
        assert result.status == ToolStatus.FAILED
    
    def test_tool_dry_run(self, mock_tool):
        """Test dry run mode"""
        context = ToolContext(working_directory=Path.cwd(), dry_run=True)
        result = mock_tool.execute(context, "test")
        assert result.success
        assert result.dry_run_preview == "Would process: test"
        assert result.output is None
    
    def test_tool_with_timeout(self, mock_tool):
        """Test tool execution with timeout"""
        class SlowTool(Tool[str]):
            def validate_input(self, *args, **kwargs):
                return []
            
            def dry_run(self, context, *args, **kwargs):
                return "Would run slowly"
            
            def _execute_impl(self, context, *args, **kwargs):
                import time
                time.sleep(2)
                return "Done"
        
        slow_tool = SlowTool("slow", ToolCategory.PROCESS, "Slow tool")
        context = ToolContext(working_directory=Path.cwd(), timeout=0.1)
        result = slow_tool.execute(context)
        
        assert result.failed
        assert "timed out" in result.error
    
    def test_tool_capabilities(self, mock_tool):
        """Test getting tool capabilities"""
        caps = mock_tool.get_capabilities()
        assert caps['name'] == "mock_tool"
        assert caps['category'] == "data_transform"
        assert caps['supports_dry_run'] is True
        assert caps['supports_timeout'] is True


class TestFileTools:
    """Test file operation tools"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def tool_context(self, temp_dir):
        return ToolContext(working_directory=temp_dir)
    
    def test_read_file_tool(self, temp_dir, tool_context):
        """Test reading files"""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        tool = ReadFileTool()
        result = tool.execute(tool_context, test_file)
        
        assert result.success
        assert result.output == "Hello, World!"
    
    def test_read_file_validation(self, tool_context):
        """Test read file validation"""
        tool = ReadFileTool()
        
        # Non-existent file
        result = tool.execute(tool_context, "nonexistent.txt")
        assert result.failed
        assert "does not exist" in result.error
    
    def test_write_file_tool(self, temp_dir, tool_context):
        """Test writing files"""
        tool = WriteFileTool()
        test_file = temp_dir / "output.txt"
        
        result = tool.execute(tool_context, test_file, "Test content")
        
        assert result.success
        assert test_file.exists()
        assert test_file.read_text() == "Test content"
    
    def test_write_file_backup(self, temp_dir, tool_context):
        """Test file backup on overwrite"""
        tool = WriteFileTool()
        test_file = temp_dir / "existing.txt"
        test_file.write_text("Original content")
        
        result = tool.execute(tool_context, test_file, "New content")
        
        assert result.success
        assert test_file.read_text() == "New content"
        
        # Check backup
        backup_file = test_file.with_suffix('.txt.backup')
        assert backup_file.exists()
        assert backup_file.read_text() == "Original content"
    
    def test_delete_file_tool(self, temp_dir, tool_context):
        """Test file deletion"""
        tool = DeleteFileTool()
        test_file = temp_dir / "delete_me.txt"
        test_file.write_text("Delete this")
        
        result = tool.execute(tool_context, test_file)
        
        assert result.success
        assert not test_file.exists()
        
        # Check trash
        trash_dir = temp_dir / '.trash'
        assert trash_dir.exists()
        assert any(f.name.startswith("delete_me.txt_") for f in trash_dir.iterdir())
    
    def test_file_path_security(self, temp_dir, tool_context):
        """Test path traversal prevention"""
        tool = ReadFileTool()
        
        # Try to access outside working directory
        result = tool.execute(tool_context, "../../../etc/passwd")
        assert result.failed
        assert "outside working directory" in result.error


class TestProcessTools:
    """Test process execution tools"""
    
    @pytest.fixture
    def tool_context(self):
        return ToolContext(working_directory=Path.cwd())
    
    def test_command_execution_validation(self, tool_context):
        """Test command validation"""
        tool = CommandExecutionTool()
        
        # Allowed command
        errors = tool.validate_input("ls -la")
        assert errors == []
        
        # Disallowed command
        errors = tool.validate_input("rm -rf /")
        assert len(errors) > 0
        assert any("not in allowed list" in e for e in errors)
        
        # Dangerous pattern
        errors = tool.validate_input("echo test && rm -rf /")
        assert len(errors) > 0
        assert any("Dangerous pattern" in e for e in errors)
    
    def test_command_execution_dry_run(self, tool_context):
        """Test command dry run"""
        tool = CommandExecutionTool()
        context = ToolContext(working_directory=Path.cwd(), dry_run=True)
        
        result = tool.execute(context, "echo hello")
        
        assert result.success
        assert "Would execute: 'echo hello'" in result.dry_run_preview
    
    @patch('subprocess.run')
    def test_command_execution(self, mock_run, tool_context):
        """Test actual command execution"""
        tool = CommandExecutionTool()
        
        # Mock successful execution
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Hello\n",
            stderr=""
        )
        
        result = tool.execute(tool_context, "echo Hello")
        
        assert result.success
        assert result.output['exit_code'] == 0
        assert result.output['stdout'] == "Hello\n"
        assert result.output['success'] is True
        
        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ['echo', 'Hello']