"""
Template Registry - Manages workflow templates
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TemplateRegistry:
    """
    Manages workflow templates for multi-agent orchestration
    """
    
    def __init__(self):
        self.templates = {}
        self.custom_templates = {}
        self._load_builtin_templates()
        
    def _load_builtin_templates(self):
        """Load built-in workflow templates"""
        # For now, define templates in code. Later can load from YAML/JSON files
        
        # Feature Development Template
        self.templates["feature_development"] = {
            "id": "feature_development",
            "name": "Feature Development Workflow",
            "description": "End-to-end feature implementation with architecture, development, and testing",
            "inputs": {
                "requirements": {
                    "type": "string",
                    "description": "Feature requirements description",
                    "required": True
                },
                "constraints": {
                    "type": "array",
                    "description": "Technical constraints or limitations",
                    "required": False
                }
            },
            "steps": [
                {
                    "name": "Design Architecture",
                    "agent": "architect",
                    "tool": "ua_architect_design",
                    "input": {
                        "requirements": "{requirements}",
                        "constraints": "{constraints}"
                    },
                    "output": "architecture_design"
                },
                {
                    "name": "Design API",
                    "agent": "backend",
                    "tool": "ua_backend_api_design",
                    "input": {
                        "requirements": "{requirements}",
                        "architecture": "{architecture_design}"
                    },
                    "output": "api_spec"
                },
                {
                    "name": "Generate Test Plan",
                    "agent": "qa",
                    "tool": "ua_qa_test_generate",
                    "input": {
                        "feature": "{requirements}",
                        "api_spec": "{api_spec}"
                    },
                    "output": "test_plan"
                },
                {
                    "name": "Implement Feature",
                    "parallel": [
                        {
                            "agent": "backend",
                            "tool": "ua_backend_implement",
                            "input": {
                                "api_spec": "{api_spec}",
                                "architecture": "{architecture_design}"
                            },
                            "output": "backend_code"
                        },
                        {
                            "agent": "frontend",
                            "tool": "ua_frontend_implement",
                            "input": {
                                "api_spec": "{api_spec}",
                                "requirements": "{requirements}"
                            },
                            "output": "frontend_code"
                        }
                    ]
                },
                {
                    "name": "Execute Tests",
                    "agent": "qa",
                    "tool": "ua_qa_test_execute",
                    "input": {
                        "test_plan": "{test_plan}",
                        "backend_code": "{backend_code}",
                        "frontend_code": "{frontend_code}"
                    },
                    "output": "test_results"
                }
            ]
        }
        
        # Bug Fix Template
        self.templates["bug_fix"] = {
            "id": "bug_fix",
            "name": "Bug Fix Workflow", 
            "description": "Systematic bug analysis and resolution",
            "inputs": {
                "bug_description": {
                    "type": "string",
                    "description": "Description of the bug",
                    "required": True
                },
                "stack_trace": {
                    "type": "string",
                    "description": "Error stack trace if available",
                    "required": False
                },
                "affected_component": {
                    "type": "string",
                    "description": "Component where bug occurs",
                    "required": False
                }
            },
            "steps": [
                {
                    "name": "Analyze Bug",
                    "agent": "qa",
                    "tool": "ua_qa_analyze_bug",
                    "input": {
                        "description": "{bug_description}",
                        "stacktrace": "{stack_trace}"
                    },
                    "output": "root_cause_analysis"
                },
                {
                    "name": "Design Fix",
                    "agent": "backend",
                    "tool": "ua_backend_debug",
                    "input": {
                        "root_cause": "{root_cause_analysis}",
                        "component": "{affected_component}"
                    },
                    "output": "fix_plan"
                },
                {
                    "name": "Implement Fix",
                    "agent": "backend",
                    "tool": "ua_backend_implement_fix",
                    "input": {
                        "fix_plan": "{fix_plan}",
                        "root_cause": "{root_cause_analysis}"
                    },
                    "output": "fix_code"
                },
                {
                    "name": "Verify Fix",
                    "agent": "qa",
                    "tool": "ua_qa_verify_fix",
                    "input": {
                        "bug_description": "{bug_description}",
                        "fix_code": "{fix_code}",
                        "root_cause": "{root_cause_analysis}"
                    },
                    "output": "verification_results"
                }
            ]
        }
        
        # Security Audit Template
        self.templates["security_audit"] = {
            "id": "security_audit",
            "name": "Security Audit Workflow",
            "description": "Comprehensive security analysis and remediation",
            "inputs": {
                "scope": {
                    "type": "string",
                    "description": "Scope of security audit",
                    "required": True
                },
                "compliance_requirements": {
                    "type": "array",
                    "description": "Compliance standards to check",
                    "required": False
                }
            },
            "steps": [
                {
                    "name": "Initial Security Scan",
                    "agent": "security",
                    "tool": "ua_security_scan",
                    "input": {
                        "scope": "{scope}",
                        "compliance": "{compliance_requirements}"
                    },
                    "output": "security_findings"
                },
                {
                    "name": "Analyze Vulnerabilities",
                    "agent": "security",
                    "tool": "ua_security_analyze",
                    "input": {
                        "findings": "{security_findings}"
                    },
                    "output": "vulnerability_analysis"
                },
                {
                    "name": "Design Remediation",
                    "parallel": [
                        {
                            "agent": "architect",
                            "tool": "ua_architect_security_design",
                            "input": {
                                "vulnerabilities": "{vulnerability_analysis}"
                            },
                            "output": "security_architecture"
                        },
                        {
                            "agent": "backend",
                            "tool": "ua_backend_security_plan",
                            "input": {
                                "vulnerabilities": "{vulnerability_analysis}"
                            },
                            "output": "remediation_plan"
                        }
                    ]
                },
                {
                    "name": "Implement Fixes",
                    "agent": "backend",
                    "tool": "ua_backend_security_implement",
                    "input": {
                        "plan": "{remediation_plan}",
                        "architecture": "{security_architecture}"
                    },
                    "output": "security_fixes"
                },
                {
                    "name": "Verify Security",
                    "agent": "security",
                    "tool": "ua_security_verify",
                    "input": {
                        "original_findings": "{security_findings}",
                        "fixes": "{security_fixes}"
                    },
                    "output": "verification_report"
                }
            ]
        }
        
        # API Design Template
        self.templates["api_design"] = {
            "id": "api_design",
            "name": "API Design Workflow",
            "description": "Design and implement REST APIs with best practices",
            "inputs": {
                "resource": {
                    "type": "string",
                    "description": "Resource to create API for",
                    "required": True
                },
                "operations": {
                    "type": "array",
                    "description": "CRUD operations needed",
                    "required": True
                },
                "authentication": {
                    "type": "boolean",
                    "description": "Whether authentication is required",
                    "required": False
                }
            },
            "steps": [
                {
                    "name": "Design API Structure",
                    "agent": "architect",
                    "tool": "ua_architect_api_design",
                    "input": {
                        "resource": "{resource}",
                        "operations": "{operations}"
                    },
                    "output": "api_architecture"
                },
                {
                    "name": "Create API Specification",
                    "agent": "backend",
                    "tool": "ua_backend_api_spec",
                    "input": {
                        "architecture": "{api_architecture}",
                        "authentication": "{authentication}"
                    },
                    "output": "openapi_spec"
                },
                {
                    "name": "Generate Tests",
                    "agent": "qa",
                    "tool": "ua_qa_api_tests",
                    "input": {
                        "spec": "{openapi_spec}"
                    },
                    "output": "api_tests"
                },
                {
                    "name": "Implement API",
                    "agent": "backend",
                    "tool": "ua_backend_api_implement",
                    "input": {
                        "spec": "{openapi_spec}",
                        "tests": "{api_tests}"
                    },
                    "output": "api_implementation"
                }
            ]
        }
        
        logger.info(f"Loaded {len(self.templates)} built-in templates")
        
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        # Check custom templates first
        if template_id in self.custom_templates:
            return self.custom_templates[template_id]
            
        # Then check built-in templates
        return self.templates.get(template_id)
        
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        all_templates = []
        
        # Built-in templates
        for template in self.templates.values():
            all_templates.append({
                "id": template["id"],
                "name": template["name"],
                "description": template["description"],
                "type": "built-in",
                "steps_count": len(template["steps"])
            })
            
        # Custom templates
        for template in self.custom_templates.values():
            all_templates.append({
                "id": template["id"],
                "name": template["name"],
                "description": template["description"],
                "type": "custom",
                "steps_count": len(template["steps"])
            })
            
        return all_templates
        
    def register_custom_template(self, template: Dict[str, Any]) -> str:
        """Register a custom workflow template"""
        # Validate template
        self._validate_template(template)
        
        # Generate ID if not provided
        if "id" not in template:
            template["id"] = f"custom_{len(self.custom_templates)}"
            
        # Store template
        self.custom_templates[template["id"]] = template
        
        logger.info(f"Registered custom template: {template['id']}")
        
        return template["id"]
        
    def _validate_template(self, template: Dict[str, Any]):
        """Validate template structure"""
        required_fields = ["name", "description", "steps"]
        
        for field in required_fields:
            if field not in template:
                raise ValueError(f"Template missing required field: {field}")
                
        if not isinstance(template["steps"], list):
            raise ValueError("Template steps must be a list")
            
        if len(template["steps"]) == 0:
            raise ValueError("Template must have at least one step")
            
        # Validate each step
        for i, step in enumerate(template["steps"]):
            if "parallel" in step:
                # Validate parallel steps
                if not isinstance(step["parallel"], list):
                    raise ValueError(f"Step {i}: parallel must be a list")
                    
                for j, parallel_step in enumerate(step["parallel"]):
                    self._validate_step(parallel_step, f"Step {i}.{j}")
            else:
                # Validate single step
                self._validate_step(step, f"Step {i}")
                
    def _validate_step(self, step: Dict[str, Any], step_id: str):
        """Validate a single step"""
        required_fields = ["agent", "tool"]
        
        for field in required_fields:
            if field not in step:
                raise ValueError(f"{step_id}: missing required field '{field}'")
                
    def export_template(self, template_id: str) -> str:
        """Export a template as JSON"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
            
        return json.dumps(template, indent=2)
        
    def import_template(self, template_json: str) -> str:
        """Import a template from JSON"""
        try:
            template = json.loads(template_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
            
        return self.register_custom_template(template)
        
    def get_template_info(self, template_id: str) -> Dict[str, Any]:
        """Get detailed information about a template"""
        template = self.get_template(template_id)
        if not template:
            return {"error": f"Template not found: {template_id}"}
            
        # Count agents used
        agents_used = set()
        tools_used = set()
        
        for step in template["steps"]:
            if "parallel" in step:
                for parallel_step in step["parallel"]:
                    agents_used.add(parallel_step.get("agent", "unknown"))
                    tools_used.add(parallel_step.get("tool", "unknown"))
            else:
                agents_used.add(step.get("agent", "unknown"))
                tools_used.add(step.get("tool", "unknown"))
                
        return {
            "template": template,
            "statistics": {
                "total_steps": len(template["steps"]),
                "agents_used": list(agents_used),
                "tools_used": list(tools_used),
                "has_parallel_steps": any("parallel" in step for step in template["steps"]),
                "inputs_required": list(template.get("inputs", {}).keys())
            }
        }