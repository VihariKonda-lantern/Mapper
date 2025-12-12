# --- collaboration.py ---
"""Collaboration and sharing features."""
import streamlit as st
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

st: Any = st


def add_comment(item_type: str, item_id: str, comment: str, 
               author: Optional[str] = None) -> Dict[str, Any]:
    """Add a comment/annotation to an item.
    
    Args:
        item_type: Type of item (mapping, validation, field)
        item_id: Item identifier
        comment: Comment text
        author: Optional author name
        
    Returns:
        Comment dictionary
    """
    comment_obj = {
        "id": f"{item_type}_{item_id}_{datetime.now().timestamp()}",
        "item_type": item_type,
        "item_id": item_id,
        "comment": comment,
        "author": author or "User",
        "timestamp": datetime.now().isoformat(),
        "resolved": False
    }
    
    if "comments" not in st.session_state:
        st.session_state.comments = []
    
    st.session_state.comments.append(comment_obj)
    return comment_obj


def get_comments(item_type: str, item_id: str) -> List[Dict[str, Any]]:
    """Get comments for an item.
    
    Args:
        item_type: Type of item
        item_id: Item identifier
        
    Returns:
        List of comments
    """
    if "comments" not in st.session_state:
        return []
    
    return [
        c for c in st.session_state.comments
        if c["item_type"] == item_type and c["item_id"] == item_id
    ]


def resolve_comment(comment_id: str) -> None:
    """Mark a comment as resolved.
    
    Args:
        comment_id: Comment identifier
    """
    if "comments" not in st.session_state:
        return
    
    for comment in st.session_state.comments:
        if comment["id"] == comment_id:
            comment["resolved"] = True
            break


def create_approval_request(mapping_id: str, mapping_data: Dict[str, Any], 
                           requester: Optional[str] = None,
                           notes: Optional[str] = None) -> Dict[str, Any]:
    """Create an approval request for a mapping.
    
    Args:
        mapping_id: Mapping identifier
        mapping_data: Mapping data
        requester: Requester name
        notes: Optional notes
        
    Returns:
        Approval request dictionary
    """
    request = {
        "id": f"approval_{mapping_id}_{datetime.now().timestamp()}",
        "mapping_id": mapping_id,
        "mapping_data": mapping_data,
        "requester": requester or "User",
        "notes": notes,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_at": None,
        "approved_by": None,
        "rejected_at": None,
        "rejected_by": None,
        "rejection_reason": None
    }
    
    if "approval_requests" not in st.session_state:
        st.session_state.approval_requests = []
    
    st.session_state.approval_requests.append(request)
    return request


def approve_mapping(request_id: str, approver: Optional[str] = None) -> bool:
    """Approve a mapping request.
    
    Args:
        request_id: Request identifier
        approver: Approver name
        
    Returns:
        True if approved successfully
    """
    if "approval_requests" not in st.session_state:
        return False
    
    for request in st.session_state.approval_requests:
        if request["id"] == request_id:
            request["status"] = "approved"
            request["approved_at"] = datetime.now().isoformat()
            request["approved_by"] = approver or "User"
            return True
    
    return False


def reject_mapping(request_id: str, reason: str, 
                 rejector: Optional[str] = None) -> bool:
    """Reject a mapping request.
    
    Args:
        request_id: Request identifier
        reason: Rejection reason
        rejector: Rejector name
        
    Returns:
        True if rejected successfully
    """
    if "approval_requests" not in st.session_state:
        return False
    
    for request in st.session_state.approval_requests:
        if request["id"] == request_id:
            request["status"] = "rejected"
            request["rejected_at"] = datetime.now().isoformat()
            request["rejected_by"] = rejector or "User"
            request["rejection_reason"] = reason
            return True
    
    return False


def track_change(item_type: str, item_id: str, change_type: str,
                old_value: Any, new_value: Any, user: Optional[str] = None) -> None:
    """Track a change to an item.
    
    Args:
        item_type: Type of item
        item_id: Item identifier
        change_type: Type of change (created, updated, deleted)
        old_value: Old value
        new_value: New value
        user: User who made the change
    """
    change = {
        "id": f"change_{item_id}_{datetime.now().timestamp()}",
        "item_type": item_type,
        "item_id": item_id,
        "change_type": change_type,
        "old_value": old_value,
        "new_value": new_value,
        "user": user or "User",
        "timestamp": datetime.now().isoformat()
    }
    
    if "change_history" not in st.session_state:
        st.session_state.change_history = []
    
    st.session_state.change_history.append(change)
    
    # Limit history size
    if len(st.session_state.change_history) > 1000:
        st.session_state.change_history = st.session_state.change_history[-1000:]


def get_change_history(item_type: Optional[str] = None, 
                      item_id: Optional[str] = None,
                      limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get change history.
    
    Args:
        item_type: Optional filter by item type
        item_id: Optional filter by item ID
        limit: Optional limit number of results
        
    Returns:
        List of changes
    """
    if "change_history" not in st.session_state:
        return []
    
    changes = st.session_state.change_history
    
    if item_type:
        changes = [c for c in changes if c["item_type"] == item_type]
    
    if item_id:
        changes = [c for c in changes if c["item_id"] == item_id]
    
    if limit:
        changes = changes[:limit]
    
    return changes


def generate_mapping_documentation(mapping: Dict[str, Dict[str, Any]],
                                  layout_df: Any,
                                  metadata: Optional[Dict[str, Any]] = None) -> str:
    """Generate mapping documentation.
    
    Args:
        mapping: Mapping dictionary
        layout_df: Layout DataFrame
        metadata: Optional metadata
        
    Returns:
        Documentation string (Markdown format)
    """
    doc_lines = []
    doc_lines.append("# Field Mapping Documentation\n")
    doc_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if metadata:
        doc_lines.append("## Metadata\n")
        for key, value in metadata.items():
            doc_lines.append(f"- **{key}**: {value}\n")
    
    doc_lines.append("\n## Field Mappings\n\n")
    doc_lines.append("| Internal Field | Source Column | Required | Mode |\n")
    doc_lines.append("|----------------|---------------|----------|------|\n")
    
    # Get required fields
    required_fields = set()
    if layout_df is not None and "Usage" in layout_df.columns:
        required_fields = set(
            layout_df[layout_df["Usage"].astype(str).str.lower() == "required"]["Internal Field"].tolist()
        )
    
    for field, mapping_info in sorted(mapping.items()):
        source_col = mapping_info.get("value", "")
        is_required = "Yes" if field in required_fields else "No"
        mode = mapping_info.get("mode", "manual")
        doc_lines.append(f"| {field} | {source_col} | {is_required} | {mode} |\n")
    
    doc_lines.append("\n## Summary\n\n")
    total_fields = len(mapping)
    mapped_fields = len([f for f in mapping.values() if f.get("value")])
    required_mapped = len([f for f, info in mapping.items() 
                          if f in required_fields and info.get("value")])
    total_required = len(required_fields)
    
    doc_lines.append(f"- **Total Fields**: {total_fields}\n")
    doc_lines.append(f"- **Mapped Fields**: {mapped_fields}\n")
    doc_lines.append(f"- **Required Fields Mapped**: {required_mapped}/{total_required}\n")
    doc_lines.append(f"- **Mapping Coverage**: {(mapped_fields/total_fields*100):.1f}%\n")
    
    return "".join(doc_lines)

