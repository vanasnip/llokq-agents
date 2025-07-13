"""
Conversation management for DiscourseAgent
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class ConversationPhase(Enum):
    """Phases of a structured conversation"""
    EXPLORATION = "exploration"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    DECISION = "decision"
    ARCHIVE = "archive"


class EntryType(Enum):
    """Types of conversation entries"""
    QUESTION = "question"
    INSIGHT = "insight"
    DECISION = "decision"
    SUMMARY = "summary"
    REFERENCE = "reference"
    PLAN = "plan"
    MEMORY = "memory"


@dataclass
class ConversationEntry:
    """A single entry in the conversation"""
    id: str
    type: EntryType
    content: str
    timestamp: datetime
    phase: ConversationPhase
    metadata: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'type': self.type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'phase': self.phase.value,
            'metadata': self.metadata,
            'references': self.references,
            'category': self.category
        }


class ConversationManager:
    """Manages conversation state and patterns"""
    
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path
        self.entries: List[ConversationEntry] = []
        self.current_phase = ConversationPhase.EXPLORATION
        self.topics: List[str] = []
        self.decisions: List[Dict[str, Any]] = []
        self.entry_counter = 0
    
    def add_entry(self, 
                  entry_type: EntryType,
                  content: str,
                  metadata: Optional[Dict[str, Any]] = None,
                  references: Optional[List[str]] = None,
                  category: Optional[str] = None) -> ConversationEntry:
        """Add a new entry to the conversation"""
        self.entry_counter += 1
        entry = ConversationEntry(
            id=f"entry_{self.entry_counter:04d}",
            type=entry_type,
            content=content,
            timestamp=datetime.now(),
            phase=self.current_phase,
            metadata=metadata or {},
            references=references or [],
            category=category
        )
        self.entries.append(entry)
        
        # Track decisions separately
        if entry_type == EntryType.DECISION:
            self.decisions.append({
                'id': entry.id,
                'decision': content,
                'timestamp': entry.timestamp,
                'context': metadata
            })
        
        return entry
    
    def transition_phase(self, new_phase: ConversationPhase) -> Dict[str, Any]:
        """Transition to a new conversation phase"""
        old_phase = self.current_phase
        self.current_phase = new_phase
        
        # Add transition summary
        summary = self._generate_phase_summary(old_phase)
        self.add_entry(
            EntryType.SUMMARY,
            f"Phase transition: {old_phase.value} → {new_phase.value}\n{summary}",
            metadata={'transition': True, 'from_phase': old_phase.value}
        )
        
        return {
            'status': 'success',
            'from_phase': old_phase.value,
            'to_phase': new_phase.value,
            'summary': summary
        }
    
    def _generate_phase_summary(self, phase: ConversationPhase) -> str:
        """Generate a summary for a completed phase"""
        phase_entries = [e for e in self.entries if e.phase == phase]
        
        if not phase_entries:
            return "No entries in this phase."
        
        summary_parts = [
            f"Completed {phase.value} phase with {len(phase_entries)} entries.",
            f"Types: {self._count_entry_types(phase_entries)}",
        ]
        
        # Add phase-specific summaries
        if phase == ConversationPhase.EXPLORATION:
            questions = [e for e in phase_entries if e.type == EntryType.QUESTION]
            summary_parts.append(f"Questions explored: {len(questions)}")
        elif phase == ConversationPhase.DECISION:
            decisions = [e for e in phase_entries if e.type == EntryType.DECISION]
            summary_parts.append(f"Decisions made: {len(decisions)}")
        
        return "\n".join(summary_parts)
    
    def _count_entry_types(self, entries: List[ConversationEntry]) -> str:
        """Count entry types in a list"""
        type_counts = {}
        for entry in entries:
            type_counts[entry.type.value] = type_counts.get(entry.type.value, 0) + 1
        return ", ".join([f"{t}: {c}" for t, c in type_counts.items()])
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get the current conversation context"""
        recent_entries = self.entries[-5:] if len(self.entries) > 5 else self.entries
        
        return {
            'phase': self.current_phase.value,
            'total_entries': len(self.entries),
            'recent_entries': [e.to_dict() for e in recent_entries],
            'topics': self.topics,
            'decisions_made': len(self.decisions),
            'categories': self._get_categories()
        }
    
    def _get_categories(self) -> List[str]:
        """Get unique categories from entries"""
        categories = set()
        for entry in self.entries:
            if entry.category:
                categories.add(entry.category)
        return sorted(list(categories))
    
    def search_entries(self, 
                      query: Optional[str] = None,
                      entry_type: Optional[EntryType] = None,
                      phase: Optional[ConversationPhase] = None,
                      category: Optional[str] = None) -> List[ConversationEntry]:
        """Search conversation entries"""
        results = self.entries
        
        if entry_type:
            results = [e for e in results if e.type == entry_type]
        
        if phase:
            results = [e for e in results if e.phase == phase]
        
        if category:
            results = [e for e in results if e.category == category]
        
        if query:
            query_lower = query.lower()
            results = [e for e in results if query_lower in e.content.lower()]
        
        return results
    
    def generate_outline(self) -> Dict[str, Any]:
        """Generate a structured outline of the conversation"""
        outline = {
            'title': f'Conversation Outline - {datetime.now().strftime("%Y-%m-%d")}',
            'phases': {}
        }
        
        for phase in ConversationPhase:
            phase_entries = [e for e in self.entries if e.phase == phase]
            if phase_entries:
                outline['phases'][phase.value] = {
                    'entry_count': len(phase_entries),
                    'entries': [
                        {
                            'id': e.id,
                            'type': e.type.value,
                            'summary': e.content[:100] + '...' if len(e.content) > 100 else e.content
                        }
                        for e in phase_entries
                    ]
                }
        
        outline['decisions'] = [
            {
                'id': d['id'],
                'decision': d['decision'],
                'timestamp': d['timestamp'].isoformat()
            }
            for d in self.decisions
        ]
        
        return outline
    
    def prepare_archive(self) -> Dict[str, Any]:
        """Prepare conversation for archival (returns data, doesn't write)"""
        archive_data = {
            'conversation_id': f'conv_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'created_at': datetime.now().isoformat(),
            'total_entries': len(self.entries),
            'phases_covered': [p.value for p in ConversationPhase if any(e.phase == p for e in self.entries)],
            'topics': self.topics,
            'decisions': self.decisions,
            'entries': [e.to_dict() for e in self.entries],
            'outline': self.generate_outline()
        }
        
        # Generate markdown representation
        markdown = self._generate_markdown_archive(archive_data)
        
        return {
            'data': archive_data,
            'markdown': markdown,
            'filename': f"{archive_data['conversation_id']}.md",
            'json_filename': f"{archive_data['conversation_id']}.json"
        }
    
    def _generate_markdown_archive(self, archive_data: Dict[str, Any]) -> str:
        """Generate markdown representation of the conversation"""
        lines = [
            f"# Conversation Archive: {archive_data['conversation_id']}",
            f"\nCreated: {archive_data['created_at']}",
            f"Total Entries: {archive_data['total_entries']}",
            f"Phases: {', '.join(archive_data['phases_covered'])}",
            ""
        ]
        
        if archive_data['topics']:
            lines.extend([
                "## Topics Discussed",
                *[f"- {topic}" for topic in archive_data['topics']],
                ""
            ])
        
        if archive_data['decisions']:
            lines.extend([
                "## Key Decisions",
                *[f"- **{d['decision']}** ({d['timestamp']})" for d in archive_data['decisions']],
                ""
            ])
        
        # Group entries by phase
        lines.append("## Conversation Flow")
        for phase in archive_data['phases_covered']:
            phase_entries = [e for e in archive_data['entries'] if e['phase'] == phase]
            if phase_entries:
                lines.extend([
                    f"\n### {phase.title()} Phase",
                    f"*{len(phase_entries)} entries*\n"
                ])
                
                for entry in phase_entries:
                    lines.extend([
                        f"**[{entry['id']}] {entry['type'].title()}** - {entry['timestamp']}",
                        f"{entry['content']}",
                        ""
                    ])
                    
                    if entry['references']:
                        lines.append(f"References: {', '.join(entry['references'])}\n")
        
        return "\n".join(lines)