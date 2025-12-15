# --- services/validation_service.py ---
"""Service for validation operations."""
from typing import Any, Dict, List
import pandas as pd
from core.models import ValidationResult, ValidationStatus
from validation.validation_engine import run_validations, dynamic_run_validations
from decorators import log_execution, handle_errors


class ValidationService:
    """Service for handling validation operations."""
    
    @staticmethod
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to run validations", return_value=[])
    def run_field_validations(
        df: pd.DataFrame,
        required_fields: List[str],
        all_mapped_fields: List[str],
        continue_on_error: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run field-level validations with optional partial validation.
        
        Args:
            df: DataFrame to validate
            required_fields: List of required field names
            all_mapped_fields: List of all mapped field names
            continue_on_error: If True, continue validation even if some rules fail
        
        Returns:
            List of validation result dictionaries
        """
        if continue_on_error:
            # Run validations with error handling to continue on failures
            results = []
            try:
                results = run_validations(df, required_fields, all_mapped_fields)
            except Exception as e:
                # Log error but continue with partial results
                from structured_logging import StructuredLogger
                logger = StructuredLogger("validation_service")
                logger.log_warning(
                    "Partial validation completed with errors",
                    {"error": str(e), "results_count": len(results)}
                )
            return results
        else:
            return run_validations(df, required_fields, all_mapped_fields)
    
    @staticmethod
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to run file-level validations")
    def run_file_validations(
        df: pd.DataFrame,
        mapping: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Run file-level validations.
        
        Args:
            df: DataFrame to validate
            mapping: Mapping dictionary
        
        Returns:
            List of validation result dictionaries
        """
        return dynamic_run_validations(df, mapping)
    
    @staticmethod
    def aggregate_validation_results(
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate validation results into summary statistics.
        
        Args:
            results: List of validation result dictionaries
        
        Returns:
            Aggregated statistics dictionary
        """
        total = len(results)
        passes = len([r for r in results if r.get("status") == "Pass"])
        warnings = len([r for r in results if r.get("status") == "Warning"])
        fails = len([r for r in results if r.get("status") == "Fail"])
        
        return {
            "total": total,
            "passed": passes,
            "warnings": warnings,
            "failed": fails,
            "pass_rate": (passes / total * 100) if total > 0 else 0.0
        }
    
    @staticmethod
    def prioritize_errors(
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize validation errors by severity.
        
        Args:
            results: List of validation result dictionaries
        
        Returns:
            Sorted list with highest priority errors first
        """
        priority_order = {"Fail": 0, "Warning": 1, "Pass": 2}
        return sorted(
            results,
            key=lambda x: (
                priority_order.get(x.get("status", "Pass"), 2),
                -float(x.get("fail_pct", "0").replace("%", "") or 0)
            )
        )
    
    @staticmethod
    def group_errors_by_type(
        results: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group validation errors by check type.
        
        Args:
            results: List of validation result dictionaries
        
        Returns:
            Dictionary grouped by check type
        """
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for result in results:
            check_type = result.get("check", "Unknown")
            if check_type not in grouped:
                grouped[check_type] = []
            grouped[check_type].append(result)
        return grouped
    
    @staticmethod
    def get_error_preview(
        results: List[Dict[str, Any]],
        max_samples: int = 5
    ) -> Dict[str, Any]:
        """
        Get a preview of errors before showing full report.
        
        Args:
            results: List of validation result dictionaries
            max_samples: Maximum number of error samples to return
        
        Returns:
            Dictionary with error preview information
        """
        failed_results = [r for r in results if r.get("status") in ["Fail", "Error"]]
        warning_results = [r for r in results if r.get("status") == "Warning"]
        
        # Prioritize errors
        prioritized = ValidationService.prioritize_errors(failed_results + warning_results)
        
        return {
            "total_errors": len(failed_results),
            "total_warnings": len(warning_results),
            "sample_errors": prioritized[:max_samples],
            "error_summary": ValidationService.aggregate_validation_results(results)
        }

