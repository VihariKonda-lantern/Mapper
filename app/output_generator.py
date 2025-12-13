# --- output_generator.py ---
"""Output generation functions."""
import streamlit as st  # type: ignore[import-not-found]
import json
from typing import Any, Dict

st: Any = st  # type: ignore[assignment]

from anonymizer import anonymize_claims_data
from mapping_ui import generate_mapping_table


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
            from improvements_utils import get_user_friendly_error
            error_msg = get_user_friendly_error(e)
            st.error(f"Error generating outputs: {error_msg}")
            st.session_state.anonymized_df = None
            st.session_state.mapping_table = None
    else:
        st.session_state.anonymized_df = None
        st.session_state.mapping_table = None

