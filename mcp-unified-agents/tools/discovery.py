"""
Agent discovery tool handlers
"""
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


def handle_discovery_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle agent discovery tools"""
    # For now, we'll use the existing server methods
    # In a future refactor, these methods should be moved to this module
    # to properly separate concerns
    
    # Import and load agents directly here to avoid circular imports
    import json
    from pathlib import Path
    
    manifest_path = Path(__file__).parent.parent / "agents.json"
    
    try:
        with open(manifest_path) as f:
            data = json.load(f)
            agents = data.get('agents', {})
            capability_graph = data.get('capability_graph', {})
    except Exception as e:
        logger.error(f"Failed to load agents manifest: {e}")
        agents = {}
        capability_graph = {}
    
    try:
        if tool_name == 'ua_agents_list':
            return {
                'content': [{
                    'type': 'text',
                    'text': _list_agents(agents)
                }]
            }
        elif tool_name == 'ua_agent_info':
            return {
                'content': [{
                    'type': 'text',
                    'text': _get_agent_info(args['agent_id'], agents, capability_graph)
                }]
            }
        elif tool_name == 'ua_capability_search':
            return {
                'content': [{
                    'type': 'text',
                    'text': _search_by_capability(args['query'], agents)
                }]
            }
        elif tool_name == 'ua_agent_compatible':
            return {
                'content': [{
                    'type': 'text',
                    'text': _find_compatible_agents(args['agent_id'], agents, capability_graph)
                }]
            }
        else:
            raise ValueError(f"Unknown discovery tool: {tool_name}")
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")


def _list_agents(agents: Dict[str, Any]) -> str:
    """List all available agents"""
    result = "# Available Agents\n\n"
    
    for agent_id, agent in agents.items():
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


def _get_agent_info(agent_id: str, agents: Dict[str, Any], capability_graph: Dict[str, Any]) -> str:
    """Get detailed information about a specific agent"""
    if agent_id not in agents:
        raise ValueError(f"Agent not found: {agent_id}")
    
    agent = agents[agent_id]
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
    if agent_id in capability_graph:
        result += "## Relationships\n"
        cap_info = capability_graph[agent_id]
        
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


def _search_by_capability(query: str, agents: Dict[str, Any]) -> str:
    """Search agents by capability or domain"""
    query_lower = query.lower()
    matches = []
    
    # Search in agent capabilities
    for agent_id, agent in agents.items():
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


def _find_compatible_agents(agent_id: str, agents: Dict[str, Any], capability_graph: Dict[str, Any]) -> str:
    """Find agents that work well with the given agent"""
    if agent_id not in agents:
        raise ValueError(f"Agent not found: {agent_id}")
    
    agent = agents[agent_id]
    result = f"# Agents Compatible with {agent['name']}\n\n"
    
    compatible = set()
    
    # Check capability graph for this agent's capabilities
    for cap in agent.get('capabilities', []):
        if cap in capability_graph:
            cap_info = capability_graph[cap]
            for comp in cap_info.get('complements', []):
                # Find agents that have this complementary capability
                for other_id, other_agent in agents.items():
                    if other_id != agent_id:
                        for other_cap in other_agent.get('capabilities', []):
                            if comp == other_cap:
                                compatible.add((other_id, other_agent['name'], f"complementary capability: {comp}"))
    
    # Also check if other capabilities complement this agent's capabilities
    for other_cap, cap_info in capability_graph.items():
        for comp in cap_info.get('complements', []):
            if comp in agent.get('capabilities', []):
                # Find agents with the other capability
                for other_id, other_agent in agents.items():
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