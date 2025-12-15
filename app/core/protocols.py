# --- protocols.py ---
"""Protocol definitions for duck typing and type safety."""
from typing import Protocol, runtime_checkable, Any, Dict, List, Optional
from abc import ABC
import pandas as pd


@runtime_checkable
class DataFrameLike(Protocol):
    """Protocol for DataFrame-like objects."""
    
    def __len__(self) -> int:
        """Return number of rows."""
        ...
    
    @property
    def columns(self) -> Any:
        """Return column names."""
        ...
    
    def __getitem__(self, key: Any) -> Any:
        """Get column or slice."""
        ...
    
    def copy(self) -> Any:
        """Return a copy."""
        ...


@runtime_checkable
class FileHandler(Protocol):
    """Protocol for file handling operations."""
    
    def read(self, size: Optional[int] = None) -> bytes:
        """Read file content."""
        ...
    
    def seek(self, position: int) -> int:
        """Seek to position."""
        ...
    
    def tell(self) -> int:
        """Get current position."""
        ...
    
    @property
    def name(self) -> str:
        """Get filename."""
        ...


@runtime_checkable
class Validator(Protocol):
    """Protocol for validation operations."""
    
    def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate data and return results."""
        ...
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get validator metadata."""
        ...


@runtime_checkable
class Transformer(Protocol):
    """Protocol for data transformation operations."""
    
    def transform(
        self,
        data: Any,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Transform data and return result."""
        ...
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get transformer metadata."""
        ...


@runtime_checkable
class Mapper(Protocol):
    """Protocol for field mapping operations."""
    
    def map_fields(
        self,
        source_data: Any,
        target_fields: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Map source fields to target fields."""
        ...
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get mapper metadata."""
        ...


@runtime_checkable
class Cacheable(Protocol):
    """Protocol for cacheable objects."""
    
    def get_cache_key(self) -> str:
        """Get cache key for this object."""
        ...
    
    def is_cacheable(self) -> bool:
        """Check if object can be cached."""
        ...


@runtime_checkable
class Serializable(Protocol):
    """Protocol for serializable objects."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create from dictionary."""
        ...


@runtime_checkable
class Configurable(Protocol):
    """Protocol for configurable objects."""
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure object with settings."""
        ...
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        ...


@runtime_checkable
class Observable(Protocol):
    """Protocol for observable objects (Observer pattern)."""
    
    def subscribe(self, observer: Any) -> None:
        """Subscribe an observer."""
        ...
    
    def unsubscribe(self, observer: Any) -> None:
        """Unsubscribe an observer."""
        ...
    
    def notify(self, event: Any) -> None:
        """Notify all observers."""
        ...


@runtime_checkable
class Repository(Protocol):
    """Protocol for repository pattern."""
    
    def save(self, item: Any, item_id: str) -> bool:
        """Save an item."""
        ...
    
    def get(self, item_id: str) -> Optional[Any]:
        """Get an item by ID."""
        ...
    
    def delete(self, item_id: str) -> bool:
        """Delete an item."""
        ...
    
    def list_all(self) -> List[Any]:
        """List all items."""
        ...


@runtime_checkable
class Service(Protocol):
    """Protocol for service layer."""
    
    def execute(self, operation: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a service operation."""
        ...
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data."""
        ...


# Type aliases using protocols
DataFrameType = pd.DataFrame | DataFrameLike
FileType = FileHandler
ValidatorType = Validator
TransformerType = Transformer
MapperType = Mapper


# Utility functions for protocol checking
def implements_protocol(obj: Any, protocol: type[Protocol]) -> bool:
    """
    Check if object implements a protocol.
    
    Args:
        obj: Object to check
        protocol: Protocol class
    
    Returns:
        True if object implements protocol
    """
    if not hasattr(protocol, '__runtime_checkable__'):
        return False
    
    return isinstance(obj, protocol)


def require_protocol(obj: Any, protocol: type[Protocol], name: str = "object") -> None:
    """
    Require that an object implements a protocol.
    
    Args:
        obj: Object to check
        protocol: Protocol class
        name: Name for error message
    
    Raises:
        TypeError: If object doesn't implement protocol
    """
    if not implements_protocol(obj, protocol):
        raise TypeError(
            f"{name} must implement {protocol.__name__} protocol"
        )

