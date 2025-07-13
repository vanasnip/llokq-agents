"""
Discourse-specific command definitions and parsing
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class DiscourseCommand:
    """Represents a parsed discourse command"""
    command: str
    content: Optional[str] = None
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


class DiscourseCommandParser:
    """Parser for discourse-specific commands"""
    
    COMMANDS = {
        'discuss': {
            'description': 'Start or continue a discussion on a topic',
            'usage': '/discuss <topic>',
            'example': '/discuss architecture patterns'
        },
        'question': {
            'description': 'Add a question to explore',
            'usage': '/question <your question>',
            'example': '/question How should we handle authentication?'
        },
        'insight': {
            'description': 'Record an insight or observation',
            'usage': '/insight <your insight> [--ref <references>]',
            'example': '/insight The current approach has scaling limitations --ref file1.py'
        },
        'decide': {
            'description': 'Make and record a decision',
            'usage': '/decide <decision>',
            'example': '/decide Use JWT tokens for authentication'
        },
        'summarize': {
            'description': 'Generate a summary of the conversation',
            'usage': '/summarize',
            'example': '/summarize'
        },
        'archive': {
            'description': 'Prepare the conversation for archival',
            'usage': '/archive',
            'example': '/archive'
        },
        'memory': {
            'description': 'Manage conversation memory',
            'usage': '/memory [--category <name>] [--action <view|categories>]',
            'example': '/memory --category decisions --action view'
        },
        'phase': {
            'description': 'Transition conversation phase',
            'usage': '/phase <exploration|analysis|synthesis|decision|archive>',
            'example': '/phase analysis'
        },
        'search': {
            'description': 'Search conversation entries',
            'usage': '/search <query> [--type <type>] [--category <cat>]',
            'example': '/search authentication --type decision'
        },
        'outline': {
            'description': 'Generate conversation outline',
            'usage': '/outline',
            'example': '/outline'
        },
        'context': {
            'description': 'Get current conversation context',
            'usage': '/context',
            'example': '/context'
        }
    }
    
    def parse(self, command_str: str) -> Optional[DiscourseCommand]:
        """Parse a discourse command string"""
        if not command_str.startswith('/'):
            return None
        
        # Extract command and content
        parts = command_str[1:].split(None, 1)
        if not parts:
            return None
        
        command = parts[0].lower()
        if command not in self.COMMANDS:
            return None
        
        content = parts[1] if len(parts) > 1 else ''
        
        # Parse options based on command
        options = self._parse_options(command, content)
        
        return DiscourseCommand(
            command=command,
            content=content,
            options=options
        )
    
    def _parse_options(self, command: str, content: str) -> Dict[str, Any]:
        """Parse command-specific options"""
        options = {}
        
        if command == 'discuss':
            options['topic'] = content.strip() if content else 'general discussion'
            
        elif command == 'question':
            options['question'] = content.strip()
            # Extract category if specified
            cat_match = re.search(r'--category\s+(\w+)', content)
            if cat_match:
                options['category'] = cat_match.group(1)
                options['question'] = re.sub(r'--category\s+\w+', '', content).strip()
                
        elif command == 'insight':
            # Extract references
            ref_match = re.search(r'--ref\s+(.+?)(?:\s+--|$)', content)
            if ref_match:
                options['references'] = [r.strip() for r in ref_match.group(1).split(',')]
                options['insight'] = re.sub(r'--ref\s+.+?(?:\s+--|$)', '', content).strip()
            else:
                options['insight'] = content.strip()
                
        elif command == 'decide':
            options['decision'] = content.strip()
            
        elif command == 'memory':
            # Parse category and action
            cat_match = re.search(r'--category\s+(\w+)', content)
            if cat_match:
                options['category'] = cat_match.group(1)
            
            action_match = re.search(r'--action\s+(\w+)', content)
            if action_match:
                options['action'] = action_match.group(1)
            else:
                options['action'] = 'view'
                
        elif command == 'phase':
            options['phase'] = content.strip().lower()
            
        elif command == 'search':
            # Extract search parameters
            type_match = re.search(r'--type\s+(\w+)', content)
            if type_match:
                options['type'] = type_match.group(1)
                
            cat_match = re.search(r'--category\s+(\w+)', content)
            if cat_match:
                options['category'] = cat_match.group(1)
                
            # Clean query
            query = content
            query = re.sub(r'--type\s+\w+', '', query)
            query = re.sub(r'--category\s+\w+', '', query)
            options['query'] = query.strip()
        
        return options
    
    def get_help(self, command: Optional[str] = None) -> str:
        """Get help text for commands"""
        if command and command in self.COMMANDS:
            cmd_info = self.COMMANDS[command]
            return f"""
{command}: {cmd_info['description']}

Usage: {cmd_info['usage']}
Example: {cmd_info['example']}
"""
        else:
            lines = ["Discourse Commands:"]
            for cmd, info in self.COMMANDS.items():
                lines.append(f"  /{cmd:<12} - {info['description']}")
            return "\n".join(lines)
    
    def validate_command(self, command: DiscourseCommand) -> Tuple[bool, Optional[str]]:
        """Validate a parsed command"""
        if command.command in ['question', 'insight', 'decide']:
            if not command.options.get(command.command):
                return False, f"{command.command} content cannot be empty"
                
        elif command.command == 'phase':
            valid_phases = ['exploration', 'analysis', 'synthesis', 'decision', 'archive']
            phase = command.options.get('phase')
            if phase not in valid_phases:
                return False, f"Invalid phase: {phase}. Must be one of: {', '.join(valid_phases)}"
                
        elif command.command == 'memory':
            valid_actions = ['view', 'categories']
            action = command.options.get('action', 'view')
            if action not in valid_actions:
                return False, f"Invalid action: {action}. Must be one of: {', '.join(valid_actions)}"
        
        return True, None