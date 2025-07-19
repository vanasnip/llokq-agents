"""
Tool handler registry for MCP Unified Agents
"""
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for agent tool handlers with pattern-based routing"""
    
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
        self._patterns: list[tuple[str, Callable]] = []
    
    def register_pattern(self, pattern: str, handler: Callable):
        """Register a handler for tools matching a pattern"""
        self._patterns.append((pattern, handler))
        logger.info(f"Registered handler for pattern: {pattern}")
    
    def register_handler(self, tool_name: str, handler: Callable):
        """Register a handler for a specific tool"""
        self._handlers[tool_name] = handler
        logger.info(f"Registered handler for tool: {tool_name}")
    
    def get_handler(self, tool_name: str) -> Optional[Callable]:
        """Get handler for a tool by exact match or pattern"""
        # First check exact matches
        if tool_name in self._handlers:
            return self._handlers[tool_name]
        
        # Then check patterns
        for pattern, handler in self._patterns:
            if tool_name.startswith(pattern):
                return handler
        
        return None
    
    def handle_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool call to appropriate handler"""
        handler = self.get_handler(tool_name)
        if not handler:
            raise ValueError(f"No handler registered for tool: {tool_name}")
        
        return handler(tool_name, args)


# Global registry instance
registry = ToolRegistry()


def register_all_handlers():
    """Register all tool handlers - called on startup"""
    # Import and register handlers as they're implemented
    try:
        from .qa import handle_qa_tool
        registry.register_pattern('ua_qa_', handle_qa_tool)
    except ImportError:
        logger.debug("QA tools not yet implemented")
    
    try:
        from .backend import handle_backend_tool
        registry.register_pattern('ua_backend_', handle_backend_tool)
    except ImportError:
        logger.debug("Backend tools not yet implemented")
    
    try:
        from .architect import handle_architect_tool
        registry.register_pattern('ua_architect_', handle_architect_tool)
    except ImportError:
        logger.debug("Architect tools not yet implemented")
    
    try:
        from .discourse import handle_discourse_tool
        registry.register_pattern('ua_discourse_', handle_discourse_tool)
    except ImportError as e:
        logger.debug(f"Discourse tools not yet implemented: {e}")
    
    # Register workflow and control tools with the main handler
    from .control import handle_control_tool
    from .workflow import handle_workflow_tool
    from .discovery import handle_discovery_tool
    
    registry.register_pattern('ua_agents_', handle_discovery_tool)
    registry.register_pattern('ua_agent_', handle_discovery_tool)
    registry.register_pattern('ua_capability_', handle_discovery_tool)
    registry.register_pattern('ua_workflow_', handle_workflow_tool)
    
    # Control tools need exact matches
    registry.register_handler('ua_suggest_agents', handle_control_tool)
    registry.register_handler('ua_approve_agents', handle_control_tool)
    registry.register_handler('ua_set_preferences', handle_control_tool)