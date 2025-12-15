# --- event_system.py ---
"""Observer pattern implementation for event handling."""
from typing import Any, Callable, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class EventType(Enum):
    """Event types in the system."""
    FILE_UPLOADED = "file_uploaded"
    FILE_PROCESSED = "file_processed"
    MAPPING_CREATED = "mapping_created"
    MAPPING_UPDATED = "mapping_updated"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    TRANSFORMATION_STARTED = "transformation_started"
    TRANSFORMATION_COMPLETED = "transformation_completed"
    ERROR_OCCURRED = "error_occurred"
    STATE_CHANGED = "state_changed"
    USER_ACTION = "user_action"


@dataclass
class Event:
    """Represents an event in the system."""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source,
            "metadata": self.metadata
        }


class EventObserver(Protocol):
    """Protocol for event observers."""
    
    def on_event(self, event: Event) -> None:
        """Handle an event."""
        ...


class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    def handle(self, event: Event) -> None:
        """Handle an event."""
        pass


class EventBus:
    """Event bus for managing events and observers (Observer Pattern)."""
    
    def __init__(self):
        self._observers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._global_observers: List[Callable[[Event], None]] = []
        self._event_history: List[Event] = []
        self._max_history: int = 1000
        self._enabled: bool = True
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], None],
        priority: int = 0
    ) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event occurs
            priority: Handler priority (higher = called first)
        """
        if event_type not in self._observers:
            self._observers[event_type] = []
        
        # Insert based on priority
        self._observers[event_type].insert(
            priority,
            handler
        )
    
    def subscribe_all(self, handler: Callable[[Event], None]) -> None:
        """
        Subscribe to all events.
        
        Args:
            handler: Function to call for all events
        """
        self._global_observers.append(handler)
    
    def unsubscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], None]
    ) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if event_type in self._observers:
            if handler in self._observers[event_type]:
                self._observers[event_type].remove(handler)
    
    def unsubscribe_all(self, handler: Callable[[Event], None]) -> None:
        """
        Unsubscribe from all events.
        
        Args:
            handler: Handler to remove
        """
        if handler in self._global_observers:
            self._global_observers.remove(handler)
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        if not self._enabled:
            return
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notify global observers
        for handler in self._global_observers:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't stop other handlers
                print(f"Error in global event handler: {e}")
        
        # Notify specific observers
        handlers = self._observers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't stop other handlers
                print(f"Error in event handler for {event.event_type.value}: {e}")
    
    def emit(
        self,
        event_type: EventType,
        data: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        Create and publish an event.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Event source
            metadata: Additional metadata
        
        Returns:
            Created event
        """
        event = Event(
            event_type=event_type,
            timestamp=datetime.now(),
            data=data or {},
            source=source,
            metadata=metadata or {}
        )
        self.publish(event)
        return event
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
        
        Returns:
            List of events
        """
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def enable(self) -> None:
        """Enable event bus."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable event bus."""
        self._enabled = False
    
    def get_subscriber_count(self, event_type: Optional[EventType] = None) -> int:
        """
        Get number of subscribers.
        
        Args:
            event_type: Optional event type to count
        
        Returns:
            Number of subscribers
        """
        if event_type:
            return len(self._observers.get(event_type, []))
        return sum(len(handlers) for handlers in self._observers.values()) + len(self._global_observers)


class EventHandlerRegistry:
    """Registry for event handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, EventHandler] = {}
    
    def register(self, name: str, handler: EventHandler) -> None:
        """Register an event handler."""
        self._handlers[name] = handler
    
    def get_handler(self, name: str) -> Optional[EventHandler]:
        """Get a handler by name."""
        return self._handlers.get(name)
    
    def list_handlers(self) -> List[str]:
        """List all registered handlers."""
        return list(self._handlers.keys())


# Convenience decorator for event handlers
def event_handler(event_type: EventType, priority: int = 0):
    """
    Decorator to register a function as an event handler.
    
    Args:
        event_type: Type of event to handle
        priority: Handler priority
    
    Example:
        @event_handler(EventType.FILE_UPLOADED)
        def handle_file_upload(event: Event):
            print(f"File uploaded: {event.data}")
    """
    def decorator(func: Callable[[Event], None]) -> Callable[[Event], None]:
        # Register with global event bus
        global_event_bus.subscribe(event_type, func, priority)
        return func
    return decorator


# Global event bus instance
global_event_bus = EventBus()
event_handler_registry = EventHandlerRegistry()


# Convenience functions
def emit_event(
    event_type: EventType,
    data: Optional[Dict[str, Any]] = None,
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Event:
    """Emit an event using the global event bus."""
    return global_event_bus.emit(event_type, data, source, metadata)


def subscribe_to_event(
    event_type: EventType,
    handler: Callable[[Event], None],
    priority: int = 0
) -> None:
    """Subscribe to an event type using the global event bus."""
    global_event_bus.subscribe(event_type, handler, priority)


def subscribe_to_all_events(handler: Callable[[Event], None]) -> None:
    """Subscribe to all events using the global event bus."""
    global_event_bus.subscribe_all(handler)

