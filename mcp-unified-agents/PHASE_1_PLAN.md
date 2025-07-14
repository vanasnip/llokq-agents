# MCP Server Phase 1: User Control & Discovery

## Overview

Enhance the MCP server with agent discovery tools and user control mechanisms, allowing Claude Code users to explore available agents and control their behavior.

## Phase 1.1: Agent Discovery Tools

### Tools to Implement

1. **ua_agents_list**
   - List all available agents with brief descriptions
   - Show agent categories and capabilities
   - Returns structured data for Claude to present

2. **ua_agent_info**
   - Get detailed information about a specific agent
   - Include personality, capabilities, compatible agents
   - Show available tools and their descriptions

3. **ua_capability_search**
   - Search agents by capability or domain
   - Find agents that can help with specific tasks
   - Support fuzzy matching for flexibility

4. **ua_agent_compatible**
   - Find agents that work well with a given agent
   - Based on capability graph relationships
   - Helps build multi-agent workflows

### Implementation Approach

- Add discovery tools to existing server.py
- Leverage capability graph for relationships
- Keep responses concise but informative
- Support both exact and fuzzy matching

## Phase 1.2: User Control Mechanisms

### Tools to Implement

1. **ua_suggest_agents**
   - Claude proposes agents for a task
   - Returns suggestion with rationale
   - Waits for user approval

2. **ua_approve_agents**
   - User approves/rejects agent suggestions
   - Can approve individual or all agents
   - Sets session preferences

3. **ua_set_preferences**
   - Configure session-wide agent preferences
   - Auto-approval settings
   - Agent filtering rules

### Control Flow

```
User: "I need to build a payment system"
↓
Claude: [calls ua_suggest_agents]
↓
Response: Suggests backend, qa, architect agents
↓
User: Approves selection
↓
Claude: [calls approved agent tools]
```

## Technical Implementation

### 1. Extend Tool Routing

```python
# Add to _handle_call_tool
elif tool_name.startswith('ua_agents_'):
    result = self._handle_discovery_tool(tool_name, arguments)
elif tool_name.startswith('ua_suggest_') or tool_name.startswith('ua_approve_'):
    result = self._handle_control_tool(tool_name, arguments)
```

### 2. Discovery Tool Handlers

```python
def _handle_discovery_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == 'ua_agents_list':
        return self._list_agents()
    elif tool_name == 'ua_agent_info':
        return self._get_agent_info(args['agent_id'])
    # etc...
```

### 3. Session State

```python
class SessionPreferences:
    def __init__(self):
        self.auto_approve = False
        self.approved_agents = set()
        self.rejected_agents = set()
```

## Benefits

1. **Discovery**: Users can explore what agents do
2. **Control**: Users maintain agency over agent selection
3. **Transparency**: Clear about which agents are active
4. **Flexibility**: Session preferences reduce friction

## Success Metrics

- Users can discover relevant agents easily
- Approval flow feels natural, not intrusive
- Session preferences reduce repetitive approvals
- Compatible agent suggestions improve workflows

## Timeline

- Phase 1.1 (Discovery): ~2 hours
- Phase 1.2 (Control): ~2 hours
- Testing & Polish: ~1 hour

Total: ~5 hours for full Phase 1 implementation