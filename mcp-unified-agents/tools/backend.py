"""
Backend Agent tool handlers
"""
from typing import Dict, Any, List, Optional


def handle_backend_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Backend agent tools"""
    try:
        if tool_name == 'ua_backend_api_design':
            return _design_api(args['resource'], args['operations'])
        elif tool_name == 'ua_backend_optimize':
            return _optimize_code(args['code'], args.get('metrics'))
        else:
            raise ValueError(f"Unknown Backend tool: {tool_name}")
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")


def _design_api(resource: str, operations: List[str]) -> Dict[str, Any]:
    """Design REST API for a resource"""
    api_design = f"""REST API Design for: {resource}

**Resource:** /{resource.lower()}

**Endpoints:**
"""
    
    operation_specs = {
        'create': f"POST /{resource.lower()}\\n  Creates a new {resource}",
        'read': f"GET /{resource.lower()}/{{id}}\\n  Retrieves a specific {resource}",
        'update': f"PUT /{resource.lower()}/{{id}}\\n  Updates an existing {resource}",
        'delete': f"DELETE /{resource.lower()}/{{id}}\\n  Deletes a {resource}",
        'list': f"GET /{resource.lower()}\\n  Lists all {resource}s with pagination",
        'search': f"GET /{resource.lower()}/search\\n  Searches {resource}s"
    }
    
    for op in operations:
        if op in operation_specs:
            api_design += f"\\n{operation_specs[op]}"
    
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
    
    return {
        'content': [{
            'type': 'text',
            'text': api_design
        }]
    }


def _optimize_code(code: str, metrics: Optional[Dict[str, Any]]) -> Dict[str, Any]:
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
        suggestions += f"\\n**Current Metrics:**\\n"
        for key, value in metrics.items():
            suggestions += f"- {key}: {value}\\n"
    
    return {
        'content': [{
            'type': 'text',
            'text': suggestions
        }]
    }