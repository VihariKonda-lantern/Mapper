# --- mapping_management.py ---
"""Enhanced mapping management with versioning, comparison, and analytics."""
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import hashlib
import json
from models import Mapping, MappingMode
from decorators import log_execution, handle_errors
from exceptions import MappingError


@dataclass
class MappingVersion:
    """Represents a version of a mapping."""
    version_id: str
    mapping: Dict[str, Dict[str, Any]]
    created_at: datetime
    created_by: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_hash(self) -> str:
        """Get hash of mapping for comparison."""
        mapping_str = json.dumps(self.mapping, sort_keys=True)
        return hashlib.md5(mapping_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "mapping": self.mapping,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "description": self.description,
            "metadata": self.metadata,
            "hash": self.get_hash()
        }


class MappingVersionManager:
    """Manager for mapping versions."""
    
    def __init__(self, max_versions: int = 50):
        self.versions: Dict[str, List[MappingVersion]] = {}  # mapping_name -> versions
        self.max_versions = max_versions
    
    @log_execution(log_args=False)
    def create_version(
        self,
        mapping_name: str,
        mapping: Dict[str, Dict[str, Any]],
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> MappingVersion:
        """
        Create a new version of a mapping.
        
        Args:
            mapping_name: Name of the mapping
            mapping: Mapping dictionary
            description: Version description
            created_by: Creator identifier
        
        Returns:
            Created MappingVersion
        """
        version_id = f"v{len(self.versions.get(mapping_name, [])) + 1}"
        version = MappingVersion(
            version_id=version_id,
            mapping=mapping.copy(),
            created_at=datetime.now(),
            created_by=created_by,
            description=description
        )
        
        if mapping_name not in self.versions:
            self.versions[mapping_name] = []
        
        self.versions[mapping_name].append(version)
        
        # Limit versions
        if len(self.versions[mapping_name]) > self.max_versions:
            self.versions[mapping_name].pop(0)
        
        return version
    
    def get_versions(self, mapping_name: str) -> List[MappingVersion]:
        """Get all versions of a mapping."""
        return self.versions.get(mapping_name, [])
    
    def get_version(self, mapping_name: str, version_id: str) -> Optional[MappingVersion]:
        """Get a specific version."""
        versions = self.get_versions(mapping_name)
        for version in versions:
            if version.version_id == version_id:
                return version
        return None
    
    def compare_versions(
        self,
        mapping_name: str,
        version_id1: str,
        version_id2: str
    ) -> Dict[str, Any]:
        """
        Compare two mapping versions.
        
        Args:
            mapping_name: Name of the mapping
            version_id1: First version ID
            version_id2: Second version ID
        
        Returns:
            Comparison results
        """
        v1 = self.get_version(mapping_name, version_id1)
        v2 = self.get_version(mapping_name, version_id2)
        
        if not v1 or not v2:
            return {"error": "One or both versions not found"}
        
        mapping1 = v1.mapping
        mapping2 = v2.mapping
        
        # Find differences
        all_fields = set(mapping1.keys()) | set(mapping2.keys())
        added = []
        removed = []
        changed = []
        
        for field in all_fields:
            if field not in mapping1:
                added.append(field)
            elif field not in mapping2:
                removed.append(field)
            elif mapping1[field] != mapping2[field]:
                changed.append({
                    "field": field,
                    "old": mapping1[field],
                    "new": mapping2[field]
                })
        
        return {
            "version1": v1.version_id,
            "version2": v2.version_id,
            "added_fields": added,
            "removed_fields": removed,
            "changed_fields": changed,
            "total_changes": len(added) + len(removed) + len(changed)
        }
    
    def merge_versions(
        self,
        mapping_name: str,
        version_id1: str,
        version_id2: str,
        conflict_resolution: str = "prefer_v1"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Merge two mapping versions.
        
        Args:
            mapping_name: Name of the mapping
            version_id1: First version ID
            version_id2: Second version ID
            conflict_resolution: How to resolve conflicts ("prefer_v1", "prefer_v2", "manual")
        
        Returns:
            Merged mapping
        """
        v1 = self.get_version(mapping_name, version_id1)
        v2 = self.get_version(mapping_name, version_id2)
        
        if not v1 or not v2:
            raise MappingError("One or both versions not found", error_code="VERSION_NOT_FOUND")
        
        merged = v1.mapping.copy()
        
        # Add fields from v2 that don't exist in v1
        for field, mapping_info in v2.mapping.items():
            if field not in merged:
                merged[field] = mapping_info
            elif conflict_resolution == "prefer_v2":
                merged[field] = mapping_info
        
        return merged


@dataclass
class MappingTemplate:
    """Rich template for mappings with metadata."""
    name: str
    description: str
    mapping: Dict[str, Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "mapping": self.mapping,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "category": self.category,
            "usage_count": self.usage_count,
            "metadata": self.metadata
        }
    
    def increment_usage(self) -> None:
        """Increment usage count."""
        self.usage_count += 1
        self.updated_at = datetime.now()


class MappingTemplateManager:
    """Manager for mapping templates."""
    
    def __init__(self):
        self.templates: Dict[str, MappingTemplate] = {}
    
    def save_template(
        self,
        name: str,
        mapping: Dict[str, Dict[str, Any]],
        description: str = "",
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> MappingTemplate:
        """Save a mapping template."""
        if name in self.templates:
            template = self.templates[name]
            template.mapping = mapping.copy()
            template.description = description
            template.updated_at = datetime.now()
            if tags:
                template.tags = tags
            if category:
                template.category = category
        else:
            template = MappingTemplate(
                name=name,
                description=description,
                mapping=mapping.copy(),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=tags or [],
                category=category
            )
            self.templates[name] = template
        
        return template
    
    def load_template(self, name: str) -> Optional[MappingTemplate]:
        """Load a mapping template."""
        template = self.templates.get(name)
        if template:
            template.increment_usage()
        return template
    
    def list_templates(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List templates with optional filtering."""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if tag:
            templates = [t for t in templates if tag in t.tags]
        
        # Sort by usage count (most used first)
        templates.sort(key=lambda x: x.usage_count, reverse=True)
        
        return [t.to_dict() for t in templates]
    
    def delete_template(self, name: str) -> bool:
        """Delete a template."""
        if name in self.templates:
            del self.templates[name]
            return True
        return False


class MappingAnalytics:
    """Analytics for mapping usage and success rates."""
    
    def __init__(self):
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self.success_stats: Dict[str, Dict[str, Any]] = {}
    
    def track_usage(
        self,
        mapping_name: str,
        success: bool,
        confidence_score: Optional[float] = None
    ) -> None:
        """Track mapping usage."""
        if mapping_name not in self.usage_stats:
            self.usage_stats[mapping_name] = {
                "total_uses": 0,
                "successful_uses": 0,
                "failed_uses": 0,
                "avg_confidence": 0.0,
                "confidence_scores": []
            }
        
        stats = self.usage_stats[mapping_name]
        stats["total_uses"] += 1
        
        if success:
            stats["successful_uses"] += 1
        else:
            stats["failed_uses"] += 1
        
        if confidence_score is not None:
            stats["confidence_scores"].append(confidence_score)
            stats["avg_confidence"] = sum(stats["confidence_scores"]) / len(stats["confidence_scores"])
    
    def get_success_rate(self, mapping_name: str) -> float:
        """Get success rate for a mapping."""
        if mapping_name not in self.usage_stats:
            return 0.0
        
        stats = self.usage_stats[mapping_name]
        if stats["total_uses"] == 0:
            return 0.0
        
        return (stats["successful_uses"] / stats["total_uses"]) * 100
    
    def get_analytics(self, mapping_name: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for mapping(s)."""
        if mapping_name:
            if mapping_name not in self.usage_stats:
                return {}
            
            stats = self.usage_stats[mapping_name]
            return {
                "mapping_name": mapping_name,
                "total_uses": stats["total_uses"],
                "successful_uses": stats["successful_uses"],
                "failed_uses": stats["failed_uses"],
                "success_rate": self.get_success_rate(mapping_name),
                "avg_confidence": stats["avg_confidence"]
            }
        else:
            return {
                "all_mappings": {
                    name: {
                        "total_uses": stats["total_uses"],
                        "success_rate": self.get_success_rate(name),
                        "avg_confidence": stats["avg_confidence"]
                    }
                    for name, stats in self.usage_stats.items()
                }
            }


# Global managers
mapping_version_manager = MappingVersionManager()
mapping_template_manager = MappingTemplateManager()
mapping_analytics = MappingAnalytics()

