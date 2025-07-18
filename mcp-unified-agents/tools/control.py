"""
User control tool handlers
"""
from typing import Dict, Any, List, Optional
import json
import logging
from pathlib import Path
from .session import get_session

logger = logging.getLogger(__name__)


def handle_control_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user control tools"""
    try:
        if tool_name == 'ua_suggest_agents':
            return {
                'content': [{
                    'type': 'text',
                    'text': json.dumps(
                        _suggest_agents(args['task'], args.get('context', '')), 
                        indent=2
                    )
                }]
            }
        elif tool_name == 'ua_approve_agents':
            return {
                'content': [{
                    'type': 'text',
                    'text': json.dumps(
                        _approve_agents(
                            args['action'],
                            args.get('agents', []),
                            args.get('suggestion_id')
                        ), 
                        indent=2
                    )
                }]
            }
        elif tool_name == 'ua_set_preferences':
            return {
                'content': [{
                    'type': 'text',
                    'text': json.dumps(
                        _set_preferences(args), 
                        indent=2
                    )
                }]
            }
        else:
            raise ValueError(f"Unknown control tool: {tool_name}")
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")


def _suggest_agents(task: str, context: str) -> Dict[str, Any]:
    """Analyze task and suggest appropriate agents"""
    # Load agents manifest
    manifest_path = Path(__file__).parent.parent / "agents.json"
    try:
        with open(manifest_path) as f:
            data = json.load(f)
            agents = data.get('agents', {})
    except Exception as e:
        logger.error(f"Failed to load agents manifest: {e}")
        agents = {}
    
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
        if agent_id not in agents:
            continue
            
        score = 0
        matched_keywords = []
        
        # Check each keyword
        for keyword in keywords:
            if keyword in task_lower:
                score += 1
                matched_keywords.append(keyword)
        
        # Check agent capabilities
        agent = agents[agent_id]
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
    session = get_session()
    suggestion_id = session.generate_suggestion_id()
    session.last_suggestion = {
        'id': suggestion_id,
        'task': task,
        'suggestions': suggestions
    }
    
    return {
        'suggestion_id': suggestion_id,
        'task': task,
        'suggestions': suggestions,
        'auto_approved': session.auto_approve
    }


def _approve_agents(action: str, agents: List[str], suggestion_id: Optional[str]) -> Dict[str, Any]:
    """Handle agent approval/rejection"""
    # Load agents manifest to validate
    manifest_path = Path(__file__).parent.parent / "agents.json"
    try:
        with open(manifest_path) as f:
            data = json.load(f)
            available_agents = data.get('agents', {})
    except Exception as e:
        logger.error(f"Failed to load agents manifest: {e}")
        available_agents = {}
    
    session = get_session()
    
    if action == 'approve':
        # Validate agents exist
        for agent_id in agents:
            if agent_id not in available_agents:
                raise ValueError(f"Unknown agent: {agent_id}")
            if agent_id not in session.block_agents:
                session.approved_agents.add(agent_id)
                session.rejected_agents.discard(agent_id)
                
    elif action == 'reject':
        for agent_id in agents:
            session.rejected_agents.add(agent_id)
            session.approved_agents.discard(agent_id)
            
    elif action == 'approve_all':
        # Approve all from last suggestion
        if session.last_suggestion and session.last_suggestion.get('suggestions'):
            for suggestion in session.last_suggestion['suggestions']:
                agent_id = suggestion['agent']
                if agent_id not in session.block_agents:
                    session.approved_agents.add(agent_id)
                    session.rejected_agents.discard(agent_id)
                    
    elif action == 'reset':
        # Clear all approvals
        session.approved_agents.clear()
        session.rejected_agents.clear()
    
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return {
        'approved': sorted(list(session.approved_agents)),
        'rejected': sorted(list(session.rejected_agents)),
        'session_status': {
            'auto_approve': session.auto_approve,
            'total_approved': len(session.approved_agents),
            'total_rejected': len(session.rejected_agents)
        }
    }


def _set_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Update session preferences"""
    session = get_session()
    
    if 'auto_approve' in preferences:
        session.auto_approve = preferences['auto_approve']
        
    if 'require_approval' in preferences:
        session.require_approval = set(preferences['require_approval'])
        
    if 'block_agents' in preferences:
        session.block_agents = set(preferences['block_agents'])
        # Remove blocked agents from approved list
        session.approved_agents -= session.block_agents
    
    return {
        'preferences': {
            'auto_approve': session.auto_approve,
            'require_approval': sorted(list(session.require_approval)),
            'block_agents': sorted(list(session.block_agents))
        },
        'session_status': {
            'approved_agents': sorted(list(session.approved_agents)),
            'total_approved': len(session.approved_agents)
        }
    }