# --- config_loader.py ---
"""Configuration loader with external file support and validation."""
from typing import Any, Callable, Dict, List, Optional
import json
import os
from pathlib import Path
from datetime import datetime

# --- Application Configuration Constants ---
# These constants are used throughout the application

# Audit & History Settings
AUDIT_LOG_MAX_SIZE: int = 100
MAPPING_HISTORY_MAX_SIZE: int = 50

# AI & Validation Settings
AI_CONFIDENCE_THRESHOLD: int = 80  # Minimum confidence (as percentage) to auto-apply mappings
VALIDATION_PAGE_SIZES: List[int] = [25, 50, 100, 200]
DEFAULT_VALIDATION_PAGE_SIZE: int = 50
MIN_MAPPING_CONFIDENCE: float = float(os.getenv("MIN_MAPPING_CONFIDENCE", "0.9"))  # Only map if confidence >= 90%

# File Processing Settings
MAX_FILE_SIZE_MB: int = 100  # Maximum file size in MB
SUPPORTED_FILE_FORMATS: List[str] = ['.csv', '.txt', '.tsv', '.xlsx', '.xls', '.json', '.parquet']

# UI Settings
DEFAULT_PAGE_SIZE: int = 50
MAX_PREVIEW_ROWS: int = 1000

# Performance Settings
CACHE_TTL_SECONDS: int = 3600  # Cache time-to-live in seconds
LAZY_LOAD_THRESHOLD: int = 1000  # Number of rows before lazy loading kicks in

# Data Quality Settings
DATA_QUALITY_THRESHOLD: float = 80.0  # Minimum acceptable data quality score
NULL_RATE_THRESHOLD: float = 15.0  # Default null rate threshold for mandatory fields
COMPLETENESS_THRESHOLD: float = 85.0  # Completeness threshold percentage

# Session Settings
SESSION_TIMEOUT_MINUTES: int = 30  # Session timeout in minutes
ACTIVITY_CHECK_INTERVAL: int = 60  # Activity check interval in seconds

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None  # type: ignore
    FileSystemEventHandler = None  # type: ignore

from core.exceptions import ConfigurationError
from decorators import log_execution, handle_errors


class ConfigLoader:
    """Loader for external configuration files."""
    
    SUPPORTED_FORMATS = {'.json'}
    
    @staticmethod
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to load configuration")
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            file_path: Path to configuration file
        
        Returns:
            Configuration dictionary
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {file_path}",
                error_code="CONFIG_FILE_NOT_FOUND"
            )
        
        if path.suffix not in ConfigLoader.SUPPORTED_FORMATS:
            raise ConfigurationError(
                f"Unsupported configuration format: {path.suffix}",
                error_code="UNSUPPORTED_CONFIG_FORMAT"
            )
        
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise ConfigurationError(
                f"Error loading configuration: {str(e)}",
                error_code="CONFIG_LOAD_ERROR"
            ) from e
    
    @staticmethod
    def load_from_env(prefix: str = "CLAIMS_MAPPER_") -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variables
        
        Returns:
            Configuration dictionary
        """
        config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Try to parse as JSON, fallback to string
                try:
                    config[config_key] = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    config[config_key] = value
        return config
    
    @staticmethod
    def validate_config(config: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration dictionary
            schema: Optional validation schema
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if schema is None:
            # Basic validation
            required_keys = ['max_file_size_mb', 'supported_file_formats']
            for key in required_keys:
                if key not in config:
                    return False, f"Missing required configuration key: {key}"
            return True, None
        
        # Schema-based validation would go here
        return True, None
    
    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.
        
        Later configs override earlier ones.
        
        Args:
            *configs: Configuration dictionaries to merge
        
        Returns:
            Merged configuration
        """
        merged = {}
        for config in configs:
            merged.update(config)
        return merged


class ConfigFileHandler(FileSystemEventHandler):
    """Handler for config file changes."""
    
    def __init__(self, callback: Callable[[], None]):
        """
        Initialize handler.
        
        Args:
            callback: Function to call when config file changes
        """
        self.callback = callback
    
    def on_modified(self, event):
        """Handle file modification."""
        if not event.is_directory:
            self.callback()


class ConfigManager:
    """Manager for application configuration."""
    
    def __init__(self, enable_hot_reload: bool = False):
        """
        Initialize config manager.
        
        Args:
            enable_hot_reload: Whether to enable automatic hot reload
        """
        self.config: Dict[str, Any] = {}
        self.config_file: Optional[str] = None
        self.last_loaded: Optional[datetime] = None
        self.enable_hot_reload = enable_hot_reload and WATCHDOG_AVAILABLE
        self.observer: Optional[Observer] = None
        self.reload_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def load_config(
        self,
        config_file: Optional[str] = None,
        use_env: bool = True,
        env_prefix: str = "CLAIMS_MAPPER_"
    ) -> Dict[str, Any]:
        """
        Load configuration from file and/or environment.
        
        Args:
            config_file: Path to configuration file
            use_env: Whether to load from environment variables
            env_prefix: Prefix for environment variables
        
        Returns:
            Loaded configuration
        """
        configs = []
        
        # Load from file if provided
        if config_file:
            file_config = ConfigLoader.load_from_file(config_file)
            configs.append(file_config)
            self.config_file = config_file
        
        # Load from environment
        if use_env:
            env_config = ConfigLoader.load_from_env(env_prefix)
            if env_config:
                configs.append(env_config)
        
        # Merge configs (env overrides file)
        if configs:
            self.config = ConfigLoader.merge_configs(*configs)
        else:
            # Fallback to defaults (constants defined at top of this file)
            self.config = {
                "max_file_size_mb": MAX_FILE_SIZE_MB,
                "supported_file_formats": SUPPORTED_FILE_FORMATS,
                "default_page_size": DEFAULT_PAGE_SIZE,
                "cache_ttl_seconds": CACHE_TTL_SECONDS
            }
        
        # Validate
        is_valid, error = ConfigLoader.validate_config(self.config)
        if not is_valid:
            raise ConfigurationError(
                f"Configuration validation failed: {error}",
                error_code="CONFIG_VALIDATION_ERROR"
            )
        
        self.last_loaded = datetime.now()
        
        # Setup hot reload if enabled
        if self.enable_hot_reload and self.config_file:
            self._setup_hot_reload()
        
        return self.config
    
    def _setup_hot_reload(self) -> None:
        """Setup file watching for hot reload."""
        if not WATCHDOG_AVAILABLE:
            return
        
        if self.observer:
            self.observer.stop()
        
        config_path = Path(self.config_file)
        if not config_path.exists():
            return
        
        def on_config_change():
            """Handle config file change."""
            try:
                new_config = self.reload()
                # Notify callbacks
                for callback in self.reload_callbacks:
                    callback(new_config)
            except Exception as e:
                print(f"Error reloading config: {e}")
        
        event_handler = ConfigFileHandler(on_config_change)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(config_path.parent), recursive=False)
        self.observer.start()
    
    def register_reload_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register callback for config reload events.
        
        Args:
            callback: Function to call when config is reloaded
        """
        self.reload_callbacks.append(callback)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def reload(self) -> Dict[str, Any]:
        """Reload configuration from file."""
        if self.config_file:
            return self.load_config(self.config_file)
        return self.config
    
    def stop_hot_reload(self) -> None:
        """Stop hot reload observer."""
        if self.observer:
            self.observer.stop()
            self.observer = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self.config.copy()


# Global config manager instance
config_manager = ConfigManager()

