# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
"""
Validation Engine - Refactored to use Validation Framework (VF) pattern

This module implements field-level and file-level validations using a rule-based architecture
similar to the Validation Framework. All rules are implemented using pandas (not Spark).

Rule Categories:
- Field-Level (Row-by-Row): Null/Required checks, Datatype validation, Age validation, Fill rate checks
- File-Level (Summary): Required field completeness, Age distribution, Date range, Diagnosis code coverage

run_validations(): Executes field-level validations (row-by-row checks)
dynamic_run_validations(): Executes file-level validations (aggregate/summary checks)
"""
import pandas as pd  # type: ignore[import-not-found]
from typing import List, Dict, Any, cast, Optional, Tuple
import streamlit as st  # type: ignore[import-not-found]
from abc import ABC, abstractmethod

st = cast(Any, st)
pd = cast(Any, pd)

# ================================================================
# Validation Framework Pattern - Base Classes
# ================================================================

class ValidationStatus:
    """Validation status constants matching VF pattern."""
    PASS = "Pass"
    FAIL = "Fail"
    WARNING = "Warning"
    ERROR = "Error"


class ValidationResult:
    """Result object for validation rules (pandas-compatible)."""
    def __init__(
        self,
        rule_name: str,
        status: str,
        failed_count: int,
        total_count: int,
        field: Optional[str] = None,
        message: Optional[str] = None,
        severity: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        self.rule_name = rule_name
        self.status = status
        self.failed_count = failed_count
        self.total_count = total_count
        self.field = field
        self.message = message or ""
        self.severity = severity or status
        self.metrics = metrics or {}
    
    def get_failure_rate(self) -> float:
        """Calculate failure rate as percentage."""
        return (self.failed_count / self.total_count * 100) if self.total_count > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with existing UI."""
        result = {
            "field": self.field or "",
            "check": self.rule_name,
            "status": self.status,
            "message": self.message
        }
        # Add optional fields if available
        if self.severity:
            result["severity"] = self.severity
        if self.metrics:
            result.update(self.metrics)
        if self.failed_count >= 0:
            result["fail_count"] = self.failed_count
            result["fail_pct"] = round(self.get_failure_rate(), 2)
        return result


class BaseValidationRule(ABC):
    """Base class for validation rules (pandas-based, VF-style)."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rule_name = config.get("rule_name", self.__class__.__name__)
        self.validation_inputs = config.get("validation_inputs", {})
    
    @abstractmethod
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """
        Execute validation logic and return (failed_records_df, failed_count).

    Args:
            df: Input pandas DataFrame

    Returns:
            Tuple of (failed_records_df, failed_count)
        """
        pass
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """
        Main validation method that wraps execution with error handling.

    Args:
            df: Input pandas DataFrame

    Returns:
            ValidationResult object
        """
        try:
            total_count = len(df)
            if total_count == 0:
                return ValidationResult(
                    rule_name=self.rule_name,
                    status=ValidationStatus.WARNING,
                    failed_count=0,
                    total_count=0,
                    message="Empty DataFrame - no validation performed"
                )
            
            failed_records_df, failed_count = self._execute_validation(df)
            
            # Determine status based on failed count
            status = self._determine_status(failed_count, total_count)
            
            # Build message
            message = self._build_message(failed_count, total_count)
            
            # Get field name if available
            field = self.config.get("column_name") or self.config.get("field")
            
            # Build metrics
            metrics = {
                "failure_rate": round((failed_count / total_count * 100) if total_count > 0 else 0.0, 2),
                "success_count": total_count - failed_count
            }
            
            return ValidationResult(
                rule_name=self.rule_name,
                status=status,
                failed_count=failed_count,
                total_count=total_count,
                field=field,
                message=message,
                severity=status,
                metrics=metrics
            )
        except Exception as e:
            return ValidationResult(
                rule_name=self.rule_name,
                status=ValidationStatus.ERROR,
                failed_count=-1,
                total_count=len(df) if df is not None else 0,
                message=f"Validation error: {str(e)}",
                severity=ValidationStatus.ERROR
            )
    
    def _determine_status(self, failed_count: int, total_count: int) -> str:
        """Determine validation status based on failure rate."""
        if failed_count == 0:
            return ValidationStatus.PASS
        failure_rate = (failed_count / total_count * 100) if total_count > 0 else 0.0
        
        # Use threshold if available, otherwise default logic
        threshold = self.validation_inputs.get("failure_threshold", 0.0)
        if threshold > 0 and failure_rate <= threshold:
            return ValidationStatus.PASS
        
        # Default: any failure is a fail for required checks, warning for optional
        severity = self.config.get("severity", "required")
        if severity == "required":
            return ValidationStatus.FAIL
        else:
            return ValidationStatus.WARNING
    
    def _build_message(self, failed_count: int, total_count: int) -> str:
        """Build human-readable message."""
        if failed_count == 0:
            return "All records passed validation"
        return f"{failed_count} of {total_count} records failed validation"


# ================================================================
# Field-Level Validation Rules (Row-by-Row Checks)
# ================================================================

class NullCheckRule(BaseValidationRule):
    """Validates that required fields are not null/empty."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        column = self.config.get("column_name")
        if not column or column not in df.columns:
            return df.iloc[0:0], 0  # Empty DataFrame
        
        # Check for null, empty string, or NaN
        null_mask = (
            df[column].isnull() |
            (df[column].astype(str).str.strip() == "") |
            (df[column].astype(str).str.strip() == "nan")
        )
        
        failed_records_df = df[null_mask].copy()
        failed_count = len(failed_records_df)
        
        return failed_records_df, failed_count


class DatatypeCheckRule(BaseValidationRule):
    """Validates that date fields can be parsed correctly."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        column = self.config.get("column_name")
        if not column or column not in df.columns:
            return df.iloc[0:0], 0
        
        # For date fields, try to parse
        if "date" in column.lower():
            parsed_dates = pd.to_datetime(df[column], errors='coerce')
            invalid_mask = df[column].notnull() & parsed_dates.isnull()
        else:
            # For other types, just check if null (basic check)
            invalid_mask = df[column].isnull()
        
        failed_records_df = df[invalid_mask].copy()
        failed_count = len(failed_records_df)
        
        return failed_records_df, failed_count


class AgeValidationRule(BaseValidationRule):
    """Validates that patients are at least 18 years old."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        dob_field = self.config.get("column_name")
        if not dob_field or dob_field not in df.columns:
            return df.iloc[0:0], 0
        
        today = pd.Timestamp.today()
        dob = pd.to_datetime(df[dob_field], errors='coerce')
        age = (today - dob).dt.days // 365
        
        underage_mask = age < 18
        failed_records_df = df[underage_mask].copy()
        failed_count = len(failed_records_df)
        
        return failed_records_df, failed_count


class FillRateCheckRule(BaseValidationRule):
    """Checks fill rate for mapped fields and warns when too sparse."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        column = self.config.get("column_name")
        if not column or column not in df.columns:
            return df.iloc[0:0], 0
        
        fill_rate = 100 * df[column].notnull().sum() / len(df) if len(df) > 0 else 0.0
        threshold = self.validation_inputs.get("min_fill_rate", 50.0)
        
        # If fill rate is below threshold, consider all nulls as "failed" for reporting
        if fill_rate < threshold:
            null_mask = df[column].isnull()
            failed_records_df = df[null_mask].copy()
            failed_count = len(failed_records_df)
        else:
            failed_records_df = df.iloc[0:0]
            failed_count = 0
        
        return failed_records_df, failed_count


# ================================================================
# File-Level Validation Rules (Summary/Aggregate Checks)
# ================================================================

class RequiredFieldsCompletenessRule(BaseValidationRule):
    """Summarizes required field completeness across the entire file."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        required_fields = self.validation_inputs.get("required_fields", [])
        if not required_fields:
            self._completeness = 100.0
            return df.iloc[0:0], 0
        
        # Filter to only fields that exist in DataFrame
        existing_fields = [f for f in required_fields if f in df.columns]
        if not existing_fields:
            self._completeness = 0.0
            return df.iloc[0:0], 0
        
        # Calculate missing values
        missing_values = df[existing_fields].isnull().sum().sum()
        total_cells = len(df) * len(existing_fields)
        completeness = ((total_cells - missing_values) / total_cells * 100) if total_cells > 0 else 0.0
        self._completeness = completeness
        
        # Determine if this is a failure (threshold-based)
        threshold = self.validation_inputs.get("completeness_threshold", 98.0)
        if completeness < threshold:
            # Return a dummy failed record to indicate file-level failure
            failed_df = pd.DataFrame([{"file_level_check": "RequiredFieldsCompleteness"}])
            return failed_df, 1
        else:
            return df.iloc[0:0], 0
    
    def _build_message(self, failed_count: int, total_count: int) -> str:
        """Override to provide completeness percentage."""
        if hasattr(self, '_completeness'):
            return f"{self._completeness:.1f}% fields filled"
        return f"{failed_count} validation issues found"


class AgeDistributionRule(BaseValidationRule):
    """Summarizes age validation (18+) rate across the file."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        dob_field = self.config.get("column_name")
        if not dob_field or dob_field not in df.columns:
            self._over_18_pct = 0.0
            return df.iloc[0:0], 0
        
        today = pd.Timestamp.today()
        dob = pd.to_datetime(df[dob_field], errors="coerce")
        age = (today - dob).dt.days / 365.25
        over_18_pct = (age >= 18).sum() / len(df) * 100 if len(df) > 0 else 0.0
        self._over_18_pct = over_18_pct
        
        threshold = self.validation_inputs.get("min_over_18_pct", 90.0)
        if over_18_pct < threshold:
            failed_df = pd.DataFrame([{"file_level_check": "AgeDistribution"}])
            return failed_df, 1
        else:
            return df.iloc[0:0], 0
    
    def _build_message(self, failed_count: int, total_count: int) -> str:
        """Override to provide percentage."""
        if hasattr(self, '_over_18_pct'):
            return f"{self._over_18_pct:.1f}% patients are 18+"
        return f"{failed_count} validation issues found"


class DateRangeCheckRule(BaseValidationRule):
    """Summarizes claims within a date range (e.g., last 6 months)."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        date_field = self.config.get("column_name")
        if not date_field or date_field not in df.columns:
            self._valid_dates_pct = 0.0
            return df.iloc[0:0], 0
        
        months_back = self.validation_inputs.get("months_back", 6)
        self._months_back = months_back
        today = pd.Timestamp.today()
        cutoff_date = today - pd.DateOffset(months=months_back)
        
        service_dates = pd.to_datetime(df[date_field], errors="coerce")
        valid_dates_pct = (service_dates >= cutoff_date).sum() / len(df) * 100 if len(df) > 0 else 0.0
        self._valid_dates_pct = valid_dates_pct
        
        threshold = self.validation_inputs.get("min_valid_pct", 80.0)
        if valid_dates_pct < threshold:
            failed_df = pd.DataFrame([{"file_level_check": "DateRange"}])
            return failed_df, 1
        else:
            return df.iloc[0:0], 0
    
    def _build_message(self, failed_count: int, total_count: int) -> str:
        """Override to provide percentage."""
        if hasattr(self, '_valid_dates_pct') and hasattr(self, '_months_back'):
            return f"{self._valid_dates_pct:.1f}% claims within last {self._months_back} months"
        return f"{failed_count} validation issues found"


class DiagnosisCodeCoverageRule(BaseValidationRule):
    """Summarizes presence of MSK/BAR diagnosis codes across fields."""
    
    def _execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        dx_fields = self.validation_inputs.get("dx_fields", [])
        if not dx_fields:
            # Auto-detect diagnosis fields
            dx_fields = [col for col in df.columns if col.lower().startswith("dx_code")]
        
        if not dx_fields:
            return df.iloc[0:0], 0
        
        total_dx = 0
        msk_count = 0
        bar_count = 0
        
        msk_keywords = ["M", "S", "K"]
        bar_keywords = ["B", "A", "R"]
        
        for field in dx_fields:
            if field in df.columns:
                values = df[field].dropna().astype(str)
                field_count = len(values)
                total_dx += field_count
                field_msk = values.str.contains('|'.join(msk_keywords), case=False, na=False).sum()
                field_bar = values.str.contains('|'.join(bar_keywords), case=False, na=False).sum()
                msk_count += field_msk
                bar_count += field_bar
        
        # Store for message building
        self._total_dx = total_dx
        self._msk_count = msk_count
        self._bar_count = bar_count
        
        if total_dx == 0:
            failed_df = pd.DataFrame([{"file_level_check": "DiagnosisCodeCoverage"}])
            return failed_df, 1
        else:
            msk_pct = (msk_count / total_dx) * 100
            bar_pct = (bar_count / total_dx) * 100
            if msk_pct + bar_pct == 0:
                failed_df = pd.DataFrame([{"file_level_check": "DiagnosisCodeCoverage"}])
                return failed_df, 1
        
        return df.iloc[0:0], 0
    
    def _build_message(self, failed_count: int, total_count: int) -> str:
        """Override to provide MSK/BAR percentages."""
        if hasattr(self, '_total_dx') and self._total_dx > 0:
            msk_pct = (self._msk_count / self._total_dx) * 100
            bar_pct = (self._bar_count / self._total_dx) * 100
            return f"MSK: {msk_pct:.1f}% | BAR: {bar_pct:.1f}%"
        return "No diagnosis codes found"


# ================================================================
# Public API - Unchanged Signatures
# ================================================================

@st.cache_data(show_spinner=False)
def run_validations(transformed_df: Any, required_fields: List[str], all_mapped_fields: List[str]) -> List[Dict[str, Any]]:
    """
    Run all field-level validations and return consolidated results.
    
    This function executes row-by-row validation checks using VF-style rules:
    - Required field null checks (for all required fields)
    - Optional field null checks (for all mapped optional fields)
    - Date validity checks (for all date fields)
    - Age validation (18+) (for DOB fields)
    - Fill rate checks (for all mapped fields)
    
    Args:
        transformed_df: Transformed claims data (pandas DataFrame)
        required_fields: Required internal fields to validate
        all_mapped_fields: All mapped internal fields (both required and optional)
        
    Returns:
        List of validation result dicts compatible with existing UI
    """
    results: List[Dict[str, Any]] = []
    
    # 1. Required Fields Null Check
    for field in required_fields:
        if field in transformed_df.columns:
            rule = NullCheckRule({
                "rule_name": "Required Field Check",
                "column_name": field,
                "severity": "required",
                "validation_inputs": {}
            })
            result = rule.validate(transformed_df)
            results.append(result.to_dict())
    
    # 2. Optional Fields Null Check (for mapped optional fields that aren't required)
    optional_mapped_fields = [f for f in all_mapped_fields if f not in required_fields]
    for field in optional_mapped_fields:
        if field in transformed_df.columns:
            rule = NullCheckRule({
                "rule_name": "Optional Field Check",
                "column_name": field,
                "severity": "optional",
                "validation_inputs": {}
            })
            result = rule.validate(transformed_df)
            # Only add if there are failures (to reduce noise, but show if issues exist)
            if result.failed_count > 0:
                results.append(result.to_dict())
    
    # 3. Date Validity Check (for all date fields)
    date_fields = [col for col in transformed_df.columns if "date" in col.lower()]
    for field in date_fields:
        rule = DatatypeCheckRule({
            "rule_name": "Date Validity Check",
            "column_name": field,
            "severity": "optional",
            "validation_inputs": {}
        })
        result = rule.validate(transformed_df)
        results.append(result.to_dict())
    
    # 4. Age Validation (18+) - Check all DOB fields
    dob_fields = [col for col in transformed_df.columns if "dob" in col.lower() or col in ["Patient_DOB", "Insured_DOB"]]
    for dob_field in dob_fields:
        if dob_field in transformed_df.columns:
            rule = AgeValidationRule({
                "rule_name": "Age ≥ 18 Check",
                "column_name": dob_field,
                "severity": "required",
                "validation_inputs": {}
            })
            result = rule.validate(transformed_df)
            results.append(result.to_dict())
    
    # 5. Fill Rate Check for ALL Mapped Internal Fields
    for field in all_mapped_fields:
        if field in transformed_df.columns:
            rule = FillRateCheckRule({
                "rule_name": "Fill Rate Check",
                "column_name": field,
                "severity": "optional",
                "validation_inputs": {"min_fill_rate": 50.0}
            })
            result = rule.validate(transformed_df)
            # Add all results (both warnings and passes for completeness)
            results.append(result.to_dict())
    
    return results


def dynamic_run_validations(transformed_df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Dynamically runs overall file-level validations.
    
    This function executes aggregate/summary validation checks using VF-style rules:
    - Required fields completeness
    - Age distribution summary
    - Service date range check
    - Diagnosis code coverage summary

    Args:
        transformed_df: Transformed claims data (pandas DataFrame)
        final_mapping: Mapping dict of required fields

    Returns:
        List of file-level validation result dicts compatible with existing UI
    """
    results: List[Dict[str, Any]] = []
    
    # 1. Required Fields Completeness
    required_fields = list(final_mapping.keys())
    rule = RequiredFieldsCompletenessRule({
        "rule_name": "Required Fields Completeness",
        "validation_inputs": {
            "required_fields": required_fields,
            "completeness_threshold": 98.0
        }
    })
    result = rule.validate(transformed_df)
    # Convert to file-level format (no field, just check/status/message)
    file_result = {
        "check": result.rule_name,
        "status": result.status,
        "message": result.message
    }
    if result.severity:
        file_result["severity"] = result.severity
    results.append(file_result)
    
    # 2. Age Check Summary
    dob_field = None
    if "Patient_DOB" in transformed_df.columns:
        dob_field = "Patient_DOB"
    elif "Insured_DOB" in transformed_df.columns:
        dob_field = "Insured_DOB"

    if dob_field:
        rule = AgeDistributionRule({
            "rule_name": "Age Validation (18+)",
            "column_name": dob_field,
            "validation_inputs": {"min_over_18_pct": 90.0}
        })
        result = rule.validate(transformed_df)
        file_result = {
            "check": result.rule_name,
            "status": result.status,
            "message": result.message
        }
        if result.severity:
            file_result["severity"] = result.severity
        results.append(file_result)
    
    # 3. Date Range Check
    if "Begin_Date" in transformed_df.columns:
        rule = DateRangeCheckRule({
            "rule_name": "Service Date Range (Last 6 Months)",
            "column_name": "Begin_Date",
            "validation_inputs": {"months_back": 6, "min_valid_pct": 80.0}
        })
        result = rule.validate(transformed_df)
        file_result = {
            "check": result.rule_name,
            "status": result.status,
            "message": result.message
        }
        if result.severity:
            file_result["severity"] = result.severity
        results.append(file_result)
    
    # 4. Diagnosis Code Summary
    dx_fields = [col for col in transformed_df.columns if col.lower().startswith("dx_code")]
    if dx_fields:
        rule = DiagnosisCodeCoverageRule({
            "rule_name": "Diagnosis Code Presence (MSK/BAR)",
            "validation_inputs": {"dx_fields": dx_fields}
        })
        result = rule.validate(transformed_df)
        file_result = {
            "check": result.rule_name,
            "status": result.status,
            "message": result.message
        }
        if result.severity:
            file_result["severity"] = result.severity
        results.append(file_result)

    return results
