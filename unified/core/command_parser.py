"""
Command Parser - Interprets user commands and applies agent context
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from unified.agents import Agent, AgentManager


@dataclass
class ParsedCommand:
    """Represents a parsed command with all its components"""
    base_command: str
    agents: List[str]
    phase: Optional[int]
    options: Dict[str, str]
    raw_input: str


class CommandParser:
    """Parses and interprets commands with agent awareness"""
    
    COMMANDS = {
        'code': 'Execute coding tasks',
        'design': 'Design and architecture tasks',
        'analyze': 'Analysis and investigation',
        'test': 'Testing and quality assurance',
        'deploy': 'Deployment and operations',
        'phase': 'D3P phase management',
        'workflow': 'Workflow orchestration',
        'team': 'Multi-agent coordination',
        'agent': 'Agent management'
    }
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
    
    def parse(self, command: str) -> ParsedCommand:
        """Parse a command string into structured components"""
        # Extract base command
        base_match = re.match(r'^/(\w+)', command)
        if not base_match:
            raise ValueError(f"Invalid command format: {command}")
        
        base_command = base_match.group(1)
        if base_command not in self.COMMANDS:
            raise ValueError(f"Unknown command: {base_command}")
        
        # Extract agents (e.g., --backend, --frontend)
        agents = re.findall(r'--(\w+)', command)
        
        # Extract phase if specified
        phase_match = re.search(r'--phase\s+(\d+)', command)
        phase = int(phase_match.group(1)) if phase_match else None
        
        # Extract other options
        options = {}
        
        # Extract workflow type
        if base_command == 'workflow':
            workflow_match = re.search(r'/workflow\s+(\w+)', command)
            if workflow_match:
                options['workflow_type'] = workflow_match.group(1)
        
        # Extract goto phase
        if base_command == 'phase':
            goto_match = re.search(r'--goto\s+(\d+)', command)
            if goto_match:
                options['goto'] = goto_match.group(1)
        
        # Extract team operations
        if base_command == 'team':
            activate_match = re.search(r'--activate\s+"([^"]+)"', command)
            if activate_match:
                options['activate'] = activate_match.group(1).split(',')
        
        return ParsedCommand(
            base_command=base_command,
            agents=agents,
            phase=phase,
            options=options,
            raw_input=command
        )
    
    def validate_agents(self, agent_names: List[str]) -> Tuple[bool, List[str]]:
        """Validate that all specified agents exist"""
        invalid_agents = []
        
        for agent_name in agent_names:
            if not self.agent_manager.get_agent(agent_name):
                invalid_agents.append(agent_name)
        
        return len(invalid_agents) == 0, invalid_agents
    
    def apply_agent_context(self, command: ParsedCommand) -> Dict[str, Any]:
        """Apply agent personality and preferences to command execution"""
        context = {
            'command': command.base_command,
            'agents': [],
            'mcp_preferences': set(),
            'communication_styles': [],
            'decision_frameworks': []
        }
        
        # Activate and collect agent contexts
        for agent_name in command.agents:
            agent = self.agent_manager.activate_agent(agent_name)
            context['agents'].append(agent)
            context['mcp_preferences'].update(agent.mcp_preferences)
            context['communication_styles'].append(agent.communication_style)
            context['decision_frameworks'].append(agent.decision_framework)
        
        # Add phase-specific agents if phase is specified
        if command.phase:
            phase_agents = self.agent_manager.get_agents_by_phase(command.phase)
            for agent in phase_agents['primary']:
                if agent.name not in command.agents:
                    context['agents'].append(agent)
                    context['mcp_preferences'].update(agent.mcp_preferences)
        
        return context
    
    def format_help(self) -> str:
        """Generate help text for available commands"""
        help_text = "Available Commands:\n\n"
        
        for cmd, desc in self.COMMANDS.items():
            help_text += f"  /{cmd:<12} - {desc}\n"
        
        help_text += "\nAgent Activation:\n"
        help_text += "  Use --<agent> to activate specific agents\n"
        help_text += "  Example: /code --backend --frontend\n"
        
        help_text += "\nAvailable Agents:\n"
        for agent in self.agent_manager.agents.values():
            help_text += f"  {agent.command:<15} - {agent.identity.split('|')[0].strip()}\n"
        
        return help_text