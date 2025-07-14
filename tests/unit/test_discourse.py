"""
Unit tests for discourse agent functionality
"""
import pytest
from unified.agents.schema import AgentCategory
from unified.agents.discourse import (
    DiscourseContext, 
    DiscourseGuardrailException, 
    discourse_safe
)


def test_discourse_enum_present():
    """Test that DISCOURSE category exists in AgentCategory"""
    assert AgentCategory.DISCOURSE
    assert AgentCategory.DISCOURSE.value == "discourse"


def test_discourse_context_initialization():
    """Test DiscourseContext initialization"""
    context = DiscourseContext()
    assert context.discourse_mode is True
    assert context.delegate_readonly is True
    assert context.execution_blocked is True


def test_discourse_context_inheritance():
    """Test context inheritance from parent"""
    parent = DiscourseContext()
    parent.discourse_mode = True
    parent.execution_blocked = True
    
    child = DiscourseContext(parent_context=parent)
    assert child.discourse_mode is True
    assert child.execution_blocked is True


def test_discourse_safe_decorator_blocks_mutations():
    """Test that discourse_safe decorator blocks mutating functions"""
    
    class MockExecutor:
        def __init__(self):
            self.context = DiscourseContext()
        
        @discourse_safe()
        def safe_read(self):
            return "read successful"
        
        @discourse_safe()
        def unsafe_write(self):
            return "write attempted"
    
    # Mark the write function as mutating
    MockExecutor.unsafe_write._mutates = True
    
    executor = MockExecutor()
    
    # Safe read should work
    assert executor.safe_read() == "read successful"
    
    # Unsafe write should raise exception
    with pytest.raises(DiscourseGuardrailException) as exc_info:
        executor.unsafe_write()
    
    assert "Execution not permitted in discourse mode" in str(exc_info.value)


def test_discourse_safe_decorator_allows_when_not_in_discourse_mode():
    """Test that mutations are allowed when not in discourse mode"""
    
    class MockExecutor:
        def __init__(self):
            self.context = None  # No discourse context
        
        @discourse_safe()
        def write_operation(self):
            return "write successful"
    
    MockExecutor.write_operation._mutates = True
    
    executor = MockExecutor()
    # Should work fine without discourse context
    assert executor.write_operation() == "write successful"


def test_discourse_context_with_kwargs():
    """Test discourse_safe decorator with context in kwargs"""
    
    @discourse_safe()
    def some_function(data: str, context: Any = None) -> str:
        return f"processed: {data}"
    
    # Without mutation flag, should work
    context = DiscourseContext()
    result = some_function("test", context=context)
    assert result == "processed: test"
    
    # With mutation flag, should fail
    some_function._mutates = True
    with pytest.raises(DiscourseGuardrailException):
        some_function("test", context=context)