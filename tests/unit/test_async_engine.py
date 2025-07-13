"""
Unit tests for Async Workflow Engine
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from unified.workflows.async_engine import (
    AsyncWorkflowEngine, WorkflowStep, StepStatus, StepResult
)
from unified.core.event_bus import EventType


class TestAsyncWorkflowEngine:
    """Test AsyncWorkflowEngine functionality"""
    
    @pytest.fixture
    def mock_managers(self):
        """Create mock agent and phase managers"""
        agent_manager = Mock()
        agent_manager.activate_agent = Mock()
        agent_manager.deactivate_agent = Mock()
        agent_manager.active_agents = set()
        
        phase_manager = Mock()
        
        return agent_manager, phase_manager
    
    @pytest.fixture
    def async_engine(self, mock_managers):
        """Create AsyncWorkflowEngine instance"""
        agent_manager, phase_manager = mock_managers
        return AsyncWorkflowEngine(agent_manager, phase_manager)
    
    def test_workflow_definitions(self, async_engine):
        """Test workflow definitions are loaded"""
        assert 'feature_async' in async_engine.workflows
        assert 'security_audit_async' in async_engine.workflows
        
        feature_workflow = async_engine.workflows['feature_async']
        assert feature_workflow['name'] == 'Async Feature Development'
        assert len(feature_workflow['steps']) == 8
    
    def test_workflow_step_dependencies(self, async_engine):
        """Test workflow step dependency structure"""
        feature_steps = async_engine.workflows['feature_async']['steps']
        
        # Find specific steps
        req_step = next(s for s in feature_steps if s.id == 'req_gather')
        backend_step = next(s for s in feature_steps if s.id == 'backend_impl')
        
        # Requirements should have no dependencies
        assert req_step.depends_on == []
        
        # Backend should depend on architecture and API design
        assert 'arch_design' in backend_step.depends_on
        assert 'api_design' in backend_step.depends_on
    
    def test_step_can_run(self):
        """Test WorkflowStep.can_run logic"""
        step = WorkflowStep(
            id='test',
            name='Test Step',
            description='Test',
            agents=['test'],
            phase=1,
            command='/test',
            depends_on=['dep1', 'dep2']
        )
        
        # No dependencies completed
        assert not step.can_run(set())
        
        # Partial dependencies
        assert not step.can_run({'dep1'})
        
        # All dependencies completed
        assert step.can_run({'dep1', 'dep2', 'other'})
    
    @pytest.mark.asyncio
    async def test_start_workflow(self, async_engine):
        """Test starting a workflow"""
        with patch.object(async_engine, '_execute_workflow'):
            result = await async_engine.start_workflow('feature_async')
            
            assert result['status'] == 'success'
            assert async_engine.active_workflow == 'feature_async'
            assert 'correlation_id' in async_engine.workflow_state
    
    @pytest.mark.asyncio
    async def test_start_workflow_invalid(self, async_engine):
        """Test starting invalid workflow"""
        result = await async_engine.start_workflow('invalid_workflow')
        
        assert result['status'] == 'error'
        assert 'Unknown workflow type' in result['message']
        assert async_engine.active_workflow is None
    
    @pytest.mark.asyncio
    async def test_start_workflow_already_active(self, async_engine):
        """Test starting workflow when one is active"""
        async_engine.active_workflow = 'existing'
        
        result = await async_engine.start_workflow('feature_async')
        
        assert result['status'] == 'error'
        assert 'already active' in result['message']
    
    @pytest.mark.asyncio
    async def test_execute_step_success(self, async_engine, mock_managers):
        """Test successful step execution"""
        step = WorkflowStep(
            id='test',
            name='Test Step',
            description='Test',
            agents=['backend'],
            phase=1,
            command='/test'
        )
        
        # Set up workflow state
        async_engine.workflow_state = {
            'correlation_id': 'test-123',
            'start_time': datetime.now()
        }
        
        # Mock executor
        async def mock_executor(s, ctx):
            return {'status': 'success', 'output': 'test_result'}
        
        async_engine._step_executors['test'] = mock_executor
        
        # Execute step
        await async_engine._execute_step(step)
        
        # Verify result
        assert 'test' in async_engine.step_results
        result = async_engine.step_results['test']
        assert result.status == StepStatus.COMPLETED
        assert result.output['status'] == 'success'
        assert 'test' in async_engine.completed_steps
        
        # Verify agent activation
        agent_manager, _ = mock_managers
        agent_manager.activate_agent.assert_called_with('backend')
        agent_manager.deactivate_agent.assert_called_with('backend')
    
    @pytest.mark.asyncio
    async def test_execute_step_failure(self, async_engine):
        """Test step execution failure"""
        step = WorkflowStep(
            id='failing',
            name='Failing Step',
            description='Test',
            agents=['test'],
            phase=1,
            command='/fail',
            max_retries=0  # No retries
        )
        
        async_engine.workflow_state = {'correlation_id': 'test-123'}
        
        # Mock failing executor
        async def failing_executor(s, ctx):
            raise ValueError("Test error")
        
        async_engine._step_executors['failing'] = failing_executor
        
        # Execute step
        await async_engine._execute_step(step)
        
        # Verify failure
        result = async_engine.step_results['failing']
        assert result.status == StepStatus.FAILED
        assert "Test error" in result.error
        assert 'failing' not in async_engine.completed_steps
    
    @pytest.mark.asyncio
    async def test_execute_step_timeout(self, async_engine):
        """Test step execution timeout"""
        step = WorkflowStep(
            id='slow',
            name='Slow Step',
            description='Test',
            agents=['test'],
            phase=1,
            command='/slow',
            timeout=0.1,  # 100ms timeout
            max_retries=0
        )
        
        async_engine.workflow_state = {'correlation_id': 'test-123'}
        
        # Mock slow executor
        async def slow_executor(s, ctx):
            await asyncio.sleep(1)  # Sleep longer than timeout
            return {'status': 'success'}
        
        async_engine._step_executors['slow'] = slow_executor
        
        # Execute step
        await async_engine._execute_step(step)
        
        # Verify timeout
        result = async_engine.step_results['slow']
        assert result.status == StepStatus.FAILED
        assert "timed out" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_step_retry(self, async_engine):
        """Test step retry logic"""
        step = WorkflowStep(
            id='retry',
            name='Retry Step',
            description='Test',
            agents=['test'],
            phase=1,
            command='/retry',
            max_retries=2
        )
        
        async_engine.workflow_state = {'correlation_id': 'test-123'}
        
        # Mock executor that fails then succeeds
        call_count = 0
        async def retry_executor(s, ctx):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return {'status': 'success'}
        
        async_engine._step_executors['retry'] = retry_executor
        
        # Execute step
        await async_engine._execute_step(step)
        
        # Verify retry succeeded
        result = async_engine.step_results['retry']
        assert result.status == StepStatus.COMPLETED
        assert call_count == 2  # Failed once, succeeded on retry
    
    def test_workflow_status_idle(self, async_engine):
        """Test workflow status when idle"""
        status = async_engine.get_workflow_status()
        
        assert status['status'] == 'idle'
        assert 'available_workflows' in status
        assert 'feature_async' in status['available_workflows']
    
    def test_workflow_status_active(self, async_engine):
        """Test workflow status when active"""
        # Set up active workflow
        async_engine.active_workflow = 'feature_async'
        async_engine.workflow_state = {
            'correlation_id': 'test-123',
            'start_time': datetime.now()
        }
        
        # Add some step results
        async_engine.step_results = {
            'req_gather': StepResult(
                step_id='req_gather',
                status=StepStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now()
            ),
            'arch_design': StepResult(
                step_id='arch_design',
                status=StepStatus.RUNNING,
                start_time=datetime.now()
            )
        }
        
        status = async_engine.get_workflow_status()
        
        assert status['status'] == 'active'
        assert status['workflow'] == 'feature_async'
        assert status['progress']['completed'] == 1
        assert status['progress']['running'] == 1
        assert len(status['running_steps']) == 1
        assert status['running_steps'][0]['id'] == 'arch_design'
    
    @pytest.mark.asyncio
    async def test_cancel_workflow(self, async_engine):
        """Test cancelling active workflow"""
        async_engine.active_workflow = 'feature_async'
        async_engine.workflow_state = {'correlation_id': 'test-123'}
        
        # Add running step
        async_engine.step_results['test'] = StepResult(
            step_id='test',
            status=StepStatus.RUNNING,
            start_time=datetime.now()
        )
        
        result = await async_engine.cancel_workflow()
        
        assert result['status'] == 'success'
        assert async_engine.active_workflow is None
        assert async_engine.step_results['test'].status == StepStatus.SKIPPED
    
    def test_visualize_workflow(self, async_engine):
        """Test workflow visualization"""
        viz = async_engine.visualize_workflow('feature_async')
        
        assert 'Async Feature Development' in viz
        assert 'Level 0:' in viz
        assert 'Requirements Gathering' in viz
        assert 'depends on:' in viz
        assert '[PARALLEL]' in viz
    
    def test_register_step_executor(self, async_engine):
        """Test registering custom step executor"""
        async def custom_executor(step, context):
            return {'custom': True}
        
        async_engine.register_step_executor('custom_step', custom_executor)
        
        assert 'custom_step' in async_engine._step_executors
        assert async_engine._step_executors['custom_step'] == custom_executor
    
    def test_register_sync_executor_fails(self, async_engine):
        """Test registering non-async executor fails"""
        def sync_executor(step, context):
            return {'sync': True}
        
        with pytest.raises(ValueError, match="must be an async function"):
            async_engine.register_step_executor('sync_step', sync_executor)
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, async_engine):
        """Test parallel step execution"""
        # Create workflow with parallel steps
        parallel_workflow = {
            'name': 'Parallel Test',
            'steps': [
                WorkflowStep(id='a', name='A', description='', agents=['a'], phase=1, command='/a', depends_on=[]),
                WorkflowStep(id='b', name='B', description='', agents=['b'], phase=1, command='/b', depends_on=[]),
                WorkflowStep(id='c', name='C', description='', agents=['c'], phase=1, command='/c', depends_on=['a', 'b'])
            ]
        }
        
        async_engine.workflows['parallel_test'] = parallel_workflow
        async_engine.active_workflow = 'parallel_test'
        async_engine.workflow_state = {'correlation_id': 'test-123', 'start_time': datetime.now()}
        
        # Track execution order
        execution_order = []
        
        async def tracking_executor(step, ctx):
            execution_order.append(f"{step.id}_start")
            await asyncio.sleep(0.1)
            execution_order.append(f"{step.id}_end")
            return {'status': 'success'}
        
        for step in parallel_workflow['steps']:
            async_engine._step_executors[step.id] = tracking_executor
        
        # Execute workflow
        await async_engine._execute_workflow()
        
        # Verify parallel execution
        # A and B should start before either completes
        a_start_idx = execution_order.index('a_start')
        b_start_idx = execution_order.index('b_start')
        a_end_idx = execution_order.index('a_end')
        b_end_idx = execution_order.index('b_end')
        
        # Both start before either ends (parallel)
        assert a_start_idx < a_end_idx
        assert b_start_idx < b_end_idx
        assert max(a_start_idx, b_start_idx) < min(a_end_idx, b_end_idx)
        
        # C starts after both A and B complete
        c_start_idx = execution_order.index('c_start')
        assert c_start_idx > max(a_end_idx, b_end_idx)