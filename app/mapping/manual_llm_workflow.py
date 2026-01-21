"""Manual LLM workflow: Generate payload for user to paste into Copilot Studio."""
from typing import Any, Dict, List, Optional
import json
import pandas as pd


def generate_batch_payload(
    layout_df: Any,
    claims_df: Any,
    existing_mappings: Optional[Dict[str, str]] = None,
    minimal: bool = True
) -> Dict[str, Any]:
    """
    Generate a batch payload for all internal fields to send to Copilot Studio.
    
    Args:
        layout_df: Internal layout DataFrame with "Internal Field" column
        claims_df: Source claims DataFrame
        existing_mappings: Optional existing field mappings
        
    Returns:
        Complete payload dictionary ready for JSON serialization
    """
    # Get usage column name
    try:
        from core.domain_config import get_domain_config
        config = get_domain_config()
        usage_col = config.internal_usage_name
    except Exception:
        usage_col = "Usage"
    
    # Filter to only mandatory fields
    if usage_col in layout_df.columns:
        mandatory_df = layout_df[layout_df[usage_col].astype(str).str.strip().str.lower() == "mandatory"]
        internal_fields: List[str] = [str(x) for x in mandatory_df["Internal Field"].dropna().tolist()]
    else:
        # If no Usage column, include all fields
        internal_fields: List[str] = [str(x) for x in layout_df["Internal Field"].dropna().tolist()]
    
    # Get examples - handle case where "Example Value" column might not exist
    # Only get examples for mandatory fields
    if "Example Value" in layout_df.columns:
        examples = {}
        for field in internal_fields:
            field_row = layout_df[layout_df["Internal Field"] == field]
            if not field_row.empty:
                example_val = field_row["Example Value"].iloc[0] if "Example Value" in field_row.columns else ""
                examples[field] = example_val
    else:
        examples = {}
    
    # Get all source columns metadata (ultra-minimal for paste limits)
    source_columns_metadata = []
    max_samples = 1 if minimal else 2  # Only 1 sample in minimal mode
    max_sample_length = 20 if minimal else 30  # Shorter truncation
    
    for col in claims_df.columns.tolist():
        # Limit samples and truncate long values
        col_sample_values = []
        if col in claims_df.columns:
            samples = claims_df[col].dropna().astype(str).head(max_samples).tolist()
            col_sample_values = [s[:max_sample_length] + "..." if len(s) > max_sample_length else s for s in samples]
        
        # Ultra-minimal metadata - only essential fields
        col_metadata = {
            "name": col
        }
        
        # Only add data_type if not minimal
        if not minimal:
            col_metadata["data_type"] = str(claims_df[col].dtype) if col in claims_df.columns else "object"
        
        # Add sample_rows with Value property for agent (required)
        if len(col_sample_values) > 0:
            col_metadata["sample_rows"] = [{"Value": val} for val in col_sample_values]
        
        source_columns_metadata.append(col_metadata)
    
    # Get field groups - create a mapping of field name to category
    field_groups_dict = {}
    if "Category" in layout_df.columns and "Internal Field" in layout_df.columns:
        for idx, row in layout_df.iterrows():
            field_name = str(row["Internal Field"] if "Internal Field" in row.index else "").strip()
            category = str(row["Category"] if "Category" in row.index else "").strip()
            if field_name:
                field_groups_dict[field_name] = category
    
    # Build payload matching agent's expected format
    payload = {
        "internal_fields": [],  # Array of all mandatory fields (batch format)
        "source_columns": source_columns_metadata,
        "domain_context": {
            "domain_name": "claims",
            "field_groups": field_groups_dict
        },
        "existing_mappings": existing_mappings or {},
        "user_preferences": {
            "prefer_exact_matches": False,
            "allow_multiple_suggestions": True
        }
    }
    
    # Note: algorithmic_suggestions would be added per-field if we had them
    # For batch processing, agent should handle all fields in internal_fields array
    
    # Create a mapping of field name to usage (already have usage_col from above)
    field_usage_map = {}
    if usage_col in layout_df.columns:
        for idx, row in layout_df.iterrows():
            # row is a pandas Series, access columns directly
            field_name = str(row["Internal Field"] if "Internal Field" in row.index else "").strip()
            usage_value = str(row[usage_col] if usage_col in row.index else "Optional").strip()
            if field_name:
                field_usage_map[field_name] = usage_value
    
    # Add each internal field
    for internal in internal_fields:
        expected_example = examples.get(internal, "")
        expected_type = "text"
        if any(keyword in internal.lower() for keyword in ["zip", "npi", "cpt", "icd", "date", "dob"]):
            expected_type = "numeric" if "zip" in internal.lower() or "npi" in internal.lower() or "cpt" in internal.lower() else "text"
        
        # Get usage value, default to "Optional"
        usage_value = field_usage_map.get(internal, "Optional")
        if usage_value.lower() in ["mandatory", "required", "yes", "true"]:
            usage_value = "Mandatory"
        else:
            usage_value = "Optional"
        
        # Truncate example value if too long
        example_val = str(expected_example)[:30] + "..." if len(str(expected_example)) > 30 else str(expected_example)
        
        # Ultra-minimal field metadata - only essential fields
        internal_field_metadata = {
            "name": internal
        }
        
        # Only add optional fields if not minimal
        if not minimal:
            internal_field_metadata["data_type"] = expected_type
            internal_field_metadata["category"] = field_groups_dict.get(internal, "")
            internal_field_metadata["usage"] = usage_value
            if example_val:
                internal_field_metadata["example_value"] = example_val
        else:
            # In minimal mode, only add if they have values
            if example_val:
                internal_field_metadata["example_value"] = example_val
        
        payload["internal_fields"].append(internal_field_metadata)
    
    return payload


def parse_llm_response(response_text: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse the LLM response and extract mappings.
    
    Args:
        response_text: Raw response text from Copilot Studio (may contain JSON)
        
    Returns:
        Dictionary of mappings: {internal_field: {"value": column, "confidence": float, "source": "llm"}}
    """
    # Try to extract JSON from text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    
    if json_start < 0 or json_end <= json_start:
        raise ValueError("No valid JSON found in response")
    
    json_str = response_text[json_start:json_end]
    
    try:
        response_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in response: {e}")
    
    # Parse the response structure
    mappings: Dict[str, Dict[str, Any]] = {}
    
    # Handle different response formats
    if "field_mappings" in response_data:
        # Format: {"field_mappings": {"field1": "column1", ...}}
        for field, column in response_data["field_mappings"].items():
            if isinstance(column, str):
                mappings[field] = {
                    "value": column,
                    "confidence": 1.0,
                    "source": "llm"
                }
            elif isinstance(column, dict):
                mappings[field] = {
                    "value": column.get("column") or column.get("value"),
                    "confidence": column.get("confidence", 1.0),
                    "source": "llm"
                }
    elif "mappings" in response_data:
        # Format: {"mappings": {"field1": "column1", "field2": "column2"}}
        for field, column in response_data["mappings"].items():
            if isinstance(column, str):
                mappings[field] = {
                    "value": column,
                    "confidence": 1.0,
                    "source": "llm"
                }
            elif isinstance(column, dict):
                mappings[field] = {
                    "value": column.get("column") or column.get("value"),
                    "confidence": column.get("confidence", 1.0),
                    "source": "llm"
                }
    elif "suggestions" in response_data:
        # Format: {"suggestions": [{"field": "field1", "column": "column1", "confidence": 0.9}, ...]}
        suggestions = response_data["suggestions"]
        if isinstance(suggestions, list):
            for suggestion in suggestions:
                field = suggestion.get("field") or suggestion.get("internal_field") or suggestion.get("name")
                column = suggestion.get("column") or suggestion.get("value")
                confidence = suggestion.get("confidence", 0.0)
                
                if field and column:
                    mappings[field] = {
                        "value": column,
                        "confidence": confidence,
                        "source": "llm"
                    }
        elif isinstance(suggestions, dict):
            # Format: {"suggestions": {"field1": {"column": "col1", "confidence": 0.9}, ...}}
            for field, suggestion in suggestions.items():
                if isinstance(suggestion, dict):
                    column = suggestion.get("column") or suggestion.get("value")
                    confidence = suggestion.get("confidence", 0.0)
                    if column:
                        mappings[field] = {
                            "value": column,
                            "confidence": confidence,
                            "source": "llm"
                        }
                elif isinstance(suggestion, str):
                    # Format: {"suggestions": {"field1": "col1", ...}}
                    mappings[field] = {
                        "value": suggestion,
                        "confidence": 1.0,
                        "source": "llm"
                    }
    else:
        # Try to parse as direct field->column mapping
        for key, value in response_data.items():
            if isinstance(value, str):
                mappings[key] = {
                    "value": value,
                    "confidence": 1.0,
                    "source": "llm"
                }
            elif isinstance(value, dict) and "column" in value:
                mappings[key] = {
                    "value": value["column"],
                    "confidence": value.get("confidence", 1.0),
                    "source": "llm"
                }
    
    return mappings
