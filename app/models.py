# --- models.py ---
"""Domain models using dataclasses for core entities."""
from dataclasses import dataclass, field as dataclass_field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class FieldUsage(Enum):
    """Field usage types."""
    MANDATORY = "mandatory"
    OPTIONAL = "optional"


class MappingMode(Enum):
    """Mapping mode types."""
    MANUAL = "manual"
    AUTO = "auto"
    TEMPLATE = "template"


class ValidationStatus(Enum):
    """Validation status types."""
    PASS = "Pass"
    WARNING = "Warning"
    FAIL = "Fail"
    ERROR = "Error"


@dataclass
class Field:
    """Represents a field definition."""
    internal_name: str
    data_type: str
    usage: FieldUsage
    description: Optional[str] = None
    example: Optional[str] = None
    validation_rules: List[str] = dataclass_field(default_factory=list)


@dataclass
class Mapping:
    """Represents a field mapping."""
    internal_field: str
    source_column: str
    mode: MappingMode
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format used in session state."""
        return {
            "value": self.source_column,
            "mode": self.mode.value,
            "confidence": self.confidence_score
        }


@dataclass
class ValidationResult:
    """Represents a validation result."""
    check_name: str
    status: ValidationStatus
    field: Optional[str] = None
    message: str = ""
    fail_count: int = 0
    total_count: int = 0
    fail_percentage: float = 0.0
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "check": self.check_name,
            "status": self.status.value,
            "field": self.field,
            "message": self.message,
            "fail_count": self.fail_count,
            "total_count": self.total_count,
            "fail_pct": f"{self.fail_percentage:.2f}",
            **self.metadata
        }


@dataclass
class FileMetadata:
    """Represents file metadata."""
    filename: str
    size_bytes: int
    uploaded_at: datetime
    file_type: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    encoding: Optional[str] = None
    delimiter: Optional[str] = None
    
    @property
    def size_mb(self) -> float:
        """Get file size in MB."""
        return self.size_bytes / (1024 * 1024)


@dataclass
class DataQualityScore:
    """Represents data quality metrics."""
    overall_score: float
    completeness: float
    uniqueness: float
    consistency: float
    timeliness: Optional[float] = None
    validity: Optional[float] = None
    breakdown: Dict[str, Any] = dataclass_field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "overall_score": self.overall_score,
            "breakdown": {
                "completeness": self.completeness,
                "uniqueness": self.uniqueness,
                "consistency": self.consistency,
                "timeliness": self.timeliness,
                "validity": self.validity,
                **self.breakdown
            }
        }


@dataclass
class AuditEvent:
    """Represents an audit log event."""
    event_type: str
    message: str
    timestamp: datetime
    user_id: Optional[str] = None
    context: Dict[str, Any] = dataclass_field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "event_type": self.event_type,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            **self.context
        }

