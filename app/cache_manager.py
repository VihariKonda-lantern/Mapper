# --- cache_manager.py ---
"""Unified cache manager with consistent API, invalidation, and metrics."""
import streamlit as st
import hashlib
import json
from typing import Any, Dict, Optional, Callable, TypeVar, Hashable
from datetime import datetime, timedelta
from functools import wraps

st: Any = st

T = TypeVar('T')


class CacheManager:
    """Unified cache manager for the application."""
    
    def __init__(self):
        """Initialize cache manager with metrics tracking."""
        if "cache_metrics" not in st.session_state:
            st.session_state.cache_metrics = {
                "hits": 0,
                "misses": 0,
                "invalidations": 0,
                "total_requests": 0
            }
        if "cache_entries" not in st.session_state:
            st.session_state.cache_entries = {}
    
    def _get_cache_key(self, key: str, *args, **kwargs) -> str:
        """Generate a cache key from function name and arguments.
        
        Args:
            key: Base cache key
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Hashed cache key
        """
        # Create a hash of the arguments
        args_str = json.dumps(args, sort_keys=True, default=str)
        kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
        combined = f"{key}:{args_str}:{kwargs_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache.
        
        Args:
            key: Cache key
            default: Default value if key doesn't exist
            
        Returns:
            Cached value or default
        """
        st.session_state.cache_metrics["total_requests"] += 1
        
        if key in st.session_state.cache_entries:
            entry = st.session_state.cache_entries[key]
            # Check TTL
            if "ttl" in entry and "timestamp" in entry:
                if datetime.now() > entry["timestamp"] + timedelta(seconds=entry["ttl"]):
                    # Expired, remove it
                    del st.session_state.cache_entries[key]
                    st.session_state.cache_metrics["misses"] += 1
                    return default
            
            st.session_state.cache_metrics["hits"] += 1
            return entry.get("value", default)
        
        st.session_state.cache_metrics["misses"] += 1
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
        """
        entry: Dict[str, Any] = {
            "value": value,
            "timestamp": datetime.now()
        }
        if ttl:
            entry["ttl"] = ttl
        
        st.session_state.cache_entries[key] = entry
    
    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        if key in st.session_state.cache_entries:
            del st.session_state.cache_entries[key]
            st.session_state.cache_metrics["invalidations"] += 1
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (substring)
        """
        keys_to_remove = [
            key for key in st.session_state.cache_entries.keys()
            if pattern in key
        ]
        for key in keys_to_remove:
            self.invalidate(key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        st.session_state.cache_entries.clear()
        st.session_state.cache_metrics["invalidations"] += len(st.session_state.cache_entries)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics.
        
        Returns:
            Dictionary with cache metrics
        """
        metrics = st.session_state.cache_metrics.copy()
        total = metrics["total_requests"]
        if total > 0:
            metrics["hit_rate"] = round((metrics["hits"] / total) * 100, 2)
            metrics["miss_rate"] = round((metrics["misses"] / total) * 100, 2)
        else:
            metrics["hit_rate"] = 0.0
            metrics["miss_rate"] = 0.0
        metrics["cache_size"] = len(st.session_state.cache_entries)
        return metrics


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance.
    
    Returns:
        CacheManager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached(key_prefix: str, ttl: Optional[int] = None):
    """Decorator for caching function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = get_cache_manager()
            cache_key = cache._get_cache_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key: str) -> None:
    """Invalidate a cache entry by key.
    
    Args:
        key: Cache key to invalidate
    """
    get_cache_manager().invalidate(key)


def invalidate_cache_pattern(pattern: str) -> None:
    """Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Pattern to match
    """
    get_cache_manager().invalidate_pattern(pattern)

