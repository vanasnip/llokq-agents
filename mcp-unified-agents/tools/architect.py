"""
System Architect tool handlers
"""
from typing import Dict, Any, List


def handle_architect_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Architect agent tools"""
    try:
        if tool_name == 'ua_architect_design':
            return _design_system(args['requirements'], args.get('constraints', []))
        else:
            raise ValueError(f"Unknown Architect tool: {tool_name}")
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")


def _design_system(requirements: str, constraints: List[str]) -> Dict[str, Any]:
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
        design += "\\n**Constraints Addressed:**\\n"
        for constraint in constraints:
            design += f"- {constraint}: Addressed by...\\n"
    
    design += """
**Scalability Plan:**
- Horizontal scaling for API/Backend
- Read replicas for database
- CDN for static assets
- Message queue for async tasks
"""
    
    return {
        'content': [{
            'type': 'text',
            'text': design
        }]
    }