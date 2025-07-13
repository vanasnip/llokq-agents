"""
Async Workflow Engine - Enables true parallel execution of workflow steps
"""
import asyncio
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import uuid

from unified.agents.manager import AgentManager
from unified.core.phase_manager import PhaseManager
from unified.core.event_bus import get_event_bus, Event, EventType

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a workflow step"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a step in an async workflow"""
    id: str
    name: str
    description: str
    agents: List[str]
    phase: int
    command: str
    depends_on: List[str] = field(default_factory=list)
    parallel: bool = True
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def can_run(self, completed_steps: Set[str]) -> bool:
        """Check if step can run based on dependencies"""
        return all(dep in completed_steps for dep in self.depends_on)


@dataclass
class StepResult:
    """Result of executing a workflow step"""
    step_id: str
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    
    def __post_init__(self):
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


class AsyncWorkflowEngine:
    """
    Asynchronous workflow engine supporting parallel execution.
    Manages dependencies and concurrent step execution.
    """
    
    def __init__(self, agent_manager: AgentManager, phase_manager: PhaseManager):
        self.agent_manager = agent_manager
        self.phase_manager = phase_manager
        self.event_bus = get_event_bus()
        self.workflows: Dict[str, Dict[str, Any]] = self._define_async_workflows()
        self.active_workflow: Optional[str] = None
        self.workflow_state: Dict[str, Any] = {}
        self.step_results: Dict[str, StepResult] = {}
        self.completed_steps: Set[str] = set()
        self._step_executors: Dict[str, Callable] = {}
        self._setup_default_executors()
    
    def _define_async_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Define workflows with async-aware step definitions"""
        return {
            'feature_async': {
                'name': 'Async Feature Development',
                'description': 'Parallel feature development workflow',
                'steps': [
                    WorkflowStep(
                        id='req_gather',
                        name='Requirements Gathering',
                        description='Gather and analyze requirements',
                        agents=['requirements'],
                        phase=1,
                        command='/analyze --requirements',
                        depends_on=[]
                    ),
                    WorkflowStep(
                        id='arch_design',
                        name='Architecture Design',
                        description='Design system architecture',
                        agents=['architect'],
                        phase=2,
                        command='/design --architecture',
                        depends_on=['req_gather']
                    ),
                    WorkflowStep(
                        id='ui_design',
                        name='UI Design',
                        description='Create UI mockups and design system',
                        agents=['layout', 'motion'],
                        phase=3,
                        command='/design --ui',
                        depends_on=['req_gather'],
                        parallel=True
                    ),
                    WorkflowStep(
                        id='api_design',
                        name='API Design',
                        description='Design API contracts',
                        agents=['api'],
                        phase=2,
                        command='/design --api',
                        depends_on=['req_gather'],
                        parallel=True
                    ),
                    WorkflowStep(
                        id='backend_impl',
                        name='Backend Implementation',
                        description='Implement backend services',
                        agents=['backend'],
                        phase=5,
                        command='/code --backend',
                        depends_on=['arch_design', 'api_design']
                    ),
                    WorkflowStep(
                        id='frontend_impl',
                        name='Frontend Implementation',
                        description='Implement frontend components',
                        agents=['frontend'],
                        phase=5,
                        command='/code --frontend',
                        depends_on=['arch_design', 'ui_design']
                    ),
                    WorkflowStep(
                        id='integration',
                        name='Integration',
                        description='Integrate frontend and backend',
                        agents=['backend', 'frontend'],
                        phase=5,
                        command='/integrate',
                        depends_on=['backend_impl', 'frontend_impl']
                    ),
                    WorkflowStep(
                        id='testing',
                        name='Testing',
                        description='Run comprehensive tests',
                        agents=['qa'],
                        phase=6,
                        command='/test --all',
                        depends_on=['integration']
                    )
                ]
            },
            'security_audit_async': {
                'name': 'Async Security Audit',
                'description': 'Parallel security analysis workflow',
                'steps': [
                    WorkflowStep(
                        id='threat_model',
                        name='Threat Modeling',
                        description='Identify potential threats',
                        agents=['security'],
                        phase=7,
                        command='/analyze --threats',
                        depends_on=[]
                    ),
                    WorkflowStep(
                        id='code_scan',
                        name='Code Scanning',
                        description='Static code analysis',
                        agents=['security'],
                        phase=7,
                        command='/scan --code',
                        depends_on=[],
                        parallel=True
                    ),
                    WorkflowStep(
                        id='dep_scan',
                        name='Dependency Scanning',
                        description='Check for vulnerable dependencies',
                        agents=['security'],
                        phase=7,
                        command='/scan --dependencies',
                        depends_on=[],
                        parallel=True
                    ),
                    WorkflowStep(
                        id='pen_test',
                        name='Penetration Testing',
                        description='Simulated attack testing',
                        agents=['security'],
                        phase=7,
                        command='/test --penetration',
                        depends_on=['threat_model']
                    ),
                    WorkflowStep(
                        id='report',
                        name='Security Report',
                        description='Compile security findings',
                        agents=['security', 'documentation'],
                        phase=7,
                        command='/report --security',
                        depends_on=['code_scan', 'dep_scan', 'pen_test']
                    )
                ]
            }
        }
    
    def _setup_default_executors(self) -> None:
        """Set up default step executors"""
        # These would be replaced with actual execution logic
        async def default_executor(step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
            """Default executor that simulates work"""
            logger.info(f"Executing step: {step.name}")
            
            # Simulate work based on step
            work_duration = 2.0 if 'scan' in step.id else 3.0
            await asyncio.sleep(work_duration)
            
            return {
                'status': 'success',
                'message': f'Completed {step.name}',
                'outputs': {
                    'artifact': f'{step.id}_output.md',
                    'metrics': {'duration': work_duration}
                }
            }
        
        # Set default executor for all steps
        for workflow in self.workflows.values():
            for step in workflow['steps']:
                self._step_executors[step.id] = default_executor
    
    async def start_workflow(self, workflow_type: str) -> Dict[str, Any]:
        """Start an async workflow"""
        if workflow_type not in self.workflows:
            return {
                'status': 'error',
                'message': f'Unknown workflow type: {workflow_type}'
            }
        
        if self.active_workflow:
            return {
                'status': 'error',
                'message': f'Workflow {self.active_workflow} already active'
            }
        
        self.active_workflow = workflow_type
        self.workflow_state = {
            'type': workflow_type,
            'start_time': datetime.now(),
            'correlation_id': str(uuid.uuid4())
        }
        self.step_results.clear()
        self.completed_steps.clear()
        
        # Publish workflow started event
        self.event_bus.publish(Event(
            type=EventType.WORKFLOW_STARTED,
            data={
                'workflow': workflow_type,
                'name': self.workflows[workflow_type]['name']
            },
            source='AsyncWorkflowEngine',
            correlation_id=self.workflow_state['correlation_id']
        ))
        
        # Start execution
        asyncio.create_task(self._execute_workflow())
        
        return {
            'status': 'success',
            'message': f'Started {self.workflows[workflow_type]["name"]}',
            'workflow': workflow_type,
            'correlation_id': self.workflow_state['correlation_id']
        }
    
    async def _execute_workflow(self) -> None:
        """Execute the active workflow"""
        if not self.active_workflow:
            return
        
        workflow = self.workflows[self.active_workflow]
        steps = workflow['steps']
        
        try:
            # Continue until all steps are processed
            while len(self.completed_steps) < len(steps):
                # Find steps ready to run
                ready_steps = [
                    step for step in steps
                    if step.id not in self.completed_steps
                    and step.id not in self.step_results
                    and step.can_run(self.completed_steps)
                ]
                
                if not ready_steps:
                    # Check for failed dependencies
                    failed_steps = [
                        step_id for step_id, result in self.step_results.items()
                        if result.status == StepStatus.FAILED
                    ]
                    
                    if failed_steps:
                        # Mark dependent steps as skipped
                        for step in steps:
                            if step.id not in self.completed_steps:
                                if any(dep in failed_steps for dep in step.depends_on):
                                    self.step_results[step.id] = StepResult(
                                        step_id=step.id,
                                        status=StepStatus.SKIPPED,
                                        start_time=datetime.now(),
                                        end_time=datetime.now(),
                                        error="Dependency failed"
                                    )
                                    self.completed_steps.add(step.id)
                    
                    # Wait a bit before checking again
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    tasks.append(self._execute_step(step))
                
                # Wait for at least one step to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            
            # Workflow completed
            self._complete_workflow()
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            self._fail_workflow(str(e))
    
    async def _execute_step(self, step: WorkflowStep) -> None:
        """Execute a single workflow step"""
        step_result = StepResult(
            step_id=step.id,
            status=StepStatus.RUNNING,
            start_time=datetime.now()
        )
        self.step_results[step.id] = step_result
        
        # Publish step started event
        self.event_bus.publish(Event(
            type=EventType.WORKFLOW_STEP_COMPLETED,  # We could add STEP_STARTED
            data={
                'step_id': step.id,
                'step_name': step.name,
                'status': 'started',
                'agents': step.agents
            },
            source='AsyncWorkflowEngine',
            correlation_id=self.workflow_state['correlation_id']
        ))
        
        try:
            # Activate agents for this step
            for agent_name in step.agents:
                self.agent_manager.activate_agent(agent_name)
            
            # Get executor and context
            executor = self._step_executors.get(step.id)
            context = {
                'workflow_state': self.workflow_state,
                'completed_steps': list(self.completed_steps),
                'step_results': {sid: r.output for sid, r in self.step_results.items() if r.output}
            }
            
            # Execute with timeout if specified
            if step.timeout:
                output = await asyncio.wait_for(
                    executor(step, context),
                    timeout=step.timeout
                )
            else:
                output = await executor(step, context)
            
            # Update result
            step_result.status = StepStatus.COMPLETED
            step_result.end_time = datetime.now()
            step_result.output = output
            self.completed_steps.add(step.id)
            
            # Publish completion event
            self.event_bus.publish(Event(
                type=EventType.WORKFLOW_STEP_COMPLETED,
                data={
                    'step_id': step.id,
                    'step_name': step.name,
                    'status': 'completed',
                    'duration': step_result.duration,
                    'output': output
                },
                source='AsyncWorkflowEngine',
                correlation_id=self.workflow_state['correlation_id']
            ))
            
        except asyncio.TimeoutError:
            step_result.status = StepStatus.FAILED
            step_result.end_time = datetime.now()
            step_result.error = f"Step timed out after {step.timeout}s"
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.end_time = datetime.now()
            step_result.error = str(e)
            
            # Retry logic
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                logger.info(f"Retrying step {step.id} (attempt {step.retry_count})")
                await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
                await self._execute_step(step)
                return
        
        finally:
            # Deactivate agents
            for agent_name in step.agents:
                self.agent_manager.deactivate_agent(agent_name)
    
    def _complete_workflow(self) -> None:
        """Mark workflow as completed"""
        self.workflow_state['end_time'] = datetime.now()
        self.workflow_state['status'] = 'completed'
        
        # Calculate summary
        total_duration = (self.workflow_state['end_time'] - self.workflow_state['start_time']).total_seconds()
        successful_steps = sum(1 for r in self.step_results.values() if r.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for r in self.step_results.values() if r.status == StepStatus.FAILED)
        
        # Publish completion event
        self.event_bus.publish(Event(
            type=EventType.WORKFLOW_COMPLETED,
            data={
                'workflow': self.active_workflow,
                'duration': total_duration,
                'steps_total': len(self.step_results),
                'steps_successful': successful_steps,
                'steps_failed': failed_steps,
                'results': {
                    step_id: {
                        'status': result.status.value,
                        'duration': result.duration
                    }
                    for step_id, result in self.step_results.items()
                }
            },
            source='AsyncWorkflowEngine',
            correlation_id=self.workflow_state['correlation_id']
        ))
        
        self.active_workflow = None
    
    def _fail_workflow(self, error: str) -> None:
        """Mark workflow as failed"""
        self.workflow_state['end_time'] = datetime.now()
        self.workflow_state['status'] = 'failed'
        self.workflow_state['error'] = error
        
        # Publish failure event
        self.event_bus.publish(Event(
            type=EventType.ERROR_OCCURRED,
            data={
                'workflow': self.active_workflow,
                'error': error,
                'step_results': {
                    step_id: result.status.value
                    for step_id, result in self.step_results.items()
                }
            },
            source='AsyncWorkflowEngine',
            correlation_id=self.workflow_state['correlation_id']
        ))
        
        self.active_workflow = None
    
    async def cancel_workflow(self) -> Dict[str, Any]:
        """Cancel the active workflow"""
        if not self.active_workflow:
            return {
                'status': 'error',
                'message': 'No active workflow to cancel'
            }
        
        workflow_name = self.workflows[self.active_workflow]['name']
        
        # Mark running steps as cancelled
        for step_id, result in self.step_results.items():
            if result.status == StepStatus.RUNNING:
                result.status = StepStatus.SKIPPED
                result.end_time = datetime.now()
                result.error = "Workflow cancelled"
        
        # Publish cancellation event
        self.event_bus.publish(Event(
            type=EventType.WORKFLOW_CANCELLED,
            data={
                'workflow': self.active_workflow,
                'completed_steps': len(self.completed_steps),
                'total_steps': len(self.workflows[self.active_workflow]['steps'])
            },
            source='AsyncWorkflowEngine',
            correlation_id=self.workflow_state.get('correlation_id')
        ))
        
        self.active_workflow = None
        
        return {
            'status': 'success',
            'message': f'Cancelled workflow: {workflow_name}'
        }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get detailed workflow status"""
        if not self.active_workflow:
            return {
                'status': 'idle',
                'message': 'No active workflow',
                'available_workflows': list(self.workflows.keys())
            }
        
        workflow = self.workflows[self.active_workflow]
        total_steps = len(workflow['steps'])
        
        # Calculate progress
        completed = len([r for r in self.step_results.values() if r.status in [StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED]])
        running = len([r for r in self.step_results.values() if r.status == StepStatus.RUNNING])
        
        # Get running steps info
        running_steps = []
        for step in workflow['steps']:
            if step.id in self.step_results and self.step_results[step.id].status == StepStatus.RUNNING:
                result = self.step_results[step.id]
                running_duration = (datetime.now() - result.start_time).total_seconds()
                running_steps.append({
                    'id': step.id,
                    'name': step.name,
                    'agents': step.agents,
                    'duration': running_duration
                })
        
        return {
            'status': 'active',
            'workflow': self.active_workflow,
            'name': workflow['name'],
            'progress': {
                'completed': completed,
                'running': running,
                'total': total_steps,
                'percentage': (completed / total_steps * 100) if total_steps > 0 else 0
            },
            'running_steps': running_steps,
            'step_results': {
                step_id: {
                    'status': result.status.value,
                    'duration': result.duration,
                    'error': result.error
                }
                for step_id, result in self.step_results.items()
            },
            'correlation_id': self.workflow_state.get('correlation_id')
        }
    
    def register_step_executor(self, step_id: str, executor: Callable) -> None:
        """Register a custom executor for a workflow step"""
        if not asyncio.iscoroutinefunction(executor):
            raise ValueError("Executor must be an async function")
        self._step_executors[step_id] = executor
    
    def visualize_workflow(self, workflow_type: str) -> str:
        """Generate a text-based visualization of workflow dependencies"""
        if workflow_type not in self.workflows:
            return f"Unknown workflow: {workflow_type}"
        
        workflow = self.workflows[workflow_type]
        steps = workflow['steps']
        
        # Build visualization
        lines = [f"Workflow: {workflow['name']}", "=" * 50]
        
        # Group steps by dependency level
        levels = {}
        for step in steps:
            level = 0
            deps = step.depends_on[:]
            while deps:
                level += 1
                new_deps = []
                for dep in deps:
                    dep_step = next((s for s in steps if s.id == dep), None)
                    if dep_step:
                        new_deps.extend(dep_step.depends_on)
                deps = new_deps
            
            if level not in levels:
                levels[level] = []
            levels[level].append(step)
        
        # Display by level
        for level in sorted(levels.keys()):
            lines.append(f"\nLevel {level}:")
            for step in levels[level]:
                deps_str = f" (depends on: {', '.join(step.depends_on)})" if step.depends_on else ""
                parallel_str = " [PARALLEL]" if step.parallel else ""
                lines.append(f"  - {step.name} ({step.id}){deps_str}{parallel_str}")
        
        return "\n".join(lines)