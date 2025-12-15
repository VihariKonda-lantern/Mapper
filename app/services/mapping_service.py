# --- services/mapping_service.py ---
"""Service for mapping operations."""
from typing import Any, Dict, List, Optional
import pandas as pd
from core.models import Mapping, MappingMode
from mapping.mapping_engine import get_enhanced_automap
from data.transformer import transform_claims_data
from decorators import log_execution, handle_errors, cache_result


class MappingService:
    """Service for handling field mapping operations."""
    
    @staticmethod
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to generate AI mapping suggestions")
    def generate_ai_suggestions(
        layout_df: pd.DataFrame,
        claims_df: pd.DataFrame,
        threshold: float = 0.6
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate AI mapping suggestions.
        
        Args:
            layout_df: Layout DataFrame
            claims_df: Claims DataFrame
            threshold: Confidence threshold for suggestions
        
        Returns:
            Dictionary of mapping suggestions
        """
        return get_enhanced_automap(layout_df, claims_df, threshold)
    
    @staticmethod
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to transform data")
    def apply_mapping(
        claims_df: pd.DataFrame,
        mapping: Dict[str, Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Apply mapping to transform claims data.
        
        Args:
            claims_df: Source claims DataFrame
            mapping: Mapping dictionary
        
        Returns:
            Transformed DataFrame
        """
        return transform_claims_data(claims_df, mapping)
    
    @staticmethod
    def validate_mapping(
        mapping: Dict[str, Dict[str, Any]],
        layout_df: pd.DataFrame,
        claims_df: pd.DataFrame
    ) -> tuple[bool, List[str]]:
        """
        Validate a mapping configuration.
        
        Args:
            mapping: Mapping dictionary
            layout_df: Layout DataFrame
            claims_df: Claims DataFrame
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors: List[str] = []
        
        # Check that all required fields are mapped
        if layout_df is not None and "Usage" in layout_df.columns:
            required_fields = layout_df[
                layout_df["Usage"].astype(str).str.lower() == "mandatory"
            ]["Internal Field"].tolist()
            
            for field in required_fields:
                if field not in mapping or not mapping[field].get("value"):
                    errors.append(f"Required field '{field}' is not mapped")
        
        # Check that mapped columns exist in claims
        if claims_df is not None:
            available_columns = set(claims_df.columns.tolist())
            for field, mapping_info in mapping.items():
                source_col = mapping_info.get("value")
                if source_col and source_col not in available_columns:
                    errors.append(f"Mapped column '{source_col}' does not exist in claims file")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def convert_to_mapping_objects(
        mapping_dict: Dict[str, Dict[str, Any]]
    ) -> List[Mapping]:
        """
        Convert mapping dictionary to Mapping objects.
        
        Args:
            mapping_dict: Mapping dictionary
        
        Returns:
            List of Mapping objects
        """
        mappings = []
        for internal_field, mapping_info in mapping_dict.items():
            mode_str = mapping_info.get("mode", "manual")
            try:
                mode = MappingMode(mode_str)
            except ValueError:
                mode = MappingMode.MANUAL
            
            mapping = Mapping(
                internal_field=internal_field,
                source_column=mapping_info.get("value", ""),
                mode=mode,
                confidence_score=mapping_info.get("confidence")
            )
            mappings.append(mapping)
        return mappings

