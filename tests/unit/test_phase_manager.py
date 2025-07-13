"""
Unit tests for Phase Manager
"""
import pytest
from unittest.mock import Mock, MagicMock
from unified.core.phase_manager import PhaseManager


class TestPhaseManager:
    """Test PhaseManager functionality"""
    
    @pytest.fixture
    def phase_manager(self, mock_agent_manager):
        """Create PhaseManager instance with mocked AgentManager"""
        # Mock agents for phases
        mock_agent_manager.get_agents_by_phase.return_value = {
            'primary': [Mock(name='requirements')],
            'support': [Mock(name='architect')]
        }
        return PhaseManager(mock_agent_manager)
    
    def test_initial_phase(self, phase_manager):
        """Test initial phase state"""
        assert phase_manager.current_phase == 1
        status = phase_manager.get_phase_status()
        assert status['phase'] == 1
        assert status['name'] == 'Requirements Gathering'
    
    def test_advance_phase(self, phase_manager):
        """Test advancing to next phase"""
        # Mark current phase complete
        phase_manager.phase_outputs[1] = {
            'requirements_doc': True,
            'user_stories': True,
            'acceptance_criteria': True
        }
        
        # Advance phase
        result = phase_manager.advance_phase()
        assert result is True
        assert phase_manager.current_phase == 2
        
        status = phase_manager.get_phase_status()
        assert status['phase'] == 2
        assert status['name'] == 'Design & Architecture'
    
    def test_advance_phase_incomplete(self, phase_manager):
        """Test advancing when current phase is incomplete"""
        # Leave outputs incomplete
        phase_manager.phase_outputs[1] = {
            'requirements_doc': True,
            'user_stories': False,
            'acceptance_criteria': False
        }
        
        result = phase_manager.advance_phase()
        assert result is False
        assert phase_manager.current_phase == 1
    
    def test_advance_phase_at_end(self, phase_manager):
        """Test advancing when at last phase"""
        phase_manager.current_phase = 10
        phase_manager.phase_outputs[10] = {
            'deployment_complete': True,
            'monitoring_setup': True
        }
        
        result = phase_manager.advance_phase()
        assert result is False
        assert phase_manager.current_phase == 10
    
    def test_goto_phase_valid(self, phase_manager):
        """Test jumping to a valid phase"""
        result = phase_manager.goto_phase(5)
        assert result is True
        assert phase_manager.current_phase == 5
        
        status = phase_manager.get_phase_status()
        assert status['phase'] == 5
        assert status['name'] == 'Testing & QA'
    
    def test_goto_phase_invalid(self, phase_manager):
        """Test jumping to invalid phase numbers"""
        # Test phase 0
        result = phase_manager.goto_phase(0)
        assert result is False
        assert phase_manager.current_phase == 1
        
        # Test phase 11
        result = phase_manager.goto_phase(11)
        assert result is False
        assert phase_manager.current_phase == 1
    
    def test_mark_output_complete(self, phase_manager):
        """Test marking phase output as complete"""
        phase_manager.mark_output_complete(1, 'requirements_doc')
        
        assert phase_manager.phase_outputs[1]['requirements_doc'] is True
        assert phase_manager.phase_outputs[1]['user_stories'] is False
    
    def test_is_phase_complete(self, phase_manager):
        """Test checking if phase is complete"""
        # Initially incomplete
        assert phase_manager.is_phase_complete(1) is False
        
        # Mark all outputs complete
        phase_manager.phase_outputs[1] = {
            'requirements_doc': True,
            'user_stories': True,
            'acceptance_criteria': True
        }
        
        assert phase_manager.is_phase_complete(1) is True
    
    def test_get_phase_agents(self, phase_manager, mock_agent_manager):
        """Test getting agents for a phase"""
        agents = phase_manager.get_phase_agents(1)
        
        assert 'primary' in agents
        assert 'support' in agents
        assert len(agents['primary']) == 1
        assert agents['primary'][0].name == 'requirements'
        
        # Verify agent manager was called correctly
        mock_agent_manager.get_agents_by_phase.assert_called_with(1)
    
    def test_get_phase_status_with_outputs(self, phase_manager):
        """Test getting detailed phase status"""
        # Set some outputs
        phase_manager.phase_outputs[1] = {
            'requirements_doc': True,
            'user_stories': False,
            'acceptance_criteria': True
        }
        
        status = phase_manager.get_phase_status()
        
        assert status['phase'] == 1
        assert status['name'] == 'Requirements Gathering'
        assert status['outputs']['requirements_doc'] is True
        assert status['outputs']['user_stories'] is False
        assert status['outputs']['acceptance_criteria'] is True
        assert status['completion'] == pytest.approx(66.67, rel=0.01)  # 2/3 * 100
    
    def test_phase_metadata(self, phase_manager):
        """Test phase metadata is correctly structured"""
        phases = phase_manager.phases
        
        assert len(phases) == 10
        assert phases[1]['name'] == 'Requirements Gathering'
        assert phases[10]['name'] == 'Deployment & DevOps'
        
        # Check phase 1 outputs
        assert 'requirements_doc' in phases[1]['outputs']
        assert 'user_stories' in phases[1]['outputs']
        
        # Check phase 5 outputs
        assert 'unit_tests' in phases[5]['outputs']
        assert 'integration_tests' in phases[5]['outputs']