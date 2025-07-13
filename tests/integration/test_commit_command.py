"""
Integration tests for /commit command
"""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from unified.cli import cli
from unified.core.command_parser import ParsedCommand


def test_commit_command_parsing():
    """Test that commit command is properly parsed"""
    from unified.agents.manager import AgentManager
    from unified.core.command_parser import CommandParser
    
    manager = AgentManager()
    parser = CommandParser(manager)
    
    # Test basic command
    parsed = parser.parse("/commit")
    assert parsed.base_command == "commit"
    assert parsed.options == {}
    
    # Test with options
    parsed = parser.parse("/commit --all --dry-run")
    assert parsed.base_command == "commit"
    assert parsed.options['all'] is True
    assert parsed.options['dry_run'] is True
    
    # Test all options
    parsed = parser.parse("/commit --all --single --dry-run --force-branch --skip-safety")
    assert parsed.options['all'] is True
    assert parsed.options['single'] is True
    assert parsed.options['dry_run'] is True
    assert parsed.options['force_branch'] is True
    assert parsed.options['skip_safety'] is True


def test_commit_in_help_text():
    """Test that commit command appears in help"""
    from unified.agents.manager import AgentManager
    from unified.core.command_parser import CommandParser
    
    manager = AgentManager()
    parser = CommandParser(manager)
    
    help_text = parser.format_help()
    assert "/commit" in help_text
    assert "Intelligent git commit with branch safety" in help_text
    assert "--all" in help_text
    assert "--dry-run" in help_text


@patch('unified.tools.git_tools.GitCommitAnalyzer._is_git_repo')
@patch('unified.tools.git_tools.GitCommitAnalyzer._get_current_branch')
@patch('unified.tools.git_tools.GitCommitAnalyzer._get_changed_files')
def test_commit_command_execution(mock_files, mock_branch, mock_is_repo):
    """Test commit command execution through CLI"""
    runner = CliRunner()
    
    # Mock git state
    mock_is_repo.return_value = True
    mock_branch.return_value = "feature/test"
    mock_files.return_value = [
        {'path': 'src/file.py', 'status': 'M', 'staged': True}
    ]
    
    # Test dry run
    result = runner.invoke(cli, ['interactive'], input='/commit --dry-run\nexit\n')
    assert result.exit_code == 0
    assert "COMMIT ANALYSIS" in result.output or "Would create" in result.output


@patch('unified.tools.git_tools.GitCommitAnalyzer._is_git_repo')
@patch('unified.tools.git_tools.GitCommitAnalyzer._get_current_branch')
@patch('unified.tools.git_tools.GitCommitAnalyzer._get_changed_files')
@patch('subprocess.run')
def test_protected_branch_handling(mock_run, mock_files, mock_branch, mock_is_repo):
    """Test protected branch detection and handling"""
    runner = CliRunner()
    
    # Mock git state - on protected branch
    mock_is_repo.return_value = True
    mock_branch.return_value = "main"
    mock_files.return_value = [
        {'path': 'src/auth.py', 'status': 'M', 'staged': True}
    ]
    
    # Mock subprocess for branch creation
    mock_run.return_value = MagicMock(returncode=0)
    
    # Test dry run on protected branch
    result = runner.invoke(cli, ['interactive'], input='/commit --dry-run\nexit\n')
    assert result.exit_code == 0
    assert "protected branch" in result.output.lower() or "Would create branch" in result.output


def test_pr_prompt_not_shown_on_dry_run():
    """Test that PR prompt is not shown on dry run"""
    runner = CliRunner()
    
    with patch('unified.tools.git_tools.GitCommitAnalyzer.execute') as mock_execute:
        mock_execute.return_value = MagicMock(
            success=True,
            output={
                'current_branch': 'feature/test',
                'on_protected_branch': False,
                'commit_groups': [{'type': 'fix', 'description': 'test'}],
                'should_prompt_pr': False  # Dry run should not prompt
            }
        )
        
        result = runner.invoke(cli, ['interactive'], input='/commit --dry-run\nexit\n')
        assert "Would you like to create a pull request?" not in result.output


def test_commit_command_in_allowed_list():
    """Test that commit is in allowed commands"""
    from unified.core.command_executor import CommandExecutor
    
    assert 'commit' in CommandExecutor.ALLOWED_COMMANDS


def test_commit_marked_as_mutating():
    """Test that commit is marked as mutating for discourse mode"""
    from unified.core.command_executor import CommandExecutor
    
    assert hasattr(CommandExecutor._execute_commit, '_mutates')
    assert CommandExecutor._execute_commit._mutates is True