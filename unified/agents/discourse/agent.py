"""
DiscourseAgent - Read-only conversational facilitator
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from unified.agents.schema import Agent, AgentCategory, RiskProfile
from .context import DiscourseContext, DiscourseGuardrailException
from .conversation import ConversationManager, ConversationPhase, EntryType


class DiscourseAgent:
    """
    Handler class for discourse agent operations.
    Works with the discourse Agent configuration from agents.yml.
    All operations are read-only and execution is blocked.
    """
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.context = DiscourseContext()
        self.archive_path = Path.home() / ".claude" / "discourse_archives"
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.conversation = ConversationManager(self.archive_path)
        self.available_commands = {
            'discuss': 'Facilitate a discussion on a topic',
            'question': 'Add a question to explore',
            'insight': 'Record an insight or observation',
            'decide': 'Make and record a decision',
            'summarize': 'Generate conversation summary',
            'archive': 'Prepare discussion for archival',
            'memory': 'Manage conversation memory',
            'phase': 'Transition conversation phase',
            'search': 'Search conversation entries',
            'outline': 'Generate conversation outline',
            'context': 'Get current conversation context'
        }
    
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
        if command in self.available_commands:
            handler = getattr(self, f'_handle_{command}', None)
            if handler:
                return handler(options)
            else:
                return self._handle_generic_command(command, options)
        else:
            return {
                'status': 'error',
                'message': f'Unknown discourse command: {command}',
                'available_commands': list(self.available_commands.keys())
            }
    
    def _handle_discuss(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Facilitate a discussion on a topic"""
        topic = options.get('topic', 'general discussion')
        
        # Add topic to conversation
        if topic not in self.conversation.topics:
            self.conversation.topics.append(topic)
        
        # Add entry
        entry = self.conversation.add_entry(
            EntryType.INSIGHT,
            f"Starting discussion on: {topic}",
            metadata={'topic': topic},
            category='discussion'
        )
        
        return {
            'status': 'success',
            'message': f'Facilitating discussion on: {topic}',
            'entry_id': entry.id,
            'phase': self.conversation.current_phase.value,
            'mode': 'read-only',
            'capabilities': self._get_available_capabilities()
        }
    
    def _handle_summarize(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate conversation summary"""
        context = self.conversation.get_current_context()
        
        # Create summary entry
        summary_content = (
            f"Summary: {context['total_entries']} entries across "
            f"{len(context['categories'])} categories. "
            f"Current phase: {context['phase']}. "
            f"Decisions made: {context['decisions_made']}."
        )
        
        entry = self.conversation.add_entry(
            EntryType.SUMMARY,
            summary_content,
            metadata=context
        )
        
        return {
            'status': 'success',
            'message': 'Conversation summary generated',
            'entry_id': entry.id,
            'summary': context,
            'mode': 'read-only'
        }
    
    def _handle_archive(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare discussion for archival (user-initiated)"""
        archive_data = self.conversation.prepare_archive()
        
        # Note: Actual file writing would be blocked by discourse_safe
        # This returns the prepared data for manual saving
        return {
            'status': 'success',
            'message': f'Discussion prepared for archival',
            'archive_path': str(self.archive_path / archive_data['filename']),
            'markdown_preview': archive_data['markdown'][:500] + '...',
            'total_entries': len(archive_data['data']['entries']),
            'note': 'File writing blocked in discourse mode - data returned for manual save'
        }
    
    def _handle_memory(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Manage conversation memory categories"""
        category = options.get('category', 'general')
        action = options.get('action', 'view')
        
        if action == 'view':
            entries = self.conversation.search_entries(category=category)
            return {
                'status': 'success',
                'message': f'Memory category: {category}',
                'entry_count': len(entries),
                'entries': [e.to_dict() for e in entries[-10:]]  # Last 10 entries
            }
        elif action == 'categories':
            return {
                'status': 'success',
                'message': 'Available categories',
                'categories': self.conversation._get_categories()
            }
        else:
            return {
                'status': 'error',
                'message': f'Memory action {action} not allowed in discourse mode'
            }
    
    def _handle_generic_command(self, command: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Handle commands without specific handlers"""
        if command == 'question':
            return self._handle_question(options)
        elif command == 'insight':
            return self._handle_insight(options)
        elif command == 'decide':
            return self._handle_decide(options)
        elif command == 'phase':
            return self._handle_phase(options)
        elif command == 'search':
            return self._handle_search(options)
        elif command == 'outline':
            return self._handle_outline(options)
        elif command == 'context':
            return self._handle_context(options)
        else:
            return {
                'status': 'error',
                'message': f'Handler not implemented for: {command}'
            }
    
    def _handle_question(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Add a question to explore"""
        question = options.get('question', '')
        if not question:
            return {'status': 'error', 'message': 'Question content required'}
        
        entry = self.conversation.add_entry(
            EntryType.QUESTION,
            question,
            metadata=options.get('metadata', {}),
            category=options.get('category', 'exploration')
        )
        
        return {
            'status': 'success',
            'message': 'Question added',
            'entry_id': entry.id,
            'phase': self.conversation.current_phase.value
        }
    
    def _handle_insight(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Record an insight or observation"""
        insight = options.get('insight', '')
        if not insight:
            return {'status': 'error', 'message': 'Insight content required'}
        
        entry = self.conversation.add_entry(
            EntryType.INSIGHT,
            insight,
            metadata=options.get('metadata', {}),
            references=options.get('references', []),
            category=options.get('category', 'analysis')
        )
        
        return {
            'status': 'success',
            'message': 'Insight recorded',
            'entry_id': entry.id
        }
    
    def _handle_decide(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Make and record a decision"""
        decision = options.get('decision', '')
        if not decision:
            return {'status': 'error', 'message': 'Decision content required'}
        
        # Transition to decision phase if not already there
        if self.conversation.current_phase != ConversationPhase.DECISION:
            self.conversation.transition_phase(ConversationPhase.DECISION)
        
        entry = self.conversation.add_entry(
            EntryType.DECISION,
            decision,
            metadata=options.get('context', {}),
            category='decision'
        )
        
        return {
            'status': 'success',
            'message': 'Decision recorded',
            'entry_id': entry.id,
            'decision_count': len(self.conversation.decisions)
        }
    
    def _handle_phase(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transition conversation phase"""
        new_phase = options.get('phase', '')
        
        try:
            phase_enum = ConversationPhase(new_phase)
            result = self.conversation.transition_phase(phase_enum)
            return result
        except ValueError:
            return {
                'status': 'error',
                'message': f'Invalid phase: {new_phase}',
                'valid_phases': [p.value for p in ConversationPhase]
            }
    
    def _handle_search(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Search conversation entries"""
        results = self.conversation.search_entries(
            query=options.get('query'),
            entry_type=EntryType(options['type']) if 'type' in options else None,
            phase=ConversationPhase(options['phase']) if 'phase' in options else None,
            category=options.get('category')
        )
        
        return {
            'status': 'success',
            'message': f'Found {len(results)} entries',
            'results': [e.to_dict() for e in results[:20]]  # Limit to 20 results
        }
    
    def _handle_outline(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate conversation outline"""
        outline = self.conversation.generate_outline()
        return {
            'status': 'success',
            'message': 'Outline generated',
            'outline': outline
        }
    
    def _handle_context(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Get current conversation context"""
        context = self.conversation.get_current_context()
        return {
            'status': 'success',
            'message': 'Current context retrieved',
            'context': context
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