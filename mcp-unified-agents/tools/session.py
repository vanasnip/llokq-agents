"""
Shared session state management
"""
from typing import Dict, Any, Set, Optional


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


# Global session instance - in production this would be per-connection
_session = SessionState()


def get_session() -> SessionState:
    """Get the current session state"""
    return _session