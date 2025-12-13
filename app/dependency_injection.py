# --- dependency_injection.py ---
"""Simple dependency injection container."""
from typing import Any, Dict, Callable, Optional, Type, TypeVar, get_type_hints
from functools import wraps
import inspect

T = TypeVar('T')


class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._singleton_flags: Dict[str, bool] = {}
    
    def register(
        self,
        service_name: str,
        service: Any,
        singleton: bool = False
    ) -> None:
        """
        Register a service instance.
        
        Args:
            service_name: Name of the service
            service: Service instance or class
            singleton: Whether to treat as singleton
        """
        self._services[service_name] = service
        self._singleton_flags[service_name] = singleton
        if singleton:
            self._singletons[service_name] = service
    
    def register_factory(
        self,
        service_name: str,
        factory: Callable[[], Any],
        singleton: bool = False
    ) -> None:
        """
        Register a service factory.
        
        Args:
            service_name: Name of the service
            factory: Factory function that creates the service
            singleton: Whether to treat as singleton
        """
        self._factories[service_name] = factory
        self._singleton_flags[service_name] = singleton
    
    def get(self, service_name: str) -> Any:
        """
        Get a service instance.
        
        Args:
            service_name: Name of the service
        
        Returns:
            Service instance
        
        Raises:
            KeyError: If service not found
        """
        # Check if singleton already created
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # Check if factory exists
        if service_name in self._factories:
            instance = self._factories[service_name]()
            if self._singleton_flags.get(service_name, False):
                self._singletons[service_name] = instance
            return instance
        
        # Check if service exists
        if service_name in self._services:
            service = self._services[service_name]
            # If it's a class, instantiate it
            if inspect.isclass(service):
                instance = service()
                if self._singleton_flags.get(service_name, False):
                    self._singletons[service_name] = instance
                return instance
            return service
        
        raise KeyError(f"Service '{service_name}' not found")
    
    def has(self, service_name: str) -> bool:
        """Check if service is registered."""
        return (
            service_name in self._services or
            service_name in self._factories or
            service_name in self._singletons
        )
    
    def inject(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to inject dependencies into function.
        
        Args:
            func: Function to inject dependencies into
        
        Returns:
            Wrapped function with dependencies injected
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Get function signature
            sig = inspect.signature(func)
            hints = get_type_hints(func)
            
            # Inject dependencies from container
            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    continue  # Already provided
                
                # Try to resolve from type hint
                param_type = hints.get(param_name)
                if param_type:
                    # Try to get service by type name
                    type_name = param_type.__name__ if hasattr(param_type, '__name__') else str(param_type)
                    if self.has(type_name):
                        kwargs[param_name] = self.get(type_name)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._singleton_flags.clear()


# Global container instance
container = DIContainer()


def inject_dependencies(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to inject dependencies from global container.
    
    Args:
        func: Function to inject dependencies into
    
    Returns:
        Wrapped function with dependencies injected
    """
    return container.inject(func)


# Example usage and default registrations
def register_default_services() -> None:
    """Register default services in the container."""
    try:
        from cache_manager import CacheManager
        from structured_logging import StructuredLogger
        from state_manager import SessionStateManager
        from processor_factory import processor_factory
        
        # Register as singletons
        container.register("CacheManager", CacheManager(), singleton=True)
        container.register("StructuredLogger", StructuredLogger("app"), singleton=True)
        container.register("SessionStateManager", SessionStateManager, singleton=False)  # Static class
        container.register("ProcessorFactory", processor_factory, singleton=True)
    except ImportError:
        # Silently fail if dependencies aren't available
        pass


# Auto-register defaults on import
try:
    register_default_services()
except Exception:
    pass

