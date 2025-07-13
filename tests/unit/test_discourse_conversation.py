"""
Unit tests for discourse conversation management
"""
import pytest
from datetime import datetime
from pathlib import Path
from unified.agents.discourse import (
    ConversationManager, 
    ConversationPhase, 
    EntryType,
    ConversationEntry,
    DiscourseCommandParser
)


def test_conversation_manager_initialization():
    """Test ConversationManager initialization"""
    archive_path = Path("/tmp/test_archives")
    manager = ConversationManager(archive_path)
    
    assert manager.archive_path == archive_path
    assert manager.current_phase == ConversationPhase.EXPLORATION
    assert len(manager.entries) == 0
    assert len(manager.topics) == 0
    assert len(manager.decisions) == 0


def test_add_entry():
    """Test adding entries to conversation"""
    manager = ConversationManager(Path("/tmp"))
    
    # Add a question
    entry = manager.add_entry(
        EntryType.QUESTION,
        "How should we handle authentication?",
        metadata={"priority": "high"},
        category="security"
    )
    
    assert entry.id == "entry_0001"
    assert entry.type == EntryType.QUESTION
    assert entry.content == "How should we handle authentication?"
    assert entry.phase == ConversationPhase.EXPLORATION
    assert entry.category == "security"
    assert entry.metadata["priority"] == "high"
    assert len(manager.entries) == 1


def test_phase_transition():
    """Test conversation phase transitions"""
    manager = ConversationManager(Path("/tmp"))
    
    # Add some entries in exploration phase
    manager.add_entry(EntryType.QUESTION, "Question 1")
    manager.add_entry(EntryType.INSIGHT, "Insight 1")
    
    # Transition to analysis phase
    result = manager.transition_phase(ConversationPhase.ANALYSIS)
    
    assert result["status"] == "success"
    assert result["from_phase"] == "exploration"
    assert result["to_phase"] == "analysis"
    assert manager.current_phase == ConversationPhase.ANALYSIS
    
    # Should have added a summary entry
    assert len(manager.entries) == 3
    assert manager.entries[-1].type == EntryType.SUMMARY


def test_decision_tracking():
    """Test decision tracking"""
    manager = ConversationManager(Path("/tmp"))
    
    # Transition to decision phase
    manager.current_phase = ConversationPhase.DECISION
    
    # Add decisions
    entry1 = manager.add_entry(
        EntryType.DECISION,
        "Use JWT tokens for authentication",
        metadata={"rationale": "Industry standard"}
    )
    
    entry2 = manager.add_entry(
        EntryType.DECISION,
        "Implement rate limiting",
        metadata={"rationale": "Security best practice"}
    )
    
    assert len(manager.decisions) == 2
    assert manager.decisions[0]["decision"] == "Use JWT tokens for authentication"
    assert manager.decisions[1]["decision"] == "Implement rate limiting"


def test_search_entries():
    """Test searching conversation entries"""
    manager = ConversationManager(Path("/tmp"))
    
    # Add various entries
    manager.add_entry(EntryType.QUESTION, "How to handle auth?", category="security")
    manager.add_entry(EntryType.INSIGHT, "JWT is widely used", category="security")
    manager.add_entry(EntryType.DECISION, "Use JWT tokens", category="security")
    manager.add_entry(EntryType.QUESTION, "Database design?", category="database")
    
    # Search by query
    results = manager.search_entries(query="JWT")
    assert len(results) == 2
    
    # Search by type
    results = manager.search_entries(entry_type=EntryType.QUESTION)
    assert len(results) == 2
    
    # Search by category
    results = manager.search_entries(category="security")
    assert len(results) == 3
    
    # Combined search
    results = manager.search_entries(
        query="auth",
        entry_type=EntryType.QUESTION,
        category="security"
    )
    assert len(results) == 1


def test_conversation_outline():
    """Test outline generation"""
    manager = ConversationManager(Path("/tmp"))
    
    # Add entries across phases
    manager.add_entry(EntryType.QUESTION, "Initial question")
    manager.transition_phase(ConversationPhase.ANALYSIS)
    manager.add_entry(EntryType.INSIGHT, "Key insight")
    manager.transition_phase(ConversationPhase.DECISION)
    manager.add_entry(EntryType.DECISION, "Final decision")
    
    outline = manager.generate_outline()
    
    assert "phases" in outline
    assert "exploration" in outline["phases"]
    assert "analysis" in outline["phases"]
    assert "decision" in outline["phases"]
    assert len(outline["decisions"]) == 1


def test_archive_preparation():
    """Test archive preparation"""
    manager = ConversationManager(Path("/tmp"))
    
    # Add some content
    manager.topics = ["authentication", "security"]
    manager.add_entry(EntryType.QUESTION, "How to secure the API?")
    manager.add_entry(EntryType.DECISION, "Use OAuth2")
    
    archive = manager.prepare_archive()
    
    assert "data" in archive
    assert "markdown" in archive
    assert "filename" in archive
    
    # Check archive data
    data = archive["data"]
    assert data["total_entries"] == 2
    assert data["topics"] == ["authentication", "security"]
    assert len(data["decisions"]) == 1
    
    # Check markdown contains key elements
    markdown = archive["markdown"]
    assert "Conversation Archive" in markdown
    assert "authentication" in markdown
    assert "Use OAuth2" in markdown


def test_discourse_command_parser():
    """Test discourse command parsing"""
    parser = DiscourseCommandParser()
    
    # Test discuss command
    cmd = parser.parse("/discuss authentication patterns")
    assert cmd.command == "discuss"
    assert cmd.options["topic"] == "authentication patterns"
    
    # Test question with category
    cmd = parser.parse("/question How to handle errors? --category architecture")
    assert cmd.command == "question"
    assert cmd.options["question"] == "How to handle errors?"
    assert cmd.options["category"] == "architecture"
    
    # Test insight with references
    cmd = parser.parse("/insight Found a bug in auth --ref auth.py,user.py")
    assert cmd.command == "insight"
    assert cmd.options["insight"] == "Found a bug in auth"
    assert cmd.options["references"] == ["auth.py", "user.py"]
    
    # Test search with filters
    cmd = parser.parse("/search authentication --type decision --category security")
    assert cmd.command == "search"
    assert cmd.options["query"] == "authentication"
    assert cmd.options["type"] == "decision"
    assert cmd.options["category"] == "security"
    
    # Test invalid command
    cmd = parser.parse("/invalid command")
    assert cmd is None


def test_discourse_command_validation():
    """Test command validation"""
    parser = DiscourseCommandParser()
    
    # Valid commands
    cmd = parser.parse("/question What is the plan?")
    valid, error = parser.validate_command(cmd)
    assert valid is True
    
    # Invalid - empty question
    cmd = parser.parse("/question")
    valid, error = parser.validate_command(cmd)
    assert valid is False
    assert "cannot be empty" in error
    
    # Invalid phase
    cmd = parser.parse("/phase invalid_phase")
    valid, error = parser.validate_command(cmd)
    assert valid is False
    assert "Invalid phase" in error
    
    # Invalid memory action
    cmd = DiscourseCommand(command="memory", options={"action": "delete"})
    valid, error = parser.validate_command(cmd)
    assert valid is False
    assert "Invalid action" in error