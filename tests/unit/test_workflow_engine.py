"""
Unit tests for Workflow Engine
"""
import pytest
from unittest.mock import Mock, MagicMock
from unified.workflows.engine import WorkflowEngine


class TestWorkflowEngine:
    """Test WorkflowEngine functionality"""
    
    @pytest.fixture
    def engine(self, mock_agent_manager):
        """Create WorkflowEngine instance with mocked dependencies"""
        mock_phase_manager = Mock()
        return WorkflowEngine(mock_agent_manager, mock_phase_manager)
    
    def test_feature_workflow_structure(self, engine):
        """Test feature workflow has correct structure"""
        workflow = engine.workflows['feature']
        
        assert workflow['name'] == 'Feature Development Workflow'
        assert workflow['type'] == 'feature'
        assert len(workflow['steps']) == 7
        
        # Check first step
        first_step = workflow['steps'][0]
        assert first_step['name'] == 'Requirements Gathering'
        assert 'requirements' in first_step['agents']
        assert first_step['phase'] == 1
    
    def test_bug_workflow_structure(self, engine):
        """Test bug workflow has correct structure"""
        workflow = engine.workflows['bug']
        
        assert workflow['name'] == 'Bug Investigation Workflow'
        assert workflow['type'] == 'bug'
        assert len(workflow['steps']) == 6
        
        # Check debugging step
        debug_step = next(s for s in workflow['steps'] if s['name'] == 'Debugging')
        assert 'backend' in debug_step['agents'] or 'frontend' in debug_step['agents']
    
    def test_security_workflow_structure(self, engine):
        """Test security workflow has correct structure"""
        workflow = engine.workflows['security']
        
        assert workflow['name'] == 'Security Audit Workflow'
        assert workflow['type'] == 'security'
        
        # Check security-specific steps
        step_names = [s['name'] for s in workflow['steps']]
        assert 'Threat Modeling' in step_names
        assert 'Vulnerability Scanning' in step_names
    
    def test_start_workflow_success(self, engine):
        """Test starting a workflow successfully"""
        result = engine.start_workflow('feature')
        
        assert result['status'] == 'success'
        assert 'Started Feature Development Workflow' in result['message']
        assert result['workflow'] == 'feature'
        assert result['next_step']['name'] == 'Requirements Gathering'
        assert engine.current_workflow == 'feature'
        assert engine.current_step == 0
    
    def test_start_workflow_invalid_type(self, engine):
        """Test starting workflow with invalid type"""
        result = engine.start_workflow('invalid')
        
        assert result['status'] == 'error'
        assert 'Unknown workflow type' in result['message']
        assert engine.current_workflow is None
    
    def test_start_workflow_already_active(self, engine):
        """Test starting workflow when one is already active"""
        # Start first workflow
        engine.start_workflow('feature')
        
        # Try to start another
        result = engine.start_workflow('bug')
        
        assert result['status'] == 'error'
        assert 'already active' in result['message']
        assert engine.current_workflow == 'feature'
    
    def test_execute_next_step(self, engine):
        """Test executing next step in workflow"""
        # Start workflow
        engine.start_workflow('feature')
        
        # Execute first step
        result = engine.execute_next_step()
        
        assert result['status'] == 'success'
        assert 'Completed: Requirements Gathering' in result['message']
        assert engine.current_step == 1
        assert result['next_step']['name'] == 'Design & Architecture'
    
    def test_execute_next_step_workflow_complete(self, engine):
        """Test executing next step when workflow is complete"""
        # Start workflow and move to last step
        engine.start_workflow('feature')
        engine.current_step = len(engine.workflows['feature']['steps']) - 1
        
        # Execute last step
        result = engine.execute_next_step()
        
        assert result['status'] == 'success'
        assert 'workflow complete' in result['message']
        assert engine.current_workflow is None
        assert engine.current_step is None
    
    def test_execute_next_step_no_workflow(self, engine):
        """Test executing next step with no active workflow"""
        result = engine.execute_next_step()
        
        assert result['status'] == 'error'
        assert 'No active workflow' in result['message']
    
    def test_get_workflow_status_active(self, engine):
        """Test getting status of active workflow"""
        # Start workflow and advance a few steps
        engine.start_workflow('feature')
        engine.current_step = 2
        
        status = engine.get_workflow_status()
        
        assert status['status'] == 'active'
        assert status['workflow'] == 'Feature Development Workflow'
        assert status['type'] == 'feature'
        assert status['current_step'] == 3  # 0-indexed + 1
        assert status['total_steps'] == 7
        assert status['progress'] == pytest.approx(42.86, rel=0.01)  # 3/7 * 100
        assert status['current_step_info']['name'] == 'Implementation'
    
    def test_get_workflow_status_inactive(self, engine):
        """Test getting status with no active workflow"""
        status = engine.get_workflow_status()
        
        assert status['status'] == 'info'
        assert 'feature' in status['available_workflows']
        assert 'bug' in status['available_workflows']
        assert 'security' in status['available_workflows']
    
    def test_cancel_workflow(self, engine):
        """Test canceling active workflow"""
        # Start workflow
        engine.start_workflow('feature')
        
        # Cancel it
        result = engine.cancel_workflow()
        
        assert result['status'] == 'success'
        assert 'Cancelled workflow' in result['message']
        assert engine.current_workflow is None
        assert engine.current_step is None
    
    def test_cancel_workflow_none_active(self, engine):
        """Test canceling when no workflow is active"""
        result = engine.cancel_workflow()
        
        assert result['status'] == 'error'
        assert 'No active workflow' in result['message']