"""
Integration tests for CLI interactive mode
"""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from unified.cli import cli


class TestCLIInteractive:
    """Test CLI interactive functionality"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()
    
    def test_cli_version(self, runner):
        """Test CLI version command"""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'unified-agents, version' in result.output
        assert '0.1.1' in result.output
    
    def test_cli_agents_command(self, runner):
        """Test agents listing command"""
        with patch('unified.cli.UnifiedCLI') as mock_cli_class:
            mock_instance = MagicMock()
            mock_cli_class.return_value = mock_instance
            
            result = runner.invoke(cli, ['agents'])
            
            assert result.exit_code == 0
            mock_instance.show_agents.assert_called_once()
    
    def test_cli_status_command(self, runner):
        """Test status command"""
        with patch('unified.cli.UnifiedCLI') as mock_cli_class:
            mock_instance = MagicMock()
            mock_cli_class.return_value = mock_instance
            
            result = runner.invoke(cli, ['status'])
            
            assert result.exit_code == 0
            mock_instance.show_phase_status.assert_called_once()
    
    def test_cli_info_command(self, runner):
        """Test agent info command"""
        with patch('unified.cli.UnifiedCLI') as mock_cli_class:
            mock_instance = MagicMock()
            mock_cli_class.return_value = mock_instance
            
            result = runner.invoke(cli, ['info', 'backend'])
            
            assert result.exit_code == 0
            mock_instance.show_agent_info.assert_called_once_with('backend')
    
    def test_cli_setup_command(self, runner):
        """Test setup command"""
        with patch('unified.cli.UnifiedCLI') as mock_cli_class:
            mock_instance = MagicMock()
            mock_cli_class.return_value = mock_instance
            
            result = runner.invoke(cli, ['setup'])
            
            assert result.exit_code == 0
            assert 'Setup complete!' in result.output
    
    @pytest.mark.slow
    def test_cli_interactive_mode_exit(self, runner):
        """Test interactive mode exit"""
        with patch('unified.cli.UnifiedCLI') as mock_cli_class:
            mock_instance = MagicMock()
            mock_cli_class.return_value = mock_instance
            
            # Simulate entering 'exit' command
            with patch('builtins.input', return_value='exit'):
                result = runner.invoke(cli, ['interactive'])
                
                assert result.exit_code == 0
                assert 'Goodbye!' in result.output