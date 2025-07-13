"""
Unit tests for Command Parser
"""
import pytest
from unittest.mock import Mock, MagicMock
from unified.core.command_parser import CommandParser, ParsedCommand
from unified.agents.schema import Agent, AgentCategory, RiskProfile


class TestCommandParser:
    """Test CommandParser functionality"""
    
    @pytest.fixture
    def parser(self, mock_agent_manager):
        """Create CommandParser instance with mocked AgentManager"""
        return CommandParser(mock_agent_manager)
    
    def test_parse_simple_command(self, parser):
        """Test parsing a simple command"""
        parsed = parser.parse("/code")
        
        assert parsed.base_command == "code"
        assert parsed.agents == []
        assert parsed.phase is None
        assert parsed.options == {}
        assert parsed.raw_input == "/code"
    
    def test_parse_command_with_agents(self, parser):
        """Test parsing command with agent flags"""
        parsed = parser.parse("/code --backend --frontend")
        
        assert parsed.base_command == "code"
        assert parsed.agents == ["backend", "frontend"]
        assert parsed.phase is None
    
    def test_parse_command_with_phase(self, parser):
        """Test parsing command with phase specification"""
        parsed = parser.parse("/design --phase 3")
        
        assert parsed.base_command == "design"
        assert parsed.agents == []
        assert parsed.phase == 3
    
    def test_parse_workflow_command(self, parser):
        """Test parsing workflow command"""
        parsed = parser.parse("/workflow feature")
        
        assert parsed.base_command == "workflow"
        assert parsed.options['workflow_type'] == "feature"
    
    def test_parse_phase_goto_command(self, parser):
        """Test parsing phase goto command"""
        parsed = parser.parse("/phase --goto 5")
        
        assert parsed.base_command == "phase"
        assert parsed.options['goto'] == "5"
    
    def test_parse_team_activate_command(self, parser):
        """Test parsing team activate command"""
        parsed = parser.parse('/team --activate "backend,frontend,qa"')
        
        assert parsed.base_command == "team"
        assert parsed.options['activate'] == ["backend", "frontend", "qa"]
    
    def test_invalid_command_format(self, parser):
        """Test handling invalid command format"""
        with pytest.raises(ValueError, match="Invalid command format"):
            parser.parse("code --backend")  # Missing leading slash
    
    def test_unknown_command(self, parser):
        """Test handling unknown command"""
        with pytest.raises(ValueError, match="Unknown command"):
            parser.parse("/unknown --test")
    
    def test_validate_agents(self, parser, mock_agent_manager):
        """Test agent validation"""
        # Mock agent existence
        mock_agent_manager.get_agent.side_effect = lambda name: Mock() if name in ["backend", "frontend"] else None
        
        # Test valid agents
        valid, invalid = parser.validate_agents(["backend", "frontend"])
        assert valid is True
        assert invalid == []
        
        # Test with invalid agents
        valid, invalid = parser.validate_agents(["backend", "unknown"])
        assert valid is False
        assert invalid == ["unknown"]
    
    def test_apply_agent_context(self, parser, mock_agent_manager):
        """Test applying agent context to command"""
        # Create mock agents
        backend_agent = Mock(
            name="backend",
            mcp_preferences=["filesystem", "database"],
            communication_style="Technical",
            decision_framework="Performance-focused"
        )
        frontend_agent = Mock(
            name="frontend",
            mcp_preferences=["filesystem", "puppeteer"],
            communication_style="User-focused",
            decision_framework="UX-centered"
        )
        
        mock_agent_manager.activate_agent.side_effect = lambda name: {
            "backend": backend_agent,
            "frontend": frontend_agent
        }.get(name)
        
        # Create parsed command
        parsed = ParsedCommand(
            base_command="code",
            agents=["backend", "frontend"],
            phase=None,
            options={},
            raw_input="/code --backend --frontend"
        )
        
        # Apply context
        context = parser.apply_agent_context(parsed)
        
        assert context['command'] == "code"
        assert len(context['agents']) == 2
        assert "filesystem" in context['mcp_preferences']
        assert "database" in context['mcp_preferences']
        assert "puppeteer" in context['mcp_preferences']
        assert "Technical" in context['communication_styles']
        assert "User-focused" in context['communication_styles']
    
    def test_format_help(self, parser, mock_agent_manager):
        """Test help text generation"""
        # Mock some agents
        mock_agent_manager.agents = {
            "backend": Mock(command="--backend", identity="Backend engineer | Node.js expert"),
            "frontend": Mock(command="--frontend", identity="Frontend architect | React specialist")
        }
        
        help_text = parser.format_help()
        
        assert "Available Commands:" in help_text
        assert "/code" in help_text
        assert "/design" in help_text
        assert "Agent Activation:" in help_text
        assert "--backend" in help_text
        assert "Backend engineer" in help_text