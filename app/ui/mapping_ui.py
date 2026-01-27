# --- mapping_ui.py ---
"""Field mapping UI functions."""
import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
from typing import Any, List, Dict, Set, Optional, Tuple
import time
import difflib
import unicodedata

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]

from data.layout_loader import get_field_groups, get_required_fields, get_optional_fields
from mapping.mapping_engine import get_enhanced_automap
from data.transformer import transform_claims_data
from core.state_manager import initialize_undo_redo
from data.anonymizer import anonymize_claims_data
from utils.improvements_utils import DEBOUNCE_DELAY_SECONDS
from ui.ui_components import render_tooltip  # type: ignore[import-untyped]
from ui.ux_enhancements import render_validation_feedback  # type: ignore[import-untyped]


def _calculate_column_confidence(field_name: str, column_name: str) -> float:
    """
    Calculate a simple confidence score between a field name and column name.
    Uses fuzzy string matching.
    
    Args:
        field_name: Internal field name
        column_name: Source column name
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    field_lower = field_name.lower().replace("_", " ").replace("-", " ")
    col_lower = column_name.lower().replace("_", " ").replace("-", " ")
    
    # Use SequenceMatcher for fuzzy matching
    ratio = difflib.SequenceMatcher(None, field_lower, col_lower).ratio()
    
    # Boost score if field name is contained in column name or vice versa
    if field_lower in col_lower or col_lower in field_lower:
        ratio = min(1.0, ratio + 0.2)
    
    return ratio


def _sort_columns_by_confidence(
    field_name: str,
    columns: List[str],
    ai_suggested_column: Optional[str] = None,
    ai_confidence: Optional[float] = None,
    algorithmic_scores: Optional[Dict[str, float]] = None
) -> List[Tuple[str, Optional[float]]]:
    """
    Sort columns by confidence score, with AI-suggested column at top if available.
    Returns tuples of (column_name, algorithmic_score) for display.
    
    Args:
        field_name: Internal field name
        columns: List of column names to sort
        ai_suggested_column: Optional AI-suggested column
        ai_confidence: Optional AI confidence score
        algorithmic_scores: Dict of column -> algorithmic confidence score
        
    Returns:
        Sorted list of tuples: [(column_name, algo_score), ...]
    """
    # Calculate confidence scores for all columns
    column_scores: List[Tuple[str, float, Optional[float]]] = []
    
    for col in columns:
        # Get algorithmic score
        algo_score = None
        if algorithmic_scores and col in algorithmic_scores:
            algo_score = algorithmic_scores[col] / 100.0  # Convert back to 0-1 range
        elif col == ai_suggested_column and ai_confidence is not None:
            algo_score = ai_confidence / 100.0 if ai_confidence > 1.0 else ai_confidence
        else:
            algo_score = _calculate_column_confidence(field_name, col)
        
        column_scores.append((col, algo_score, algo_score))
    
    # Sort by confidence (descending), then alphabetically for ties
    column_scores.sort(key=lambda x: (-x[1], x[0]))
    
    # Return tuples with scores for display
    return [(col, algo_score) for col, _, algo_score in column_scores]


def dual_input_field(field_label: str, options: List[str], key_prefix: str, col_name_map: Optional[Dict[str, str]] = None, default_value: Optional[str] = None, allow_manual_input: bool = False) -> Optional[str]:
    """
    Renders a dropdown with optional manual text input.
    Returns the selected value or manual input.
    
    Args:
        field_label: Label for the field
        options: List of dropdown options (may include confidence scores)
        key_prefix: Unique key prefix for the widget
        col_name_map: Optional mapping from display text to actual column name
        default_value: Optional default column name to select
        allow_manual_input: If True, shows a text input field for manual entry
    """
    # Find the index of the default value if provided
    select_idx = 0  # Default to empty (unmapped)
    if default_value and col_name_map:
        # Reverse lookup: find display text for the actual column name
        for display_text, actual_col in col_name_map.items():
            if actual_col == default_value:
                # Find index in options
                for idx, option in enumerate(options):
                    if option == display_text:
                        select_idx = idx + 1  # +1 because options list has "" prepended
                        break
                break
    
    if allow_manual_input:
        # Show both dropdown and text input for manual entry
        col_dropdown, col_input = st.columns([2, 1])
        
        with col_dropdown:
            dropdown_selection = st.selectbox(
                "Select column", 
                options=[""] + options,
                index=select_idx,
                key=f"{key_prefix}_dropdown",
                label_visibility="collapsed"
            )
        
        with col_input:
            manual_input = st.text_input(
                "Or type manually",
                value="",
                key=f"{key_prefix}_manual",
                placeholder="Type value...",
                label_visibility="collapsed"
            )
        
        # Prioritize manual input if provided, otherwise use dropdown
        if manual_input and manual_input.strip():
            return manual_input.strip()
        elif dropdown_selection and dropdown_selection != "":
            if col_name_map and dropdown_selection in col_name_map:
                return col_name_map[dropdown_selection]
            elif " (" in dropdown_selection:
                return dropdown_selection.split(" (")[0]
            else:
                return dropdown_selection.strip()
        return None
    else:
        # Dropdown only (for Client_Name)
        dropdown_selection = st.selectbox(
            "Select column", 
            options=[""] + options,
            index=select_idx,
            key=f"{key_prefix}_dropdown",
            label_visibility="collapsed"
        )
        
        # Extract column name from selected option (remove confidence scores)
        if dropdown_selection and dropdown_selection != "":
            if col_name_map and dropdown_selection in col_name_map:
                return col_name_map[dropdown_selection]
            elif " (" in dropdown_selection:
                return dropdown_selection.split(" (")[0]
            else:
                return dropdown_selection.strip()
        return None


def generate_mapping_table(layout_df: Any, final_mapping: Dict[str, Dict[str, Any]], claims_df: Any) -> Any:
    """Build a comprehensive mapping table across internal and claims fields.

    Includes internal fields with mapped claims columns, data types, and
    required/optional flag, plus a section for unmapped claims columns.

    Args:
        layout_df: Internal layout DataFrame-like.
        final_mapping: Final field mappings `{internal: {"value": col}}`.
        claims_df: Uploaded claims DataFrame-like.

    Returns:
        DataFrame-like representing the full mapping table.
    """
    records: List[Dict[str, Any]] = []

    # --- 1. Internal Layout Side ---
    for _, row in layout_df.iterrows():
        internal_field = row["Internal Field"]
        usage = row["Usage"].strip().lower()
        required_status = "Required" if usage == "mandatory" else "Optional"

        mapped_column = final_mapping.get(internal_field, {}).get("value", "")
        data_type = ""

        if mapped_column and mapped_column in claims_df.columns:
            data_type = str(claims_df[mapped_column].dtype)  # type: ignore[no-untyped-call]

        records.append({
            "Internal Field": internal_field,
            "Claims File Column": mapped_column,
            "Data Type": data_type,
            "Required/Optional": required_status
        })

    # --- 2. Unmapped Claims Columns Side ---
    mapped_claims_cols: Set[str] = {str(info.get("value", "")) for info in final_mapping.values()}
    all_claims_cols = set(claims_df.columns)

    unmapped_claims_cols = all_claims_cols - mapped_claims_cols

    for col in sorted(unmapped_claims_cols):
        data_type = str(claims_df[col].dtype)  # type: ignore[no-untyped-call]
        records.append({
            "Internal Field": "",
            "Claims File Column": col,
            "Data Type": data_type,
            "Required/Optional": "Unmapped Claim Column"
        })

    # --- Final Mapping Table ---
    mapping_table = pd.DataFrame(records)
    return mapping_table


def calculate_mapping_progress(layout_df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> Tuple[int, int, int]:
    """Calculates progress stats for required fields mapping."""
    required_fields = get_required_fields(layout_df)["Internal Field"].tolist()
    mapped_fields = [field for field in required_fields if field in final_mapping and final_mapping[field]["value"]]
    total_required = len(required_fields)
    mapped_required = len(mapped_fields)
    percent_complete = int((mapped_required / total_required) * 100) if total_required > 0 else 0

    return mapped_required, total_required, percent_complete


def render_field_mapping_tab():
    """
    Renders the Field Mapping tab where users map source columns to internal fields.
    Fields are grouped by category and separated by required/optional.
    """
    layout_df = st.session_state.get("layout_df")
    claims_df = st.session_state.get("claims_df")

    if layout_df is None or claims_df is None:
        st.info("Please upload both layout and claims files to begin mapping.")
        return

    # Initialize undo/redo
    initialize_undo_redo()
    # Initialize widget counter for unique keys (reset each time function is called)
    widget_counter = 0

    # --- Real-time Mapping Preview (shows as soon as any field is mapped) ---
    final_mapping = st.session_state.get("final_mapping", {})
    has_any_mapping = any(info.get("value") for info in final_mapping.values())
    
    if has_any_mapping:
        st.markdown("#### Real-time Mapping Preview")
        try:
            # Show max 5 rows (4 data rows + 1 header = 5 total)
            # First anonymize the original claims data, then transform it
            claims_preview = claims_df.head(4)
            anonymized_preview = anonymize_claims_data(claims_preview, final_mapping)
            preview_mapped = transform_claims_data(anonymized_preview, final_mapping)
            if preview_mapped is not None and not preview_mapped.empty:
                st.dataframe(preview_mapped, use_container_width=True)  # type: ignore[no-untyped-call]
                st.caption(f"Showing first 4 rows of anonymized mapped data ({len(preview_mapped.columns)} mapped fields)")
            else:
                st.info("No mapped data to preview yet. Start mapping fields to see the preview.")
        except Exception as e:
            st.warning(f"Preview unavailable: {e}")
    else:
        # Show placeholder when no mappings yet
        st.info("Map fields below to see a real-time preview of your transformed data.")

    required_fields = get_required_fields(layout_df)

    # --- Safety Check ---
    if not isinstance(required_fields, pd.DataFrame):  # type: ignore[redundant-cast,type-py]
        st.error("Error: Required fields extraction failed. Please check layout file format.")
        st.stop()

    field_groups = get_field_groups(required_fields)

    if "final_mapping" not in st.session_state:
        st.session_state.final_mapping = {}

    final_mapping: Dict[str, Dict[str, Any]] = st.session_state.get("final_mapping", {})

    # --- AI Auto-Mapping Suggestions ---
    if "auto_mapping" not in st.session_state or not st.session_state.auto_mapping:
        st.session_state.auto_mapping = get_enhanced_automap(layout_df, claims_df)

    ai_suggestions = st.session_state.get("auto_mapping", {})

    # --- Auto-Apply High Confidence Suggestions (≥80%) ---
    from core.config_loader import AI_CONFIDENCE_THRESHOLD
    if "final_mapping" not in st.session_state:
        st.session_state.final_mapping = {}

    auto_mapped: List[str] = []
    for field, info in ai_suggestions.items():
        score = info.get("score", 0)
        # Only auto-apply if confidence >= 80% (AI_CONFIDENCE_THRESHOLD)
        if score >= AI_CONFIDENCE_THRESHOLD and field not in final_mapping:
            final_mapping[field] = {
                "mode": "auto",
                "value": info["value"],
                "confidence": score,
                "source": info.get("source", "algorithmic")
            }
            auto_mapped.append(field)

    st.session_state.auto_mapped_fields = auto_mapped

    # --- Mapping Progress ---
    _mapped_required, total_required, _percent_complete = calculate_mapping_progress(layout_df, final_mapping)
    
    # --- Enhanced Search and Filter with Debouncing ---
    search_col1, search_col2, search_col3 = st.columns([3, 2, 2])
    with search_col1:
        # Get raw input
        raw_search_input = st.text_input(
            "🔍 Search fields:",
            value=st.session_state.get("field_search_input_raw", ""),
            key="field_search_input_raw",
            placeholder="Type to search field names...",
            help="Search for fields by name (debounced)"
        )
        
        # Debounce the search input
        current_time = time.time()
        last_search_time = st.session_state.get("field_search_last_time", 0)
        debounced_search = st.session_state.get("field_search_input", "")
        
        # Update debounced value if enough time has passed or if input changed significantly
        if raw_search_input != st.session_state.get("field_search_input_raw_prev", ""):
            st.session_state.field_search_input_raw_prev = raw_search_input
            if current_time - last_search_time >= DEBOUNCE_DELAY_SECONDS:
                debounced_search = raw_search_input
                st.session_state.field_search_input = debounced_search
                st.session_state.field_search_last_time = current_time
            else:
                # Store pending input
                st.session_state.field_search_pending = raw_search_input
        
        # Check if debounce delay has passed for pending input
        if "field_search_pending" in st.session_state:
            if current_time - last_search_time >= DEBOUNCE_DELAY_SECONDS:
                debounced_search = st.session_state.field_search_pending
                st.session_state.field_search_input = debounced_search
                st.session_state.field_search_last_time = current_time
                del st.session_state.field_search_pending
        
        search_query = debounced_search
    
    with search_col2:
        filter_status = st.selectbox(
            "Filter by status:",
            options=["All", "Mapped", "Unmapped", "AI Suggested"],
            key="filter_status",
            help="Filter fields by mapping status"
        )
    
    with search_col3:
        filter_required = st.selectbox(
            "Filter by type:",
            options=["All", "Required", "Optional"],
            key="filter_required",
            help="Filter by field requirement"
        )
            
    # --- Required Fields Mapping ---
    # Get search query from session state
    search_query = st.session_state.get("field_search_input", "")
    
    for group in field_groups:
        group_fields = required_fields[required_fields["Category"] == group]
        
        # Deduplicate fields within the group - keep first occurrence of each field
        group_fields = group_fields.drop_duplicates(subset=["Internal Field"], keep="first")  # type: ignore[no-untyped-call]

        # Apply search filter
        if search_query and search_query.strip():
            search_lower = search_query.lower()
            group_fields = group_fields[
                group_fields["Internal Field"].str.lower().str.contains(search_lower, na=False)  # type: ignore[no-untyped-call]
            ]

        group_field_names = group_fields["Internal Field"].tolist()
        
        # Apply status filter
        if filter_status == "Mapped":
            group_field_names = [f for f in group_field_names if f in final_mapping and final_mapping[f].get("value")]
        elif filter_status == "Unmapped":
            group_field_names = [f for f in group_field_names if f not in final_mapping or not final_mapping[f].get("value")]
        elif filter_status == "AI Suggested":
            group_field_names = [f for f in group_field_names if f in ai_suggestions]
        
        if not group_field_names:
            continue
        
        mapped_count = sum(
            1 for f in group_field_names
            if f in final_mapping and final_mapping[f].get("value")
        )
        total_in_group = len(group_field_names)
        
        group_label = f"{group} ({mapped_count}/{total_in_group} mapped)"

        # Keep expander open if it has mapped fields to prevent collapse when selecting dropdown
        with st.expander(group_label, expanded=(mapped_count > 0)):
            for _, (_, row) in enumerate(group_fields.iterrows()):
                field_name = row["Internal Field"]
                raw_columns = claims_df.columns.tolist()
                
                # Clean and filter column names - remove empty, blank, or whitespace-only columns
                # Also handle BOM and encoding issues
                cleaned_columns = []
                for col in raw_columns:
                    if col is None:
                        continue
                    # Convert to string and strip
                    col_str = str(col).strip()
                    # Remove BOM and other invisible characters
                    col_str = col_str.encode('utf-8').decode('utf-8-sig')  # Remove BOM
                    col_str = unicodedata.normalize('NFKC', col_str)  # Normalize unicode
                    col_str = col_str.strip()
                    # Skip empty or whitespace-only columns
                    if col_str:
                        cleaned_columns.append(col_str)
                
                # If no valid columns found, skip this field
                if not cleaned_columns:
                    continue

                # --- AI suggestion if available ---
                suggestion_info = ai_suggestions.get(field_name, {})
                suggested_column = suggestion_info.get("value")
                suggestion_score = suggestion_info.get("score")
                suggestion_source = suggestion_info.get("source", "algorithmic")  # Default to algorithmic
                
                # Convert score to percentage if it's between 0 and 1
                if suggestion_score is not None and suggestion_score <= 1.0:
                    suggestion_score = suggestion_score * 100

                # Get algorithmic scores
                algorithmic_scores = suggestion_info.get("algorithmic_scores", {})
                
                # Sort columns by confidence score (returns tuples with scores)
                field_col_options_with_scores = _sort_columns_by_confidence(
                    field_name,
                    cleaned_columns,
                    suggested_column,
                    suggestion_score,
                    algorithmic_scores
                )
                
                # Format dropdown options with confidence scores
                field_col_options = []
                field_col_name_map = {}  # Map display text to actual column name
                for col_name, algo_score in field_col_options_with_scores:
                    # Ensure col_name is not empty
                    if not col_name or not col_name.strip():
                        continue
                    
                    display_parts = []
                    if algo_score is not None:
                        display_parts.append(f"Algo: {algo_score*100:.0f}%")
                    
                    if len(display_parts) > 0:
                        display_text = f"{col_name} ({', '.join(display_parts)})"
                    else:
                        display_text = col_name
                    
                    field_col_options.append(display_text)
                    field_col_name_map[display_text] = col_name

                default_value = final_mapping.get(field_name, {}).get("value", None)
                req_default_label: Optional[str] = str(default_value) if default_value else None

                # Create unique key using group, field name, and incrementing counter
                # Counter ensures absolute uniqueness even with duplicate rows
                widget_counter += 1
                unique_key = f"req_{group}_{field_name}_{widget_counter}"
                # Sanitize key to remove special characters that might cause issues
                unique_key = unique_key.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")

                # --- Clean 2-column layout ---
                col1, col2 = st.columns([2.5, 3.5])
                
                with col1:
                    # Field name
                    display_name = field_name
                    if search_query and search_query.strip():
                        import re
                        pattern = re.compile(re.escape(search_query), re.IGNORECASE)
                        display_name = pattern.sub(lambda m: f"<mark style='background-color: #e5e7eb; padding: 2px 4px;'>{m.group()}</mark>", field_name)
                    
                    st.markdown(f"**{display_name}**", unsafe_allow_html=True)
                    
                    # Show algorithmic confidence score below field name
                    algorithmic_scores = suggestion_info.get("algorithmic_scores", {})
                    
                    if suggested_column:
                        algo_score = algorithmic_scores.get(suggested_column, None)
                        
                        if algo_score is not None:
                            scores_text = f"Algo: {algo_score:.0f}%"
                            st.caption(f"<span style='color: #6c757d; font-size: 0.85em;'>{scores_text}</span>", unsafe_allow_html=True)
                    
                    # Subtle status indicator (only if mapped)
                    if field_name in final_mapping and final_mapping[field_name].get("value"):
                        mapped_col = final_mapping[field_name].get("value")
                        if mapped_col and mapped_col in claims_df.columns:
                            col_data = claims_df[mapped_col]
                            null_pct = (col_data.isna().sum() / len(col_data) * 100) if len(col_data) > 0 else 0
                            if null_pct > 50:
                                st.caption("⚠️ High null rate")
                            elif null_pct > 20:
                                st.caption("⚠️ Moderate null rate")
                
                with col2:
                    selected_clean: Optional[str] = None
                    if field_name in ["plan_sponsor_name", "insurance_plan_name", "client_name"]:
                        widget_counter += 1
                        key_prefix = f"req_{group}_{field_name}_{widget_counter}"
                        key_prefix = key_prefix.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")
                        # Allow manual input for plan_sponsor_name, insurance_plan_name, and client_name
                        allow_manual = field_name in ["insurance_plan_name", "plan_sponsor_name", "client_name"]
                        # Pass the default value so it shows the mapped column
                        selected = dual_input_field(field_name, field_col_options, key_prefix=key_prefix, col_name_map=field_col_name_map, default_value=req_default_label, allow_manual_input=allow_manual)
                        selected_clean = selected.strip() if selected else None
                        # For dual_input_field, also read current value from session state for immediate preview
                        if not selected_clean and allow_manual:
                            # Check manual input first
                            manual_key = f"{key_prefix}_manual"
                            manual_value = st.session_state.get(manual_key, "")
                            if manual_value and manual_value.strip():
                                selected_clean = manual_value.strip()
                        if not selected_clean:
                            dropdown_key = f"{key_prefix}_dropdown"
                            current_selection = st.session_state.get(dropdown_key, "")
                            if current_selection and current_selection != "":
                                selected_clean = field_col_name_map.get(current_selection, current_selection.split(" (")[0] if " (" in current_selection else current_selection) if field_col_name_map else current_selection.strip()
                    else:
                        # Find index by matching column name (before confidence scores)
                        # Need to account for the empty string prepended to options
                        select_idx = 0  # Default to empty (unmapped)
                        if req_default_label:
                            # First try to find in the column name map (reverse lookup)
                            for display_text, actual_col in field_col_name_map.items():
                                if actual_col == req_default_label:
                                    # Found the mapped column, now find its index in options
                                    for idx, option in enumerate(field_col_options):
                                        if option == display_text:
                                            select_idx = idx + 1  # +1 because options list has "" prepended
                                            break
                                    break
                            
                            # Fallback: try direct matching if not found in map
                            if select_idx == 0:
                                for idx, option in enumerate(field_col_options):
                                    # Check if option starts with the mapped column name
                                    if option.startswith(req_default_label + " (") or option == req_default_label:
                                        select_idx = idx + 1  # +1 because options list has "" prepended
                                        break
                        
                        selected = st.selectbox(
                            "Select column mapping",
                            options=[""] + field_col_options,
                            index=select_idx,
                            key=unique_key,
                            help=f"Map {field_name} to a column",
                            label_visibility="collapsed"
                        )
                        
                        # Extract column name from selected option (remove confidence scores)
                        # Also read from session state for immediate preview (works even inside form)
                        current_selection = st.session_state.get(unique_key, selected)
                        if current_selection and current_selection != "":
                            selected_clean = field_col_name_map.get(current_selection, current_selection.split(" (")[0] if " (" in current_selection else current_selection)
                        else:
                            selected_clean = None
                    
                    # Preview panel (only when mapped) - shows immediately based on current dropdown selection
                    # For manual inputs, show a simple indicator instead of data preview
                    if selected_clean:
                        if selected_clean in claims_df.columns:
                            try:
                                col_data = claims_df[selected_clean]
                                samples = col_data.dropna().head(3).tolist()
                                fill_rate = (col_data.notna().sum() / len(col_data) * 100) if len(col_data) > 0 else 0.0
                                
                                # Format samples for display
                                sample_display = []
                                for sample in samples[:3]:
                                    sample_str = str(sample)
                                    if len(sample_str) > 30:
                                        sample_str = sample_str[:27] + "..."
                                    sample_display.append(f"• {sample_str}")
                                
                                if not sample_display:
                                    sample_display = ["• (no data)"]
                                
                                st.markdown(f"""
                                    <div style='background-color: #f8f9fa; padding: 0.5rem; border-radius: 4px; border-left: 3px solid #6b7280; font-size: 0.85rem;'>
                                        <div style='color: #6c757d; margin-bottom: 0.2rem;'>{'<br>'.join(sample_display)}</div>
                                        <div style='color: #6c757d; font-size: 0.8rem;'>
                                        <span>Fill Rate: <strong>{fill_rate:.1f}%</strong></span>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            except Exception:
                                pass
                            
                            # Inline validation feedback for mapped columns
                            try:
                                col_data = claims_df[selected_clean]
                                fill_rate = (col_data.notna().sum() / len(col_data) * 100) if len(col_data) > 0 else 0.0
                                if fill_rate < 50:
                                    render_validation_feedback(
                                        is_valid=False,
                                        error_message=f"Low fill rate ({fill_rate:.1f}%) - many null values"
                                    )
                                elif fill_rate >= 50:
                                    render_validation_feedback(
                                        is_valid=True,
                                        success_message=f"Good fill rate ({fill_rate:.1f}%)"
                                    )
                            except Exception:
                                pass
                        elif field_name in ["plan_sponsor_name", "insurance_plan_name", "client_name"]:
                            # For manual inputs, show a simple indicator
                            st.markdown(f"""
                                <div style='background-color: #e8f5e9; padding: 0.5rem; border-radius: 4px; border-left: 3px solid #4caf50; font-size: 0.85rem;'>
                                    <div style='color: #2e7d32;'>
                                        <span>✓ Manual value: <strong>{selected_clean[:50]}{'...' if len(selected_clean) > 50 else ''}</strong></span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            render_validation_feedback(
                                is_valid=True,
                                success_message="Manual value entered"
                            )
                    
                    # Value Mapping UI for Patient_Relationship
                    # Patient_Relationship maps to both patient_relationship_code and patient_relationship_desc
                    # Value mapping is used for patient_relationship_code (SVMRule)
                    if field_name == "patient_relationship_code" and selected_clean:
                        value_mapping_key = f"{unique_key}_value_mapping"
                        existing_value_mapping = final_mapping.get(field_name, {}).get("value_mapping", "")
                        
                        st.markdown("**Value Mapping (for patient_relationship_code):**")
                        st.caption("Enter value mappings in format: source_value,target_value (one per line). Example:\nM,Male\nF,Female\n18,Child")
                        value_mapping_input = st.text_area(
                            "Value Mapping",
                            value=existing_value_mapping,
                            key=value_mapping_key,
                            height=100,
                            help="Map source values to target values. Format: source_value,target_value (one per line). This will be used in SVMRule for patient_relationship_code mapping."
                        )
                        
                        # Save value mapping immediately when changed
                        if value_mapping_input and value_mapping_input.strip():
                            if field_name not in final_mapping:
                                final_mapping[field_name] = {}
                            final_mapping[field_name]["value_mapping"] = value_mapping_input.strip()
                            st.session_state["final_mapping"] = final_mapping.copy()
                    
                    # Value Mapping UI for Patient_Relationship_Desc
                    if field_name == "patient_relationship_desc" and selected_clean:
                        value_mapping_key = f"{unique_key}_value_mapping"
                        existing_value_mapping = final_mapping.get(field_name, {}).get("value_mapping", "")
                        
                        st.markdown("**Value Mapping (for patient_relationship_desc):**")
                        st.caption("Enter value mappings in format: source_value,target_value (one per line). Example:\nM,Male\nF,Female\n18,Child")
                        value_mapping_input = st.text_area(
                            "Value Mapping",
                            value=existing_value_mapping,
                            key=value_mapping_key,
                            height=100,
                            help="Map source values to target values. Format: source_value,target_value (one per line). This will be used in SVMRule for patient_relationship_desc mapping."
                        )
                        
                        # Save value mapping immediately when changed
                        if value_mapping_input and value_mapping_input.strip():
                            if field_name not in final_mapping:
                                final_mapping[field_name] = {}
                            final_mapping[field_name]["value_mapping"] = value_mapping_input.strip()
                            st.session_state["final_mapping"] = final_mapping.copy()

                if selected_clean:
                    # Check if this field needs value mapping (e.g., Patient_Relationship)
                    value_mapping = None
                    if field_name == "patient_relationship_code" or field_name == "patient_relationship_desc":
                        # Get value mapping from session state
                        value_mapping_key = f"{unique_key}_value_mapping"
                        value_mapping = st.session_state.get(value_mapping_key, "")
                        if value_mapping and value_mapping.strip():
                            value_mapping = value_mapping.strip()
                        else:
                            # Also check if it's already in final_mapping
                            value_mapping = final_mapping.get(field_name, {}).get("value_mapping", None)
                    
                    final_mapping[field_name] = {
                            "mode": "manual" if selected_clean != suggested_column else "auto",
                            "value": selected_clean
                        }
                    if value_mapping:
                        final_mapping[field_name]["value_mapping"] = value_mapping
                    # Update session state immediately for automatic saving
                    st.session_state["final_mapping"] = final_mapping.copy()

    # --- Show Unmapped Required Fields ---
    unmapped = [
        field for field in required_fields["Internal Field"].tolist()
        if field not in final_mapping or not final_mapping[field]["value"]
    ]

    if total_required == 0:
        st.info("No required fields defined in layout file.")
    elif unmapped:
        st.markdown(
            f"""
            <div style="border: 1px solid #9ca3af; background-color: #ffffff; padding: 16px; border-radius: 8px; margin-top: 10px;">
                <strong style="color: #374151;">⚠️ Unmapped Required Fields</strong><br>
                <span style="color: #1f2937;">{', '.join(unmapped)}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.success("All required fields mapped.")

    # --- Optional Fields Mapping ---
    st.markdown("### Optional Fields Mapping")

    optional_fields = get_optional_fields(layout_df)

    # --- Safety Check ---
    if not isinstance(optional_fields, pd.DataFrame):  # type: ignore[redundant-cast,type-py]
        st.error("Error: Optional fields extraction failed. Please check layout file format.")
        st.stop()

    if "Internal Field" not in optional_fields.columns or "Category" not in optional_fields.columns:
        st.error("Error: Layout file must contain 'Internal Field' and 'Category' columns.")
        st.stop()

    optional_fields = optional_fields[optional_fields["Internal Field"].notnull()]
    optional_fields = optional_fields[optional_fields["Category"].notnull()]
    optional_fields = optional_fields[~optional_fields["Internal Field"].isin(required_fields["Internal Field"].tolist())]  # type: ignore[no-untyped-call]

    if not optional_fields.empty:
        optional_field_groups = get_field_groups(optional_fields)

        for group in optional_field_groups:
            group_fields = optional_fields[optional_fields["Category"] == group]
            
            # Deduplicate fields within the group - keep first occurrence of each field
            group_fields = group_fields.drop_duplicates(subset=["Internal Field"], keep="first")  # type: ignore[no-untyped-call]

            group_field_names = group_fields["Internal Field"].tolist()
            mapped_count = sum(
                1 for f in group_field_names
                if f in final_mapping and final_mapping[f].get("value")
            )
            total_in_group = len(group_field_names)
            group_label = f"{group} ({mapped_count}/{total_in_group} mapped)"

            # Keep expander open if it has mapped fields to prevent collapse when selecting dropdown
            with st.expander(group_label, expanded=(mapped_count > 0)):
                for _, (_, row) in enumerate(group_fields.iterrows()):
                    field_name = row["Internal Field"]
                    raw_columns = claims_df.columns.tolist()
                    
                    # Clean and filter column names - remove empty, blank, or whitespace-only columns
                    # Also handle BOM and encoding issues
                    cleaned_columns = []
                    for col in raw_columns:
                        if col is None:
                            continue
                        # Convert to string and strip
                        col_str = str(col).strip()
                        # Remove BOM and other invisible characters
                        col_str = col_str.encode('utf-8').decode('utf-8-sig')  # Remove BOM
                        col_str = unicodedata.normalize('NFKC', col_str)  # Normalize unicode
                        col_str = col_str.strip()
                        # Skip empty or whitespace-only columns
                        if col_str:
                            cleaned_columns.append(col_str)
                    
                    # If no valid columns found, skip this field
                    if not cleaned_columns:
                        continue

                    suggestion_info = ai_suggestions.get(field_name, {})
                    suggested_column = suggestion_info.get("value")
                    suggestion_score = suggestion_info.get("score")
                    suggestion_source = suggestion_info.get("source", "algorithmic")  # Default to algorithmic
                    
                    # Convert score to percentage if it's between 0 and 1
                    if suggestion_score is not None and suggestion_score <= 1.0:
                        suggestion_score = suggestion_score * 100

                    # Get algorithmic scores
                    algorithmic_scores = suggestion_info.get("algorithmic_scores", {})
                    
                    # Sort columns by confidence score (returns tuples with scores)
                    opt_col_options_with_scores = _sort_columns_by_confidence(
                        field_name,
                        cleaned_columns,
                        suggested_column,
                        suggestion_score,
                        algorithmic_scores
                    )
                    
                    # Format dropdown options with confidence scores
                    opt_col_options = []
                    opt_col_name_map = {}  # Map display text to actual column name
                    for col_name, algo_score in opt_col_options_with_scores:
                        # Ensure col_name is not empty
                        if not col_name or not col_name.strip():
                            continue
                        
                        display_parts = []
                        if algo_score is not None:
                            display_parts.append(f"Algo: {algo_score*100:.0f}%")
                        
                        if len(display_parts) > 0:
                            display_text = f"{col_name} ({', '.join(display_parts)})"
                        else:
                            display_text = col_name
                        
                        opt_col_options.append(display_text)
                        opt_col_name_map[display_text] = col_name

                    default_value = final_mapping.get(field_name, {}).get("value", None)
                    default_label: Optional[str] = str(default_value) if default_value else None

                    # Create unique key using group, field name, and incrementing counter
                    # Counter ensures absolute uniqueness even with duplicate rows
                    widget_counter += 1
                    unique_key = f"opt_{group}_{field_name}_{widget_counter}"
                    # Sanitize key to remove special characters that might cause issues
                    unique_key = unique_key.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")

                    # --- Clean 2-column layout ---
                    col1, col2 = st.columns([2.5, 3.5])
                    
                    with col1:
                        # Field name
                        display_name = field_name
                        st.markdown(f"**{display_name}**", unsafe_allow_html=True)
                        
                        # Show algorithmic confidence score below field name
                        algorithmic_scores = suggestion_info.get("algorithmic_scores", {})
                        
                        if suggested_column:
                            algo_score = algorithmic_scores.get(suggested_column, None)
                            
                            if algo_score is not None:
                                scores_text = f"Algo: {algo_score:.0f}%"
                                st.caption(f"<span style='color: #6c757d; font-size: 0.85em;'>{scores_text}</span>", unsafe_allow_html=True)
                    
                    with col2:
                        field_selected_clean: Optional[str] = None
                        if field_name in ["plan_sponsor_name", "insurance_plan_name", "client_name"]:
                            widget_counter += 1
                            key_prefix = f"opt_{group}_{field_name}_{widget_counter}"
                            key_prefix = key_prefix.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")
                            # Allow manual input for plan_sponsor_name, insurance_plan_name, and client_name
                            allow_manual = field_name in ["plan_sponsor_name", "insurance_plan_name", "client_name"]
                            # Get default value for optional fields too
                            opt_default_value = final_mapping.get(field_name, {}).get("value", None)
                            opt_default_label = str(opt_default_value) if opt_default_value else None
                            selected = dual_input_field(field_name, opt_col_options, key_prefix=key_prefix, col_name_map=opt_col_name_map, default_value=opt_default_label, allow_manual_input=allow_manual)
                            field_selected_clean = selected.strip() if selected else None
                            # For dual_input_field, also read current value from session state for immediate preview
                            if not field_selected_clean and allow_manual:
                                # Check manual input first
                                manual_key = f"{key_prefix}_manual"
                                manual_value = st.session_state.get(manual_key, "")
                                if manual_value and manual_value.strip():
                                    field_selected_clean = manual_value.strip()
                            if not field_selected_clean:
                                dropdown_key = f"{key_prefix}_dropdown"
                                current_selection = st.session_state.get(dropdown_key, "")
                                if current_selection and current_selection != "":
                                    field_selected_clean = opt_col_name_map.get(current_selection, current_selection.split(" (")[0] if " (" in current_selection else current_selection) if opt_col_name_map else current_selection.strip()
                            # For dual_input_field, also read current value from session state for immediate preview
                            if not field_selected_clean:
                                dropdown_key = f"{key_prefix}_dropdown"
                                current_selection = st.session_state.get(dropdown_key, "")
                                if current_selection and current_selection != "":
                                    field_selected_clean = opt_col_name_map.get(current_selection, current_selection.split(" (")[0] if " (" in current_selection else current_selection) if opt_col_name_map else current_selection.strip()
                        else:
                            # Find index by matching column name (before confidence scores)
                            # Need to account for the empty string prepended to options
                            select_idx = 0  # Default to empty (unmapped)
                            if default_label:
                                # First try to find in the column name map (reverse lookup)
                                for display_text, actual_col in opt_col_name_map.items():
                                    if actual_col == default_label:
                                        # Found the mapped column, now find its index in options
                                        for idx, option in enumerate(opt_col_options):
                                            if option == display_text:
                                                select_idx = idx + 1  # +1 because options list has "" prepended
                                                break
                                        break
                                
                                # Fallback: try direct matching if not found in map
                                if select_idx == 0:
                                    for idx, option in enumerate(opt_col_options):
                                        # Check if option starts with the mapped column name
                                        if option.startswith(default_label + " (") or option == default_label:
                                            select_idx = idx + 1  # +1 because options list has "" prepended
                                            break
                            
                            selected = st.selectbox(
                                "Select column mapping",
                                options=[""] + opt_col_options,
                                index=select_idx,
                                key=unique_key,
                                label_visibility="collapsed"
                            )
                            
                            # Extract column name from selected option (remove confidence scores)
                            # Also read from session state for immediate preview (works even inside form)
                            current_selection = st.session_state.get(unique_key, selected)
                            if current_selection and current_selection != "":
                                field_selected_clean = opt_col_name_map.get(current_selection, current_selection.split(" (")[0] if " (" in current_selection else current_selection)
                            else:
                                field_selected_clean = None
                        
                        # Preview panel (only when mapped) - shows immediately based on current dropdown selection
                        # For manual inputs, show a simple indicator instead of data preview
                        if field_selected_clean:
                            if field_selected_clean in claims_df.columns:
                                try:
                                    col_data = claims_df[field_selected_clean]
                                    samples = col_data.dropna().head(3).tolist()
                                    fill_rate = (col_data.notna().sum() / len(col_data) * 100) if len(col_data) > 0 else 0.0
                                    
                                    # Format samples for display
                                    sample_display = []
                                    for sample in samples[:3]:
                                        sample_str = str(sample)
                                        if len(sample_str) > 30:
                                            sample_str = sample_str[:27] + "..."
                                        sample_display.append(f"• {sample_str}")
                                    
                                    if not sample_display:
                                        sample_display = ["• (no data)"]
                                    
                                    st.markdown(f"""
                                    <div style='background-color: #f8f9fa; padding: 0.5rem; border-radius: 4px; border-left: 3px solid #6b7280; font-size: 0.85rem;'>
                                        <div style='color: #6c757d; margin-bottom: 0.2rem;'>{'<br>'.join(sample_display)}</div>
                                        <div style='color: #6c757d; font-size: 0.8rem;'>
                                            <span>Fill Rate: <strong>{fill_rate:.1f}%</strong></span>
                                        </div>
                                </div>
                            """, unsafe_allow_html=True)
                                except Exception:
                                    pass
                        elif field_name in ["plan_sponsor_name", "insurance_plan_name", "client_name"]:
                                # For manual inputs, show a simple indicator
                                st.markdown(f"""
                                    <div style='background-color: #e8f5e9; padding: 0.5rem; border-radius: 4px; border-left: 3px solid #4caf50; font-size: 0.85rem;'>
                                        <div style='color: #2e7d32;'>
                                            <span>✓ Manual value: <strong>{field_selected_clean[:50]}{'...' if len(field_selected_clean) > 50 else ''}</strong></span>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # Value Mapping UI for Patient_Relationship (optional fields)
                        if field_name == "patient_relationship_code" and field_selected_clean:
                            value_mapping_key = f"{unique_key}_value_mapping"
                            existing_value_mapping = final_mapping.get(field_name, {}).get("value_mapping", "")
                            
                            st.markdown("**Value Mapping (for patient_relationship_code):**")
                            st.caption("Enter value mappings in format: source_value,target_value (one per line). Example:\nM,Male\nF,Female\n18,Child")
                            value_mapping_input = st.text_area(
                                "Value Mapping",
                                value=existing_value_mapping,
                                key=value_mapping_key,
                                height=100,
                                help="Map source values to target values. Format: source_value,target_value (one per line). This will be used in SVMRule for patient_relationship_code mapping."
                            )
                            
                            # Save value mapping immediately when changed
                            if value_mapping_input and value_mapping_input.strip():
                                if field_name not in final_mapping:
                                    final_mapping[field_name] = {}
                                final_mapping[field_name]["value_mapping"] = value_mapping_input.strip()
                                st.session_state["final_mapping"] = final_mapping.copy()
                        
                        # Value Mapping UI for Patient_Relationship_Desc (optional fields)
                        if field_name == "patient_relationship_desc" and field_selected_clean:
                            value_mapping_key = f"{unique_key}_value_mapping"
                            existing_value_mapping = final_mapping.get(field_name, {}).get("value_mapping", "")
                            
                            st.markdown("**Value Mapping (for patient_relationship_desc):**")
                            st.caption("Enter value mappings in format: source_value,target_value (one per line). Example:\nM,Male\nF,Female\n18,Child")
                            value_mapping_input = st.text_area(
                                "Value Mapping",
                                value=existing_value_mapping,
                                key=value_mapping_key,
                                height=100,
                                help="Map source values to target values. Format: source_value,target_value (one per line). This will be used in SVMRule for patient_relationship_desc mapping."
                            )
                            
                            # Save value mapping immediately when changed
                            if value_mapping_input and value_mapping_input.strip():
                                if field_name not in final_mapping:
                                    final_mapping[field_name] = {}
                                final_mapping[field_name]["value_mapping"] = value_mapping_input.strip()
                                st.session_state["final_mapping"] = final_mapping.copy()

                    if field_selected_clean:
                        # Record correction if user overrode AI suggestion
                        if suggested_column and field_selected_clean != suggested_column:
                            try:
                                from mapping.mapping_enhancements import record_mapping_correction
                                record_mapping_correction(
                                    field_name,
                                    suggested_column,
                                    field_selected_clean
                                )
                            except Exception:
                                pass  # Fail silently if learning not available
                        
                        # Check if this field needs value mapping (e.g., Patient_Relationship)
                        value_mapping = None
                        if field_name == "patient_relationship_code" or field_name == "patient_relationship_desc":
                            # Get value mapping from session state
                            value_mapping_key = f"{unique_key}_value_mapping"
                            value_mapping = st.session_state.get(value_mapping_key, "")
                            if value_mapping and value_mapping.strip():
                                value_mapping = value_mapping.strip()
                            else:
                                # Also check if it's already in final_mapping
                                value_mapping = final_mapping.get(field_name, {}).get("value_mapping", None)
                        
                        final_mapping[field_name] = {
                            "mode": "manual" if field_selected_clean != suggested_column else "auto",
                            "value": field_selected_clean
                        }
                        if value_mapping:
                            final_mapping[field_name]["value_mapping"] = value_mapping
                        # Update session state immediately for automatic saving
                        st.session_state["final_mapping"] = final_mapping.copy()

    # --- After ALL mappings, refresh transformed_df and generate outputs automatically ---
    claims_df = st.session_state.get("claims_df")
    
    # Ensure final_mapping is saved to session state
    st.session_state["final_mapping"] = final_mapping.copy()

    if claims_df is not None and final_mapping:
        try:
            st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping, layout_df)
        except Exception:
            pass  # Don't fail if transformation fails

    # Generate outputs automatically when mappings exist
    if final_mapping and any(info.get("value") for info in final_mapping.values()):
        # Import here to avoid circular dependency
        from data.output_generator import generate_all_outputs
        try:
            generate_all_outputs()
        except Exception:
            pass  # Don't fail if output generation fails

