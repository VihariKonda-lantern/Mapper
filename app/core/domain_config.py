"""Domain configuration for making the app layout-agnostic."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class DomainConfig:
    """Domain-specific configuration for terminology, labels, and structure.
    
    This allows the app to work with any domain (claims, invoices, orders, etc.)
    by configuring terminology and layout structure.
    """
    # Domain name/identifier
    domain_name: str = "claims"
    
    # App-level labels
    app_title: str = "Data Mapper and Validator"
    app_description: str = "Map, validate, and transform data files"
    
    # File labels
    source_file_label: str = "Source File"
    source_file_help: str = "Upload your source data file (CSV, TXT, TSV, XLSX, JSON, PARQUET)"
    target_layout_label: str = "Target Layout"
    target_layout_help: str = "Upload your target layout file (.xlsx) that defines the expected structure"
    lookup_file_label: str = "Lookup File"
    lookup_file_help: str = "Upload lookup/reference file (.xlsx) for validation"
    
    # State management keys (for backward compatibility, defaults to claims terminology)
    source_dataframe_key: str = "claims_df"
    source_file_obj_key: str = "claims_file_obj"
    source_file_metadata_key: str = "claims_file_metadata"
    target_layout_key: str = "layout_df"
    target_layout_obj_key: str = "layout_file_obj"
    lookup_file_obj_key: str = "lookup_file_obj"
    
    # Layout file column mappings (fully configurable)
    layout_columns: Dict[str, str] = field(default_factory=lambda: {
        "field_name": "Data Field",  # The column name in layout file for field names
        "usage": "Usage",  # The column name for required/optional flag
        "category": "Category",  # The column name for grouping/categorization
    })
    
    # Internal column names (after normalization)
    internal_field_name: str = "Internal Field"
    internal_usage_name: str = "Usage"
    internal_category_name: str = "Category"
    
    # Usage value mappings (what values mean "mandatory" vs "optional")
    usage_mappings: Dict[str, List[str]] = field(default_factory=lambda: {
        "mandatory": ["Mandatory", "Required", "Yes", "Y", "1", "true", "TRUE"],
        "optional": ["Optional", "No", "N", "0", "false", "FALSE"]
    })
    
    # Lookup file configuration (optional - if not provided, validations pass)
    lookup_config: Optional[Dict[str, Any]] = None
    
    # Validation rules configuration
    validation_config: Dict[str, Any] = field(default_factory=lambda: {
        "require_lookups": False,  # If True, validation fails if lookups missing
        "skip_if_no_lookups": True,  # If True, skip lookup-based validations if lookups unavailable
    })
    
    # Output configuration
    output_config: Dict[str, Any] = field(default_factory=lambda: {
        "include_anonymization": True,
        "default_format": "csv",
    })
    
    def get_mandatory_usage_values(self) -> List[str]:
        """Get all values that indicate mandatory/required fields."""
        return self.usage_mappings.get("mandatory", [])
    
    def get_optional_usage_values(self) -> List[str]:
        """Get all values that indicate optional fields."""
        return self.usage_mappings.get("optional", [])
    
    def is_mandatory(self, usage_value: str) -> bool:
        """Check if a usage value indicates mandatory/required."""
        normalized = str(usage_value).strip()
        return normalized in [v.lower() for v in self.get_mandatory_usage_values()]
    
    def is_optional(self, usage_value: str) -> bool:
        """Check if a usage value indicates optional."""
        normalized = str(usage_value).strip()
        return normalized in [v.lower() for v in self.get_optional_usage_values()]
    
    def normalize_usage_value(self, usage_value: str) -> str:
        """Normalize usage value to standard 'Mandatory' or 'Optional'."""
        normalized = str(usage_value).strip()
        mandatory_values = [v.lower() for v in self.get_mandatory_usage_values()]
        optional_values = [v.lower() for v in self.get_optional_usage_values()]
        
        if normalized.lower() in mandatory_values:
            return "Mandatory"
        elif normalized.lower() in optional_values:
            return "Optional"
        else:
            # Default to optional if unclear
            return "Optional"


# Default domain configurations
DEFAULT_CLAIMS_CONFIG = DomainConfig(
    domain_name="claims",
    app_title="Claims Mapper and Validator",
    app_description="Map, validate, and transform healthcare claims data",
    source_file_label="external file",
    source_file_help="Upload your external file (CSV, TXT, TSV, XLSX, JSON, PARQUET)",
    target_layout_label="Internal Layout",
    target_layout_help="Upload your internal layout file that defines the expected structure",
    lookup_file_label="Lookup file",
    lookup_file_help="Upload lookup file (optional) for validation",
)

DEFAULT_GENERIC_CONFIG = DomainConfig(
    domain_name="generic",
    app_title="Data Mapper and Validator",
    app_description="Map, validate, and transform data files",
    source_file_label="Source File",
    target_layout_label="Target Layout",
    lookup_file_label="Lookup File",
)


def get_domain_config(domain_name: Optional[str] = None) -> DomainConfig:
    """Get domain configuration for the specified domain.
    
    Args:
        domain_name: Name of the domain. If None, returns default claims config
            for backward compatibility.
    
    Returns:
        DomainConfig instance for the specified domain.
    """
    if domain_name is None:
        # Default to claims for backward compatibility
        return DEFAULT_CLAIMS_CONFIG
    
    domain_name_lower = domain_name.lower()
    
    # Map known domains
    domain_map = {
        "claims": DEFAULT_CLAIMS_CONFIG,
        "generic": DEFAULT_GENERIC_CONFIG,
    }
    
    if domain_name_lower in domain_map:
        return domain_map[domain_name_lower]
    
    # Return generic config for unknown domains
    config = DEFAULT_GENERIC_CONFIG
    config.domain_name = domain_name_lower
    return config
