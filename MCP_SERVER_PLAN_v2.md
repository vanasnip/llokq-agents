# Unified Agents MCP Server Plan v2

## Overview

This updated plan incorporates feedback from the initial review, focusing on a lean MVP approach with phased rollout. The core insight is to start small (~400 lines) and build incrementally based on usage patterns.

## Key Changes from v1

1. **Phase 0.5 MVP** - Start with 3 agents instead of 15
2. **YAML/JSON Manifests** - Registry as data, not code
3. **Capability Graph** - Replace flat compatibility lists
4. **Stdio Transport** - Begin with simplest transport
5. **Phased Rollout** - Learn and iterate from real usage

## Phase 0.5: Lean MVP (~400 lines)

### Scope
- 3 representative agents (qa, backend, architect)
- Basic tool exposure via stdio
- Minimal configuration
- No complex orchestration

### Architecture

```
mcp-unified-agents/
├── server.py              # Main MCP server (~100 lines)
├── agents.yaml            # Agent manifest (~50 lines)
├── tools.py               # Tool implementations (~200 lines)
└── README.md              # Quick start (~50 lines)
```

### Agent Manifest (agents.yaml)

```yaml
version: "1.0"
agents:
  qa:
    name: "QA Agent"
    description: "Quality assurance and testing"
    capabilities:
      - test_generation
      - bug_analysis
      - coverage_analysis
    tools:
      - name: ua_qa_test_generate
        description: "Generate test cases"
        parameters:
          feature: string
          test_type: enum[unit, integration, e2e]
      - name: ua_qa_analyze_bug
        description: "Analyze bug root cause"
        parameters:
          description: string
          stacktrace?: string

  backend:
    name: "Backend Agent"
    description: "Backend development and APIs"
    capabilities:
      - api_design
      - database_design
      - performance_optimization
    tools:
      - name: ua_backend_api_design
        description: "Design REST API"
        parameters:
          resource: string
          operations: array[string]
      - name: ua_backend_optimize
        description: "Suggest optimizations"
        parameters:
          code: string
          metrics?: object

  architect:
    name: "System Architect"
    description: "System design and architecture"
    capabilities:
      - system_design
      - pattern_selection
      - dependency_analysis
    tools:
      - name: ua_architect_design
        description: "Design system architecture"
        parameters:
          requirements: string
          constraints?: array[string]
```

### Capability Graph

Instead of flat compatibility lists, use a capability graph:

```yaml
capability_graph:
  test_generation:
    requires: [code_understanding]
    provides: [quality_assurance]
    complements: [api_design, system_design]
    
  api_design:
    requires: [system_design]
    provides: [backend_implementation]
    complements: [test_generation, database_design]
    
  system_design:
    provides: [api_design, database_design]
    complements: [test_generation]
```

### Simple Server Implementation

```python
# server.py - Core MCP server
import json
import sys
from typing import Dict, Any
import yaml

class UnifiedAgentServer:
    def __init__(self):
        self.agents = self._load_agents()
        
    def _load_agents(self):
        with open('agents.yaml') as f:
            return yaml.safe_load(f)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        
        if method == 'tools/list':
            return self._list_tools()
        elif method == 'tools/call':
            return self._call_tool(request['params'])
        else:
            return {'error': f'Unknown method: {method}'}
    
    def _list_tools(self):
        tools = []
        for agent_id, agent in self.agents['agents'].items():
            for tool in agent['tools']:
                tools.append({
                    'name': tool['name'],
                    'description': f"[{agent['name']}] {tool['description']}",
                    'inputSchema': self._build_schema(tool['parameters'])
                })
        return {'tools': tools}
    
    def run(self):
        # Simple stdio transport
        for line in sys.stdin:
            request = json.loads(line)
            response = self.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
```

## Phase 1: User Control & Discovery

After MVP validation, add:

1. **Agent Discovery**
   ```yaml
   discovery_tools:
     - ua_agents_list
     - ua_agent_info
     - ua_capability_search
   ```

2. **User Control**
   ```yaml
   control_tools:
     - ua_suggest_agents
     - ua_approve_agents
     - ua_set_preferences
   ```

## Phase 2: Intelligent Orchestration

Based on usage patterns:

1. **Workflow Templates**
   - Common multi-agent patterns
   - User-defined workflows
   
2. **Context Sharing**
   - Agent memory
   - Shared workspace

## Phase 3: Advanced Features

After proven value:

1. **Multiple Transports**
   - HTTP/REST
   - WebSocket
   
2. **Plugin Architecture**
   - Custom agents
   - External tools

## Implementation Timeline

### Week 1: MVP
- [ ] Basic server.py
- [ ] Agent manifest
- [ ] 3 core agents
- [ ] Simple tools

### Week 2: Testing & Feedback
- [ ] User testing
- [ ] Performance baseline
- [ ] Usage patterns

### Week 3: Iteration
- [ ] Add most requested features
- [ ] Refine based on feedback
- [ ] Documentation

## Success Criteria

### MVP Success
- Successfully expose 3 agents via MCP
- < 500 lines of code
- < 50ms response time
- Works with Claude Code

### Learning Goals
- Which agents get used most?
- What workflows emerge?
- Where do users struggle?

## Key Differences from v1

1. **Start Small**: 3 agents vs 15
2. **Data-Driven**: YAML manifests vs code
3. **Graph-Based**: Capability relationships vs flat lists
4. **Iterative**: Learn from usage vs big-bang
5. **Simple Transport**: stdio vs complex options

## Migration Path

Users of the full system can:
1. Start with MVP for Claude Code
2. Use full CLI for complex tasks
3. Gradually migrate favorites to MCP

## Next Steps

1. Implement MVP server.py
2. Create agent manifests
3. Test with Claude Code
4. Gather feedback
5. Iterate based on usage

## Appendix: Full Vision

The complete vision from v1 remains valid as the long-term goal. This v2 plan provides a practical path to get there through validated learning and incremental development.

Key principles:
- Start with value, not features
- Let usage guide development
- Keep it simple until complexity is needed
- Measure and learn continuously

---

*This plan balances ambition with pragmatism, ensuring we deliver value quickly while building toward the comprehensive vision.*