# --- persistent_storage.py ---
"""Persistent storage utilities for mappings, templates, and configurations."""
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import pickle
from datetime import datetime
from dataclasses import dataclass, asdict
from exceptions import FileError, ConfigurationError
from path_utils import ensure_directory, ensure_file_path, get_file_info
from decorators import log_execution, handle_errors


@dataclass
class StorageMetadata:
    """Metadata for stored items."""
    id: str
    name: str
    item_type: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    tags: List[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "item_type": self.item_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "tags": self.tags,
            "description": self.description,
            "metadata": self.metadata
        }


class PersistentStorage:
    """Persistent storage manager for application data."""
    
    def __init__(self, base_dir: str = "storage"):
        self.base_dir = Path(base_dir)
        ensure_directory(self.base_dir)
        
        # Subdirectories
        self.mappings_dir = self.base_dir / "mappings"
        self.templates_dir = self.base_dir / "templates"
        self.configs_dir = self.base_dir / "configs"
        self.backups_dir = self.base_dir / "backups"
        
        # Ensure directories exist
        for directory in [self.mappings_dir, self.templates_dir, self.configs_dir, self.backups_dir]:
            ensure_directory(directory)
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to save mapping")
    def save_mapping(
        self,
        mapping: Dict[str, Dict[str, Any]],
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        version: int = 1
    ) -> str:
        """
        Save mapping to persistent storage.
        
        Args:
            mapping: Mapping dictionary
            name: Mapping name
            description: Optional description
            tags: Optional tags
            version: Version number
        
        Returns:
            Storage ID
        """
        storage_id = f"mapping_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = self.mappings_dir / f"{storage_id}.json"
        
        metadata = StorageMetadata(
            id=storage_id,
            name=name,
            item_type="mapping",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=version,
            tags=tags or [],
            description=description
        )
        
        data = {
            "metadata": metadata.to_dict(),
            "mapping": mapping
        }
        
        ensure_file_path(file_path)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return storage_id
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to load mapping", return_value=None)
    def load_mapping(self, storage_id: str) -> Optional[Dict[str, Any]]:
        """
        Load mapping from persistent storage.
        
        Args:
            storage_id: Storage ID
        
        Returns:
            Mapping dictionary or None if not found
        """
        file_path = self.mappings_dir / f"{storage_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return data.get("mapping")
    
    def list_mappings(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List all stored mappings.
        
        Args:
            tags: Optional filter by tags
        
        Returns:
            List of mapping metadata
        """
        mappings = []
        
        for file_path in self.mappings_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                    
                    if tags:
                        item_tags = metadata.get("tags", [])
                        if not any(tag in item_tags for tag in tags):
                            continue
                    
                    mappings.append(metadata)
            except Exception:
                continue
        
        return sorted(mappings, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to save template")
    def save_template(
        self,
        template: Dict[str, Any],
        name: str,
        template_type: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Save template to persistent storage.
        
        Args:
            template: Template data
            name: Template name
            template_type: Type of template
            description: Optional description
            tags: Optional tags
        
        Returns:
            Storage ID
        """
        storage_id = f"template_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = self.templates_dir / f"{storage_id}.json"
        
        metadata = StorageMetadata(
            id=storage_id,
            name=name,
            item_type=template_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags or [],
            description=description
        )
        
        data = {
            "metadata": metadata.to_dict(),
            "template": template
        }
        
        ensure_file_path(file_path)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return storage_id
    
    def load_template(self, storage_id: str) -> Optional[Dict[str, Any]]:
        """Load template from persistent storage."""
        file_path = self.templates_dir / f"{storage_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return data.get("template")
    
    def list_templates(self, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all stored templates."""
        templates = []
        
        for file_path in self.templates_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                    
                    if template_type and metadata.get("item_type") != template_type:
                        continue
                    
                    templates.append(metadata)
            except Exception:
                continue
        
        return sorted(templates, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    @log_execution(log_args=False)
    def create_backup(self, item_type: str, item_id: str) -> str:
        """
        Create backup of an item.
        
        Args:
            item_type: Type of item (mapping, template, etc.)
            item_id: Item ID
        
        Returns:
            Backup file path
        """
        if item_type == "mapping":
            source_file = self.mappings_dir / f"{item_id}.json"
            backup_file = self.backups_dir / f"{item_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        elif item_type == "template":
            source_file = self.templates_dir / f"{item_id}.json"
            backup_file = self.backups_dir / f"{item_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            raise FileError(f"Unknown item type: {item_type}", error_code="UNKNOWN_ITEM_TYPE")
        
        if not source_file.exists():
            raise FileError(f"Item not found: {item_id}", error_code="ITEM_NOT_FOUND")
        
        # Copy file
        import shutil
        ensure_file_path(backup_file)
        shutil.copy2(source_file, backup_file)
        
        return str(backup_file)
    
    def restore_backup(self, backup_file: str, item_type: str) -> bool:
        """
        Restore item from backup.
        
        Args:
            backup_file: Path to backup file
            item_type: Type of item
        
        Returns:
            True if successful
        """
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return False
        
        # Extract item ID from backup filename
        item_id = backup_path.stem.split("_backup_")[0]
        
        if item_type == "mapping":
            target_file = self.mappings_dir / f"{item_id}.json"
        elif item_type == "template":
            target_file = self.templates_dir / f"{item_id}.json"
        else:
            return False
        
        # Copy backup to target
        import shutil
        ensure_file_path(target_file)
        shutil.copy2(backup_path, target_file)
        
        return True
    
    def list_backups(self, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all backups."""
        backups = []
        
        for file_path in self.backups_dir.glob("*_backup_*.json"):
            try:
                file_info = get_file_info(file_path)
                backups.append({
                    "file": str(file_path),
                    "name": file_path.name,
                    "size": file_info.get("size", 0),
                    "modified": file_info.get("modified", 0)
                })
            except Exception:
                continue
        
        return sorted(backups, key=lambda x: x.get("modified", 0), reverse=True)
    
    def delete_item(self, item_type: str, item_id: str) -> bool:
        """
        Delete an item from storage.
        
        Args:
            item_type: Type of item
            item_id: Item ID
        
        Returns:
            True if deleted
        """
        if item_type == "mapping":
            file_path = self.mappings_dir / f"{item_id}.json"
        elif item_type == "template":
            file_path = self.templates_dir / f"{item_id}.json"
        else:
            return False
        
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return {
            "mappings_count": len(list(self.mappings_dir.glob("*.json"))),
            "templates_count": len(list(self.templates_dir.glob("*.json"))),
            "backups_count": len(list(self.backups_dir.glob("*.json"))),
            "total_size": sum(
                f.stat().st_size
                for f in self.base_dir.rglob("*.json")
            )
        }


# Global storage instance
persistent_storage = PersistentStorage()

