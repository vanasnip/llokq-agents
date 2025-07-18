"""
Workflow orchestration tool handlers
"""
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


def handle_workflow_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle workflow orchestration tools"""
    # Import here to avoid circular imports
    from ..server import UnifiedAgentServer
    
    # This is a bit of a hack - in production you'd pass the server instance properly
    # For now, we'll create a temporary instance just to access the methods
    temp_server = UnifiedAgentServer()
    
    try:
        result = temp_server._handle_workflow_tool(tool_name, args)
        return result
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")
    except Exception as e:
        raise ValueError(f"Workflow error: {str(e)}")