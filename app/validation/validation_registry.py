# --- validation_registry.py ---
"""Validation rule registry for dynamic rule loading."""
from typing import Any, Dict, List, Callable, Optional
from abc import ABC, abstractmethod
import pandas as pd
from core.models import ValidationResult, ValidationStatus


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


class ComposedValidationRule(ValidationRule):
    """Composed rule that combines multiple validation rules."""
    
    def __init__(
        self,
        name: str,
        rules: List[ValidationRule],
        composition_type: str = "all",  # "all", "any", "majority"
        description: str = ""
    ):
        """
        Create a composed validation rule.
        
        Args:
            name: Name of the composed rule
            rules: List of rules to compose
            composition_type: How to combine results ("all", "any", "majority")
            description: Rule description
        """
        super().__init__(name, description or f"Composed rule with {len(rules)} sub-rules")
        self.rules = rules
        self.composition_type = composition_type
    
    def validate(self, df: pd.DataFrame, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Execute all composed rules and combine results."""
        results = []
        for rule in self.rules:
            result = rule.validate(df, context)
            results.append(result)
        
        # Combine results based on composition type
        if self.composition_type == "all":
            # All rules must pass
            all_pass = all(r.status == ValidationStatus.PASS for r in results)
            overall_status = ValidationStatus.PASS if all_pass else ValidationStatus.FAIL
            total_fails = sum(r.fail_count for r in results)
            total_count = results[0].total_count if results else 0
            fail_pct = (total_fails / total_count * 100) if total_count > 0 else 0.0
            
            messages = [r.message for r in results if r.status != ValidationStatus.PASS]
            combined_message = "; ".join(messages) if messages else "All checks passed"
            
        elif self.composition_type == "any":
            # At least one rule must pass
            any_pass = any(r.status == ValidationStatus.PASS for r in results)
            overall_status = ValidationStatus.PASS if any_pass else ValidationStatus.FAIL
            total_fails = sum(r.fail_count for r in results)
            total_count = results[0].total_count if results else 0
            fail_pct = (total_fails / total_count * 100) if total_count > 0 else 0.0
            
            passed_messages = [r.message for r in results if r.status == ValidationStatus.PASS]
            combined_message = "; ".join(passed_messages) if passed_messages else "No checks passed"
            
        elif self.composition_type == "majority":
            # Majority of rules must pass
            pass_count = sum(1 for r in results if r.status == ValidationStatus.PASS)
            majority = len(results) / 2
            overall_status = ValidationStatus.PASS if pass_count > majority else ValidationStatus.FAIL
            total_fails = sum(r.fail_count for r in results)
            total_count = results[0].total_count if results else 0
            fail_pct = (total_fails / total_count * 100) if total_count > 0 else 0.0
            
            combined_message = f"{pass_count}/{len(results)} checks passed"
            
        else:
            # Default to "all"
            all_pass = all(r.status == ValidationStatus.PASS for r in results)
            overall_status = ValidationStatus.PASS if all_pass else ValidationStatus.FAIL
            total_fails = sum(r.fail_count for r in results)
            total_count = results[0].total_count if results else 0
            fail_pct = (total_fails / total_count * 100) if total_count > 0 else 0.0
            combined_message = f"Composed rule result ({self.composition_type})"
        
        return ValidationResult(
            check_name=self.name,
            status=overall_status,
            field=None,  # Composed rules may span multiple fields
            message=combined_message,
            fail_count=int(total_fails),
            total_count=total_count,
            fail_percentage=fail_pct,
            metadata={
                "composition_type": self.composition_type,
                "sub_rules": [r.get_metadata() for r in self.rules],
                "sub_results": [r.to_dict() for r in results]
            }
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get rule metadata including sub-rules."""
        metadata = super().get_metadata()
        metadata.update({
            "composition_type": self.composition_type,
            "sub_rule_count": len(self.rules),
            "sub_rules": [r.get_metadata() for r in self.rules]
        })
        return metadata


def compose_rules(
    name: str,
    rules: List[ValidationRule],
    composition_type: str = "all",
    description: str = ""
) -> ComposedValidationRule:
    """
    Compose multiple validation rules into a single rule.
    
    Args:
        name: Name for the composed rule
        rules: List of rules to compose
        composition_type: How to combine results ("all", "any", "majority")
        description: Optional description
    
    Returns:
        ComposedValidationRule
    
    Example:
        null_rule = NullCheckRule("field1", 10.0)
        range_rule = RangeCheckRule("field1", 0, 100)
        composed = compose_rules("field1_validation", [null_rule, range_rule], "all")
    """
    return ComposedValidationRule(name, rules, composition_type, description)


# Register default rules
def register_default_rules() -> None:
    """Register default validation rules."""
    # Rules are registered dynamically when needed
    pass

