"""Audit logging utility module to avoid circular imports."""
from typing import Any
from state_manager import SessionStateManager


def log_event(event_type: str, message: str) -> None:
    """Log an event to the in-memory audit log.

    Args:
        event_type: Type of event (e.g., "file_upload", "mapping", "validation", "output")
        message: Descriptive message about the event
    """
    try:
        SessionStateManager.add_audit_event(event_type, message)
    except Exception as e:
        # Log to console for debugging instead of silently failing
        import sys
        print(f"Error logging event: {e}", file=sys.stderr)

