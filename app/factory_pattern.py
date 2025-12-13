# --- factory_pattern.py ---
"""Factory pattern implementations for dynamic object creation."""
from typing import Any, Dict, Optional, Type, Callable, Protocol
from abc import ABC, abstractmethod
import pandas as pd
from exceptions import ClaimsMapperError


class ValidatorFactory:
    """Factory for creating validators dynamically."""
    
    _validators: Dict[str, Type[Any]] = {}
    _validator_creators: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
    
    @classmethod
    def register_validator(cls, name: str, validator_class: Type[Any]) -> None:
        """Register a validator class."""
        cls._validators[name] = validator_class
    
    @classmethod
    def register_validator_creator(cls, name: str, creator: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a validator creator function."""
        cls._validator_creators[name] = creator
    
    @classmethod
    def create_validator(cls, name: str, config: Dict[str, Any]) -> Any:
        """
        Create a validator instance.
        
        Args:
            name: Validator name
            config: Validator configuration
        
        Returns:
            Validator instance
        
        Raises:
            ClaimsMapperError: If validator not found
        """
        if name in cls._validator_creators:
            return cls._validator_creators[name](config)
        
        if name in cls._validators:
            validator_class = cls._validators[name]
            return validator_class(config)
        
        raise ClaimsMapperError(
            f"Validator '{name}' not found",
            error_code="VALIDATOR_NOT_FOUND",
            context={"name": name, "available": list(cls._validators.keys())}
        )
    
    @classmethod
    def list_validators(cls) -> list[str]:
        """List all registered validators."""
        return list(set(cls._validators.keys()) | set(cls._validator_creators.keys()))


class TransformerFactory:
    """Factory for creating transformers dynamically."""
    
    _transformers: Dict[str, Type[Any]] = {}
    _transformer_creators: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
    
    @classmethod
    def register_transformer(cls, name: str, transformer_class: Type[Any]) -> None:
        """Register a transformer class."""
        cls._transformers[name] = transformer_class
    
    @classmethod
    def register_transformer_creator(cls, name: str, creator: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a transformer creator function."""
        cls._transformer_creators[name] = creator
    
    @classmethod
    def create_transformer(cls, name: str, config: Dict[str, Any]) -> Any:
        """
        Create a transformer instance.
        
        Args:
            name: Transformer name
            config: Transformer configuration
        
        Returns:
            Transformer instance
        
        Raises:
            ClaimsMapperError: If transformer not found
        """
        if name in cls._transformer_creators:
            return cls._transformer_creators[name](config)
        
        if name in cls._transformers:
            transformer_class = cls._transformers[name]
            return transformer_class(config)
        
        raise ClaimsMapperError(
            f"Transformer '{name}' not found",
            error_code="TRANSFORMER_NOT_FOUND",
            context={"name": name, "available": list(cls._transformers.keys())}
        )
    
    @classmethod
    def list_transformers(cls) -> list[str]:
        """List all registered transformers."""
        return list(set(cls._transformers.keys()) | set(cls._transformer_creators.keys()))


class MapperFactory:
    """Factory for creating mappers dynamically."""
    
    _mappers: Dict[str, Type[Any]] = {}
    _mapper_creators: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
    
    @classmethod
    def register_mapper(cls, name: str, mapper_class: Type[Any]) -> None:
        """Register a mapper class."""
        cls._mappers[name] = mapper_class
    
    @classmethod
    def register_mapper_creator(cls, name: str, creator: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a mapper creator function."""
        cls._mapper_creators[name] = creator
    
    @classmethod
    def create_mapper(cls, name: str, config: Dict[str, Any]) -> Any:
        """
        Create a mapper instance.
        
        Args:
            name: Mapper name
            config: Mapper configuration
        
        Returns:
            Mapper instance
        
        Raises:
            ClaimsMapperError: If mapper not found
        """
        if name in cls._mapper_creators:
            return cls._mapper_creators[name](config)
        
        if name in cls._mappers:
            mapper_class = cls._mappers[name]
            return mapper_class(config)
        
        raise ClaimsMapperError(
            f"Mapper '{name}' not found",
            error_code="MAPPER_NOT_FOUND",
            context={"name": name, "available": list(cls._mappers.keys())}
        )
    
    @classmethod
    def list_mappers(cls) -> list[str]:
        """List all registered mappers."""
        return list(set(cls._mappers.keys()) | set(cls._mapper_creators.keys()))


class ProcessorFactory:
    """Unified factory for creating processors (validators, transformers, mappers)."""
    
    def __init__(self):
        self.validator_factory = ValidatorFactory()
        self.transformer_factory = TransformerFactory()
        self.mapper_factory = MapperFactory()
    
    def create_processor(
        self,
        processor_type: str,
        name: str,
        config: Dict[str, Any]
    ) -> Any:
        """
        Create a processor by type.
        
        Args:
            processor_type: Type of processor ("validator", "transformer", "mapper")
            name: Processor name
            config: Processor configuration
        
        Returns:
            Processor instance
        
        Raises:
            ClaimsMapperError: If processor type is invalid
        """
        if processor_type == "validator":
            return self.validator_factory.create_validator(name, config)
        elif processor_type == "transformer":
            return self.transformer_factory.create_transformer(name, config)
        elif processor_type == "mapper":
            return self.mapper_factory.create_mapper(name, config)
        else:
            raise ClaimsMapperError(
                f"Invalid processor type: {processor_type}",
                error_code="INVALID_PROCESSOR_TYPE",
                context={"type": processor_type, "valid_types": ["validator", "transformer", "mapper"]}
            )
    
    def list_processors(self, processor_type: Optional[str] = None) -> Dict[str, list[str]]:
        """
        List all registered processors.
        
        Args:
            processor_type: Optional filter by type
        
        Returns:
            Dictionary mapping processor types to lists of names
        """
        if processor_type:
            if processor_type == "validator":
                return {"validator": self.validator_factory.list_validators()}
            elif processor_type == "transformer":
                return {"transformer": self.transformer_factory.list_transformers()}
            elif processor_type == "mapper":
                return {"mapper": self.mapper_factory.list_mappers()}
            else:
                return {}
        
        return {
            "validator": self.validator_factory.list_validators(),
            "transformer": self.transformer_factory.list_transformers(),
            "mapper": self.mapper_factory.list_mappers()
        }


# Global factory instance
processor_factory = ProcessorFactory()


# Example registrations (would be done at module import time)
def register_default_validators() -> None:
    """Register default validators."""
    from validation_registry import NullCheckRule, RangeCheckRule
    
    def create_null_check(config: Dict[str, Any]) -> Any:
        field = config.get("field", "")
        threshold = config.get("threshold", 10.0)
        return NullCheckRule(field, threshold)
    
    def create_range_check(config: Dict[str, Any]) -> Any:
        field = config.get("field", "")
        min_value = config.get("min_value")
        max_value = config.get("max_value")
        return RangeCheckRule(field, min_value, max_value)
    
    ValidatorFactory.register_validator_creator("null_check", create_null_check)
    ValidatorFactory.register_validator_creator("range_check", create_range_check)


def register_default_transformers() -> None:
    """Register default transformers."""
    from base_classes import BaseTransformer
    
    class DateStandardizer(BaseTransformer):
        """Transformer for standardizing dates."""
        
        def __init__(self):
            super().__init__("date_standardizer")
        
        def transform(self, df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
            """Standardize date columns."""
            # Implementation would go here
            return df
    
    TransformerFactory.register_transformer("date_standardizer", DateStandardizer)


def register_default_mappers() -> None:
    """Register default mappers."""
    from base_classes import BaseMapper
    
    class FuzzyMapper(BaseMapper):
        """Mapper using fuzzy matching."""
        
        def __init__(self):
            super().__init__("fuzzy_mapper")
        
        def map_fields(
            self,
            source_df: pd.DataFrame,
            target_fields: list[str],
            **kwargs: Any
        ) -> Dict[str, str]:
            """Map fields using fuzzy matching."""
            # Implementation would go here
            return {}
    
    MapperFactory.register_mapper("fuzzy_mapper", FuzzyMapper)


# Auto-register defaults on import
try:
    register_default_validators()
    register_default_transformers()
    register_default_mappers()
except Exception:
    # Silently fail if dependencies aren't available
    pass

