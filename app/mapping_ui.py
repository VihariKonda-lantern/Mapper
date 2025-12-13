# --- mapping_ui.py ---
"""Field mapping UI functions."""
import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
from typing import Any, List, Dict, Set, Optional, Tuple
import time

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]

from layout_loader import get_field_groups, get_required_fields, get_optional_fields
from mapping_engine import get_enhanced_automap
from transformer import transform_claims_data
from session_state import initialize_undo_redo
from anonymizer import anonymize_claims_data
from improvements_utils import DEBOUNCE_DELAY_SECONDS
from ui_improvements import render_tooltip  # type: ignore[import-untyped]


def dual_input_field(field_label: str, options: List[str], key_prefix: str) -> Optional[str]:
    """
    Renders a dropdown + manual text input side-by-side.
    Returns whichever the user picked or typed.
    """
    col1, col2 = st.columns([2, 3])

    with col1:
        dropdown_selection = st.selectbox(
            f"Select {field_label}", 
            options=[""] + options,
            key=f"{key_prefix}_dropdown"
        )

    with col2:
        manual_entry = st.text_input(
            f"Or manually enter {field_label}", 
            key=f"{key_prefix}_manual"
        )

    if manual_entry.strip():
        return manual_entry.strip()
    else:
        return dropdown_selection.strip() if dropdown_selection else None


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
        st.markdown("#### 🔍 Real-time Mapping Preview")
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
        st.info("💡 **Tip:** Start mapping fields to see a real-time preview of your mapped data here.")

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
    if "final_mapping" not in st.session_state:
        st.session_state.final_mapping = {}

    auto_mapped: List[str] = []
    for field, info in ai_suggestions.items():
        score = info.get("score", 0)
        if score >= 80 and field not in final_mapping:
            final_mapping[field] = {
                "mode": "auto",
                "value": info["value"]
            }
            auto_mapped.append(field)

    st.session_state.auto_mapped_fields = auto_mapped

    # --- Mapping Progress ---
    _mapped_required, total_required, _percent_complete = calculate_mapping_progress(layout_df, final_mapping)
    
    # --- Required Fields Heading ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Mandatory Fields Mapping")
    
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

        with st.expander(group_label, expanded=False):
            for _, (_, row) in enumerate(group_fields.iterrows()):
                field_name = row["Internal Field"]
                raw_columns = claims_df.columns.tolist()

                # --- AI suggestion if available ---
                suggestion_info = ai_suggestions.get(field_name, {})
                suggested_column = suggestion_info.get("value")
                suggestion_score = suggestion_info.get("score")

                field_col_options: List[str] = []
                for col in raw_columns:
                    if col == suggested_column:
                        label = f"{col} (AI Suggested)"
                        if suggestion_score:
                            label = f"{col} (AI: {suggestion_score}%)"
                            # Add tooltip for AI suggestions
                            render_tooltip(
                                label,
                                f"AI confidence: {suggestion_score}%. This column was automatically matched based on name similarity, data patterns, and field types.",
                                key=f"ai_tooltip_{field_name}_{col}"
                            )
                        field_col_options.append(str(label))
                    else:
                        field_col_options.append(str(col))

                default_value = final_mapping.get(field_name, {}).get("value", None)
                req_default_label: Optional[str] = None
                if default_value:
                    if default_value == suggested_column and suggestion_score:
                        req_default_label = f"{default_value} (AI: {suggestion_score}%)"
                    else:
                        req_default_label = str(default_value)

                # Create unique key using group, field name, and incrementing counter
                # Counter ensures absolute uniqueness even with duplicate rows
                widget_counter += 1
                unique_key = f"req_{group}_{field_name}_{widget_counter}"
                # Sanitize key to remove special characters that might cause issues
                unique_key = unique_key.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")

                # --- New Visual Layout: 3-column row ---
                col1, col2, col3 = st.columns([2, 3, 3])
                
                with col1:
                    # Internal field name with AI suggestion indicator and search highlighting
                    has_suggestion = field_name in ai_suggestions
                    display_name = field_name
                    
                    # Highlight search query in field name
                    if search_query and search_query.strip():
                        import re
                        pattern = re.compile(re.escape(search_query), re.IGNORECASE)
                        display_name = pattern.sub(lambda m: f"<mark style='background-color: #ffeb3b; padding: 2px 4px;'>{m.group()}</mark>", field_name)
                    
                    if has_suggestion:
                        st.markdown(f"**{display_name}** <span style='color: #ff9800; font-size: 0.85em;'>(AI: {suggestion_score}%)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{display_name}**", unsafe_allow_html=True)
                    
                    # Real-time validation status indicator
                    if field_name in final_mapping and final_mapping[field_name].get("value"):
                        mapped_col = final_mapping[field_name].get("value")
                        if mapped_col and mapped_col in claims_df.columns:
                            # Quick validation check
                            col_data = claims_df[mapped_col]
                            null_pct = (col_data.isna().sum() / len(col_data) * 100) if len(col_data) > 0 else 0
                            if null_pct > 50:
                                st.markdown("<span style='color: #f44336; font-size: 0.75em;'>⚠️ High null rate</span>", unsafe_allow_html=True)
                            elif null_pct > 20:
                                st.markdown("<span style='color: #ff9800; font-size: 0.75em;'>⚠️ Moderate null rate</span>", unsafe_allow_html=True)
                            else:
                                st.markdown("<span style='color: #4caf50; font-size: 0.75em;'>✓ Good</span>", unsafe_allow_html=True)
                
                with col2:
                    selected_clean: Optional[str] = None
                    if field_name in ["Plan_Sponsor_Name", "Insurance_Plan_Name", "Client_Name"]:
                        widget_counter += 1
                        key_prefix = f"req_{group}_{field_name}_{widget_counter}"
                        key_prefix = key_prefix.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")
                        selected = dual_input_field(field_name, field_col_options, key_prefix=key_prefix)
                        manual_key = f"{key_prefix}_manual"
                        manual_value = st.session_state.get(manual_key)

                        if manual_value:
                            selected_clean = manual_value.strip()
                        else:
                            selected_clean = selected.replace(f" (AI: {suggestion_score}%)", "").replace(" (AI Suggested)", "") if selected else None
                    else:
                        select_idx = field_col_options.index(req_default_label) + 1 if (req_default_label is not None and req_default_label in field_col_options) else 0
                        selected = st.selectbox(
                            "Select column:",
                            options=[""] + field_col_options,
                            index=select_idx,
                            key=unique_key,
                            help=f"Map {field_name} to a claims file column",
                            label_visibility="collapsed"
                        )
                        selected_clean = selected.replace(f" (AI: {suggestion_score}%)", "").replace(" (AI Suggested)", "") if selected else None
                    
                    # --- Mapped Chip ---
                    if selected_clean:
                        st.markdown(f"""
                            <div style='margin-top: 0.25rem;'>
                                <span style='background-color: #e7f3ff; color: #0066cc; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.75rem; font-weight: 500;'>
                                    Mapped to: <strong>{selected_clean}</strong>
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                
                with col3:
                    # --- Sample & Stats Panel ---
                    if selected_clean and selected_clean in claims_df.columns:
                        try:
                            col_data = claims_df[selected_clean]
                            # Get 3 sample values
                            samples = col_data.dropna().head(3).tolist()
                            # Get dtype
                            dtype = str(col_data.dtype)
                            # Calculate fill rate
                            total_count = len(col_data)
                            non_null_count = col_data.notna().sum()
                            fill_rate = (non_null_count / total_count * 100) if total_count > 0 else 0.0
                            
                            # Format samples for display
                            sample_display = []
                            for i, sample in enumerate(samples[:3]):
                                sample_str = str(sample)
                                if len(sample_str) > 30:
                                    sample_str = sample_str[:27] + "..."
                                sample_display.append(f"• {sample_str}")
                            
                            if not sample_display:
                                sample_display = ["• (no data)"]
                            
                            st.markdown(f"""
                                <div style='background-color: #f8f9fa; padding: 0.5rem; border-radius: 4px; border-left: 3px solid #667eea; font-size: 0.85rem;'>
                                    <div style='font-weight: 600; margin-bottom: 0.25rem; color: #000000;'>Sample & Stats</div>
                                    <div style='color: #000000; margin-bottom: 0.2rem;'>{'<br>'.join(sample_display)}</div>
                                    <div style='color: #000000; font-size: 0.8rem;'>
                                        <span>Type: <code>{dtype}</code></span><br>
                                        <span>Fill Rate: <strong>{fill_rate:.1f}%</strong></span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        except Exception:
                            st.markdown("<div style='color: #000000; font-size: 0.85rem;'>No data available</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='color: #000000; font-size: 0.85rem; font-style: italic;'>Select a column to preview</div>", unsafe_allow_html=True)

                if selected_clean:
                    final_mapping[field_name] = {
                            "mode": "manual" if selected_clean != suggested_column else "auto",
                            "value": selected_clean
                        }
                    # Don't save to history here - wait for form submission

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
            <div style="border: 1px solid #ffa94d; background-color: #ffffff; padding: 16px; border-radius: 8px; margin-top: 10px;">
                <strong style="color: #d9480f;">⚠️ Unmapped Required Fields</strong><br>
                <span style="color: #212529;">{', '.join(unmapped)}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.success("All required fields mapped.")

    # --- Optional Fields Mapping ---
    st.markdown("<br>", unsafe_allow_html=True)
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

    # --- Optional Fields Mapping ---
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

            with st.expander(group_label, expanded=False):
                for _, (_, row) in enumerate(group_fields.iterrows()):
                    field_name = row["Internal Field"]
                    raw_columns = claims_df.columns.tolist()

                    suggestion_info = ai_suggestions.get(field_name, {})
                    suggested_column = suggestion_info.get("value")
                    suggestion_score = suggestion_info.get("score")

                    opt_col_options: List[str] = []
                    for col in raw_columns:
                        if col == suggested_column:
                            label = f"{col} (AI Suggested)"
                            if suggestion_score:
                                label = f"{col} (AI: {suggestion_score}%)"
                            opt_col_options.append(str(label))
                        else:
                            opt_col_options.append(str(col))

                    default_value = final_mapping.get(field_name, {}).get("value", None)
                    default_label: Optional[str] = None
                    if default_value:
                        if default_value == suggested_column and suggestion_score:
                            default_label = f"{default_value} (AI: {suggestion_score}%)"
                        else:
                            default_label = str(default_value)

                    # Create unique key using group, field name, and incrementing counter
                    # Counter ensures absolute uniqueness even with duplicate rows
                    widget_counter += 1
                    unique_key = f"opt_{group}_{field_name}_{widget_counter}"
                    # Sanitize key to remove special characters that might cause issues
                    unique_key = unique_key.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")

                    # --- New Visual Layout: 3-column row ---
                    col1, col2, col3 = st.columns([2, 3, 3])
                    
                    with col1:
                        # Internal field name with AI suggestion indicator
                        has_suggestion = field_name in ai_suggestions
                        if has_suggestion:
                            st.markdown(f"**{field_name}** <span style='color: #ff9800; font-size: 0.85em;'>(AI: {suggestion_score}%)</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**{field_name}**")
                    
                    with col2:
                        field_selected_clean: Optional[str] = None
                        if field_name in ["Plan_Sponsor_Name", "Insurance_Plan_Name", "Client_Name"]:
                            widget_counter += 1
                            key_prefix = f"opt_{group}_{field_name}_{widget_counter}"
                            key_prefix = key_prefix.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_")
                            selected = dual_input_field(field_name, opt_col_options, key_prefix=key_prefix)
                            manual_key = f"{key_prefix}_manual"
                            manual_value = st.session_state.get(manual_key)

                            if manual_value:
                                field_selected_clean = manual_value.strip()
                            else:
                                field_selected_clean = selected.replace(f" (AI: {suggestion_score}%)", "").replace(" (AI Suggested)", "") if selected else None
                        else:
                            select_idx = opt_col_options.index(default_label) + 1 if (default_label is not None and default_label in opt_col_options) else 0
                            selected = st.selectbox(
                                f"{field_name}",
                                options=[""] + opt_col_options,
                                index=select_idx,
                                key=unique_key,
                                label_visibility="collapsed"
                            )
                            field_selected_clean = selected.replace(f" (AI: {suggestion_score}%)", "").replace(" (AI Suggested)", "") if selected else None
                        
                        # --- Mapped Chip ---
                        if field_selected_clean:
                            st.markdown(f"""
                                <div style='margin-top: 0.25rem;'>
                                    <span style='background-color: #e7f3ff; color: #0066cc; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.75rem; font-weight: 500;'>
                                        Mapped to: <strong>{field_selected_clean}</strong>
                                    </span>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with col3:
                        # --- Sample & Stats Panel ---
                        if field_selected_clean and field_selected_clean in claims_df.columns:
                            try:
                                col_data = claims_df[field_selected_clean]
                                # Get 3 sample values
                                samples = col_data.dropna().head(3).tolist()
                                # Get dtype
                                dtype = str(col_data.dtype)
                                # Calculate fill rate
                                total_count = len(col_data)
                                non_null_count = col_data.notna().sum()
                                fill_rate = (non_null_count / total_count * 100) if total_count > 0 else 0.0
                                
                                # Format samples for display
                                sample_display = []
                                for i, sample in enumerate(samples[:3]):
                                    sample_str = str(sample)
                                    if len(sample_str) > 30:
                                        sample_str = sample_str[:27] + "..."
                                    sample_display.append(f"• {sample_str}")
                                
                                if not sample_display:
                                    sample_display = ["• (no data)"]
                                
                                st.markdown(f"""
                                    <div style='background-color: #f8f9fa; padding: 0.5rem; border-radius: 4px; border-left: 3px solid #667eea; font-size: 0.85rem;'>
                                        <div style='font-weight: 600; margin-bottom: 0.25rem; color: #495057;'>Sample & Stats</div>
                                        <div style='color: #6c757d; margin-bottom: 0.2rem;'>{'<br>'.join(sample_display)}</div>
                                        <div style='color: #6c757d; font-size: 0.8rem;'>
                                            <span>Type: <code>{dtype}</code></span><br>
                                            <span>Fill Rate: <strong>{fill_rate:.1f}%</strong></span>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            except Exception:
                                st.markdown("<div style='color: #000000; font-size: 0.85rem;'>No data available</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='color: #000000; font-size: 0.85rem; font-style: italic;'>Select a column to preview</div>", unsafe_allow_html=True)

                    if field_selected_clean:
                        final_mapping[field_name] = {
                            "mode": "manual" if field_selected_clean != suggested_column else "auto",
                            "value": field_selected_clean
                        }

    # --- After ALL mappings, refresh transformed_df ---
    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})

    if claims_df is not None and final_mapping:
        st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping)
        st.session_state.final_mapping = final_mapping

    if st.session_state.get("final_mapping"):
        # Import here to avoid circular dependency
        from output_generator import generate_all_outputs
        generate_all_outputs()

