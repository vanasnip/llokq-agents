"""
Unit tests for Event Bus
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from unified.core.event_bus import EventBus, Event, EventType, on_event, get_event_bus


class TestEventBus:
    """Test EventBus functionality"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh EventBus instance"""
        return EventBus()
    
    @pytest.fixture
    def sample_event(self):
        """Create a sample event"""
        return Event(
            type=EventType.AGENT_ACTIVATED,
            data={"agent": "backend", "phase": 1},
            source="test"
        )
    
    def test_subscribe_sync_handler(self, event_bus):
        """Test subscribing a synchronous handler"""
        handler = Mock()
        event_bus.subscribe(EventType.AGENT_ACTIVATED, handler)
        
        count = event_bus.get_handlers_count(EventType.AGENT_ACTIVATED)
        assert count["sync"] == 1
        assert count["async"] == 0
    
    def test_subscribe_async_handler(self, event_bus):
        """Test subscribing an asynchronous handler"""
        async def handler(event): pass
        
        event_bus.subscribe_async(EventType.AGENT_ACTIVATED, handler)
        
        count = event_bus.get_handlers_count(EventType.AGENT_ACTIVATED)
        assert count["sync"] == 0
        assert count["async"] == 1
    
    def test_subscribe_wrong_handler_type(self, event_bus):
        """Test error when subscribing wrong handler type"""
        async def async_handler(event): pass
        def sync_handler(event): pass
        
        # Async handler to sync subscribe
        with pytest.raises(ValueError, match="Use subscribe_async"):
            event_bus.subscribe(EventType.AGENT_ACTIVATED, async_handler)
        
        # Sync handler to async subscribe
        with pytest.raises(ValueError, match="Handler must be async"):
            event_bus.subscribe_async(EventType.AGENT_ACTIVATED, sync_handler)
    
    def test_publish_sync(self, event_bus, sample_event):
        """Test publishing event to sync handlers"""
        handler1 = Mock()
        handler2 = Mock()
        
        event_bus.subscribe(EventType.AGENT_ACTIVATED, handler1)
        event_bus.subscribe(EventType.AGENT_ACTIVATED, handler2)
        
        event_bus.publish(sample_event)
        
        handler1.assert_called_once_with(sample_event)
        handler2.assert_called_once_with(sample_event)
    
    @pytest.mark.asyncio
    async def test_publish_async(self, event_bus, sample_event):
        """Test publishing event to async handlers"""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe_async(EventType.AGENT_ACTIVATED, handler1)
        event_bus.subscribe_async(EventType.AGENT_ACTIVATED, handler2)
        
        await event_bus.publish_async(sample_event)
        
        handler1.assert_called_once_with(sample_event)
        handler2.assert_called_once_with(sample_event)
    
    def test_unsubscribe(self, event_bus):
        """Test unsubscribing handlers"""
        handler = Mock()
        
        event_bus.subscribe(EventType.AGENT_ACTIVATED, handler)
        count = event_bus.get_handlers_count(EventType.AGENT_ACTIVATED)
        assert count["sync"] == 1
        
        event_bus.unsubscribe(EventType.AGENT_ACTIVATED, handler)
        count = event_bus.get_handlers_count(EventType.AGENT_ACTIVATED)
        assert count["sync"] == 0
    
    def test_event_history(self, event_bus):
        """Test event history tracking"""
        events = [
            Event(type=EventType.AGENT_ACTIVATED, data={"agent": f"agent{i}"}, source="test")
            for i in range(5)
        ]
        
        for event in events:
            event_bus.publish(event)
        
        history = event_bus.get_history()
        assert len(history) == 5
        
        # Test filtered history
        event_bus.publish(Event(type=EventType.PHASE_STARTED, data={}, source="test"))
        
        agent_history = event_bus.get_history(EventType.AGENT_ACTIVATED)
        assert len(agent_history) == 5
        
        phase_history = event_bus.get_history(EventType.PHASE_STARTED)
        assert len(phase_history) == 1
    
    def test_middleware(self, event_bus):
        """Test event middleware"""
        handler = Mock()
        event_bus.subscribe(EventType.AGENT_ACTIVATED, handler)
        
        # Add middleware that modifies event
        def add_timestamp(event: Event) -> Event:
            event.data["processed_at"] = "2023-01-01"
            return event
        
        event_bus.add_middleware(add_timestamp)
        
        event = Event(type=EventType.AGENT_ACTIVATED, data={}, source="test")
        event_bus.publish(event)
        
        # Check handler received modified event
        called_event = handler.call_args[0][0]
        assert called_event.data["processed_at"] == "2023-01-01"
    
    def test_middleware_filter(self, event_bus):
        """Test middleware filtering events"""
        handler = Mock()
        event_bus.subscribe(EventType.AGENT_ACTIVATED, handler)
        
        # Add middleware that filters events
        def filter_backend(event: Event) -> Event:
            if event.data.get("agent") == "backend":
                return None  # Filter out
            return event
        
        event_bus.add_middleware(filter_backend)
        
        # This should be filtered
        event1 = Event(type=EventType.AGENT_ACTIVATED, data={"agent": "backend"}, source="test")
        event_bus.publish(event1)
        
        # This should pass
        event2 = Event(type=EventType.AGENT_ACTIVATED, data={"agent": "frontend"}, source="test")
        event_bus.publish(event2)
        
        # Only event2 should reach handler
        assert handler.call_count == 1
        assert handler.call_args[0][0].data["agent"] == "frontend"
    
    def test_error_handling(self, event_bus):
        """Test error handling in handlers"""
        def failing_handler(event):
            raise ValueError("Handler error")
        
        error_handler = Mock()
        
        event_bus.subscribe(EventType.AGENT_ACTIVATED, failing_handler)
        event_bus.subscribe(EventType.ERROR_OCCURRED, error_handler)
        
        event = Event(type=EventType.AGENT_ACTIVATED, data={}, source="test")
        event_bus.publish(event)
        
        # Error handler should be called
        error_handler.assert_called_once()
        error_event = error_handler.call_args[0][0]
        assert error_event.type == EventType.ERROR_OCCURRED
        assert "Handler error" in error_event.data["error"]
        assert error_event.data["handler"] == "failing_handler"
    
    def test_correlation_id(self, event_bus):
        """Test correlation ID propagation"""
        handler = Mock()
        event_bus.subscribe(EventType.AGENT_ACTIVATED, handler)
        
        event = Event(
            type=EventType.AGENT_ACTIVATED,
            data={},
            source="test",
            correlation_id="test-correlation-123"
        )
        
        event_bus.publish(event)
        
        called_event = handler.call_args[0][0]
        assert called_event.correlation_id == "test-correlation-123"
    
    def test_decorator_sync(self):
        """Test @on_event decorator for sync handlers"""
        mock_handler = Mock()
        
        @on_event(EventType.WORKFLOW_STARTED)
        def decorated_handler(event):
            mock_handler(event)
        
        event = Event(type=EventType.WORKFLOW_STARTED, data={}, source="test")
        get_event_bus().publish(event)
        
        mock_handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_decorator_async(self):
        """Test @on_event decorator for async handlers"""
        mock_handler = Mock()
        
        @on_event(EventType.WORKFLOW_COMPLETED)
        async def decorated_handler(event):
            mock_handler(event)
        
        event = Event(type=EventType.WORKFLOW_COMPLETED, data={}, source="test")
        await get_event_bus().publish_async(event)
        
        # Give async handler time to execute
        await asyncio.sleep(0.1)
        
        mock_handler.assert_called_once()