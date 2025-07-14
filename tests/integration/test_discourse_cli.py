"""
Integration tests for discourse agent CLI functionality
"""
import pytest
from click.testing import CliRunner
from unified.cli import cli
from unified.agents.discourse import DiscourseGuardrailException


def test_discourse_agent_blocks_code_execution():
    """Test that --discourse prevents code execution"""
    runner = CliRunner()
    
    # Try to execute code with discourse agent
    result = runner.invoke(cli, ['interactive'], input='/code --discourse\nexit\n')
    
    # Should either show error or indicate read-only mode
    assert result.exit_code == 0
    assert 'discourse' in result.output.lower() or 'read-only' in result.output.lower()


def test_discourse_agent_allows_analysis():
    """Test that --discourse allows read-only analysis"""
    runner = CliRunner()
    
    # Try to analyze with discourse agent
    result = runner.invoke(cli, ['interactive'], input='/analyze --discourse\nexit\n')
    
    # Should succeed
    assert result.exit_code == 0
    # Analyze should work in discourse mode
    assert 'error' not in result.output.lower() or 'Analysis execution context prepared' in result.output


def test_discourse_agent_blocks_deployment():
    """Test that --discourse prevents deployment"""
    runner = CliRunner()
    
    # Try to deploy with discourse agent
    result = runner.invoke(cli, ['interactive'], input='/deploy --discourse\nexit\n')
    
    # Should show error or indicate blocked
    assert result.exit_code == 0
    assert 'discourse' in result.output.lower() or 'not permitted' in result.output.lower()


def test_discourse_agent_info():
    """Test that discourse agent info is available"""
    runner = CliRunner()
    
    # Get info about discourse agent
    result = runner.invoke(cli, ['info', 'discourse'])
    
    # Should show discourse agent details
    assert result.exit_code == 0
    assert 'discourse' in result.output.lower()
    assert 'conversational facilitator' in result.output.lower()


def test_discourse_agent_in_agent_list():
    """Test that discourse agent appears in agent list"""
    runner = CliRunner()
    
    # List all agents
    result = runner.invoke(cli, ['agents'])
    
    # Should include discourse agent
    assert result.exit_code == 0
    assert 'discourse' in result.output.lower()
    assert '--discourse' in result.output