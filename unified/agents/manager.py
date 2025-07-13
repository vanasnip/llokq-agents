"""
Agent Manager - Handles loading, activation, and coordination of agents
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set
from unified.agents.schema import Agent, AgentCategory
from unified.core.event_bus import get_event_bus, Event, EventType
from unified.core.schema_version import get_schema_validator, SchemaType
import uuid


class AgentManager:
    """Manages all agents in the unified system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".claude" / "agents.yml"
        self.agents: Dict[str, Agent] = {}
        self.active_agents: Set[str] = set()
        self.event_bus = get_event_bus()
        self.schema_validator = get_schema_validator()
        self._load_agents()
    
    def _load_agents(self) -> None:
        """Load all agent definitions from configuration with schema migration"""
        if not self.config_path.exists():
            self._create_default_config()
        
        # Load with schema migration
        config = self.schema_validator.load_config_with_migration(
            self.config_path,
            SchemaType.AGENT
        )
        
        for agent_name, agent_data in config.get('agents', {}).items():
            # Skip disabled agents
            if not agent_data.get('enabled', True):
                continue
                
            agent = Agent.from_dict(agent_data)
            self.agents[agent_name] = agent
    
    def _create_default_config(self) -> None:
        """Create default configuration with sample agents"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            'agents': {
                'architect': {
                    'name': 'architect',
                    'command': '--architect',
                    'category': 'architecture',
                    'identity': 'System Architecture Specialist | Distributed systems expert',
                    'core_belief': 'Architecture is the foundation of maintainable, scalable systems',
                    'primary_question': 'What patterns and structures best serve our goals?',
                    'decision_framework': 'Simplicity > complexity | Proven > novel | Maintainable > clever',
                    'risk_profile': 'balanced',
                    'success_metrics': 'Clean interfaces | Minimal coupling | Clear boundaries',
                    'communication_style': 'Visual diagrams | Clear abstractions | Technical precision',
                    'problem_solving': 'Top-down design | Pattern matching | Trade-off analysis',
                    'mcp_preferences': ['filesystem', 'memory', 'sequential'],
                    'focus_areas': ['System design', 'API architecture', 'Data modeling'],
                    'primary_phases': [2, 4],
                    'support_phases': [1, 3, 5]
                }
            }
        }
        
        # Add schema version
        default_config = self.schema_validator.add_version_to_config(
            default_config,
            SchemaType.AGENT
        )
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def get_agents_by_category(self, category: AgentCategory) -> List[Agent]:
        """Get all agents in a specific category"""
        return [a for a in self.agents.values() if a.category == category]
    
    def get_agents_by_phase(self, phase: int) -> Dict[str, List[Agent]]:
        """Get primary and support agents for a specific phase"""
        primary = [a for a in self.agents.values() if phase in a.primary_phases]
        support = [a for a in self.agents.values() if phase in a.support_phases]
        return {'primary': primary, 'support': support}
    
    def activate_agent(self, name: str) -> Agent:
        """Activate an agent and return its configuration"""
        agent = self.get_agent(name)
        if not agent:
            raise ValueError(f"Agent '{name}' not found")
        
        self.active_agents.add(name)
        
        # Publish activation event
        self.event_bus.publish(Event(
            type=EventType.AGENT_ACTIVATED,
            data={
                "agent_name": name,
                "agent": agent.to_dict(),
                "active_agents": list(self.active_agents)
            },
            source="AgentManager",
            correlation_id=str(uuid.uuid4())
        ))
        
        return agent
    
    def deactivate_agent(self, name: str) -> None:
        """Deactivate an agent"""
        if name in self.active_agents:
            self.active_agents.discard(name)
            
            # Publish deactivation event
            self.event_bus.publish(Event(
                type=EventType.AGENT_DEACTIVATED,
                data={
                    "agent_name": name,
                    "active_agents": list(self.active_agents)
                },
                source="AgentManager",
                correlation_id=str(uuid.uuid4())
            ))
    
    def get_active_agents(self) -> List[Agent]:
        """Get all currently active agents"""
        return [self.agents[name] for name in self.active_agents]
    
    def handoff(self, from_agent: str, to_agent: str) -> Dict[str, str]:
        """Perform handoff between agents"""
        source = self.get_agent(from_agent)
        target = self.get_agent(to_agent)
        
        if not source or not target:
            raise ValueError("Invalid agent names for handoff")
        
        # Create correlation ID for related events
        correlation_id = str(uuid.uuid4())
        
        # Deactivate source, activate target
        self.deactivate_agent(from_agent)
        self.activate_agent(to_agent)
        
        # Get handoff protocol
        protocol = source.handoff_protocols.get(to_agent, {
            'action': 'standard_handoff',
            'message': f'Transitioning from {from_agent} to {to_agent}'
        })
        
        # Publish handoff event
        self.event_bus.publish(Event(
            type=EventType.AGENT_ACTIVATED,  # Using existing event type
            data={
                "handoff": True,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "protocol": protocol
            },
            source="AgentManager",
            correlation_id=correlation_id
        ))
        
        return protocol
    
    def validate_agent_compatibility(self, agents: List[str]) -> bool:
        """Check if multiple agents can work together"""
        for agent_name in agents:
            agent = self.get_agent(agent_name)
            if not agent:
                return False
            
            # Check if other agents are in compatible list
            for other in agents:
                if other != agent_name and other not in agent.compatible_agents:
                    # Allow if not explicitly listed (assume compatible by default)
                    pass
        
        return True