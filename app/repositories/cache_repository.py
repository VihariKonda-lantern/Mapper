# --- repositories/cache_repository.py ---
"""Repository for cache operations."""
from typing import Any, Optional
from abc import ABC, abstractmethod
from cache_manager import CacheManager


class CacheRepository(ABC):
    """Abstract base class for cache repositories."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache."""
        pass


class StreamlitCacheRepository(CacheRepository):
    """Cache repository implementation using CacheManager."""
    
    def __init__(self) -> None:
        self.cache = CacheManager()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        self.cache.set(key, value, ttl=ttl)
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.cache.delete(key)
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear_all()

