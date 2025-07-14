"""
Step Executor - Handles individual step and parallel execution
"""
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger(__name__)


class StepExecutor:
    """
    Executes workflow steps with support for parallel execution
    """
    
    def __init__(self, agent_registry: Dict[str, Any], max_workers: int = 4):
        self.agents = agent_registry
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def execute_step(self, step: Dict[str, Any], context: Any, 
                    resolve_inputs: Callable) -> Dict[str, Any]:
        """
        Execute a single workflow step
        
        Args:
            step: Step definition
            context: Workflow context
            resolve_inputs: Function to resolve input variables
            
        Returns:
            Step execution result
        """
        if "parallel" in step:
            return self.execute_parallel_steps(step["parallel"], context, resolve_inputs)
        else:
            return self.execute_single_step(step, context, resolve_inputs)
            
    def execute_single_step(self, step: Dict[str, Any], context: Any,
                          resolve_inputs: Callable) -> Dict[str, Any]:
        """Execute a single agent step"""
        agent_id = step.get("agent", "system")
        tool = step.get("tool", "unknown")
        
        # Resolve inputs
        inputs = resolve_inputs(step.get("input", {}), context)
        
        logger.info(f"Executing {agent_id}.{tool}")
        
        # Get agent
        agent = self.agents.get(agent_id, {})
        
        # Mock execution for now - in real implementation would call actual agent
        result = self._mock_execute_tool(agent_id, tool, inputs)
        
        # Add execution metadata
        result["_metadata"] = {
            "agent": agent_id,
            "tool": tool,
            "executed_at": datetime.now().isoformat(),
            "inputs": inputs
        }
        
        return result
        
    def execute_parallel_steps(self, steps: List[Dict[str, Any]], context: Any,
                             resolve_inputs: Callable) -> Dict[str, Any]:
        """
        Execute multiple steps in parallel
        
        Args:
            steps: List of steps to execute in parallel
            context: Workflow context
            resolve_inputs: Function to resolve inputs
            
        Returns:
            Combined results from all parallel steps
        """
        logger.info(f"Executing {len(steps)} steps in parallel")
        
        # Submit all tasks
        futures = {}
        for i, step in enumerate(steps):
            future = self.executor.submit(
                self.execute_single_step, 
                step, 
                context,
                resolve_inputs
            )
            futures[future] = (i, step)
            
        # Collect results
        results = {}
        errors = []
        
        for future in as_completed(futures):
            i, step = futures[future]
            try:
                result = future.result()
                # Store with step output name or index
                key = step.get("output", f"parallel_{i}")
                results[key] = result
                
                # Log completion
                agent = step.get("agent", "system")
                tool = step.get("tool", "unknown")
                logger.info(f"Completed parallel step {i}: {agent}.{tool}")
                
            except Exception as e:
                logger.error(f"Parallel step {i} failed: {e}")
                errors.append({
                    "step": i,
                    "agent": step.get("agent", "unknown"),
                    "tool": step.get("tool", "unknown"),
                    "error": str(e)
                })
                
        # Add metadata
        results["_parallel_metadata"] = {
            "total_steps": len(steps),
            "completed": len(results) - 1,  # Exclude metadata
            "errors": errors,
            "executed_at": datetime.now().isoformat()
        }
        
        # If any errors, include them in results
        if errors:
            results["_errors"] = errors
            
        return results
        
    def _mock_execute_tool(self, agent_id: str, tool: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Mock tool execution for testing"""
        
        # Simulate different tool outputs
        mock_responses = {
            "ua_architect_design": {
                "architecture": {
                    "components": ["auth_service", "user_db", "token_manager"],
                    "patterns": ["JWT", "RBAC", "refresh_tokens"],
                    "technologies": inputs.get("constraints", [])
                }
            },
            "ua_backend_api_design": {
                "endpoints": [
                    {"path": "/auth/login", "method": "POST", "auth": False},
                    {"path": "/auth/logout", "method": "POST", "auth": True},
                    {"path": "/auth/refresh", "method": "POST", "auth": False},
                    {"path": "/users/profile", "method": "GET", "auth": True}
                ],
                "schemas": {
                    "LoginRequest": {"username": "string", "password": "string"},
                    "LoginResponse": {"token": "string", "refresh_token": "string"}
                }
            },
            "ua_qa_test_generate": {
                "test_cases": [
                    {"name": "test_login_success", "type": "unit", "priority": "high"},
                    {"name": "test_login_invalid", "type": "unit", "priority": "high"},
                    {"name": "test_token_refresh", "type": "integration", "priority": "medium"},
                    {"name": "test_concurrent_sessions", "type": "integration", "priority": "low"}
                ],
                "coverage_target": "85%"
            },
            "ua_backend_implement": {
                "implementation": {
                    "files_created": ["auth_service.py", "token_manager.py", "models/user.py"],
                    "lines_of_code": 450,
                    "tests_included": True
                }
            },
            "ua_frontend_implement": {
                "implementation": {
                    "files_created": ["LoginForm.tsx", "AuthContext.tsx", "useAuth.ts"],
                    "components": 12,
                    "lines_of_code": 380
                }
            },
            "ua_qa_test_execute": {
                "results": {
                    "total_tests": 24,
                    "passed": 22,
                    "failed": 2,
                    "coverage": "83%",
                    "duration": "4.2s"
                }
            },
            "ua_qa_analyze_bug": {
                "analysis": {
                    "root_cause": "Null check missing in user lookup",
                    "affected_code": "auth_service.py:45",
                    "severity": "high",
                    "suggested_fix": "Add null check before accessing user.id"
                }
            },
            "ua_backend_debug": {
                "fix_plan": {
                    "approach": "Add defensive null checks",
                    "files_to_modify": ["auth_service.py"],
                    "estimated_time": "30 minutes",
                    "risk": "low"
                }
            },
            "ua_backend_implement_fix": {
                "fix": {
                    "files_modified": ["auth_service.py"],
                    "lines_changed": 5,
                    "tests_added": 2
                }
            },
            "ua_qa_verify_fix": {
                "verification": {
                    "bug_fixed": True,
                    "regression_tests_passed": True,
                    "new_tests_passed": True
                }
            },
            "ua_security_scan": {
                "findings": [
                    {"type": "sql_injection", "severity": "high", "location": "user_dao.py:23"},
                    {"type": "weak_encryption", "severity": "medium", "location": "crypto.py:45"}
                ]
            },
            "ua_architect_api_design": {
                "api_design": {
                    "style": "RESTful",
                    "versioning": "URL path (/v1/)",
                    "authentication": "Bearer token",
                    "rate_limiting": "100 req/min"
                }
            }
        }
        
        # Return mock response or generic success
        tool_key = tool
        if tool_key in mock_responses:
            return mock_responses[tool_key]
        else:
            return {
                "status": "completed",
                "agent": agent_id,
                "tool": tool,
                "message": f"Successfully executed {tool} with inputs: {json.dumps(inputs, indent=2)}"
            }
            
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)