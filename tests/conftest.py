"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for testing"""
    return {
        'name': 'test_agent',
        'command': '--test',
        'category': 'development',
        'identity': 'Test Agent for unit testing',
        'core_belief': 'Testing is essential',
        'primary_question': 'Is this code tested?',
        'decision_framework': 'Test-driven development',
        'risk_profile': 'conservative',
        'success_metrics': 'Test coverage above 80%',
        'communication_style': 'Clear and concise',
        'problem_solving': 'Systematic testing',
        'mcp_preferences': ['testing', 'mocking'],
        'focus_areas': ['unit tests', 'integration tests'],
        'values': 'Quality assurance',
        'limitations': 'Testing only',
        'compatible_agents': ['qa'],
        'handoff_protocols': {},
        'primary_phases': [5],
        'support_phases': [4, 6]
    }


@pytest.fixture
def mock_agent_manager(mocker):
    """Mock AgentManager for testing"""
    from unified.agents.manager import AgentManager
    manager = mocker.Mock(spec=AgentManager)
    manager.agents = {}
    return manager