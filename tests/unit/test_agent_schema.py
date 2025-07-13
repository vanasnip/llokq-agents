"""
Unit tests for Agent schema
"""
import pytest
from unified.agents.schema import Agent, AgentCategory, RiskProfile


class TestAgentSchema:
    """Test Agent dataclass and related enums"""
    
    def test_risk_profile_enum(self):
        """Test RiskProfile enum values"""
        assert RiskProfile.CONSERVATIVE.value == "conservative"
        assert RiskProfile.BALANCED.value == "balanced"
        assert RiskProfile.AGGRESSIVE.value == "aggressive"
        assert RiskProfile.ZERO_TOLERANCE.value == "zero_tolerance"
    
    def test_agent_category_enum(self):
        """Test AgentCategory enum values"""
        assert AgentCategory.DESIGN.value == "design"
        assert AgentCategory.DEVELOPMENT.value == "development"
        assert AgentCategory.OPERATIONS.value == "operations"
        assert AgentCategory.QUALITY.value == "quality"
        assert AgentCategory.ARCHITECTURE.value == "architecture"
    
    def test_agent_creation(self, sample_agent_config):
        """Test creating an Agent instance"""
        # Convert string values to enums
        sample_agent_config['category'] = AgentCategory.DEVELOPMENT
        sample_agent_config['risk_profile'] = RiskProfile.CONSERVATIVE
        
        agent = Agent(**sample_agent_config)
        
        assert agent.name == 'test_agent'
        assert agent.command == '--test'
        assert agent.category == AgentCategory.DEVELOPMENT
        assert agent.risk_profile == RiskProfile.CONSERVATIVE
        assert agent.identity == 'Test Agent for unit testing'
        assert agent.mcp_preferences == ['testing', 'mocking']
        assert agent.primary_phases == [5]
    
    def test_agent_to_dict(self, sample_agent_config):
        """Test converting Agent to dictionary"""
        sample_agent_config['category'] = AgentCategory.DEVELOPMENT
        sample_agent_config['risk_profile'] = RiskProfile.CONSERVATIVE
        
        agent = Agent(**sample_agent_config)
        agent_dict = agent.to_dict()
        
        assert agent_dict['name'] == 'test_agent'
        assert agent_dict['category'] == 'development'
        assert agent_dict['risk_profile'] == RiskProfile.CONSERVATIVE
        assert agent_dict['mcp_preferences'] == ['testing', 'mocking']
    
    def test_agent_from_dict(self, sample_agent_config):
        """Test creating Agent from dictionary"""
        agent = Agent.from_dict(sample_agent_config)
        
        assert agent.name == 'test_agent'
        assert agent.category == AgentCategory.DEVELOPMENT
        assert isinstance(agent.risk_profile, str)  # Note: from_dict doesn't convert risk_profile to enum
        assert agent.mcp_preferences == ['testing', 'mocking']
    
    def test_agent_repr(self, sample_agent_config):
        """Test Agent string representation"""
        sample_agent_config['category'] = AgentCategory.DEVELOPMENT
        sample_agent_config['risk_profile'] = RiskProfile.CONSERVATIVE
        
        agent = Agent(**sample_agent_config)
        repr_str = repr(agent)
        
        assert 'Agent(test_agent' in repr_str
        assert 'command=--test' in repr_str
        assert 'category=development' in repr_str