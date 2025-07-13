"""
Integration tests for discourse mode Claude Code integration
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from unified.agents.discourse import (
    DiscourseMCPServer,
    DiscourseCLIHandler,
    DiscourseFileDelegate,
    DiscourseAgent
)
from unified.agents.schema import Agent, AgentCategory, RiskProfile


class TestDiscourseMCPServer:
    """Test MCP server functionality"""
    
    def setup_method(self):
        """Set up test instance"""
        self.server = DiscourseMCPServer()
    
    def test_mcp_tools_defined(self):
        """Test that all MCP tools are properly defined"""
        tools = self.server.get_tools()
        
        # Check we have all expected tools
        tool_names = [t['name'] for t in tools]
        expected_tools = [
            'discourse_discuss',
            'discourse_question',
            'discourse_insight',
            'discourse_decide',
            'discourse_phase',
            'discourse_search',
            'discourse_context',
            'discourse_summarize',
            'discourse_outline',
            'discourse_export'
        ]
        
        for expected in expected_tools:
            assert expected in tool_names
    
    def test_execute_discuss_tool(self):
        """Test executing discuss tool"""
        result = self.server.execute_tool('discourse_discuss', {'topic': 'test topic'})
        assert result['status'] == 'success'
        assert 'test topic' in result['message']
    
    def test_execute_question_tool(self):
        """Test executing question tool"""
        result = self.server.execute_tool('discourse_question', {
            'question': 'How does this work?',
            'category': 'technical'
        })
        assert result['status'] == 'success'
        assert result.get('entry_id') is not None
    
    def test_execute_export_tool(self):
        """Test export functionality"""
        # Add some content first
        self.server.execute_tool('discourse_question', {'question': 'Test question'})
        self.server.execute_tool('discourse_insight', {'insight': 'Test insight'})
        
        # Export as markdown
        result = self.server.execute_tool('discourse_export', {'format': 'markdown'})
        assert result['status'] == 'success'
        assert result['format'] == 'markdown'
        assert 'Test question' in result['content']
        assert 'Test insight' in result['content']
    
    def test_mcp_config(self):
        """Test MCP configuration"""
        config = self.server.get_mcp_config()
        
        assert config['name'] == 'discourse'
        assert 'tools' in config
        assert 'prompts' in config
        assert config['capabilities']['read_only'] is True
        assert config['capabilities']['conversation_tracking'] is True
    
    def test_system_prompts(self):
        """Test system prompts for discourse mode"""
        prompts = self.server.get_prompts()
        
        assert 'system' in prompts
        assert 'assistant' in prompts
        assert 'READ-ONLY' in prompts['system']
        assert 'Discourse Mode' in prompts['assistant']


class TestDiscourseCLIHandler:
    """Test CLI handler functionality"""
    
    def setup_method(self):
        """Set up test instance"""
        agent = MagicMock(spec=Agent)
        agent.name = 'discourse'
        agent.category = AgentCategory.DISCOURSE
        
        discourse = DiscourseAgent(agent)
        self.handler = DiscourseCLIHandler(discourse)
    
    def test_enter_discourse_mode(self):
        """Test entering discourse mode"""
        assert not self.handler.in_discourse_mode
        
        with patch.object(self.handler.console, 'print') as mock_print:
            self.handler.enter_discourse_mode()
        
        assert self.handler.in_discourse_mode
        # Check that welcome message was printed
        assert mock_print.called
    
    def test_handle_natural_language(self):
        """Test natural language input becomes questions"""
        self.handler.in_discourse_mode = True
        
        # Natural language should be converted to questions
        handled = self.handler.handle_command("What about authentication?")
        assert handled is True
    
    def test_handle_discourse_commands(self):
        """Test handling discourse-specific commands"""
        self.handler.in_discourse_mode = True
        
        # Test valid command
        handled = self.handler.handle_command("/question What is the plan?")
        assert handled is True
        
        # Test help command
        with patch.object(self.handler, '_show_help') as mock_help:
            handled = self.handler.handle_command("/help")
            assert handled is True
            assert mock_help.called
    
    def test_exit_discourse_mode(self):
        """Test exiting discourse mode"""
        self.handler.in_discourse_mode = True
        
        with patch.object(self.handler.console, 'print') as mock_print:
            self.handler.exit_discourse_mode()
        
        assert not self.handler.in_discourse_mode
        assert mock_print.called
    
    def test_export_conversation(self):
        """Test conversation export"""
        # Add some content
        self.handler.discourse.execute('question', {'question': 'Test export'})
        
        # Export as markdown
        content = self.handler.export_conversation('markdown')
        assert content is not None
        assert 'Test export' in content


class TestDiscourseFileDelegate:
    """Test file delegation functionality"""
    
    def setup_method(self):
        """Set up test instance"""
        self.delegate = DiscourseFileDelegate(Path("/tmp/test"))
    
    @patch('unified.tools.file_tools.ReadFileTool.execute')
    def test_read_file(self, mock_execute):
        """Test read-only file access"""
        # Mock successful read
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = "file content"
        mock_result.end_time = "2023-01-01T00:00:00"
        mock_execute.return_value = mock_result
        
        result = self.delegate.read_file("/tmp/test/file.txt")
        
        assert result['status'] == 'success'
        assert result['content'] == "file content"
        assert len(self.delegate.accessed_files) == 1
    
    def test_search_files(self):
        """Test file search functionality"""
        with patch('pathlib.Path.rglob') as mock_rglob:
            # Mock file results
            mock_file = MagicMock()
            mock_file.is_file.return_value = True
            mock_file.stat.return_value.st_size = 1024
            mock_file.stat.return_value.st_mtime = 1234567890
            mock_rglob.return_value = [mock_file]
            
            result = self.delegate.search_files("*.py")
            
            assert result['status'] == 'success'
            assert result['pattern'] == "*.py"
            assert len(result['matches']) > 0
    
    def test_get_file_info(self):
        """Test getting file metadata"""
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('pathlib.Path.is_file') as mock_is_file:
                with patch('pathlib.Path.stat') as mock_stat:
                    mock_exists.return_value = True
                    mock_is_file.return_value = True
                    
                    # Mock file stats
                    mock_stat.return_value.st_size = 2048
                    mock_stat.return_value.st_mtime = 1234567890
                    mock_stat.return_value.st_ctime = 1234567890
                    
                    result = self.delegate.get_file_info("/tmp/test/file.py")
                    
                    assert result['status'] == 'success'
                    assert result['size'] == 2048
                    assert result['size_human'] == '2.0 KB'
                    assert result['is_text'] is True
    
    def test_list_directory(self):
        """Test directory listing"""
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('pathlib.Path.is_dir') as mock_is_dir:
                with patch('pathlib.Path.iterdir') as mock_iterdir:
                    mock_exists.return_value = True
                    mock_is_dir.return_value = True
                    
                    # Mock directory contents
                    file_mock = MagicMock()
                    file_mock.is_file.return_value = True
                    file_mock.name = "test.py"
                    file_mock.stat.return_value.st_size = 1024
                    file_mock.suffix = ".py"
                    
                    dir_mock = MagicMock()
                    dir_mock.is_file.return_value = False
                    dir_mock.is_dir.return_value = True
                    dir_mock.name = "subdir"
                    dir_mock.iterdir.return_value = []
                    
                    mock_iterdir.return_value = [file_mock, dir_mock]
                    
                    result = self.delegate.list_directory()
                    
                    assert result['status'] == 'success'
                    assert result['total_files'] == 1
                    assert result['total_directories'] == 1


class TestDiscourseIntegration:
    """Test full discourse integration"""
    
    def test_discourse_mode_blocks_mutations(self):
        """Test that discourse mode blocks all mutations"""
        from unified.core.command_executor import CommandExecutor
        
        # Create executor in discourse mode
        executor = CommandExecutor(discourse_mode=True)
        
        # Build context for code execution (which mutates)
        context = {
            'command': 'code',
            'raw_input': '/code --discourse',
            'agents': [],
            'discourse_context': executor.discourse_context
        }
        
        # Attempt to execute code command
        with pytest.raises(Exception) as exc_info:
            executor._execute_code(context)
        
        # Should be blocked by discourse_safe decorator
        assert "discourse mode" in str(exc_info.value).lower()
    
    def test_discourse_agent_in_help(self):
        """Test that discourse agent appears in help text"""
        from unified.core.command_parser import CommandParser
        from unified.agents.manager import AgentManager
        
        manager = AgentManager()
        parser = CommandParser(manager)
        
        help_text = parser.format_help()
        
        # Check for discourse agent
        assert '--discourse' in help_text or 'discourse' in help_text.lower()