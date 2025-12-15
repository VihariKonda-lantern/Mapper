# --- validation_templates.py ---
"""Pre-built validation rule templates."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from validation_registry import ValidationRuleRegistry, ValidationRule


@dataclass
class ValidationTemplate:
    """Template for validation rules."""
    name: str
    description: str
    category: str
    rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "rules": self.rules,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationTemplate":
        """Create from dictionary."""
        template = cls(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            rules=data.get("rules", [])
        )
        if "created_at" in data:
            template.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            template.updated_at = datetime.fromisoformat(data["updated_at"])
        return template


class ValidationTemplateManager:
    """Manager for validation templates."""
    
    def __init__(self):
        self.templates: Dict[str, ValidationTemplate] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self) -> None:
        """Initialize default validation templates."""
        # Required Fields Template
        required_fields_template = ValidationTemplate(
            name="Required Fields Check",
            description="Validates that all required fields are present and non-null",
            category="completeness",
            rules=[
                {
                    "type": "null_check",
                    "field": "field_name",
                    "threshold": 0.0,
                    "severity": "required"
                }
            ]
        )
        self.templates["required_fields"] = required_fields_template
        
        # Data Quality Template
        data_quality_template = ValidationTemplate(
            name="Data Quality Check",
            description="Comprehensive data quality validation",
            category="quality",
            rules=[
                {
                    "type": "null_check",
                    "field": "field_name",
                    "threshold": 10.0,
                    "severity": "optional"
                },
                {
                    "type": "range_check",
                    "field": "numeric_field",
                    "min_value": 0,
                    "max_value": 1000000
                }
            ]
        )
        self.templates["data_quality"] = data_quality_template
        
        # Date Validation Template
        date_validation_template = ValidationTemplate(
            name="Date Validation",
            description="Validates date fields for format and range",
            category="date_validation",
            rules=[
                {
                    "type": "datatype_check",
                    "field": "date_field",
                    "expected_type": "date"
                },
                {
                    "type": "range_check",
                    "field": "date_field",
                    "min_value": "1900-01-01",
                    "max_value": "2100-12-31"
                }
            ]
        )
        self.templates["date_validation"] = date_validation_template
        
        # Numeric Range Template
        numeric_range_template = ValidationTemplate(
            name="Numeric Range Check",
            description="Validates numeric fields are within expected ranges",
            category="numeric_validation",
            rules=[
                {
                    "type": "range_check",
                    "field": "numeric_field",
                    "min_value": 0,
                    "max_value": None
                }
            ]
        )
        self.templates["numeric_range"] = numeric_range_template
        
        # Format Validation Template
        format_validation_template = ValidationTemplate(
            name="Format Validation",
            description="Validates field formats (email, phone, etc.)",
            category="format_validation",
            rules=[
                {
                    "type": "pattern_match",
                    "field": "email_field",
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                }
            ]
        )
        self.templates["format_validation"] = format_validation_template
    
    def get_template(self, name: str) -> Optional[ValidationTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all templates, optionally filtered by category."""
        templates = self.templates.values()
        if category:
            templates = [t for t in templates if t.category == category]
        return [t.to_dict() for t in templates]
    
    def create_template(
        self,
        name: str,
        description: str,
        category: str,
        rules: List[Dict[str, Any]]
    ) -> ValidationTemplate:
        """Create a new validation template."""
        template = ValidationTemplate(
            name=name,
            description=description,
            category=category,
            rules=rules
        )
        self.templates[name] = template
        return template
    
    def apply_template(
        self,
        template_name: str,
        df: Any,
        field_mappings: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply a validation template to a DataFrame.
        
        Args:
            template_name: Name of the template
            df: DataFrame to validate
            field_mappings: Optional mapping from template field names to actual field names
        
        Returns:
            List of validation results
        """
        template = self.get_template(template_name)
        if not template:
            return []
        
        results = []
        field_mappings = field_mappings or {}
        
        for rule_config in template.rules:
            # Map field name if needed
            field_name = rule_config.get("field", "")
            actual_field = field_mappings.get(field_name, field_name)
            
            # Create rule based on type
            rule_type = rule_config.get("type")
            if rule_type == "null_check":
                from validation_registry import NullCheckRule
                threshold = rule_config.get("threshold", 10.0)
                rule = NullCheckRule(actual_field, threshold)
                result = rule.validate(df)
                results.append(result.to_dict())
            elif rule_type == "range_check":
                from validation_registry import RangeCheckRule
                min_value = rule_config.get("min_value")
                max_value = rule_config.get("max_value")
                rule = RangeCheckRule(actual_field, min_value, max_value)
                result = rule.validate(df)
                results.append(result.to_dict())
            # Add more rule types as needed
        
        return results


# Global template manager instance
validation_template_manager = ValidationTemplateManager()

