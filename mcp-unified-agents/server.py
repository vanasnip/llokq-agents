#!/usr/bin/env python3
"""
Unified Agents MCP Server - With Workflow Orchestration
Exposes agents via Model Context Protocol with workflow capabilities

Phase 2: Adds workflow orchestration and context sharing
"""
import json
import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import traceback
import os
import re
from datetime import datetime
from contextlib import contextmanager

# Configuration constants
DEBUG_MODE = os.environ.get('MCP_DEBUG', '').lower() in ('true', '1', 'yes')
DEBUG_LOG_PATH = os.environ.get('MCP_DEBUG_LOG', '/tmp/mcp-unified-agents-startup.log')
DEFAULT_PROTOCOL_VERSION = '2025-06-18'
PROTOCOL_VERSION_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# Debug logging context manager
@contextmanager
def debug_log(message: str):
    """Context manager for debug logging with proper resource management"""
    if not DEBUG_MODE:
        yield
        return
    
    try:
        with open(DEBUG_LOG_PATH, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
        yield
    except Exception:
        # Fail silently in debug logging
        yield

# Startup debugging
if DEBUG_MODE:
    with debug_log(f"\n{'='*60}"):
        pass
    with debug_log(f"MCP Server startup"):
        pass
    with debug_log(f"Python: {sys.executable}"):
        pass
    with debug_log(f"Script: {__file__}"):
        pass
    with debug_log(f"CWD: {os.getcwd()}"):
        pass
    with debug_log(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}"):
        pass
    with debug_log(f"sys.path: {sys.path[:3]}..."):
        pass

try:
    # Import workflow components
    from workflow import WorkflowEngine, ContextManager
    if DEBUG_MODE:
        with debug_log("✅ Workflow imports successful"):
            pass
except Exception as e:
    if DEBUG_MODE:
        with debug_log(f"❌ Workflow import failed: {e}\n{traceback.format_exc()}"):
            pass
    raise

try:
    # Import deployment components
    from deployment import DeploymentManager
    if DEBUG_MODE:
        with debug_log("✅ Deployment imports successful"):
            pass
except Exception as e:
    if DEBUG_MODE:
        with debug_log(f"❌ Deployment import failed: {e}\n{traceback.format_exc()}"):
            pass
    # Deployment is optional, don't raise
    pass

try:
    # Import tool registry
    from tools import registry, register_all_handlers
    if DEBUG_MODE:
        with debug_log("✅ Tool registry imports successful"):
            pass
except Exception as e:
    if DEBUG_MODE:
        with debug_log(f"❌ Tool registry import failed: {e}\n{traceback.format_exc()}"):
            pass
    raise

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# JSON Schema for agent manifest validation
AGENT_MANIFEST_SCHEMA = {
    "type": "object",
    "required": ["version", "agents"],
    "properties": {
        "version": {"type": "string"},
        "agents": {
            "type": "object",
            "patternProperties": {
                "^[a-z_]+$": {
                    "type": "object",
                    "required": ["name", "description", "tools"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "tools": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["name", "description", "parameters"],
                                "properties": {
                                    "name": {"type": "string", "pattern": "^ua_[a-z]+_[a-z_]+$"},
                                    "description": {"type": "string"},
                                    "parameters": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


def validate_manifest(data: Dict[str, Any]) -> None:
    """Validate agent manifest against schema"""
    # Simple validation without external dependencies
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    
    if "version" not in data:
        raise ValueError("Manifest missing required field: version")
    
    if "agents" not in data:
        raise ValueError("Manifest missing required field: agents")
    
    if not isinstance(data["agents"], dict):
        raise ValueError("Agents field must be an object")
    
    for agent_id, agent in data["agents"].items():
        if not isinstance(agent, dict):
            raise ValueError(f"Agent {agent_id} must be an object")
        
        for field in ["name", "description", "tools"]:
            if field not in agent:
                raise ValueError(f"Agent {agent_id} missing required field: {field}")
        
        if not isinstance(agent["tools"], list):
            raise ValueError(f"Agent {agent_id} tools must be an array")
        
        for i, tool in enumerate(agent["tools"]):
            if not isinstance(tool, dict):
                raise ValueError(f"Agent {agent_id} tool {i} must be an object")
            
            for field in ["name", "description", "parameters"]:
                if field not in tool:
                    raise ValueError(f"Agent {agent_id} tool {i} missing required field: {field}")
            
            # Validate tool name pattern
            if not tool["name"].startswith("ua_"):
                raise ValueError(f"Tool name must start with 'ua_': {tool['name']}")


class SessionState:
    """Manages user preferences and agent approvals for a session"""
    
    def __init__(self):
        self.approved_agents = set()
        self.rejected_agents = set()
        self.auto_approve = False
        self.require_approval = set()  # Agents that always need approval
        self.block_agents = set()  # Agents to never use
        self.last_suggestion = None
        self.suggestion_counter = 0
    
    def generate_suggestion_id(self) -> str:
        """Generate unique suggestion ID"""
        self.suggestion_counter += 1
        return f"sug_{self.suggestion_counter}"
    
    def clear_old_suggestions(self):
        """Clear old suggestion data (called periodically)"""
        # In a real implementation, we'd track timestamps
        pass


class UnifiedAgentServer:
    """MCP server that exposes unified agents as tools with workflow orchestration"""
    
    def __init__(self, manifest_path: str = "agents.json"):
        # Make path absolute relative to script location
        if not os.path.isabs(manifest_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.manifest_path = Path(script_dir) / manifest_path
        else:
            self.manifest_path = Path(manifest_path)
        
        # Debug logging
        with debug_log(f"Resolved manifest path: {self.manifest_path}"):
            pass
        with debug_log(f"Manifest exists: {self.manifest_path.exists()}"):
            pass
        
        self.agents = self._load_agents()
        self.capability_graph = self._load_capability_graph()
        self.session = SessionState()  # Simple session management
        
        # Initialize workflow components
        self.context_manager = ContextManager()
        self.workflow_engine = WorkflowEngine(
            agent_registry=self.agents,
            context_manager=self.context_manager
        )
        
        # Initialize deployment manager if available
        try:
            import os
            dev_path = os.environ.get('MCP_DEV_PATH', str(Path(__file__).parent.parent))
            prod_path = os.environ.get('MCP_PROD_PATH', os.path.expanduser("~/mcp-config/servers/mcp-unified-agents"))
            self.deployment_mgr = DeploymentManager(dev_path, prod_path)
        except Exception as e:
            logger.warning(f"Deployment manager not available: {e}")
            self.deployment_mgr = None
        
        # Initialize tool handlers
        register_all_handlers()
        logger.info("Tool handlers registered")
        
    def _load_agents(self) -> Dict[str, Any]:
        """Load agent manifest from JSON"""
        try:
            with open(self.manifest_path) as f:
                data = json.load(f)
            
            # Validate manifest structure
            validate_manifest(data)
            return data.get('agents', {})
            
        except FileNotFoundError:
            logger.error(f"Manifest file not found: {self.manifest_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in manifest: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid manifest structure: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load agents manifest: {e}")
            raise
    
    def _load_capability_graph(self) -> Dict[str, Any]:
        """Load capability graph from manifest"""
        try:
            with open(self.manifest_path) as f:
                data = json.load(f)
                return data.get('capability_graph', {})
        except Exception:
            # Capability graph is optional, return empty if not found
            return {}
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        method = request.get('method')
        request_id = request.get('id')
        
        try:
            if method == 'initialize':
                # Extract the protocol version from the request
                client_protocol = request.get('params', {}).get('protocolVersion', DEFAULT_PROTOCOL_VERSION)
                return self._handle_initialize(request_id, client_protocol)
            elif method == 'tools/list':
                return self._handle_list_tools(request_id)
            elif method == 'tools/call':
                return self._handle_call_tool(request_id, request.get('params', {}))
            else:
                return self._error_response(request_id, f"Unknown method: {method}", -32601)
        except ValueError as e:
            # Invalid parameters or validation errors
            logger.error(f"Invalid parameters: {e}")
            return self._error_response(request_id, str(e), -32602)
        except Exception as e:
            # Internal server error
            logger.error(f"Error handling request: {e}")
            return self._error_response(request_id, str(e), -32603)
    
    def _handle_initialize(self, request_id: Any, client_protocol: str) -> Dict[str, Any]:
        """Handle initialization request with protocol version validation"""
        # Validate protocol version format
        if not self._validate_protocol_version(client_protocol):
            logger.warning(f"Invalid protocol version format: {client_protocol}, using default")
            client_protocol = DEFAULT_PROTOCOL_VERSION
        
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'protocolVersion': client_protocol,
                'capabilities': {
                    'tools': {},
                    'prompts': {}
                },
                'serverInfo': {
                    'name': 'unified-agents',
                    'version': '0.1.0'
                }
            }
        }
    
    def _validate_protocol_version(self, version: str) -> bool:
        """Validate protocol version format (YYYY-MM-DD)"""
        if not isinstance(version, str):
            return False
        return bool(PROTOCOL_VERSION_PATTERN.match(version))
    
    def _handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """List all available tools"""
        tools = []
        
        # Add discovery tools
        discovery_tools = [
            {
                'name': 'ua_agents_list',
                'description': 'List all available agents with their descriptions and capabilities',
                'inputSchema': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            },
            {
                'name': 'ua_agent_info',
                'description': 'Get detailed information about a specific agent',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'agent_id': {
                            'type': 'string',
                            'description': 'The agent identifier (e.g., qa, backend, architect)'
                        }
                    },
                    'required': ['agent_id']
                }
            },
            {
                'name': 'ua_capability_search',
                'description': 'Search for agents by capability or domain',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Search query for capabilities or domains'
                        }
                    },
                    'required': ['query']
                }
            },
            {
                'name': 'ua_agent_compatible',
                'description': 'Find agents that work well with a given agent',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'agent_id': {
                            'type': 'string',
                            'description': 'The agent to find compatible partners for'
                        }
                    },
                    'required': ['agent_id']
                }
            }
        ]
        
        tools.extend(discovery_tools)
        
        # Add control tools
        control_tools = [
            {
                'name': 'ua_suggest_agents',
                'description': 'Analyze a task and suggest appropriate agents',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'task': {
                            'type': 'string',
                            'description': 'Description of the task to accomplish'
                        },
                        'context': {
                            'type': 'string',
                            'description': 'Additional context about the project'
                        }
                    },
                    'required': ['task']
                }
            },
            {
                'name': 'ua_approve_agents',
                'description': 'Approve or reject agent suggestions',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'action': {
                            'type': 'string',
                            'enum': ['approve', 'reject', 'approve_all', 'reset'],
                            'description': 'Action to take on agents'
                        },
                        'agents': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Agent IDs to approve/reject'
                        },
                        'suggestion_id': {
                            'type': 'string',
                            'description': 'Reference to specific suggestion'
                        }
                    },
                    'required': ['action']
                }
            },
            {
                'name': 'ua_set_preferences',
                'description': 'Configure session-wide agent preferences',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'auto_approve': {
                            'type': 'boolean',
                            'description': 'Auto-approve all agent suggestions'
                        },
                        'require_approval': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Agents that always need approval'
                        },
                        'block_agents': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Agents to never use'
                        }
                    }
                }
            }
        ]
        
        tools.extend(control_tools)
        
        # Add workflow tools
        workflow_tools = [
            {
                'name': 'ua_workflow_start',
                'description': 'Start a workflow template execution',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'template': {
                            'type': 'string',
                            'description': 'Workflow template name (e.g., feature_development, bug_fix)'
                        },
                        'inputs': {
                            'type': 'object',
                            'description': 'Input parameters for the workflow'
                        },
                        'require_approval': {
                            'type': 'boolean',
                            'description': 'Require approval before starting workflow'
                        }
                    },
                    'required': ['template', 'inputs']
                }
            },
            {
                'name': 'ua_workflow_status',
                'description': 'Get workflow execution status',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'workflow_id': {
                            'type': 'string',
                            'description': 'Workflow execution ID'
                        }
                    },
                    'required': ['workflow_id']
                }
            },
            {
                'name': 'ua_workflow_list',
                'description': 'List all workflow executions',
                'inputSchema': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'ua_workflow_templates',
                'description': 'List available workflow templates',
                'inputSchema': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'ua_workflow_suggest',
                'description': 'Suggest workflows for a task',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'task': {
                            'type': 'string',
                            'description': 'Task description'
                        }
                    },
                    'required': ['task']
                }
            },
            {
                'name': 'ua_workflow_create',
                'description': 'Create a custom workflow template',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Workflow name'
                        },
                        'description': {
                            'type': 'string',
                            'description': 'Workflow description'
                        },
                        'steps': {
                            'type': 'array',
                            'description': 'List of workflow steps',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'agent': {'type': 'string'},
                                    'tool': {'type': 'string'},
                                    'input': {'type': 'object'},
                                    'output': {'type': 'string'}
                                }
                            }
                        }
                    },
                    'required': ['name', 'description', 'steps']
                }
            },
            {
                'name': 'ua_workflow_cancel',
                'description': 'Cancel a running workflow',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'workflow_id': {
                            'type': 'string',
                            'description': 'Workflow execution ID to cancel'
                        },
                        'reason': {
                            'type': 'string',
                            'description': 'Reason for cancellation'
                        }
                    },
                    'required': ['workflow_id']
                }
            },
            {
                'name': 'ua_workflow_dry_run',
                'description': 'Preview what a workflow would do without executing it',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'template': {
                            'type': 'string',
                            'description': 'Workflow template name'
                        },
                        'inputs': {
                            'type': 'object',
                            'description': 'Input parameters for the workflow'
                        }
                    },
                    'required': ['template', 'inputs']
                }
            }
        ]
        
        tools.extend(workflow_tools)
        
        # Add deployment tools if available
        if self.deployment_mgr:
            deployment_tools = [
                {
                    'name': 'ua_self_deploy',
                    'description': 'Deploy changes from development to production with automatic backup',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'dry_run': {
                                'type': 'boolean',
                                'description': 'Preview changes without deploying',
                                'default': False
                            }
                        },
                        'required': []
                    }
                },
                {
                    'name': 'ua_self_status',
                    'description': 'Check deployment status and pending changes',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                },
                {
                    'name': 'ua_self_rollback',
                    'description': 'Rollback to a previous deployment',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'version': {
                                'type': 'string',
                                'description': 'Specific version to rollback to (optional, defaults to last)'
                            }
                        },
                        'required': []
                    }
                }
            ]
            tools.extend(deployment_tools)
        
        # Add agent-specific tools
        for agent_id, agent in self.agents.items():
            for tool in agent.get('tools', []):
                # Build parameter schema
                schema = {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
                
                for param_name, param_def in tool.get('parameters', {}).items():
                    is_optional = param_name.endswith('?')
                    clean_name = param_name.rstrip('?')
                    
                    if isinstance(param_def, str):
                        # Simple type
                        schema['properties'][clean_name] = {'type': param_def}
                    elif isinstance(param_def, dict):
                        # Complex type with enum
                        if 'enum' in param_def:
                            schema['properties'][clean_name] = {
                                'type': 'string',
                                'enum': param_def['enum']
                            }
                        else:
                            schema['properties'][clean_name] = param_def
                    
                    if not is_optional:
                        schema['required'].append(clean_name)
                
                tools.append({
                    'name': tool['name'],
                    'description': f"[{agent['name']}] {tool['description']}",
                    'inputSchema': schema
                })
        
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'tools': tools
            }
        }
    
    def _handle_call_tool(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool invocation"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        # Use the registry to route to appropriate handler
        try:
            handler = registry.get_handler(tool_name)
            if not handler:
                # Special handling for deployment tools if manager is available
                if tool_name.startswith('ua_self_') and self.deployment_mgr:
                    result = self._handle_deployment_tool(tool_name, arguments)
                else:
                    return self._error_response(request_id, f"Unknown tool: {tool_name}", -32601)
            else:
                # Pass server instance to handlers that need it
                # This is a temporary solution - handlers currently create their own instances
                result = handler(tool_name, arguments)
        except ValueError as e:
            # Tool-specific errors (unknown tool, missing params)
            return self._error_response(request_id, str(e), -32602)
        
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': result
        }
    
    def _handle_qa_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle QA agent tools"""
        try:
            if tool_name == 'ua_qa_test_generate':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._generate_tests(args['feature'], args.get('test_type', 'unit'))
                    }]
                }
            elif tool_name == 'ua_qa_analyze_bug':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._analyze_bug(args['description'], args.get('stacktrace'))
                    }]
                }
            else:
                raise ValueError(f"Unknown QA tool: {tool_name}")
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    def _handle_backend_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Backend agent tools"""
        try:
            if tool_name == 'ua_backend_api_design':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._design_api(args['resource'], args['operations'])
                    }]
                }
            elif tool_name == 'ua_backend_optimize':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._optimize_code(args['code'], args.get('metrics'))
                    }]
                }
            else:
                raise ValueError(f"Unknown Backend tool: {tool_name}")
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    def _handle_architect_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Architect agent tools"""
        try:
            if tool_name == 'ua_architect_design':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._design_system(args['requirements'], args.get('constraints', []))
                    }]
                }
            else:
                raise ValueError(f"Unknown Architect tool: {tool_name}")
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    def _handle_discovery_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent discovery tools"""
        try:
            if tool_name == 'ua_agents_list':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._list_agents()
                    }]
                }
            elif tool_name == 'ua_agent_info':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._get_agent_info(args['agent_id'])
                    }]
                }
            elif tool_name == 'ua_capability_search':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._search_by_capability(args['query'])
                    }]
                }
            elif tool_name == 'ua_agent_compatible':
                return {
                    'content': [{
                        'type': 'text',
                        'text': self._find_compatible_agents(args['agent_id'])
                    }]
                }
            else:
                raise ValueError(f"Unknown discovery tool: {tool_name}")
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    def _handle_control_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user control tools"""
        try:
            if tool_name == 'ua_suggest_agents':
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(self._suggest_agents(args['task'], args.get('context', '')), indent=2)
                    }]
                }
            elif tool_name == 'ua_approve_agents':
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(self._approve_agents(
                            args['action'],
                            args.get('agents', []),
                            args.get('suggestion_id')
                        ), indent=2)
                    }]
                }
            elif tool_name == 'ua_set_preferences':
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(self._set_preferences(args), indent=2)
                    }]
                }
            else:
                raise ValueError(f"Unknown control tool: {tool_name}")
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    # Tool implementation methods
    def _generate_tests(self, feature: str, test_type: str) -> str:
        """Generate test cases for a feature"""
        test_templates = {
            'unit': f"""Generated Unit Tests for: {feature}

```python
import pytest
from unittest.mock import Mock, patch

class Test{feature.replace(' ', '')}:
    def test_basic_functionality(self):
        # Arrange
        # TODO: Set up test data
        
        # Act
        # TODO: Execute the feature
        
        # Assert
        # TODO: Verify expected behavior
        
    def test_edge_cases(self):
        # Test null/empty inputs
        # Test boundary conditions
        # Test error scenarios
        pass
```

Key test scenarios identified:
1. Happy path - normal operation
2. Edge cases - boundary conditions
3. Error handling - invalid inputs
4. Performance - response times""",
            
            'integration': f"""Generated Integration Tests for: {feature}

```python
class Test{feature.replace(' ', '')}Integration:
    def test_component_interaction(self):
        # Test interaction between components
        pass
        
    def test_database_operations(self):
        # Test with real database
        pass
```""",
            
            'e2e': f"""Generated E2E Tests for: {feature}

```javascript
describe('{feature}', () => {{
    it('should complete user journey', () => {{
        // Navigate to feature
        // Perform user actions
        // Verify end result
    }});
}});
```"""
        }
        
        return test_templates.get(test_type, test_templates['unit'])
    
    def _analyze_bug(self, description: str, stacktrace: Optional[str]) -> str:
        """Analyze a bug and suggest root cause"""
        analysis = f"""Bug Analysis: {description}

**Initial Assessment:**
Based on the description, this appears to be related to:
"""
        
        if stacktrace:
            if "NullPointerException" in stacktrace or "undefined" in stacktrace:
                analysis += "- Null reference or undefined value access\n"
            if "timeout" in stacktrace.lower():
                analysis += "- Performance or timeout issue\n"
            if "connection" in stacktrace.lower():
                analysis += "- Network or database connectivity\n"
        
        analysis += f"""
**Potential Root Causes:**
1. Input validation missing
2. Edge case not handled
3. Race condition in async code
4. Resource exhaustion

**Recommended Actions:**
1. Add logging at failure point
2. Check recent code changes
3. Verify input data validity
4. Review error handling

**Prevention:**
- Add comprehensive input validation
- Implement proper error boundaries
- Add monitoring for this scenario
"""
        
        return analysis
    
    def _design_api(self, resource: str, operations: List[str]) -> str:
        """Design REST API for a resource"""
        api_design = f"""REST API Design for: {resource}

**Resource:** /{resource.lower()}

**Endpoints:**
"""
        
        operation_specs = {
            'create': f"POST /{resource.lower()}\n  Creates a new {resource}",
            'read': f"GET /{resource.lower()}/{{id}}\n  Retrieves a specific {resource}",
            'update': f"PUT /{resource.lower()}/{{id}}\n  Updates an existing {resource}",
            'delete': f"DELETE /{resource.lower()}/{{id}}\n  Deletes a {resource}",
            'list': f"GET /{resource.lower()}\n  Lists all {resource}s with pagination",
            'search': f"GET /{resource.lower()}/search\n  Searches {resource}s"
        }
        
        for op in operations:
            if op in operation_specs:
                api_design += f"\n{operation_specs[op]}"
        
        api_design += f"""

**Data Model:**
```json
{{
  "id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  // Add resource-specific fields
}}
```

**Best Practices Applied:**
- RESTful naming conventions
- Proper HTTP status codes
- Pagination for lists
- Consistent error responses
- API versioning ready
"""
        
        return api_design
    
    def _optimize_code(self, code: str, metrics: Optional[Dict[str, Any]]) -> str:
        """Suggest code optimizations"""
        suggestions = f"""Code Optimization Analysis

**Code Review:**
{code[:200]}... (truncated)

**Optimization Suggestions:**

1. **Performance:**
   - Consider caching frequently accessed data
   - Use batch operations for multiple items
   - Implement lazy loading where appropriate

2. **Memory:**
   - Release resources explicitly
   - Use streaming for large data sets
   - Consider object pooling

3. **Scalability:**
   - Make operations async where possible
   - Implement connection pooling
   - Add rate limiting

4. **Code Quality:**
   - Extract complex logic to separate functions
   - Add error handling
   - Improve variable naming
"""
        
        if metrics:
            suggestions += f"\n**Current Metrics:**\n"
            for key, value in metrics.items():
                suggestions += f"- {key}: {value}\n"
        
        return suggestions
    
    def _design_system(self, requirements: str, constraints: List[str]) -> str:
        """Design system architecture"""
        design = f"""System Architecture Design

**Requirements:** {requirements}

**Proposed Architecture:**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│     API     │────▶│   Backend   │
│   (React)   │     │  (GraphQL)  │     │  (Python)   │
└─────────────┘     └─────────────┘     └─────────────┘
                            │                    │
                            ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │    Cache    │     │  Database   │
                    │   (Redis)   │     │ (PostgreSQL)│
                    └─────────────┘     └─────────────┘
```

**Key Components:**
1. **Frontend**: React SPA with responsive design
2. **API Layer**: GraphQL for flexible queries
3. **Backend**: Python microservices
4. **Database**: PostgreSQL for ACID compliance
5. **Cache**: Redis for performance

**Design Patterns:**
- Repository pattern for data access
- Observer pattern for real-time updates
- Factory pattern for object creation
- Strategy pattern for business logic
"""
        
        if constraints:
            design += "\n**Constraints Addressed:**\n"
            for constraint in constraints:
                design += f"- {constraint}: Addressed by...\n"
        
        design += """
**Scalability Plan:**
- Horizontal scaling for API/Backend
- Read replicas for database
- CDN for static assets
- Message queue for async tasks
"""
        
        return design
    
    # Discovery tool implementations
    def _list_agents(self) -> str:
        """List all available agents"""
        result = "# Available Agents\n\n"
        
        for agent_id, agent in self.agents.items():
            result += f"## {agent['name']} (`{agent_id}`)\n"
            result += f"{agent['description']}\n\n"
            
            if 'personality' in agent:
                result += f"**Personality**: {agent['personality']}\n\n"
            
            if 'capabilities' in agent:
                result += "**Capabilities**:\n"
                for cap in agent['capabilities']:
                    result += f"- {cap}\n"
                result += "\n"
            
            result += "**Available Tools**:\n"
            for tool in agent.get('tools', []):
                result += f"- `{tool['name']}`: {tool['description']}\n"
            result += "\n---\n\n"
        
        return result.strip()
    
    def _get_agent_info(self, agent_id: str) -> str:
        """Get detailed information about a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = self.agents[agent_id]
        result = f"# {agent['name']} Agent\n\n"
        result += f"**ID**: `{agent_id}`\n"
        result += f"**Description**: {agent['description']}\n\n"
        
        if 'personality' in agent:
            result += f"**Personality**: {agent['personality']}\n\n"
        
        if 'capabilities' in agent:
            result += "## Capabilities\n"
            for cap in agent['capabilities']:
                result += f"- {cap}\n"
            result += "\n"
        
        # Show compatible agents from capability graph
        if agent_id in self.capability_graph:
            result += "## Relationships\n"
            cap_info = self.capability_graph[agent_id]
            
            if 'requires' in cap_info:
                result += "**Requires**:\n"
                for req in cap_info['requires']:
                    result += f"- {req}\n"
                result += "\n"
            
            if 'provides' in cap_info:
                result += "**Provides**:\n"
                for prov in cap_info['provides']:
                    result += f"- {prov}\n"
                result += "\n"
            
            if 'complements' in cap_info:
                result += "**Works Well With**:\n"
                for comp in cap_info['complements']:
                    result += f"- {comp}\n"
                result += "\n"
        
        result += "## Available Tools\n"
        for tool in agent.get('tools', []):
            result += f"\n### `{tool['name']}`\n"
            result += f"{tool['description']}\n\n"
            
            if 'parameters' in tool:
                result += "**Parameters**:\n"
                for param, details in tool['parameters'].items():
                    required = "" if param.endswith("?") else " (required)"
                    param_clean = param.rstrip("?")
                    if isinstance(details, dict):
                        param_type = details.get('type', 'any')
                        desc = details.get('description', '')
                        result += f"- `{param_clean}` ({param_type}){required}: {desc}\n"
                    else:
                        result += f"- `{param_clean}` ({details}){required}\n"
                result += "\n"
        
        return result.strip()
    
    def _search_by_capability(self, query: str) -> str:
        """Search agents by capability or domain"""
        query_lower = query.lower()
        matches = []
        
        # Search in agent capabilities
        for agent_id, agent in self.agents.items():
            score = 0
            reasons = []
            
            # Check agent name and description
            if query_lower in agent['name'].lower():
                score += 3
                reasons.append("name match")
            if query_lower in agent['description'].lower():
                score += 2
                reasons.append("description match")
            
            # Check capabilities
            for cap in agent.get('capabilities', []):
                if query_lower in cap.lower():
                    score += 2
                    reasons.append(f"capability: {cap}")
            
            # Check tool names and descriptions
            for tool in agent.get('tools', []):
                if query_lower in tool['name'].lower():
                    score += 1
                    reasons.append(f"tool: {tool['name']}")
                if query_lower in tool['description'].lower():
                    score += 1
                    reasons.append(f"tool description: {tool['name']}")
            
            if score > 0:
                matches.append((score, agent_id, agent['name'], reasons))
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x[0], reverse=True)
        
        if not matches:
            return f"No agents found matching '{query}'"
        
        result = f"# Agents matching '{query}'\n\n"
        for score, agent_id, name, reasons in matches:
            result += f"## {name} (`{agent_id}`)\n"
            result += f"**Match reasons**: {', '.join(reasons)}\n"
            result += f"**Relevance score**: {score}\n\n"
        
        return result.strip()
    
    def _find_compatible_agents(self, agent_id: str) -> str:
        """Find agents that work well with the given agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = self.agents[agent_id]
        result = f"# Agents Compatible with {agent['name']}\n\n"
        
        compatible = set()
        
        # Check capability graph for this agent's capabilities
        for cap in agent.get('capabilities', []):
            if cap in self.capability_graph:
                cap_info = self.capability_graph[cap]
                for comp in cap_info.get('complements', []):
                    # Find agents that have this complementary capability
                    for other_id, other_agent in self.agents.items():
                        if other_id != agent_id:
                            for other_cap in other_agent.get('capabilities', []):
                                if comp == other_cap:
                                    compatible.add((other_id, other_agent['name'], f"complementary capability: {comp}"))
        
        # Also check if other capabilities complement this agent's capabilities
        for other_cap, cap_info in self.capability_graph.items():
            for comp in cap_info.get('complements', []):
                if comp in agent.get('capabilities', []):
                    # Find agents with the other capability
                    for other_id, other_agent in self.agents.items():
                        if other_id != agent_id and other_cap in other_agent.get('capabilities', []):
                            compatible.add((other_id, other_agent['name'], f"provides {other_cap} which complements {comp}"))
        
        if not compatible:
            result += f"No specific compatibility information found for {agent['name']}.\n"
            result += "However, all agents can work together for different aspects of development."
        else:
            for other_id, other_name, reason in sorted(compatible):
                result += f"## {other_name} (`{other_id}`)\n"
                result += f"**Compatibility**: {reason}\n\n"
        
        return result.strip()
    
    # Control tool implementations
    def _suggest_agents(self, task: str, context: str) -> Dict[str, Any]:
        """Analyze task and suggest appropriate agents"""
        task_lower = task.lower()
        suggestions = []
        
        # Keywords for each agent type
        agent_keywords = {
            'qa': ['test', 'quality', 'bug', 'coverage', 'validation', 'verify', 'check'],
            'backend': ['api', 'database', 'server', 'endpoint', 'backend', 'rest', 'crud', 'data'],
            'architect': ['design', 'architecture', 'system', 'structure', 'scale', 'pattern', 'build']
        }
        
        # Score each agent based on task keywords
        for agent_id, keywords in agent_keywords.items():
            if agent_id not in self.agents:
                continue
                
            score = 0
            matched_keywords = []
            
            # Check each keyword
            for keyword in keywords:
                if keyword in task_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Check agent capabilities
            agent = self.agents[agent_id]
            for capability in agent.get('capabilities', []):
                if any(word in capability.lower() for word in task_lower.split()):
                    score += 0.5
                    matched_keywords.append(f"capability:{capability}")
            
            # Calculate confidence (0-1 scale)
            confidence = min(score / 3.0, 1.0)  # Normalize to max 1.0
            
            if confidence > 0.2:  # Only suggest if reasonably confident
                reason = f"Matches: {', '.join(matched_keywords[:3])}"
                if len(matched_keywords) > 3:
                    reason += f" (+{len(matched_keywords)-3} more)"
                
                suggestions.append({
                    'agent': agent_id,
                    'confidence': round(confidence, 2),
                    'reason': reason
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Generate suggestion ID and store
        suggestion_id = self.session.generate_suggestion_id()
        self.session.last_suggestion = {
            'id': suggestion_id,
            'task': task,
            'suggestions': suggestions
        }
        
        return {
            'suggestion_id': suggestion_id,
            'task': task,
            'suggestions': suggestions,
            'auto_approved': self.session.auto_approve
        }
    
    def _approve_agents(self, action: str, agents: List[str], suggestion_id: Optional[str]) -> Dict[str, Any]:
        """Handle agent approval/rejection"""
        if action == 'approve':
            # Validate agents exist
            for agent_id in agents:
                if agent_id not in self.agents:
                    raise ValueError(f"Unknown agent: {agent_id}")
                if agent_id not in self.session.block_agents:
                    self.session.approved_agents.add(agent_id)
                    self.session.rejected_agents.discard(agent_id)
                    
        elif action == 'reject':
            for agent_id in agents:
                self.session.rejected_agents.add(agent_id)
                self.session.approved_agents.discard(agent_id)
                
        elif action == 'approve_all':
            # Approve all from last suggestion
            if self.session.last_suggestion and self.session.last_suggestion.get('suggestions'):
                for suggestion in self.session.last_suggestion['suggestions']:
                    agent_id = suggestion['agent']
                    if agent_id not in self.session.block_agents:
                        self.session.approved_agents.add(agent_id)
                        self.session.rejected_agents.discard(agent_id)
                        
        elif action == 'reset':
            # Clear all approvals
            self.session.approved_agents.clear()
            self.session.rejected_agents.clear()
        
        else:
            raise ValueError(f"Invalid action: {action}")
        
        return {
            'approved': sorted(list(self.session.approved_agents)),
            'rejected': sorted(list(self.session.rejected_agents)),
            'session_status': {
                'auto_approve': self.session.auto_approve,
                'total_approved': len(self.session.approved_agents),
                'total_rejected': len(self.session.rejected_agents)
            }
        }
    
    def _set_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update session preferences"""
        if 'auto_approve' in preferences:
            self.session.auto_approve = preferences['auto_approve']
            
        if 'require_approval' in preferences:
            self.session.require_approval = set(preferences['require_approval'])
            
        if 'block_agents' in preferences:
            self.session.block_agents = set(preferences['block_agents'])
            # Remove blocked agents from approved list
            self.session.approved_agents -= self.session.block_agents
        
        return {
            'preferences': {
                'auto_approve': self.session.auto_approve,
                'require_approval': sorted(list(self.session.require_approval)),
                'block_agents': sorted(list(self.session.block_agents))
            },
            'session_status': {
                'approved_agents': sorted(list(self.session.approved_agents)),
                'total_approved': len(self.session.approved_agents)
            }
        }
    
    def _handle_workflow_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow orchestration tools"""
        try:
            if tool_name == 'ua_workflow_start':
                # Start a new workflow
                result = self.workflow_engine.start_workflow(
                    template_name=args['template'],
                    inputs=args['inputs'],
                    require_approval=args.get('require_approval', False),
                    session_state=self.session
                )
                
                # Handle approval required case
                if isinstance(result, dict) and result.get('status') == 'pending_approval':
                    return {
                        'content': [{
                            'type': 'text',
                            'text': json.dumps(result, indent=2)
                        }]
                    }
                
                # Normal workflow start
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps({
                            'workflow_id': result,
                            'status': 'started',
                            'template': args['template']
                        }, indent=2)
                    }]
                }
                
            elif tool_name == 'ua_workflow_status':
                # Get workflow status
                status = self.workflow_engine.get_status(args['workflow_id'])
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(status, indent=2)
                    }]
                }
                
            elif tool_name == 'ua_workflow_list':
                # List all workflows
                workflows = self.workflow_engine.list_workflows()
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps({
                            'workflows': workflows,
                            'total': len(workflows)
                        }, indent=2)
                    }]
                }
                
            elif tool_name == 'ua_workflow_templates':
                # List available templates
                templates = self.workflow_engine.template_registry.list_templates()
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps({
                            'templates': templates,
                            'total': len(templates)
                        }, indent=2)
                    }]
                }
                
            elif tool_name == 'ua_workflow_suggest':
                # Suggest workflows for a task
                suggestions = self.workflow_engine.suggest_workflow(args['task'])
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps({
                            'task': args['task'],
                            'suggestions': suggestions
                        }, indent=2)
                    }]
                }
                
            elif tool_name == 'ua_workflow_create':
                # Create custom workflow
                template_id = self.workflow_engine.create_custom_workflow(
                    name=args['name'],
                    description=args['description'],
                    steps=args['steps']
                )
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps({
                            'template_id': template_id,
                            'status': 'created',
                            'name': args['name'],
                            'steps': len(args['steps'])
                        }, indent=2)
                    }]
                }
                
            elif tool_name == 'ua_workflow_cancel':
                # Cancel workflow
                result = self.workflow_engine.cancel_workflow(
                    workflow_id=args['workflow_id'],
                    reason=args.get('reason')
                )
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(result, indent=2)
                    }]
                }
                
            elif tool_name == 'ua_workflow_dry_run':
                # Dry run workflow
                result = self.workflow_engine.dry_run_workflow(
                    template_name=args['template'],
                    inputs=args['inputs']
                )
                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(result, indent=2)
                    }]
                }
                
            else:
                raise ValueError(f"Unknown workflow tool: {tool_name}")
                
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
        except Exception as e:
            raise ValueError(f"Workflow error: {str(e)}")
    
    def _handle_deployment_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deployment tools"""
        if not self.deployment_mgr:
            raise ValueError("Deployment manager not available")
        
        try:
            if tool_name == 'ua_self_deploy':
                # Deploy changes
                dry_run = args.get('dry_run', False)
                result = self.deployment_mgr.deploy(dry_run=dry_run)
                
                if result['success']:
                    if result.get('message'):
                        response_text = result['message']
                    elif dry_run:
                        response_text = f"# Deployment Preview (Dry Run)\n\n"
                        response_text += f"**Files to update:** {len(result['files_updated'])}\n\n"
                        for file in result['files_updated']:
                            response_text += f"- {file}\n"
                    else:
                        response_text = f"# Deployment Successful! 🚀\n\n"
                        response_text += f"**Version:** {result['version']}\n"
                        response_text += f"**Files updated:** {len(result['files_updated'])}\n\n"
                        for file in result['files_updated']:
                            response_text += f"- ✓ {file}\n"
                else:
                    response_text = f"# Deployment Failed ❌\n\n"
                    response_text += f"**Error:** {result.get('error', 'Unknown error')}\n"
                    if result.get('rollback_performed'):
                        response_text += "\n⚠️ Automatic rollback was performed."
                
                return {
                    'content': [{
                        'type': 'text',
                        'text': response_text
                    }]
                }
            
            elif tool_name == 'ua_self_status':
                # Get deployment status
                status = self.deployment_mgr.get_status()
                
                response_text = f"# Deployment Status\n\n"
                response_text += f"**Current version:** {status['current_version']}\n"
                
                if status['last_deployment']:
                    last = status['last_deployment']
                    response_text += f"**Last deployment:** {last['deployed']} (v{last['version']})\n"
                    response_text += f"**Deployed from:** {last['deployed_from']}\n"
                    if last.get('git_commit'):
                        response_text += f"**Git commit:** {last['git_commit']}\n"
                
                if status['pending_changes']:
                    response_text += f"\n## Pending Changes ({len(status['pending_changes'])} files)\n\n"
                    for change in status['pending_changes']:
                        response_text += f"- {change['file']} ({change['action']})\n"
                else:
                    response_text += "\n✅ No pending changes - production is up to date!"
                
                if status['is_locked']:
                    lock_info = status['lock_info']
                    response_text += f"\n⚠️ **Deployment locked by:** {lock_info['user']}@{lock_info['hostname']}\n"
                    response_text += f"**Since:** {lock_info['locked_at']}\n"
                
                return {
                    'content': [{
                        'type': 'text',
                        'text': response_text
                    }]
                }
            
            elif tool_name == 'ua_self_rollback':
                # Rollback deployment
                version = args.get('version')
                
                # Get available backups
                from pathlib import Path
                backup_dir = Path(self.deployment_mgr.backup_dir)
                backups = sorted(backup_dir.glob("v*_*"), reverse=True)
                
                if not backups:
                    return {
                        'content': [{
                            'type': 'text',
                            'text': "❌ No backups available for rollback"
                        }]
                    }
                
                if version:
                    # Find specific version
                    backup_path = None
                    for backup in backups:
                        if backup.name.startswith(f"v{version}_"):
                            backup_path = backup
                            break
                    if not backup_path:
                        return {
                            'content': [{
                                'type': 'text',
                                'text': f"❌ No backup found for version {version}"
                            }]
                        }
                else:
                    # Use most recent backup
                    backup_path = backups[0]
                    version = backup_path.name.split('_')[0][1:]  # Extract version
                
                # Perform rollback
                self.deployment_mgr.rollback(backup_path)
                
                response_text = f"# Rollback Successful! ⏪\n\n"
                response_text += f"**Restored to version:** {version}\n"
                response_text += f"**From backup:** {backup_path.name}\n"
                
                return {
                    'content': [{
                        'type': 'text',
                        'text': response_text
                    }]
                }
            
            else:
                raise ValueError(f"Unknown deployment tool: {tool_name}")
                
        except Exception as e:
            return {
                'content': [{
                    'type': 'text',
                    'text': f"❌ Deployment operation failed: {str(e)}"
                }]
            }
    
    def _error_response(self, request_id: Any, message: str, code: int = -32603) -> Dict[str, Any]:
        """Generate error response with proper JSON-RPC error codes
        
        Error codes:
        -32700: Parse error
        -32600: Invalid Request
        -32601: Method not found
        -32602: Invalid params
        -32603: Internal error
        """
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': code,
                'message': message
            }
        }
    
    def run(self):
        """Run the MCP server using stdio transport"""
        logger.info("Starting Unified Agents MCP Server...")
        
        with debug_log("Server entering main loop, waiting for stdin..."):
            pass
        
        # Process requests from stdin
        try:
            for line in sys.stdin:
                try:
                    with debug_log(f"Received line: {line[:100]}..."):
                        pass
                    
                    # Parse JSON-RPC request
                    request = json.loads(line.strip())
                    logger.debug(f"Received request: {request}")
                    
                    with debug_log(f"Parsed request: {request.get('method')} (id: {request.get('id')})"):
                        pass
                    
                    # Handle the request
                    response = self.handle_request(request)
                    
                    with debug_log(f"Response ready: {json.dumps(response)[:100]}..."):
                        pass
                    
                    # Send response to stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                    
                    with debug_log("Response sent successfully"):
                        pass
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = self._error_response(None, "Parse error", -32700)
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    with debug_log(f"❌ Error processing request: {e}\n{traceback.format_exc()}"):
                        pass
                    error_response = self._error_response(None, "Internal error")
                    print(json.dumps(error_response))
                    sys.stdout.flush()
        
        except (EOFError, KeyboardInterrupt):
            with debug_log("Server shutting down (stdin closed or interrupted)"):
                pass
        except Exception as e:
            with debug_log(f"❌ Server crashed: {e}\n{traceback.format_exc()}"):
                pass
            raise


if __name__ == "__main__":
    try:
        with debug_log("Starting server initialization..."):
            pass
        server = UnifiedAgentServer()
        with debug_log("✅ Server initialized successfully"):
            pass
        with debug_log("Starting server.run()..."):
            pass
        
        # Heartbeat disabled after successful debugging
        # To enable heartbeat logging, set MCP_HEARTBEAT=true
        if os.environ.get('MCP_HEARTBEAT', '').lower() in ('true', '1', 'yes'):
            import threading
            def heartbeat():
                while True:
                    with debug_log(f"💓 Heartbeat: Server alive at {datetime.now()}"):
                        pass
                    threading.Event().wait(10)  # Wait 10 seconds
            
            heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
            heartbeat_thread.start()
        
        server.run()
    except Exception as e:
        with debug_log(f"❌ Server startup failed: {e}\n{traceback.format_exc()}"):
            pass
        # Re-raise to ensure proper exit code
        raise