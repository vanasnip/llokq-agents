"""
Event Bus implementation for decoupled communication between components
"""
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system"""
    AGENT_ACTIVATED = "agent.activated"
    AGENT_DEACTIVATED = "agent.deactivated"
    PHASE_STARTED = "phase.started"
    PHASE_COMPLETED = "phase.completed"
    PHASE_CHANGED = "phase.changed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_CANCELLED = "workflow.cancelled"
    COMMAND_EXECUTED = "command.executed"
    ERROR_OCCURRED = "error.occurred"


@dataclass
class Event:
    """Represents an event in the system"""
    type: EventType
    data: Dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        """Ensure data is always a dict"""
        if self.data is None:
            self.data = {}


class EventBus:
    """
    Central event bus for publish/subscribe pattern.
    Supports both sync and async handlers.
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._async_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._middleware: List[Callable] = []
        self._event_history: List[Event] = []
        self._max_history_size = 1000
    
    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe a synchronous handler to an event type"""
        if asyncio.iscoroutinefunction(handler):
            raise ValueError("Use subscribe_async for async handlers")
        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type.value}")
    
    def subscribe_async(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe an asynchronous handler to an event type"""
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError("Handler must be async")
        self._async_handlers[event_type].append(handler)
        logger.debug(f"Subscribed async {handler.__name__} to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """Unsubscribe a handler from an event type"""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
        elif handler in self._async_handlers[event_type]:
            self._async_handlers[event_type].remove(handler)
        logger.debug(f"Unsubscribed {handler.__name__} from {event_type.value}")
    
    def publish(self, event: Event) -> None:
        """
        Publish an event synchronously.
        Async handlers will be scheduled on the event loop.
        """
        # Add to history
        self._add_to_history(event)
        
        # Apply middleware
        for middleware in self._middleware:
            event = middleware(event)
            if event is None:
                logger.debug("Event filtered by middleware")
                return
        
        # Call sync handlers
        for handler in self._handlers[event.type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in handler {handler.__name__}: {e}")
                self._publish_error(e, handler.__name__, event)
        
        # Schedule async handlers
        if self._async_handlers[event.type]:
            asyncio.create_task(self._handle_async(event))
    
    async def publish_async(self, event: Event) -> None:
        """Publish an event asynchronously, waiting for all handlers"""
        # Add to history
        self._add_to_history(event)
        
        # Apply middleware
        for middleware in self._middleware:
            event = middleware(event)
            if event is None:
                logger.debug("Event filtered by middleware")
                return
        
        # Gather all handlers (sync and async)
        tasks = []
        
        # Wrap sync handlers
        for handler in self._handlers[event.type]:
            tasks.append(self._run_sync_handler(handler, event))
        
        # Add async handlers
        for handler in self._async_handlers[event.type]:
            tasks.append(self._run_async_handler(handler, event))
        
        # Execute all handlers concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _handle_async(self, event: Event) -> None:
        """Handle async handlers for sync publish"""
        tasks = []
        for handler in self._async_handlers[event.type]:
            tasks.append(self._run_async_handler(handler, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_sync_handler(self, handler: Callable, event: Event) -> None:
        """Run a sync handler in an executor"""
        try:
            await asyncio.get_event_loop().run_in_executor(None, handler, event)
        except Exception as e:
            logger.error(f"Error in handler {handler.__name__}: {e}")
            self._publish_error(e, handler.__name__, event)
    
    async def _run_async_handler(self, handler: Callable, event: Event) -> None:
        """Run an async handler"""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in async handler {handler.__name__}: {e}")
            self._publish_error(e, handler.__name__, event)
    
    def add_middleware(self, middleware: Callable[[Event], Optional[Event]]) -> None:
        """Add middleware to process/filter events"""
        self._middleware.append(middleware)
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to history with size limit"""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
    
    def _publish_error(self, error: Exception, handler_name: str, original_event: Event) -> None:
        """Publish an error event when a handler fails"""
        error_event = Event(
            type=EventType.ERROR_OCCURRED,
            data={
                "error": str(error),
                "handler": handler_name,
                "original_event_type": original_event.type.value,
                "original_event_data": original_event.data
            },
            source="event_bus",
            correlation_id=original_event.correlation_id
        )
        # Only publish to sync handlers to avoid recursion
        for handler in self._handlers[EventType.ERROR_OCCURRED]:
            try:
                handler(error_event)
            except Exception:
                logger.error(f"Error in error handler: {handler.__name__}")
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by type"""
        history = self._event_history
        if event_type:
            history = [e for e in history if e.type == event_type]
        return history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()
    
    def get_handlers_count(self, event_type: EventType) -> Dict[str, int]:
        """Get count of handlers for an event type"""
        return {
            "sync": len(self._handlers[event_type]),
            "async": len(self._async_handlers[event_type])
        }


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    return _event_bus


# Decorator for easy subscription
def on_event(event_type: EventType):
    """Decorator to subscribe a function to an event"""
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            _event_bus.subscribe_async(event_type, func)
        else:
            _event_bus.subscribe(event_type, func)
        return func
    return decorator