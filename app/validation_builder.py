# --- validation_builder.py ---
"""Custom validation rules builder."""
import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Optional, Callable

st: Any = st
pd: Any = pd


class CustomValidationRule:
    """Base class for custom validation rules."""
    
    def __init__(self, name: str, field: str, rule_type: str, threshold: float = 0.0):
        self.name = name
        self.field = field
        self.rule_type = rule_type
        self.threshold = threshold
    
    def validate(self, df: Any) -> Dict[str, Any]:
        """Validate the rule against the dataframe."""
        if self.field not in df.columns:
            return {
                "status": "Fail",
                "message": f"Field '{self.field}' not found in data",
                "check": self.name
            }
        
        col_data = df[self.field]
        
        if self.rule_type == "null_check":
            null_pct = (col_data.isna().sum() / len(col_data) * 100) if len(col_data) > 0 else 100
            if null_pct > self.threshold:
                return {
                    "status": "Fail",
                    "message": f"{null_pct:.1f}% null values (threshold: {self.threshold}%)",
                    "check": self.name,
                    "field": self.field
                }
            else:
                return {
                    "status": "Pass",
                    "message": f"{null_pct:.1f}% null values (within threshold)",
                    "check": self.name,
                    "field": self.field
                }
        
        elif self.rule_type == "min_value":
            if col_data.dtype in ['int64', 'float64']:
                min_val = col_data.min()
                if min_val < self.threshold:
                    return {
                        "status": "Fail",
                        "message": f"Minimum value {min_val} is below threshold {self.threshold}",
                        "check": self.name,
                        "field": self.field
                    }
                else:
                    return {
                        "status": "Pass",
                        "message": f"Minimum value {min_val} meets threshold",
                        "check": self.name,
                        "field": self.field
                    }
        
        elif self.rule_type == "max_value":
            if col_data.dtype in ['int64', 'float64']:
                max_val = col_data.max()
                if max_val > self.threshold:
                    return {
                        "status": "Fail",
                        "message": f"Maximum value {max_val} exceeds threshold {self.threshold}",
                        "check": self.name,
                        "field": self.field
                    }
                else:
                    return {
                        "status": "Pass",
                        "message": f"Maximum value {max_val} within threshold",
                        "check": self.name,
                        "field": self.field
                    }
        
        elif self.rule_type == "pattern_match":
            # Simple pattern matching (would need regex support)
            return {
                "status": "Pass",
                "message": "Pattern check not yet implemented",
                "check": self.name,
                "field": self.field
            }
        
        return {
            "status": "Warning",
            "message": f"Unknown rule type: {self.rule_type}",
            "check": self.name,
            "field": self.field
        }


def save_custom_rule(rule: CustomValidationRule) -> Dict[str, Any]:
    """Save a custom validation rule to session state."""
    if "custom_validation_rules" not in st.session_state:
        st.session_state.custom_validation_rules = []
    
    rule_dict = {
        "name": rule.name,
        "field": rule.field,
        "rule_type": rule.rule_type,
        "threshold": rule.threshold
    }
    
    st.session_state.custom_validation_rules.append(rule_dict)
    return rule_dict


def load_custom_rules() -> List[Dict[str, Any]]:
    """Load custom validation rules from session state."""
    return st.session_state.get("custom_validation_rules", [])


def run_custom_validations(df: Any, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run custom validation rules against a dataframe."""
    results = []
    
    for rule_dict in rules:
        rule = CustomValidationRule(
            name=rule_dict["name"],
            field=rule_dict["field"],
            rule_type=rule_dict["rule_type"],
            threshold=rule_dict["threshold"]
        )
        result = rule.validate(df)
        results.append(result)
    
    return results

