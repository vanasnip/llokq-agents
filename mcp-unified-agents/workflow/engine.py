"""
Workflow Engine - Orchestrates multi-agent workflows
"""
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

from .context import SharedContext
from .templates import TemplateRegistry
from .executor import StepExecutor
from .monitor import ResourceMonitor

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowExecution:
    """Represents a single workflow execution"""
    
    def __init__(self, workflow_id: str, template_name: str, inputs: Dict[str, Any]):
        self.id = workflow_id
        self.template_name = template_name
        self.inputs = inputs
        self.status = WorkflowStatus.PENDING
        self.context = SharedContext()
        self.current_step = 0
        self.steps_completed = []
        self.started_at = datetime.now()
        self.completed_at = None
        self.error = None
        self.artifacts = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary"""
        return {
            "id": self.id,
            "template": self.template_name,
            "status": self.status.value,
            "current_step": self.current_step,
            "steps_completed": self.steps_completed,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "artifacts": list(self.artifacts.keys())
        }


class WorkflowEngine:
    """
    Orchestrates workflow execution for multi-agent collaboration
    """
    
    def __init__(self, agent_registry: Dict[str, Any], context_manager: Any,
                 max_concurrent_workflows: int = 5, 
                 workflow_timeout_seconds: int = 3600,
                 max_workflow_memory_mb: int = 512):
        self.agents = agent_registry
        self.context_manager = context_manager
        self.template_registry = TemplateRegistry()
        self.step_executor = StepExecutor(agent_registry)
        self.executions = {}
        self._execution_counter = 0
        
        # Resource limits
        self.max_concurrent_workflows = max_concurrent_workflows
        self.workflow_timeout_seconds = workflow_timeout_seconds
        self.max_workflow_memory_mb = max_workflow_memory_mb
        self._resource_monitor = ResourceMonitor(max_memory_mb=max_workflow_memory_mb)
        
    def start_workflow(self, template_name: str, inputs: Dict[str, Any], 
                      require_approval: bool = None, session_state: Any = None) -> str:
        """
        Start a new workflow execution
        
        Args:
            template_name: Name of the workflow template
            inputs: Input parameters for the workflow
            require_approval: Whether to require approval before starting
            session_state: Session state for approval checking
            
        Returns:
            Workflow ID
        """
        # Generate unique workflow ID
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}_{self._execution_counter}"
        self._execution_counter += 1
        
        # Get template
        template = self.template_registry.get_template(template_name)
        if not template:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        # Check resource limits
        active_workflows = [e for e in self.executions.values() 
                          if e.status == WorkflowStatus.RUNNING]
        if len(active_workflows) >= self.max_concurrent_workflows:
            raise ValueError(
                f"Maximum concurrent workflows ({self.max_concurrent_workflows}) reached. "
                f"Please wait for existing workflows to complete."
            )
        
        # Check if approval is required
        if require_approval or (session_state and not session_state.auto_approve):
            # Get agents used in workflow
            agents_in_workflow = self._get_workflow_agents(template)
            
            # Check if all agents are approved
            if session_state:
                unapproved = [a for a in agents_in_workflow 
                            if a not in session_state.approved_agents]
                if unapproved:
                    return {
                        "workflow_id": workflow_id,
                        "status": "pending_approval",
                        "template": template_name,
                        "agents_required": agents_in_workflow,
                        "agents_unapproved": unapproved,
                        "message": f"Workflow requires approval for agents: {', '.join(unapproved)}"
                    }
        
        # Create execution
        execution = WorkflowExecution(workflow_id, template_name, inputs)
        execution.status = WorkflowStatus.RUNNING
        
        # Store execution
        self.executions[workflow_id] = execution
        
        # Start resource monitoring
        self._resource_monitor.start_monitoring(workflow_id)
        
        logger.info(f"Started workflow {workflow_id} with template {template_name}")
        
        # Execute first step (simplified for now - real impl would be async)
        self._execute_next_step(workflow_id)
        
        return workflow_id
        
    def get_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        if workflow_id not in self.executions:
            return {"error": f"Unknown workflow: {workflow_id}"}
            
        execution = self.executions[workflow_id]
        return {
            "workflow": execution.to_dict(),
            "template": self.template_registry.get_template(execution.template_name)
        }
        
    def cancel_workflow(self, workflow_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel a running workflow"""
        if workflow_id not in self.executions:
            return {"error": f"Unknown workflow: {workflow_id}"}
            
        execution = self.executions[workflow_id]
        if execution.status != WorkflowStatus.RUNNING:
            return {"error": f"Workflow not running: {execution.status.value}"}
            
        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.now()
        if reason:
            execution.error = f"Cancelled: {reason}"
            
        # Stop resource monitoring
        self._resource_monitor.stop_monitoring(workflow_id)
        
        # Cancel any running parallel tasks
        self.step_executor.shutdown()
        
        logger.info(f"Cancelled workflow {workflow_id}")
        
        return {
            "status": "cancelled", 
            "workflow_id": workflow_id,
            "reason": reason or "User requested cancellation"
        }
        
    def _execute_next_step(self, workflow_id: str):
        """Execute the next step in the workflow"""
        execution = self.executions[workflow_id]
        template = self.template_registry.get_template(execution.template_name)
        
        if execution.current_step >= len(template["steps"]):
            # Workflow complete
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            self._resource_monitor.stop_monitoring(workflow_id)
            return
            
        step = template["steps"][execution.current_step]
        
        try:
            # Check resource limits before each step
            if not self._resource_monitor.check_memory_limit(workflow_id):
                raise RuntimeError(f"Workflow {workflow_id} exceeded memory limit")
                
            # Check for cancellation
            if execution.status == WorkflowStatus.CANCELLED:
                logger.info(f"Workflow {workflow_id} was cancelled")
                return
                
            # Execute step using the step executor
            result = self.step_executor.execute_step(
                step, 
                execution,
                self._resolve_inputs
            )
                
            # Store result if output specified
            if "output" in step:
                execution.artifacts[step["output"]] = result
                execution.context.add_artifact(
                    step["output"], 
                    result,
                    producer=step.get("agent", "system")
                )
                
            # Mark step complete
            execution.steps_completed.append({
                "step": execution.current_step,
                "agent": step.get("agent", "system"),
                "tool": step.get("tool", "unknown"),
                "completed_at": datetime.now().isoformat()
            })
            
            # Move to next step
            execution.current_step += 1
            
            # Execute next step (in real impl this would be scheduled)
            self._execute_next_step(workflow_id)
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed at step {execution.current_step}: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now()
            self._resource_monitor.stop_monitoring(workflow_id)
            
        
    def _resolve_inputs(self, input_spec: Any, execution: WorkflowExecution) -> Any:
        """Resolve input values from template variables and context"""
        if isinstance(input_spec, str):
            # Check for template variables
            if input_spec.startswith("{") and input_spec.endswith("}"):
                var_name = input_spec[1:-1]
                
                # First check direct inputs
                if var_name in execution.inputs:
                    return execution.inputs[var_name]
                    
                # Then check artifacts
                if var_name in execution.artifacts:
                    return execution.artifacts[var_name]
                    
                # Finally check context
                try:
                    return execution.context.get_artifact(var_name, "workflow_engine")
                except:
                    return f"<unresolved: {var_name}>"
                    
            return input_spec
            
        elif isinstance(input_spec, dict):
            # Recursively resolve dict values
            return {k: self._resolve_inputs(v, execution) for k, v in input_spec.items()}
            
        elif isinstance(input_spec, list):
            # Recursively resolve list items
            return [self._resolve_inputs(item, execution) for item in input_spec]
            
        else:
            # Return as-is for other types
            return input_spec
            
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflow executions"""
        return [
            execution.to_dict() 
            for execution in self.executions.values()
        ]
        
    def suggest_workflow(self, task_description: str) -> List[Dict[str, Any]]:
        """Suggest workflows based on task description"""
        suggestions = []
        task_lower = task_description.lower()
        
        # Simple keyword matching for now
        if any(word in task_lower for word in ["feature", "implement", "build", "create"]):
            suggestions.append({
                "template": "feature_development",
                "confidence": 0.85,
                "reason": "Task involves building new functionality"
            })
            
        if any(word in task_lower for word in ["bug", "fix", "issue", "error", "problem"]):
            suggestions.append({
                "template": "bug_fix", 
                "confidence": 0.90,
                "reason": "Task involves fixing issues"
            })
            
        if any(word in task_lower for word in ["security", "audit", "vulnerability", "scan"]):
            suggestions.append({
                "template": "security_audit",
                "confidence": 0.88,
                "reason": "Task involves security analysis"
            })
            
        if any(word in task_lower for word in ["api", "endpoint", "rest", "service"]):
            suggestions.append({
                "template": "api_design",
                "confidence": 0.82,
                "reason": "Task involves API development"
            })
            
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return suggestions
        
    def create_custom_workflow(self, name: str, description: str, 
                             steps: List[Dict[str, Any]]) -> str:
        """
        Create a custom workflow template
        
        Args:
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps
            
        Returns:
            Template ID
        """
        # Create template definition
        template = {
            "name": name,
            "description": description,
            "steps": steps,
            "inputs": {}  # Will be inferred from steps
        }
        
        # Infer required inputs from step definitions
        required_inputs = set()
        for step in steps:
            if "input" in step:
                inputs = step["input"]
                if isinstance(inputs, dict):
                    for value in inputs.values():
                        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                            var_name = value[1:-1]
                            # Skip variables that are outputs from other steps
                            if not any(s.get("output") == var_name for s in steps):
                                required_inputs.add(var_name)
                                
        # Add inferred inputs to template
        for input_name in required_inputs:
            template["inputs"][input_name] = {
                "type": "string",
                "description": f"Input for {input_name}",
                "required": True
            }
            
        # Register the custom template
        template_id = self.template_registry.register_custom_template(template)
        
        logger.info(f"Created custom workflow template: {template_id}")
        
        return template_id
        
    def get_workflow_info(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed information about a workflow execution"""
        if workflow_id not in self.executions:
            return {"error": f"Unknown workflow: {workflow_id}"}
            
        execution = self.executions[workflow_id]
        template = self.template_registry.get_template(execution.template_name)
        
        # Get context summary
        context_summary = execution.context.get_summary() if hasattr(execution.context, 'get_summary') else {}
        
        return {
            "workflow": execution.to_dict(),
            "template": template,
            "context": context_summary,
            "progress": {
                "total_steps": len(template["steps"]) if template else 0,
                "completed_steps": len(execution.steps_completed),
                "current_step_name": template["steps"][execution.current_step].get("name", "Unknown") 
                    if template and execution.current_step < len(template["steps"]) else None
            }
        }
        
    def cleanup_old_workflows(self, hours: int = 24):
        """Clean up workflows older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        to_remove = []
        for workflow_id, execution in self.executions.items():
            if execution.completed_at and execution.completed_at < cutoff_time:
                to_remove.append(workflow_id)
                
        for workflow_id in to_remove:
            del self.executions[workflow_id]
            logger.info(f"Cleaned up old workflow: {workflow_id}")
            
        return len(to_remove)
        
    def _get_workflow_agents(self, template: Dict[str, Any]) -> List[str]:
        """Extract all agents used in a workflow template"""
        agents = set()
        
        for step in template.get("steps", []):
            if "parallel" in step:
                # Handle parallel steps
                for parallel_step in step["parallel"]:
                    if "agent" in parallel_step:
                        agents.add(parallel_step["agent"])
            else:
                # Handle single step
                if "agent" in step:
                    agents.add(step["agent"])
                    
        return sorted(list(agents))
        
    def dry_run_workflow(self, template_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a dry run of a workflow to preview what would happen
        
        Args:
            template_name: Name of the workflow template
            inputs: Input parameters for the workflow
            
        Returns:
            Dry run analysis
        """
        # Get template
        template = self.template_registry.get_template(template_name)
        if not template:
            return {"error": f"Unknown workflow template: {template_name}"}
            
        # Analyze workflow
        agents_used = self._get_workflow_agents(template)
        steps_analysis = []
        
        for i, step in enumerate(template.get("steps", [])):
            if "parallel" in step:
                # Analyze parallel steps
                parallel_analysis = []
                for p_step in step["parallel"]:
                    parallel_analysis.append({
                        "agent": p_step.get("agent", "unknown"),
                        "tool": p_step.get("tool", "unknown"),
                        "inputs": self._analyze_inputs(p_step.get("input", {}), inputs),
                        "output": p_step.get("output", "none")
                    })
                steps_analysis.append({
                    "step": i + 1,
                    "type": "parallel",
                    "name": step.get("name", f"Step {i+1}"),
                    "parallel_steps": parallel_analysis
                })
            else:
                # Analyze single step
                steps_analysis.append({
                    "step": i + 1,
                    "type": "sequential",
                    "name": step.get("name", f"Step {i+1}"),
                    "agent": step.get("agent", "unknown"),
                    "tool": step.get("tool", "unknown"),
                    "inputs": self._analyze_inputs(step.get("input", {}), inputs),
                    "output": step.get("output", "none")
                })
                
        # Estimate resource usage
        estimated_time = len(template.get("steps", [])) * 2  # 2 seconds per step estimate
        estimated_memory = len(agents_used) * 50  # 50MB per agent estimate
        
        return {
            "template": template_name,
            "description": template.get("description", "No description"),
            "agents_required": agents_used,
            "total_steps": len(template.get("steps", [])),
            "steps_analysis": steps_analysis,
            "resource_estimates": {
                "estimated_time_seconds": estimated_time,
                "estimated_memory_mb": estimated_memory,
                "parallel_steps": sum(1 for s in steps_analysis if s["type"] == "parallel")
            },
            "required_inputs": list(template.get("inputs", {}).keys()),
            "provided_inputs": list(inputs.keys()),
            "missing_inputs": [k for k in template.get("inputs", {}).keys() if k not in inputs]
        }
        
    def _analyze_inputs(self, input_spec: Any, provided_inputs: Dict[str, Any]) -> Any:
        """Analyze what inputs would be used in dry run"""
        if isinstance(input_spec, str):
            if input_spec.startswith("{") and input_spec.endswith("}"):
                var_name = input_spec[1:-1]
                if var_name in provided_inputs:
                    return f"<{var_name}: provided>"
                else:
                    return f"<{var_name}: from previous step>"
            return input_spec
        elif isinstance(input_spec, dict):
            return {k: self._analyze_inputs(v, provided_inputs) for k, v in input_spec.items()}
        elif isinstance(input_spec, list):
            return [self._analyze_inputs(item, provided_inputs) for item in input_spec]
        else:
            return input_spec