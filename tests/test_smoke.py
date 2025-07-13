"""
Smoke tests to ensure basic functionality works
"""
import pytest


@pytest.mark.smoke
class TestSmoke:
    """Basic smoke tests"""
    
    def test_imports(self):
        """Test that all main modules can be imported"""
        import unified
        import unified.agents
        import unified.core
        import unified.workflows
        
        # Test version is accessible
        assert hasattr(unified, '__version__')
        assert unified.__version__ == '0.1.1'
    
    def test_enums_accessible(self):
        """Test that enums are properly defined"""
        from unified.agents.schema import AgentCategory, RiskProfile
        
        assert AgentCategory.DESIGN
        assert RiskProfile.CONSERVATIVE
    
    def test_cli_importable(self):
        """Test CLI can be imported"""
        from unified.cli import cli
        assert cli is not None