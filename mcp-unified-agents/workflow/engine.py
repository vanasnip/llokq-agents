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
    
    def __init__(self, agent_registry: Dict[str, Any], context_manager: Any):
        self.agents = agent_registry
        self.context_manager = context_manager
        self.template_registry = TemplateRegistry()
        self.step_executor = StepExecutor(agent_registry)
        self.executions = {}
        self._execution_counter = 0
        
    def start_workflow(self, template_name: str, inputs: Dict[str, Any]) -> str:
        """
        Start a new workflow execution
        
        Args:
            template_name: Name of the workflow template
            inputs: Input parameters for the workflow
            
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
        
        # Create execution
        execution = WorkflowExecution(workflow_id, template_name, inputs)
        execution.status = WorkflowStatus.RUNNING
        
        # Store execution
        self.executions[workflow_id] = execution
        
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
        
    def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a running workflow"""
        if workflow_id not in self.executions:
            return {"error": f"Unknown workflow: {workflow_id}"}
            
        execution = self.executions[workflow_id]
        if execution.status != WorkflowStatus.RUNNING:
            return {"error": f"Workflow not running: {execution.status.value}"}
            
        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.now()
        
        return {"status": "cancelled", "workflow_id": workflow_id}
        
    def _execute_next_step(self, workflow_id: str):
        """Execute the next step in the workflow"""
        execution = self.executions[workflow_id]
        template = self.template_registry.get_template(execution.template_name)
        
        if execution.current_step >= len(template["steps"]):
            # Workflow complete
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            return
            
        step = template["steps"][execution.current_step]
        
        try:
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