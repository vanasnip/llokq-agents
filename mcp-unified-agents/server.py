#!/usr/bin/env python3
"""
Unified Agents MCP Server - Lean MVP
Exposes 3 core agents (QA, Backend, Architect) via Model Context Protocol
"""
import json
import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. Install with: pip install PyYAML", file=sys.stderr)
    # Fallback to JSON format
    yaml = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UnifiedAgentServer:
    """MCP server that exposes unified agents as tools"""
    
    def __init__(self, manifest_path: str = "agents.yaml"):
        self.manifest_path = Path(manifest_path)
        self.agents = self._load_agents()
        self.capability_graph = self._load_capability_graph()
        
    def _load_agents(self) -> Dict[str, Any]:
        """Load agent manifest from YAML or JSON"""
        try:
            # Try YAML first if available
            if yaml and self.manifest_path.suffix == '.yaml':
                with open(self.manifest_path) as f:
                    data = yaml.safe_load(f)
                    return data.get('agents', {})
            else:
                # Fallback to JSON
                json_path = self.manifest_path.with_suffix('.json')
                with open(json_path) as f:
                    data = json.load(f)
                    return data.get('agents', {})
        except Exception as e:
            logger.error(f"Failed to load agents manifest: {e}")
            return {}
    
    def _load_capability_graph(self) -> Dict[str, Any]:
        """Load capability graph from manifest"""
        try:
            # Try YAML first if available
            if yaml and self.manifest_path.suffix == '.yaml':
                with open(self.manifest_path) as f:
                    data = yaml.safe_load(f)
                    return data.get('capability_graph', {})
            else:
                # Fallback to JSON
                json_path = self.manifest_path.with_suffix('.json')
                with open(json_path) as f:
                    data = json.load(f)
                    return data.get('capability_graph', {})
        except Exception:
            return {}
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        method = request.get('method')
        request_id = request.get('id')
        
        try:
            if method == 'initialize':
                return self._handle_initialize(request_id)
            elif method == 'tools/list':
                return self._handle_list_tools(request_id)
            elif method == 'tools/call':
                return self._handle_call_tool(request_id, request.get('params', {}))
            else:
                return self._error_response(request_id, f"Unknown method: {method}")
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._error_response(request_id, str(e))
    
    def _handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'protocolVersion': '0.1.0',
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
    
    def _handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """List all available tools"""
        tools = []
        
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
        
        # Route to appropriate handler
        if tool_name.startswith('ua_qa_'):
            result = self._handle_qa_tool(tool_name, arguments)
        elif tool_name.startswith('ua_backend_'):
            result = self._handle_backend_tool(tool_name, arguments)
        elif tool_name.startswith('ua_architect_'):
            result = self._handle_architect_tool(tool_name, arguments)
        else:
            return self._error_response(request_id, f"Unknown tool: {tool_name}")
        
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': result
        }
    
    def _handle_qa_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle QA agent tools"""
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
    
    def _handle_backend_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Backend agent tools"""
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
    
    def _handle_architect_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Architect agent tools"""
        if tool_name == 'ua_architect_design':
            return {
                'content': [{
                    'type': 'text',
                    'text': self._design_system(args['requirements'], args.get('constraints', []))
                }]
            }
        else:
            raise ValueError(f"Unknown Architect tool: {tool_name}")
    
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
    
    def _error_response(self, request_id: Any, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32603,
                'message': message
            }
        }
    
    def run(self):
        """Run the MCP server using stdio transport"""
        logger.info("Starting Unified Agents MCP Server...")
        
        # Process requests from stdin
        for line in sys.stdin:
            try:
                # Parse JSON-RPC request
                request = json.loads(line.strip())
                logger.debug(f"Received request: {request}")
                
                # Handle the request
                response = self.handle_request(request)
                
                # Send response to stdout
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = self._error_response(None, "Parse error")
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                error_response = self._error_response(None, "Internal error")
                print(json.dumps(error_response))
                sys.stdout.flush()


if __name__ == "__main__":
    server = UnifiedAgentServer()
    server.run()