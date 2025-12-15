# --- notification_center.py ---
"""Centralized notification system with persistence and categorization."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import streamlit as st


class NotificationType(Enum):
    """Notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    """Represents a notification."""
    id: str
    message: str
    notification_type: NotificationType
    timestamp: datetime
    persistent: bool = False
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    read: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "message": self.message,
            "type": self.notification_type.value,
            "timestamp": self.timestamp.isoformat(),
            "persistent": self.persistent,
            "action_url": self.action_url,
            "action_label": self.action_label,
            "metadata": self.metadata,
            "read": self.read
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            message=data["message"],
            notification_type=NotificationType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            persistent=data.get("persistent", False),
            action_url=data.get("action_url"),
            action_label=data.get("action_label"),
            metadata=data.get("metadata", {}),
            read=data.get("read", False)
        )


class NotificationCenter:
    """Centralized notification management system."""
    
    def __init__(self, max_notifications: int = 100):
        self.max_notifications = max_notifications
        self._notifications: List[Notification] = []
    
    def add_notification(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        persistent: bool = False,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a notification.
        
        Args:
            message: Notification message
            notification_type: Type of notification
            persistent: Whether notification should persist
            action_url: Optional action URL
            action_label: Optional action label
            metadata: Optional metadata
        
        Returns:
            Notification ID
        """
        notification_id = f"notif_{len(self._notifications)}_{datetime.now().timestamp()}"
        notification = Notification(
            id=notification_id,
            message=message,
            notification_type=notification_type,
            timestamp=datetime.now(),
            persistent=persistent,
            action_url=action_url,
            action_label=action_label,
            metadata=metadata or {}
        )
        
        self._notifications.insert(0, notification)  # Add to beginning
        
        # Limit notifications
        if len(self._notifications) > self.max_notifications:
            # Remove oldest non-persistent notifications first
            non_persistent = [n for n in self._notifications if not n.persistent]
            if non_persistent:
                self._notifications.remove(non_persistent[-1])
            else:
                self._notifications.pop()
        
        return notification_id
    
    def get_notifications(
        self,
        notification_type: Optional[NotificationType] = None,
        unread_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Notification]:
        """
        Get notifications with optional filtering.
        
        Args:
            notification_type: Filter by type
            unread_only: Return only unread notifications
            limit: Maximum number of notifications to return
        
        Returns:
            List of notifications
        """
        notifications = self._notifications
        
        if notification_type:
            notifications = [n for n in notifications if n.notification_type == notification_type]
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    def mark_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        for notification in self._notifications:
            if notification.id == notification_id:
                notification.read = True
                return True
        return False
    
    def mark_all_read(self) -> None:
        """Mark all notifications as read."""
        for notification in self._notifications:
            notification.read = True
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification."""
        for i, notification in enumerate(self._notifications):
            if notification.id == notification_id:
                self._notifications.pop(i)
                return True
        return False
    
    def clear_notifications(self, persistent_only: bool = False) -> None:
        """Clear notifications."""
        if persistent_only:
            self._notifications = [n for n in self._notifications if n.persistent]
        else:
            self._notifications.clear()
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications."""
        return len([n for n in self._notifications if not n.read])
    
    def get_notification_summary(self) -> Dict[str, Any]:
        """Get notification summary statistics."""
        total = len(self._notifications)
        unread = self.get_unread_count()
        by_type = {
            NotificationType.INFO.value: len([n for n in self._notifications if n.notification_type == NotificationType.INFO]),
            NotificationType.SUCCESS.value: len([n for n in self._notifications if n.notification_type == NotificationType.SUCCESS]),
            NotificationType.WARNING.value: len([n for n in self._notifications if n.notification_type == NotificationType.WARNING]),
            NotificationType.ERROR.value: len([n for n in self._notifications if n.notification_type == NotificationType.ERROR])
        }
        
        return {
            "total": total,
            "unread": unread,
            "read": total - unread,
            "by_type": by_type
        }


# Session-based notification center
def get_notification_center() -> NotificationCenter:
    """Get or create notification center in session state."""
    if "notification_center" not in st.session_state:
        st.session_state.notification_center = NotificationCenter()
    return st.session_state.notification_center


def show_notification(
    message: str,
    notification_type: NotificationType = NotificationType.INFO,
    persistent: bool = False,
    action_url: Optional[str] = None,
    action_label: Optional[str] = None
) -> str:
    """
    Show a notification (convenience function).
    
    Args:
        message: Notification message
        notification_type: Type of notification
        persistent: Whether notification should persist
        action_url: Optional action URL
        action_label: Optional action label
    
    Returns:
        Notification ID
    """
    center = get_notification_center()
    return center.add_notification(
        message=message,
        notification_type=notification_type,
        persistent=persistent,
        action_url=action_url,
        action_label=action_label
    )


def render_notification_center() -> None:
    """Render notification center UI."""
    center = get_notification_center()
    unread_count = center.get_unread_count()
    
    # Notification bell icon with badge
    col1, col2 = st.columns([1, 10])
    with col1:
        badge = f"🔔 ({unread_count})" if unread_count > 0 else "🔔"
        if st.button(badge, key="notification_center_toggle", use_container_width=True):
            st.session_state["notification_center_open"] = not st.session_state.get("notification_center_open", False)
    
    # Show notification center if open
    if st.session_state.get("notification_center_open", False):
        with st.expander("📬 Notifications", expanded=True):
            notifications = center.get_notifications(limit=20)
            
            if not notifications:
                st.info("No notifications")
            else:
                for notification in notifications:
                    # Determine icon and color based on type
                    icons = {
                        NotificationType.INFO: "ℹ️",
                        NotificationType.SUCCESS: "✅",
                        NotificationType.WARNING: "⚠️",
                        NotificationType.ERROR: "❌"
                    }
                    colors = {
                        NotificationType.INFO: "#2196F3",
                        NotificationType.SUCCESS: "#4CAF50",
                        NotificationType.WARNING: "#FF9800",
                        NotificationType.ERROR: "#F44336"
                    }
                    
                    icon = icons.get(notification.notification_type, "ℹ️")
                    color = colors.get(notification.notification_type, "#757575")
                    read_style = "opacity: 0.6;" if notification.read else ""
                    
                    col1, col2, col3 = st.columns([10, 1, 1])
                    with col1:
                        st.markdown(f"""
                            <div style="
                                background-color: #f5f5f5;
                                padding: 0.5rem;
                                border-radius: 4px;
                                margin-bottom: 0.5rem;
                                border-left: 3px solid {color};
                                {read_style}
                            ">
                                <div style="color: {color}; font-weight: 600;">
                                    {icon} {notification.message}
                                </div>
                                <div style="color: #666; font-size: 0.8em; margin-top: 0.25rem;">
                                    {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if not notification.read:
                            if st.button("✓", key=f"read_{notification.id}", help="Mark as read"):
                                center.mark_read(notification.id)
                                st.rerun()
                    
                    with col3:
                        if st.button("×", key=f"delete_{notification.id}", help="Delete"):
                            center.delete_notification(notification.id)
                            st.rerun()
                
                # Actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Mark All Read", use_container_width=True):
                        center.mark_all_read()
                        st.rerun()
                with col2:
                    if st.button("Clear All", use_container_width=True):
                        center.clear_notifications()
                        st.rerun()


# Convenience functions for different notification types
def notify_info(message: str, persistent: bool = False) -> str:
    """Show info notification."""
    return show_notification(message, NotificationType.INFO, persistent)


def notify_success(message: str, persistent: bool = False) -> str:
    """Show success notification."""
    return show_notification(message, NotificationType.SUCCESS, persistent)


def notify_warning(message: str, persistent: bool = True) -> str:
    """Show warning notification."""
    return show_notification(message, NotificationType.WARNING, persistent)


def notify_error(message: str, persistent: bool = True) -> str:
    """Show error notification."""
    return show_notification(message, NotificationType.ERROR, persistent)

