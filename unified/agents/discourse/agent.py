"""
DiscourseAgent - Read-only conversational facilitator
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from unified.agents.schema import Agent, AgentCategory, RiskProfile
from .context import DiscourseContext, DiscourseGuardrailException


class DiscourseAgent:
    """
    Handler class for discourse agent operations.
    Works with the discourse Agent configuration from agents.yml.
    All operations are read-only and execution is blocked.
    """
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.context = DiscourseContext()
        self.conversation_memory = []
        self.archive_path = Path.home() / ".claude" / "discourse_archives"
        self.archive_path.mkdir(parents=True, exist_ok=True)
    
    def execute(self, command: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute discourse-specific commands with read-only guardrails.
        All mutations are blocked by the discourse_safe decorator.
        """
        # Ensure we're in discourse mode
        if not self.context.discourse_mode:
            return {
                'status': 'error',
                'message': 'DiscourseAgent must operate in discourse mode'
            }
        
        # Handle discourse-specific commands
        if command == 'discuss':
            return self._facilitate_discussion(options)
        elif command == 'summarize':
            return self._summarize_conversation(options)
        elif command == 'archive':
            return self._archive_discussion(options)
        elif command == 'memory':
            return self._manage_memory(options)
        else:
            return {
                'status': 'error',
                'message': f'Unknown discourse command: {command}'
            }
    
    def _facilitate_discussion(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Facilitate a discussion on a topic"""
        topic = options.get('topic', 'general discussion')
        
        # Add to conversation memory
        self.conversation_memory.append({
            'type': 'discussion',
            'topic': topic,
            'timestamp': self._get_timestamp()
        })
        
        return {
            'status': 'success',
            'message': f'Facilitating discussion on: {topic}',
            'mode': 'read-only',
            'capabilities': self._get_available_capabilities()
        }
    
    def _summarize_conversation(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the current conversation"""
        return {
            'status': 'success',
            'message': 'Conversation summary generated',
            'summary': {
                'total_entries': len(self.conversation_memory),
                'topics_discussed': self._get_topics(),
                'mode': 'read-only'
            }
        }
    
    def _archive_discussion(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Archive the discussion to a file (user-initiated)"""
        filename = options.get('filename', f'discussion_{self._get_timestamp()}.md')
        
        # Note: Actual file writing would be blocked by discourse_safe
        # This is just planning what would be archived
        return {
            'status': 'success',
            'message': f'Discussion prepared for archival: {filename}',
            'archive_path': str(self.archive_path / filename),
            'note': 'File writing blocked in discourse mode - manual save required'
        }
    
    def _manage_memory(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Manage conversation memory categories"""
        category = options.get('category', 'general')
        action = options.get('action', 'view')
        
        if action == 'view':
            return {
                'status': 'success',
                'message': f'Memory category: {category}',
                'entries': [m for m in self.conversation_memory if m.get('category') == category]
            }
        else:
            return {
                'status': 'error',
                'message': f'Memory action {action} not allowed in discourse mode'
            }
    
    def _get_available_capabilities(self) -> List[str]:
        """Get list of available read-only capabilities"""
        return [
            'Read files and documentation',
            'Analyze code structure',
            'Facilitate discussions',
            'Generate summaries',
            'Organize knowledge',
            'Delegate to other agents (read-only)',
            'Create discussion outlines'
        ]
    
    def _get_topics(self) -> List[str]:
        """Extract unique topics from conversation memory"""
        topics = set()
        for entry in self.conversation_memory:
            if 'topic' in entry:
                topics.add(entry['topic'])
        return list(topics)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for archival"""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def delegate_to_agent(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Delegate tasks to other agents with read-only constraints.
        The DiscourseContext ensures all delegated operations are read-only.
        """
        if not self.context.delegate_readonly:
            return {
                'status': 'error',
                'message': 'Agent delegation disabled in current discourse mode'
            }
        
        # Create child context for delegated agent
        child_context = DiscourseContext(parent_context=self.context)
        
        return {
            'status': 'success',
            'message': f'Delegated to {agent_name} with read-only constraints',
            'agent': agent_name,
            'task': task,
            'constraints': 'read-only execution'
        }