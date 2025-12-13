# --- validation_registry.py ---
"""Validation rule registry for dynamic rule loading."""
from typing import Any, Dict, List, Callable, Optional
from abc import ABC, abstractmethod
import pandas as pd
from models import ValidationResult, ValidationStatus


class ValidationRule(ABC):
    """Abstract base class for validation rules."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    def validate(self, df: pd.DataFrame, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Execute the validation rule."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get rule metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        }


class ValidationRuleRegistry:
    """Registry for validation rules."""
    
    def __init__(self) -> None:
        self.rules: Dict[str, ValidationRule] = {}
        self.rule_factories: Dict[str, Callable[[], ValidationRule]] = {}
    
    def register(self, rule: ValidationRule) -> None:
        """Register a validation rule."""
        self.rules[rule.name] = rule
    
    def register_factory(self, name: str, factory: Callable[[], ValidationRule]) -> None:
        """Register a rule factory for dynamic creation."""
        self.rule_factories[name] = factory
    
    def get_rule(self, name: str) -> Optional[ValidationRule]:
        """Get a registered rule by name."""
        if name in self.rules:
            return self.rules[name]
        if name in self.rule_factories:
            rule = self.rule_factories[name]()
            self.rules[name] = rule
            return rule
        return None
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """List all registered rules."""
        return [rule.get_metadata() for rule in self.rules.values()]
    
    def create_rule(self, name: str, config: Dict[str, Any]) -> Optional[ValidationRule]:
        """Create a rule dynamically from configuration."""
        if name in self.rule_factories:
            factory = self.rule_factories[name]
            rule = factory()
            # Apply configuration if rule supports it
            if hasattr(rule, 'configure'):
                rule.configure(config)  # type: ignore
            return rule
        return None


# Global registry instance
validation_registry = ValidationRuleRegistry()


# Example rule implementations
class NullCheckRule(ValidationRule):
    """Rule for checking null values."""
    
    def __init__(self, field: str, threshold: float = 10.0):
        super().__init__(
            name=f"null_check_{field}",
            description=f"Check null percentage for {field}"
        )
        self.field = field
        self.threshold = threshold
    
    def validate(self, df: pd.DataFrame, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate null percentage."""
        if self.field not in df.columns:
            return ValidationResult(
                check_name=self.name,
                status=ValidationStatus.ERROR,
                field=self.field,
                message=f"Field '{self.field}' not found in data"
            )
        
        total = len(df)
        null_count = df[self.field].isna().sum()
        null_pct = (null_count / total * 100) if total > 0 else 0.0
        
        status = ValidationStatus.PASS if null_pct <= self.threshold else ValidationStatus.FAIL
        
        return ValidationResult(
            check_name=self.name,
            status=status,
            field=self.field,
            message=f"Null percentage: {null_pct:.2f}% (threshold: {self.threshold}%)",
            fail_count=int(null_count),
            total_count=total,
            fail_percentage=null_pct
        )


class RangeCheckRule(ValidationRule):
    """Rule for checking value ranges."""
    
    def __init__(self, field: str, min_value: Optional[float] = None, max_value: Optional[float] = None):
        super().__init__(
            name=f"range_check_{field}",
            description=f"Check value range for {field}"
        )
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, df: pd.DataFrame, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate value range."""
        if self.field not in df.columns:
            return ValidationResult(
                check_name=self.name,
                status=ValidationStatus.ERROR,
                field=self.field,
                message=f"Field '{self.field}' not found in data"
            )
        
        numeric_col = pd.to_numeric(df[self.field], errors='coerce')
        total = len(numeric_col)
        failures = 0
        
        if self.min_value is not None:
            failures += (numeric_col < self.min_value).sum()
        if self.max_value is not None:
            failures += (numeric_col > self.max_value).sum()
        
        fail_pct = (failures / total * 100) if total > 0 else 0.0
        status = ValidationStatus.PASS if failures == 0 else ValidationStatus.FAIL
        
        return ValidationResult(
            check_name=self.name,
            status=status,
            field=self.field,
            message=f"Range violations: {failures} records",
            fail_count=int(failures),
            total_count=total,
            fail_percentage=fail_pct
        )


# Register default rules
def register_default_rules() -> None:
    """Register default validation rules."""
    # Rules are registered dynamically when needed
    pass

