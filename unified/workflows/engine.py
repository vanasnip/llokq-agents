"""
Workflow Engine - Orchestrates multi-phase, multi-agent workflows
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import yaml
import json
from datetime import datetime
from unified.agents import Agent, AgentManager
from unified.core.phase_manager import PhaseManager
from unified.core.command_executor import CommandExecutor
from unified.core.command_parser import ParsedCommand


class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    description: str
    agents: List[str]
    command: str
    parallel: bool = False
    required_outputs: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None


@dataclass
class Workflow:
    """Represents a complete workflow"""
    name: str
    description: str
    type: str  # feature, bug, security, etc.
    steps: List[WorkflowStep]
    required_agents: List[str] = field(default_factory=list)
    estimated_duration: Optional[str] = None
    
    def get_all_agents(self) -> List[str]:
        """Get all unique agents required for this workflow"""
        agents = set(self.required_agents)
        for step in self.steps:
            agents.update(step.agents)
        return list(agents)


class WorkflowEngine:
    """Orchestrates complex multi-agent workflows"""
    
    def __init__(self, agent_manager: AgentManager, phase_manager: PhaseManager):
        self.agent_manager = agent_manager
        self.phase_manager = phase_manager
        self.command_executor = CommandExecutor()
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflow: Optional[Workflow] = None
        self.workflow_state = WorkflowState.PENDING
        self.current_step_index = 0
        self.workflow_history = []
        self._load_workflows()
    
    def _load_workflows(self):
        """Load workflow definitions"""
        # For now, define workflows programmatically
        # Later, load from YAML files
        
        # Feature Development Workflow
        feature_workflow = Workflow(
            name="feature_development",
            type="feature",
            description="Complete feature development from requirements to deployment",
            estimated_duration="2-5 days",
            steps=[
                WorkflowStep(
                    name="requirements_discovery",
                    description="Discover and document requirements",
                    agents=["riley", "architect"],
                    command="/analyze --riley --architect",
                    required_outputs=["requirements.md", "ambiguities.md"],
                    validation_criteria=["All user stories defined", "Acceptance criteria clear"]
                ),
                WorkflowStep(
                    name="architecture_design",
                    description="Design system architecture",
                    agents=["architect", "api"],
                    command="/design --architect --api",
                    required_outputs=["architecture.md", "api_spec.yaml"],
                    validation_criteria=["Architecture documented", "API contracts defined"]
                ),
                WorkflowStep(
                    name="ui_design",
                    description="Create UI/UX designs",
                    agents=["layout_loom", "chromatic_architect", "aura"],
                    command="/design --layout_loom --chromatic_architect --aura",
                    parallel=True,
                    required_outputs=["wireframes/", "design_system.md"],
                    validation_criteria=["Designs approved", "Accessibility verified"]
                ),
                WorkflowStep(
                    name="implementation",
                    description="Implement feature",
                    agents=["backend", "frontend"],
                    command="/code --backend --frontend",
                    parallel=True,
                    required_outputs=["src/", "tests/"],
                    validation_criteria=["Code complete", "Tests passing"]
                ),
                WorkflowStep(
                    name="testing",
                    description="Comprehensive testing",
                    agents=["qa", "security", "performance"],
                    command="/test --qa --security --performance",
                    parallel=True,
                    required_outputs=["test_report.md", "security_report.md"],
                    validation_criteria=["All tests passing", "No critical issues"]
                ),
                WorkflowStep(
                    name="deployment",
                    description="Deploy to production",
                    agents=["devops"],
                    command="/deploy --devops",
                    required_outputs=["deployment_log.md"],
                    validation_criteria=["Deployment successful", "Health checks passing"]
                )
            ]
        )
        self.workflows['feature'] = feature_workflow
        
        # Bug Investigation Workflow
        bug_workflow = Workflow(
            name="bug_investigation",
            type="bug",
            description="Systematic bug investigation and resolution",
            estimated_duration="1-3 days",
            steps=[
                WorkflowStep(
                    name="triage",
                    description="Triage and reproduce bug",
                    agents=["qa"],
                    command="/analyze --qa",
                    required_outputs=["bug_report.md", "reproduction_steps.md"],
                    validation_criteria=["Bug reproduced", "Impact assessed"]
                ),
                WorkflowStep(
                    name="root_cause_analysis",
                    description="Find root cause",
                    agents=["backend", "frontend", "architect"],
                    command="/analyze --backend --frontend --architect",
                    required_outputs=["root_cause.md"],
                    validation_criteria=["Root cause identified", "Fix approach defined"]
                ),
                WorkflowStep(
                    name="fix_implementation",
                    description="Implement fix",
                    agents=["backend", "frontend"],
                    command="/code --backend --frontend",
                    required_outputs=["fix/", "tests/"],
                    validation_criteria=["Fix implemented", "Tests added"]
                ),
                WorkflowStep(
                    name="verification",
                    description="Verify fix",
                    agents=["qa"],
                    command="/test --qa",
                    required_outputs=["verification_report.md"],
                    validation_criteria=["Bug fixed", "No regressions"]
                ),
                WorkflowStep(
                    name="deployment",
                    description="Deploy fix",
                    agents=["devops"],
                    command="/deploy --devops",
                    required_outputs=["hotfix_deployment.md"],
                    validation_criteria=["Fix deployed", "Bug resolved in production"]
                )
            ]
        )
        self.workflows['bug'] = bug_workflow
        
        # Security Audit Workflow
        security_workflow = Workflow(
            name="security_audit",
            type="security",
            description="Comprehensive security assessment",
            estimated_duration="3-5 days",
            steps=[
                WorkflowStep(
                    name="threat_modeling",
                    description="Model threats and attack vectors",
                    agents=["security", "architect"],
                    command="/analyze --security --architect",
                    required_outputs=["threat_model.md"],
                    validation_criteria=["All vectors identified", "Risk matrix complete"]
                ),
                WorkflowStep(
                    name="vulnerability_scanning",
                    description="Scan for vulnerabilities",
                    agents=["security"],
                    command="/test --security",
                    required_outputs=["vulnerability_report.md"],
                    validation_criteria=["Scan complete", "All systems covered"]
                ),
                WorkflowStep(
                    name="remediation",
                    description="Fix identified vulnerabilities",
                    agents=["security", "backend", "devops"],
                    command="/code --security --backend --devops",
                    required_outputs=["security_fixes/"],
                    validation_criteria=["Critical vulnerabilities fixed", "Patches tested"]
                ),
                WorkflowStep(
                    name="verification",
                    description="Verify security improvements",
                    agents=["security", "qa"],
                    command="/test --security --qa",
                    required_outputs=["security_verification.md"],
                    validation_criteria=["All fixes verified", "No new vulnerabilities"]
                )
            ]
        )
        self.workflows['security'] = security_workflow
    
    def start_workflow(self, workflow_type: str) -> Dict[str, Any]:
        """Start a workflow"""
        if workflow_type not in self.workflows:
            return {
                'status': 'error',
                'message': f'Unknown workflow type: {workflow_type}'
            }
        
        workflow = self.workflows[workflow_type]
        
        # Check if all required agents exist
        missing_agents = []
        for agent_name in workflow.get_all_agents():
            if not self.agent_manager.get_agent(agent_name):
                missing_agents.append(agent_name)
        
        if missing_agents:
            return {
                'status': 'error',
                'message': f'Missing agents: {", ".join(missing_agents)}'
            }
        
        # Initialize workflow
        self.active_workflow = workflow
        self.workflow_state = WorkflowState.RUNNING
        self.current_step_index = 0
        
        # Record workflow start
        workflow_record = {
            'workflow': workflow.name,
            'type': workflow.type,
            'started_at': datetime.now().isoformat(),
            'state': self.workflow_state.value,
            'current_step': 0,
            'total_steps': len(workflow.steps)
        }
        self.workflow_history.append(workflow_record)
        
        return {
            'status': 'success',
            'message': f'Started {workflow.name} workflow',
            'workflow': workflow_record,
            'next_step': self._get_step_info(workflow.steps[0])
        }
    
    def execute_next_step(self) -> Dict[str, Any]:
        """Execute the next step in the active workflow"""
        if not self.active_workflow:
            return {
                'status': 'error',
                'message': 'No active workflow'
            }
        
        if self.workflow_state != WorkflowState.RUNNING:
            return {
                'status': 'error',
                'message': f'Workflow is {self.workflow_state.value}'
            }
        
        if self.current_step_index >= len(self.active_workflow.steps):
            return self._complete_workflow()
        
        step = self.active_workflow.steps[self.current_step_index]
        
        # Activate agents for this step
        for agent_name in step.agents:
            self.agent_manager.activate_agent(agent_name)
        
        # Parse and execute command
        parsed_command = ParsedCommand(
            base_command=step.command.split()[0].strip('/'),
            agents=step.agents,
            phase=None,
            options={},
            raw_input=step.command
        )
        
        # Get active agents
        agents = [self.agent_manager.get_agent(name) for name in step.agents]
        agents = [a for a in agents if a]  # Filter None values
        
        # Execute command
        execution_result = self.command_executor.execute(parsed_command, agents)
        
        # Record step execution
        step_record = {
            'step_index': self.current_step_index,
            'step_name': step.name,
            'executed_at': datetime.now().isoformat(),
            'agents': step.agents,
            'result': execution_result
        }
        
        # Move to next step
        self.current_step_index += 1
        
        return {
            'status': 'success',
            'message': f'Executed step: {step.name}',
            'step_record': step_record,
            'execution_result': execution_result,
            'next_step': self._get_step_info(
                self.active_workflow.steps[self.current_step_index]
                if self.current_step_index < len(self.active_workflow.steps)
                else None
            )
        }
    
    def _get_step_info(self, step: Optional[WorkflowStep]) -> Optional[Dict[str, Any]]:
        """Get information about a workflow step"""
        if not step:
            return None
        
        return {
            'name': step.name,
            'description': step.description,
            'agents': step.agents,
            'command': step.command,
            'parallel': step.parallel,
            'required_outputs': step.required_outputs,
            'validation_criteria': step.validation_criteria
        }
    
    def _complete_workflow(self) -> Dict[str, Any]:
        """Complete the active workflow"""
        self.workflow_state = WorkflowState.COMPLETED
        
        completion_record = {
            'workflow': self.active_workflow.name,
            'completed_at': datetime.now().isoformat(),
            'total_steps': len(self.active_workflow.steps),
            'state': self.workflow_state.value
        }
        
        self.active_workflow = None
        self.current_step_index = 0
        
        return {
            'status': 'success',
            'message': 'Workflow completed successfully',
            'completion_record': completion_record
        }
    
    def pause_workflow(self) -> Dict[str, Any]:
        """Pause the active workflow"""
        if not self.active_workflow:
            return {
                'status': 'error',
                'message': 'No active workflow'
            }
        
        self.workflow_state = WorkflowState.PAUSED
        
        return {
            'status': 'success',
            'message': 'Workflow paused',
            'current_step': self.current_step_index,
            'workflow': self.active_workflow.name
        }
    
    def resume_workflow(self) -> Dict[str, Any]:
        """Resume a paused workflow"""
        if not self.active_workflow:
            return {
                'status': 'error',
                'message': 'No active workflow'
            }
        
        if self.workflow_state != WorkflowState.PAUSED:
            return {
                'status': 'error',
                'message': f'Workflow is {self.workflow_state.value}, not paused'
            }
        
        self.workflow_state = WorkflowState.RUNNING
        
        return {
            'status': 'success',
            'message': 'Workflow resumed',
            'current_step': self.current_step_index,
            'workflow': self.active_workflow.name
        }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of the active workflow"""
        if not self.active_workflow:
            return {
                'status': 'info',
                'message': 'No active workflow',
                'available_workflows': list(self.workflows.keys())
            }
        
        return {
            'status': 'success',
            'workflow': self.active_workflow.name,
            'type': self.active_workflow.type,
            'state': self.workflow_state.value,
            'current_step': self.current_step_index,
            'total_steps': len(self.active_workflow.steps),
            'progress': (self.current_step_index / len(self.active_workflow.steps)) * 100,
            'current_step_info': self._get_step_info(
                self.active_workflow.steps[self.current_step_index]
                if self.current_step_index < len(self.active_workflow.steps)
                else None
            )
        }