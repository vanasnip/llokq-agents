"""
Discourse Agent tool handlers
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json
import logging
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from conversation_store import ConversationStore

logger = logging.getLogger(__name__)


class ConversationPhase(Enum):
    """Phases of a structured conversation"""
    EXPLORATION = "exploration"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    DECISION = "decision"
    ARCHIVE = "archive"


class ConversationEntry:
    """A single entry in the conversation"""
    def __init__(self, entry_type: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.id = f"entry_{datetime.now().timestamp()}"
        self.type = entry_type
        self.content = content
        self.timestamp = datetime.now().isoformat()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }


class DiscourseSession:
    """Manages a discourse conversation session"""
    
    def __init__(self):
        self.entries: List[ConversationEntry] = []
        self.phase = ConversationPhase.EXPLORATION
        self.topic = None
        self.decisions = []
        self.insights = []
        self.questions = []
        self.store = ConversationStore()
    
    def add_entry(self, entry_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> ConversationEntry:
        """Add an entry to the conversation"""
        entry = ConversationEntry(entry_type, content, metadata)
        self.entries.append(entry)
        
        # Track special entry types
        if entry_type == "question":
            self.questions.append(entry)
        elif entry_type == "insight":
            self.insights.append(entry)
        elif entry_type == "decision":
            self.decisions.append(entry)
            # Auto-transition to decision phase
            if self.phase != ConversationPhase.DECISION:
                self.phase = ConversationPhase.DECISION
        
        return entry
    
    def get_summary(self, depth: str = "brief") -> str:
        """Generate a summary of the conversation"""
        if depth == "brief":
            return self._brief_summary()
        else:
            return self._detailed_summary()
    
    def _brief_summary(self) -> str:
        """Generate a brief summary"""
        summary = f"# Conversation Summary\n\n"
        if self.topic:
            summary += f"**Topic**: {self.topic}\n\n"
        summary += f"**Phase**: {self.phase.value}\n"
        summary += f"**Entries**: {len(self.entries)}\n"
        summary += f"**Questions**: {len(self.questions)}\n"
        summary += f"**Insights**: {len(self.insights)}\n"
        summary += f"**Decisions**: {len(self.decisions)}\n"
        return summary
    
    def _detailed_summary(self) -> str:
        """Generate a detailed summary"""
        summary = self._brief_summary()
        
        if self.questions:
            summary += "\n## Questions Explored\n"
            for q in self.questions[-5:]:  # Last 5 questions
                summary += f"- {q.content}\n"
        
        if self.insights:
            summary += "\n## Key Insights\n"
            for i in self.insights[-5:]:  # Last 5 insights
                summary += f"- {i.content}\n"
        
        if self.decisions:
            summary += "\n## Decisions Made\n"
            for d in self.decisions:
                summary += f"- {d.content}\n"
        
        return summary
    
    def archive(self, title: Optional[str] = None) -> str:
        """Archive the conversation"""
        archive_data = {
            'title': title or f"Discourse on {self.topic or 'General Topic'}",
            'topic': self.topic,
            'phase': self.phase.value,
            'created_at': datetime.now().isoformat(),
            'entries': [e.to_dict() for e in self.entries],
            'summary': {
                'total_entries': len(self.entries),
                'questions': len(self.questions),
                'insights': len(self.insights),
                'decisions': len(self.decisions)
            }
        }
        
        # Save to store
        filename = self.store.save_conversation('discourse', archive_data)
        return filename


# Global session - in production this would be per-connection
_discourse_session = DiscourseSession()


def get_session() -> DiscourseSession:
    """Get the current discourse session"""
    return _discourse_session


def handle_discourse_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Discourse agent tools"""
    try:
        if tool_name == 'ua_discourse_discuss':
            return _discourse_discuss(args['topic'], args.get('context', {}))
        elif tool_name == 'ua_discourse_question':
            return _discourse_question(args['question'], args.get('category'))
        elif tool_name == 'ua_discourse_insight':
            return _discourse_insight(args['insight'], args.get('references', []))
        elif tool_name == 'ua_discourse_decide':
            return _discourse_decide(args['decision'], args.get('context', {}))
        elif tool_name == 'ua_discourse_summarize':
            return _discourse_summarize(args.get('depth', 'brief'))
        elif tool_name == 'ua_discourse_archive':
            return _discourse_archive(args.get('title'))
        else:
            raise ValueError(f"Unknown Discourse tool: {tool_name}")
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")


def _discourse_discuss(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Start or continue a discussion on a topic"""
    session = get_session()
    session.topic = topic
    
    # Add discussion entry
    entry = session.add_entry(
        "discussion",
        f"Beginning discourse on: {topic}",
        metadata={'context': context}
    )
    
    response = f"# Discourse: {topic}\n\n"
    response += "I'm ready to facilitate a structured discussion on this topic. "
    response += "Let's explore through questions, capture insights, and work toward decisions.\n\n"
    response += f"**Current Phase**: {session.phase.value}\n\n"
    response += "What aspects would you like to explore first?"
    
    return {
        'content': [{
            'type': 'text',
            'text': response
        }]
    }


def _discourse_question(question: str, category: Optional[str]) -> Dict[str, Any]:
    """Add a question to explore"""
    session = get_session()
    
    entry = session.add_entry(
        "question",
        question,
        metadata={'category': category} if category else None
    )
    
    response = f"## Question Added\n\n"
    response += f"**Q**: {question}\n\n"
    
    # Suggest exploration approaches
    response += "This question opens several avenues for exploration:\n"
    response += "- What assumptions underlie this question?\n"
    response += "- What evidence or examples might illuminate it?\n"
    response += "- How does this connect to our broader topic?\n\n"
    response += f"Total questions in this discourse: {len(session.questions)}"
    
    return {
        'content': [{
            'type': 'text',
            'text': response
        }]
    }


def _discourse_insight(insight: str, references: List[str]) -> Dict[str, Any]:
    """Record an insight or observation"""
    session = get_session()
    
    # Transition to analysis phase if still exploring
    if session.phase == ConversationPhase.EXPLORATION:
        session.phase = ConversationPhase.ANALYSIS
    
    entry = session.add_entry(
        "insight",
        insight,
        metadata={'references': references} if references else None
    )
    
    response = f"## Insight Captured\n\n"
    response += f"**Insight**: {insight}\n\n"
    
    if references:
        response += "**References**:\n"
        for ref in references:
            response += f"- {ref}\n"
        response += "\n"
    
    response += f"This brings our total insights to {len(session.insights)}. "
    response += "How does this insight influence our understanding?"
    
    return {
        'content': [{
            'type': 'text',
            'text': response
        }]
    }


def _discourse_decide(decision: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Make and record a decision"""
    session = get_session()
    
    entry = session.add_entry(
        "decision",
        decision,
        metadata={'context': context}
    )
    
    response = f"## Decision Recorded\n\n"
    response += f"**Decision**: {decision}\n\n"
    
    if context:
        response += "**Context**:\n"
        response += json.dumps(context, indent=2)
        response += "\n\n"
    
    response += f"Total decisions made: {len(session.decisions)}\n\n"
    response += "This decision has been captured. Would you like to:\n"
    response += "- Explore implications of this decision?\n"
    response += "- Make additional related decisions?\n"
    response += "- Summarize our discourse so far?"
    
    return {
        'content': [{
            'type': 'text',
            'text': response
        }]
    }


def _discourse_summarize(depth: str) -> Dict[str, Any]:
    """Generate conversation summary"""
    session = get_session()
    
    summary = session.get_summary(depth)
    
    # Add summary as an entry
    session.add_entry(
        "summary",
        f"Generated {depth} summary",
        metadata={'summary_text': summary}
    )
    
    return {
        'content': [{
            'type': 'text',
            'text': summary
        }]
    }


def _discourse_archive(title: Optional[str]) -> Dict[str, Any]:
    """Archive the current conversation"""
    session = get_session()
    
    if len(session.entries) == 0:
        return {
            'content': [{
                'type': 'text',
                'text': "No conversation to archive. Start a discussion first."
            }]
        }
    
    # Transition to archive phase
    session.phase = ConversationPhase.ARCHIVE
    
    # Archive the conversation
    filename = session.archive(title)
    
    response = f"## Conversation Archived\n\n"
    response += f"**Filename**: {filename}\n"
    response += f"**Location**: ~/.mcp/conversations/discourse/\n\n"
    response += session.get_summary("brief")
    response += "\n\nThe conversation has been preserved for future reference."
    
    # Reset session for new conversation
    global _discourse_session
    _discourse_session = DiscourseSession()
    
    return {
        'content': [{
            'type': 'text',
            'text': response
        }]
    }