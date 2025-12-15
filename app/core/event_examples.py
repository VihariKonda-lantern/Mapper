# --- event_examples.py ---
"""Examples of using the event system."""
from typing import Any
from core.event_system import (
    EventType,
    Event,
    global_event_bus,
    emit_event,
    subscribe_to_event,
    event_handler
)


# Example 1: Using decorator
@event_handler(EventType.FILE_UPLOADED)
def handle_file_upload(event: Event) -> None:
    """Handle file upload events."""
    print(f"File uploaded: {event.data.get('filename')}")
    # Log to audit log, update UI, etc.


# Example 2: Manual subscription
def handle_validation_complete(event: Event) -> None:
    """Handle validation completion."""
    results = event.data.get('results', [])
    print(f"Validation completed: {len(results)} checks")
    # Update validation tab, show notifications, etc.


# Subscribe to validation events
subscribe_to_event(EventType.VALIDATION_COMPLETED, handle_validation_complete)


# Example 3: Subscribe to all events
def log_all_events(event: Event) -> None:
    """Log all events for debugging."""
    print(f"[EVENT] {event.event_type.value}: {event.data}")


global_event_bus.subscribe_all(log_all_events)


# Example 4: Emitting events
def example_file_upload(filename: str) -> None:
    """Example: Emit file upload event."""
    emit_event(
        EventType.FILE_UPLOADED,
        data={"filename": filename, "size": 1024},
        source="file_handler",
        metadata={"user_id": "user123"}
    )


def example_validation_start(df_size: int) -> None:
    """Example: Emit validation start event."""
    emit_event(
        EventType.VALIDATION_STARTED,
        data={"record_count": df_size},
        source="validation_engine"
    )


def example_error(error: Exception, context: dict[str, Any]) -> None:
    """Example: Emit error event."""
    emit_event(
        EventType.ERROR_OCCURRED,
        data={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        },
        source="error_handler"
    )


# Example 5: Class-based event handler
class ValidationEventHandler:
    """Event handler for validation-related events."""
    
    def __init__(self):
        # Subscribe to events
        subscribe_to_event(EventType.VALIDATION_STARTED, self.on_validation_start)
        subscribe_to_event(EventType.VALIDATION_COMPLETED, self.on_validation_complete)
    
    def on_validation_start(self, event: Event) -> None:
        """Handle validation start."""
        print(f"Starting validation for {event.data.get('record_count')} records")
        # Show progress indicator, disable UI, etc.
    
    def on_validation_complete(self, event: Event) -> None:
        """Handle validation complete."""
        results = event.data.get('results', [])
        print(f"Validation complete: {len(results)} results")
        # Update UI, show notifications, etc.


# Initialize handler
validation_handler = ValidationEventHandler()


# Example 6: Get event history
def get_recent_events(event_type: EventType, limit: int = 10) -> list[Event]:
    """Get recent events of a specific type."""
    return global_event_bus.get_history(event_type=event_type, limit=limit)


# Example 7: Integration with existing code
def integrate_with_file_upload() -> None:
    """Example integration with file upload."""
    # In file upload handler:
    # After successful upload:
    emit_event(
        EventType.FILE_UPLOADED,
        data={
            "filename": "claims.csv",
            "size": 1024000,
            "rows": 50000
        },
        source="upload_handler"
    )


def integrate_with_validation() -> None:
    """Example integration with validation."""
    # Before validation:
    emit_event(
        EventType.VALIDATION_STARTED,
        data={"record_count": 50000},
        source="validation_engine"
    )
    
    # After validation:
    emit_event(
        EventType.VALIDATION_COMPLETED,
        data={
            "results": [...],  # validation results
            "execution_time": 2.5
        },
        source="validation_engine"
    )

