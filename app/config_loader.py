# --- config_loader.py ---
"""Configuration loader with external file support and validation."""
from typing import Any, Dict, Optional
import json
import os
from pathlib import Path

from exceptions import ConfigurationError
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


class ConfigManager:
    """Manager for application configuration."""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.config_file: Optional[str] = None
        self.last_loaded: Optional[Any] = None
    
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
            # Fallback to defaults from config.py
            from config import (
                MAX_FILE_SIZE_MB,
                SUPPORTED_FILE_FORMATS,
                DEFAULT_PAGE_SIZE,
                CACHE_TTL_SECONDS
            )
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
        
        self.last_loaded = __import__("datetime").datetime.now()
        return self.config
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self.config.copy()


# Global config manager instance
config_manager = ConfigManager()

