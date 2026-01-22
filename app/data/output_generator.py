# --- output_generator.py ---
"""Output generation functions."""
import streamlit as st  # type: ignore[import-not-found]
import json
from typing import Any, Dict, Optional, List
import pandas as pd  # type: ignore[import-not-found]

st: Any = st  # type: ignore[assignment]

from data.anonymizer import anonymize_claims_data
from ui.mapping_ui import generate_mapping_table


def save_mapping_template(final_mapping: Dict[str, Dict[str, Any]], filename: str = "mapping_template.json") -> str:
    """Export mapping as JSON template."""
    return json.dumps(final_mapping, indent=2)


def load_mapping_template(template_json: str) -> Dict[str, Dict[str, Any]]:
    """Load mapping from JSON template."""
    return json.loads(template_json)


def generate_all_outputs():
    """
    Generates anonymized claims file and mapping table outputs
    based on the latest field mappings.
    Includes error handling and progress tracking.
    """
    final_mapping = st.session_state.get("final_mapping")
    claims_df = st.session_state.get("claims_df")
    layout_df = st.session_state.get("layout_df")

    if final_mapping and claims_df is not None and layout_df is not None:
        try:
            # --- Generate outputs with error handling ---
            anonymized_df = anonymize_claims_data(claims_df, final_mapping)
            mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)

            # --- Save in session_state
            st.session_state.anonymized_df = anonymized_df
            st.session_state.mapping_table = mapping_table
        except Exception as e:
            # Import here to avoid circular imports
            from core.error_handling import get_user_friendly_error
            error_msg = get_user_friendly_error(e)
            st.error(f"Error generating outputs: {error_msg}")
            st.session_state.anonymized_df = None
            st.session_state.mapping_table = None
    else:
        st.session_state.anonymized_df = None
        st.session_state.mapping_table = None


def generate_onboarding_script_output(
    client_name: str,
    plan_sponsor_name: str,
    domain_name: str = "PlanSponsorClaims",
    preprocessor_name: Optional[str] = None,
    file_name_date_format: str = "yyyyMMdd",
    file_name_regex_pattern: Optional[str] = None,
    primary_key: Optional[str] = None,
    preprocessing_primary_key: Optional[str] = None,
    entity_type: str = "Medical",
    demographic_match_tier_config: str = "tier1,tier2",
    sort_col_name: Optional[str] = None,
    null_threshold_percentage: int = 15,
    process_curation: bool = True,
    inbound_path: str = "/mnt/data/inbound/raw/",
    layout_df: Optional[Any] = None,
    final_mapping: Optional[Dict[str, Dict[str, Any]]] = None
) -> str:
    """
    Generate onboarding SQL script.
    
    Returns:
        SQL script as string
    """
    from data.onboarding_scripts import generate_onboarding_sql_script
    
    # Get file metadata from session state
    file_metadata = st.session_state.get("claims_file_metadata", {})
    file_format = file_metadata.get("format", "csv")
    file_separator = file_metadata.get("sep", "\t")
    file_has_header = file_metadata.get("header", False)
    file_date_format = file_metadata.get("dateFormat", "yyyyMd")
    mapping_date_format = "yyyy-MM-dd"  # Default mapping date format
    
    return generate_onboarding_sql_script(
        client_name=client_name,
        plan_sponsor_name=plan_sponsor_name,
        domain_name=domain_name,
        preprocessor_name=preprocessor_name,
        file_name_date_format=file_name_date_format,
        file_name_regex_pattern=file_name_regex_pattern,
        primary_key=primary_key,
        preprocessing_primary_key=preprocessing_primary_key,
        entity_type=entity_type,
        demographic_match_tier_config=demographic_match_tier_config,
        sort_col_name=sort_col_name,
        null_threshold_percentage=null_threshold_percentage,
        process_curation=process_curation,
        inbound_path=inbound_path,
        file_format=file_format,
        file_separator=file_separator,
        file_has_header=file_has_header,
        file_date_format=file_date_format,
        mapping_date_format=mapping_date_format,
        layout_df=layout_df,
        final_mapping=final_mapping
    )


def generate_test_data_outputs(
    layout_df: Any,
    final_mapping: Dict[str, Dict[str, Any]],
    records_per_scenario: int = 30,
    include_scenarios: Optional[List[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Generate test data with scenarios.
    
    Returns:
        Dictionary mapping scenario names to DataFrames (always returns DataFrames for combining)
    """
    from data.test_data_generator import generate_test_data_with_scenarios
    
    claims_df = st.session_state.get("claims_df")
    file_metadata = st.session_state.get("claims_file_metadata", {})
    # Don't pass file_format to keep as DataFrames - conversion happens in tab_downloads
    file_separator = file_metadata.get("sep", "\t")
    file_has_header = file_metadata.get("header", False)
    file_date_format = file_metadata.get("dateFormat", "yyyyMMdd")
    
    # Always return DataFrames (file_format=None) so we can combine them
    result = generate_test_data_with_scenarios(
        layout_df=layout_df,
        final_mapping=final_mapping,
        claims_df=claims_df,
        records_per_scenario=records_per_scenario,
        include_scenarios=include_scenarios,
        file_format=None,  # Keep as DataFrames for combining
        file_separator=file_separator,
        file_has_header=file_has_header,
        file_date_format=file_date_format,
        apply_reverse_mappings=True
    )
    
    # Ensure all values are DataFrames (in case conversion happened anyway)
    dataframes_only = {}
    for scenario_name, scenario_data in result.items():
        if isinstance(scenario_data, pd.DataFrame):
            dataframes_only[scenario_name] = scenario_data
        # Skip non-DataFrame values (shouldn't happen with file_format=None)
    
    return dataframes_only

