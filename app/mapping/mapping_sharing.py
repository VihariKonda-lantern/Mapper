"""Mapping sharing with permissions."""
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class Permission(Enum):
    """Permission levels for shared mappings."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class SharedMapping:
    """Represents a shared mapping."""
    mapping_id: str
    owner: str
    mapping_data: Dict[str, Any]
    permissions: Dict[str, Permission] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    description: str = ""
    is_public: bool = False


class MappingShareManager:
    """Manages mapping sharing and permissions."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize share manager.
        
        Args:
            storage_path: Path to store shared mappings
        """
        self.storage_path = storage_path or Path("shared_mappings")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._shared_mappings: Dict[str, SharedMapping] = {}
        self._load_shared_mappings()
    
    def _load_shared_mappings(self) -> None:
        """Load shared mappings from storage."""
        shared_file = self.storage_path / "shared_mappings.json"
        if shared_file.exists():
            try:
                with open(shared_file, 'r') as f:
                    data = json.load(f)
                    for mapping_id, mapping_data in data.items():
                        mapping = self._dict_to_shared_mapping(mapping_id, mapping_data)
                        self._shared_mappings[mapping_id] = mapping
            except Exception:
                pass
    
    def _save_shared_mappings(self) -> None:
        """Save shared mappings to storage."""
        shared_file = self.storage_path / "shared_mappings.json"
        data = {}
        for mapping_id, mapping in self._shared_mappings.items():
            data[mapping_id] = self._shared_mapping_to_dict(mapping)
        
        with open(shared_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _dict_to_shared_mapping(self, mapping_id: str, data: Dict[str, Any]) -> SharedMapping:
        """Convert dictionary to SharedMapping."""
        permissions = {}
        for user, perm_str in data.get("permissions", {}).items():
            permissions[user] = Permission(perm_str)
        
        return SharedMapping(
            mapping_id=mapping_id,
            owner=data["owner"],
            mapping_data=data["mapping_data"],
            permissions=permissions,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            tags=data.get("tags", []),
            description=data.get("description", ""),
            is_public=data.get("is_public", False)
        )
    
    def _shared_mapping_to_dict(self, mapping: SharedMapping) -> Dict[str, Any]:
        """Convert SharedMapping to dictionary."""
        return {
            "owner": mapping.owner,
            "mapping_data": mapping.mapping_data,
            "permissions": {user: perm.value for user, perm in mapping.permissions.items()},
            "created_at": mapping.created_at.isoformat(),
            "updated_at": mapping.updated_at.isoformat(),
            "tags": mapping.tags,
            "description": mapping.description,
            "is_public": mapping.is_public
        }
    
    def share_mapping(
        self,
        mapping_id: str,
        owner: str,
        mapping_data: Dict[str, Any],
        is_public: bool = False,
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> SharedMapping:
        """
        Share a mapping.
        
        Args:
            mapping_id: Unique mapping ID
            owner: Owner username
            mapping_data: Mapping data
            is_public: Whether mapping is publicly accessible
            description: Description of mapping
            tags: Optional tags
        
        Returns:
            SharedMapping object
        """
        shared = SharedMapping(
            mapping_id=mapping_id,
            owner=owner,
            mapping_data=mapping_data,
            is_public=is_public,
            description=description,
            tags=tags or []
        )
        
        self._shared_mappings[mapping_id] = shared
        self._save_shared_mappings()
        
        return shared
    
    def grant_permission(
        self,
        mapping_id: str,
        user: str,
        permission: Permission,
        granted_by: str
    ) -> bool:
        """
        Grant permission to a user.
        
        Args:
            mapping_id: Mapping ID
            user: User to grant permission to
            permission: Permission level
            granted_by: User granting permission
        
        Returns:
            True if successful
        """
        if mapping_id not in self._shared_mappings:
            return False
        
        mapping = self._shared_mappings[mapping_id]
        
        # Check if granted_by has admin permission
        if not self.has_permission(mapping_id, granted_by, Permission.ADMIN):
            return False
        
        mapping.permissions[user] = permission
        mapping.updated_at = datetime.now()
        self._save_shared_mappings()
        
        return True
    
    def revoke_permission(
        self,
        mapping_id: str,
        user: str,
        revoked_by: str
    ) -> bool:
        """
        Revoke permission from a user.
        
        Args:
            mapping_id: Mapping ID
            user: User to revoke permission from
            revoked_by: User revoking permission
        
        Returns:
            True if successful
        """
        if mapping_id not in self._shared_mappings:
            return False
        
        mapping = self._shared_mappings[mapping_id]
        
        # Check if revoked_by has admin permission
        if not self.has_permission(mapping_id, revoked_by, Permission.ADMIN):
            return False
        
        if user in mapping.permissions:
            del mapping.permissions[user]
            mapping.updated_at = datetime.now()
            self._save_shared_mappings()
        
        return True
    
    def has_permission(
        self,
        mapping_id: str,
        user: str,
        required_permission: Permission
    ) -> bool:
        """
        Check if user has required permission.
        
        Args:
            mapping_id: Mapping ID
            user: User to check
            required_permission: Required permission level
        
        Returns:
            True if user has permission
        """
        if mapping_id not in self._shared_mappings:
            return False
        
        mapping = self._shared_mappings[mapping_id]
        
        # Owner has all permissions
        if mapping.owner == user:
            return True
        
        # Public mappings are readable by all
        if mapping.is_public and required_permission == Permission.READ:
            return True
        
        # Check explicit permissions
        if user not in mapping.permissions:
            return False
        
        user_permission = mapping.permissions[user]
        
        # Permission hierarchy: READ < WRITE < ADMIN
        permission_levels = {
            Permission.READ: 1,
            Permission.WRITE: 2,
            Permission.ADMIN: 3
        }
        
        return permission_levels[user_permission] >= permission_levels[required_permission]
    
    def get_shared_mapping(
        self,
        mapping_id: str,
        user: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get shared mapping if user has permission.
        
        Args:
            mapping_id: Mapping ID
            user: User requesting mapping
        
        Returns:
            Mapping data if accessible, None otherwise
        """
        if not self.has_permission(mapping_id, user, Permission.READ):
            return None
        
        mapping = self._shared_mappings[mapping_id]
        return mapping.mapping_data
    
    def list_shared_mappings(
        self,
        user: Optional[str] = None,
        tags: Optional[List[str]] = None,
        public_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List shared mappings accessible to user.
        
        Args:
            user: User to list for (None = all public)
            tags: Filter by tags
            public_only: Only show public mappings
        
        Returns:
            List of mapping summaries
        """
        results = []
        
        for mapping_id, mapping in self._shared_mappings.items():
            # Filter by public
            if public_only and not mapping.is_public:
                continue
            
            # Filter by user access
            if user and not self.has_permission(mapping_id, user, Permission.READ):
                continue
            
            # Filter by tags
            if tags and not any(tag in mapping.tags for tag in tags):
                continue
            
            results.append({
                "mapping_id": mapping_id,
                "owner": mapping.owner,
                "description": mapping.description,
                "tags": mapping.tags,
                "is_public": mapping.is_public,
                "created_at": mapping.created_at,
                "updated_at": mapping.updated_at
            })
        
        return results
    
    def update_mapping(
        self,
        mapping_id: str,
        mapping_data: Dict[str, Any],
        user: str
    ) -> bool:
        """
        Update shared mapping.
        
        Args:
            mapping_id: Mapping ID
            mapping_data: Updated mapping data
            user: User updating mapping
        
        Returns:
            True if successful
        """
        if not self.has_permission(mapping_id, user, Permission.WRITE):
            return False
        
        mapping = self._shared_mappings[mapping_id]
        mapping.mapping_data = mapping_data
        mapping.updated_at = datetime.now()
        self._save_shared_mappings()
        
        return True
    
    def delete_mapping(
        self,
        mapping_id: str,
        user: str
    ) -> bool:
        """
        Delete shared mapping.
        
        Args:
            mapping_id: Mapping ID
            user: User deleting mapping
        
        Returns:
            True if successful
        """
        if mapping_id not in self._shared_mappings:
            return False
        
        mapping = self._shared_mappings[mapping_id]
        
        # Only owner or admin can delete
        if mapping.owner != user and not self.has_permission(mapping_id, user, Permission.ADMIN):
            return False
        
        del self._shared_mappings[mapping_id]
        self._save_shared_mappings()
        
        return True

