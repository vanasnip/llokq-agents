"""
Discourse context and guardrails for read-only conversation mode
"""
from contextlib import ContextDecorator
from typing import Any, Callable


class DiscourseGuardrailException(RuntimeError):
    """Raised when any execution or mutation is attempted in discourse mode."""
    pass


class discourse_safe(ContextDecorator):
    """
    Decorator for command methods: blocks any write/exec tool
    when DiscourseContext.discourse_mode is True.
    """
    
    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Try to get context from kwargs or first arg
            context = kwargs.get("context")
            if not context and args:
                # Check if first arg has context attribute
                context = getattr(args[0], "context", None)
            
            # Check if we're in discourse mode and function mutates
            if context and getattr(context, "discourse_mode", False):
                if getattr(func, "_mutates", False):
                    raise DiscourseGuardrailException(
                        f"Execution not permitted in discourse mode: {func.__name__}"
                    )
            
            return func(*args, **kwargs)
        
        return wrapper


class DiscourseContext:
    """
    Shared context injected into DiscourseAgent and all delegates.
    Ensures read-only operations throughout the conversation.
    """
    
    def __init__(self, parent_context: Any = None, delegate_readonly: bool = True):
        self.discourse_mode = True
        self.delegate_readonly = delegate_readonly
        self.execution_blocked = True
        
        # Inherit from parent context if provided
        if parent_context:
            self.inherit_from(parent_context)
    
    def inherit_from(self, parent_context: Any) -> None:
        """Inherit security settings from parent context"""
        if hasattr(parent_context, "discourse_mode"):
            self.discourse_mode = parent_context.discourse_mode
        if hasattr(parent_context, "execution_blocked"):
            self.execution_blocked = parent_context.execution_blocked