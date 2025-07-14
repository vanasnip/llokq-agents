"""
Agent Schema Definition for Unified D3P-SuperClaude System
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class RiskProfile(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ZERO_TOLERANCE = "zero_tolerance"


class AgentCategory(Enum):
    DESIGN = "design"
    DEVELOPMENT = "development"
    OPERATIONS = "operations"
    QUALITY = "quality"
    ARCHITECTURE = "architecture"
    DISCOURSE = "discourse"  # conversational facilitator (read-only)


@dataclass
class Agent:
    """Unified agent definition combining D3P richness with SuperClaude simplicity"""
    
    # Core identification
    name: str
    command: str  # e.g., "--backend", "--aura"
    category: AgentCategory
    
    # Rich D3P characteristics
    identity: str
    core_belief: str
    primary_question: str
    decision_framework: str
    risk_profile: RiskProfile
    success_metrics: str
    communication_style: str
    problem_solving: str
    
    # Technical preferences
    mcp_preferences: List[str] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)
    
    # Operational details
    values: Optional[str] = None
    limitations: Optional[str] = None
    compatible_agents: List[str] = field(default_factory=list)
    handoff_protocols: Dict[str, str] = field(default_factory=dict)
    
    # Phase integration
    primary_phases: List[int] = field(default_factory=list)
    support_phases: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for YAML serialization"""
        return {
            "name": self.name,
            "command": self.command,
            "category": self.category.value,
            "identity": self.identity,
            "core_belief": self.core_belief,
            "primary_question": self.primary_question,
            "decision_framework": self.decision_framework,
            "risk_profile": self.risk_profile,
            "success_metrics": self.success_metrics,
            "communication_style": self.communication_style,
            "problem_solving": self.problem_solving,
            "mcp_preferences": self.mcp_preferences,
            "focus_areas": self.focus_areas,
            "values": self.values,
            "limitations": self.limitations,
            "compatible_agents": self.compatible_agents,
            "handoff_protocols": self.handoff_protocols,
            "primary_phases": self.primary_phases,
            "support_phases": self.support_phases,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create agent from dictionary"""
        data["category"] = AgentCategory(data["category"])
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"Agent({self.name}, command={self.command}, category={self.category.value})"