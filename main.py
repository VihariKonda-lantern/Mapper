# --- main.py ---
"""
pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownAttributeType=false
"""
import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
from typing import Any

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]
import zipfile
import io
from typing import Tuple, Optional, List, Dict, Any, Set
# Removed unused matplotlib import

# --- App Modules ---
from upload_handlers import capture_claims_file_metadata
from file_handler import (
    read_claims_with_header_option,
    detect_delimiter,
)
from layout_loader import (
    load_internal_layout,
    get_field_groups,
    get_required_fields,
    get_optional_fields,
    render_layout_summary_section
)
from diagnosis_loader import load_msk_bar_lookups
from mapping_engine import get_enhanced_automap
from utils import render_claims_file_summary
from transformer import transform_claims_data
from validation_engine import (
    run_validations,
)
from anonymizer import anonymize_claims_data

# --- Streamlit Setup ---
st.set_page_config(page_title="Claims Mapper and Validator", layout="wide")

# --- Helpers ---
def _notify(msg: str) -> None:
    st.toast(msg)

# --- Utility Functions ---
def custom_file_uploader(label_text: str, key: str, types: List[str]) -> Optional[Any]:
    """Custom wrapper for st.file_uploader with a clean label and minimal visual noise."""
    st.markdown(f"<div style='margin-bottom: 4px; font-weight: 500;'>{label_text}</div>", unsafe_allow_html=True)
    return st.file_uploader(label="", type=types, key=key, label_visibility="collapsed")

def render_file_upload_button(label: str, key: str, types: List[str]) -> Optional[Any]:
    """Custom button-driven file uploader."""
    container = st.empty()

    if f"{key}_clicked" not in st.session_state:
        st.session_state[f"{key}_clicked"] = False

    if not st.session_state[f"{key}_clicked"]:
        if container.button(f"📁 {label}", key=f"btn_{key}"):
            st.session_state[f"{key}_clicked"] = True

    if st.session_state[f"{key}_clicked"]:
        st.caption(f"[debug] File types accepted: {types}")
        return container.file_uploader("", type=types, key=key, label_visibility="collapsed")
    
    return None

def render_title():
    """Renders the app title."""
    st.markdown("<div style='font-size: 22px; font-weight: 600; margin-bottom: 10px;'>Claims File Mapper and Validator</div>", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_layout_cached(file: Any) -> Any:
    return load_internal_layout(file)

@st.cache_data(show_spinner=False)
def load_lookups_cached(file: Any):
    return load_msk_bar_lookups(file)

def render_lookup_summary_section():
    """Loads and previews the MSK and BAR diagnosis lookup file."""
    if "msk_codes" in st.session_state and "bar_codes" in st.session_state:
        msk_codes = st.session_state.msk_codes
        bar_codes = st.session_state.bar_codes

        st.markdown("#### Diagnosis Lookup Summary")
        st.write(f"**MSK Codes Loaded:** {len(msk_codes)}")  # type: ignore[no-untyped-call]
        st.write(f"**BAR Codes Loaded:** {len(bar_codes)}")  # type: ignore[no-untyped-call]

        with st.expander("View Sample MSK Codes"):
            st.write(list(msk_codes)[:10])  # type: ignore[no-untyped-call]
        with st.expander("View Sample BAR Codes"):
            st.write(list(bar_codes)[:10])  # type: ignore[no-untyped-call]
    else:
        st.info("Upload a valid diagnosis lookup file to preview MSK/BAR codes.")

@st.cache_data(show_spinner=False)
def generate_mapping_table(layout_df: Any, final_mapping: Dict[str, Dict[str, Any]], claims_df: Any) -> Any:
    """
    Generates a full mapping table listing:
    - All internal fields from layout (mapped or unmapped)
    - Their corresponding claims file column (if mapped)
    - Data type of mapped column (from claims_df)
    - Required/Optional
    - Also lists unmapped claims file columns after

    Args:
        layout_df (pd.DataFrame): Internal layout DataFrame
        final_mapping (dict): Final field mappings
        claims_df (pd.DataFrame): Uploaded claims DataFrame

    Returns:
        Any: Full mapping table
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

def render_upload_and_claims_preview():
    """
    Upload Section for Layout, Lookup, Claims, and Headerless detection.
    Allows proper external header upload if needed.
    """
    st.markdown("### Step 1: Upload Files and Confirm Claims File Headers")

    # --- Top Row (Layout + Lookup) ---
    top1, top2 = st.columns(2)
    with top1:
        layout_file = st.file_uploader("Upload Layout File (.xlsx)", type=["xlsx"], key="layout_file")
        if layout_file:
            layout_df = load_layout_cached(layout_file)
            st.session_state.layout_df = layout_df
            st.session_state.layout_file_obj = layout_file

    with top2:
        lookup_file = st.file_uploader("Upload Diagnosis Lookup (.xlsx)", type=["xlsx"], key="lookup_file")
        if lookup_file:
            msk_codes, bar_codes = load_lookups_cached(lookup_file)
            st.session_state.msk_codes = msk_codes
            st.session_state.bar_codes = bar_codes
            st.session_state.lookup_file_obj = lookup_file

    # --- Bottom Row (Header + Claims File) ---
    bottom1, bottom2 = st.columns(2)
    with bottom1:
        header_file = st.file_uploader("Upload Header File (optional)", type=["csv", "txt", "xlsx", "xls"], key="external_header_upload")
        st.session_state.header_file_obj = header_file if header_file else None

    with bottom2:
        claims_file = st.file_uploader("Upload Claims File (.csv, .txt, .tsv, .xlsx)", 
                                       type=["csv", "txt", "tsv", "xlsx", "xls"], key="claims_file")
        if claims_file:
            # Reset session if file changed
            if "claims_file_obj" in st.session_state and st.session_state.claims_file_obj.name != claims_file.name:
                st.session_state.pop("claims_df", None)
                st.session_state.pop("final_mapping", None)
                st.session_state.pop("auto_mapping", None)
                st.session_state.pop("auto_mapped_fields", None)
            st.session_state.claims_file_obj = claims_file

    # --- Proceed Button ---
    if st.button("➡️ Proceed with File Loading"):
        # --- Guard Clause ---
        if not ("layout_file_obj" in st.session_state and "lookup_file_obj" in st.session_state and "claims_file_obj" in st.session_state):
            st.warning("⬆️ Please upload Layout, Lookup, and Claims files to continue.")
            st.stop()

        claims_file = st.session_state.claims_file_obj
        header_file = st.session_state.get("header_file_obj")
        ext = claims_file.name.lower()
        delimiter = detect_delimiter(claims_file) if ext.endswith((".csv", ".txt", ".tsv")) else None

        try:
            # --- Preview first 3 rows
            with st.spinner("Preparing preview..."):
                claims_file.seek(0)
                preview_df = (
                    pd.read_csv(claims_file, nrows=3, header=None, delimiter=delimiter, on_bad_lines="skip")  # type: ignore[no-untyped-call]
                    if ext.endswith((".csv", ".txt", ".tsv")) else
                    pd.read_excel(claims_file, nrows=3, header=None)  # type: ignore[no-untyped-call]
                )

                st.markdown("**Preview of Claims File (First 3 Rows):**")
                st.dataframe(preview_df, use_container_width=True)  # type: ignore[no-untyped-call]

            # --- Read full claims file
            with st.spinner("Loading claims file..."):
                claims_file.seek(0)
                claims_df = read_claims_with_header_option(
                    claims_file,
                    headerless=(header_file is not None),
                    header_file=header_file,
                    delimiter=delimiter
                )

                # Fallback for junk columns
                if claims_df.columns.isnull().any():
                    claims_df.columns = [f"col_{i}" if not col or pd.isna(col) else str(col) for i, col in enumerate(claims_df.columns)]

                # Save to session
                st.session_state.claims_df = claims_df
                capture_claims_file_metadata(claims_file, has_header=(header_file is None))

                st.success("✅ Claims file loaded successfully using " +
                           ("embedded headers." if header_file is None else "external header file."))

        except Exception as e:
            st.error(f"Error processing claims file: {e}")

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

    # --- Claims File Preview ---
    st.markdown("#### Claims File Preview (First 5 Rows)")
    st.dataframe(claims_df.head(), use_container_width=True)  # type: ignore[no-untyped-call]

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
            
    # --- Required Fields Mapping ---
    for group in field_groups:
        group_fields = required_fields[required_fields["Category"] == group]

        group_field_names = group_fields["Internal Field"].tolist()
        mapped_count = sum(
            1 for f in group_field_names
            if f in final_mapping and final_mapping[f].get("value")
        )
        total_in_group = len(group_field_names)
        group_label = f"{group} ({mapped_count}/{total_in_group} mapped)"

        with st.expander(group_label, expanded=False):
            for _, row in group_fields.iterrows():
                field_name = row["Internal Field"]
                raw_columns = claims_df.columns.tolist()

                # --- AI suggestion if available ---
                suggestion_info = ai_suggestions.get(field_name, {})
                suggested_column = suggestion_info.get("value")
                suggestion_score = suggestion_info.get("score")

                col_options: List[str] = []
                for col in raw_columns:
                    if col == suggested_column:
                        label = f"{col} (AI Suggested)"
                        if suggestion_score:
                            label = f"{col} (AI: {suggestion_score}%)"
                        col_options.append(str(label))
                    else:
                        col_options.append(str(col))

                default_value = final_mapping.get(field_name, {}).get("value", None)
                default_label: Optional[str] = None
                if default_value:
                    if default_value == suggested_column and suggestion_score:
                        default_label = f"{default_value} (AI: {suggestion_score}%)"
                    else:
                        default_label = str(default_value)

                selected_clean: Optional[str] = None
                if field_name in ["Plan_Sponsor_Name", "Insurance_Plan_Name", "Client_Name"]:
                    selected = dual_input_field(field_name, col_options, key_prefix=f"optional_dropdown_{field_name}_optional")
                    manual_key = f"{field_name}_manual"
                    manual_value = st.session_state.get(manual_key)

                    if manual_value:
                        selected_clean = manual_value.strip()
                    else:
                        selected_clean = selected.replace(f" (AI: {suggestion_score}%)", "").replace(" (AI Suggested)", "") if selected else None
                else:
                    idx = col_options.index(default_label) + 1 if (default_label is not None and default_label in col_options) else 0
                    selected = st.selectbox(
                        f"{field_name}",
                        options=[""] + col_options,
                        index=idx,
                        key=f"required_dropdown_{field_name}_required"
                    )
                    selected_clean = selected.replace(f" (AI: {suggestion_score}%)", "").replace(" (AI Suggested)", "") if selected else None

                if selected_clean:
                        final_mapping[field_name] = {
                            "mode": "manual" if selected_clean != suggested_column else "auto",
                            "value": selected_clean
                        }

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

            group_field_names = group_fields["Internal Field"].tolist()
            mapped_count = sum(
                1 for f in group_field_names
                if f in final_mapping and final_mapping[f].get("value")
            )
            total_in_group = len(group_field_names)
            group_label = f"{group} ({mapped_count}/{total_in_group} mapped)"

            with st.expander(group_label, expanded=False):
                for _, row in group_fields.iterrows():
                    field_name = row["Internal Field"]
                    raw_columns = claims_df.columns.tolist()

                    suggestion_info = ai_suggestions.get(field_name, {})
                    suggested_column = suggestion_info.get("value")
                    suggestion_score = suggestion_info.get("score")

                    col_options: List[str] = []
                    for col in raw_columns:
                        if col == suggested_column:
                            label = f"{col} (AI Suggested)"
                            if suggestion_score:
                                label = f"{col} (AI: {suggestion_score}%)"
                            col_options.append(str(label))
                        else:
                            col_options.append(str(col))

                    default_value = final_mapping.get(field_name, {}).get("value", None)
                    default_label = None
                    if default_value:
                        if default_value == suggested_column and suggestion_score:
                            default_label = f"{default_value} (AI: {suggestion_score}%)"
                        else:
                            default_label = default_value

                    selected_clean: Optional[str] = None
                    if field_name in ["Plan_Sponsor_Name", "Insurance_Plan_Name", "Client_Name"]:
                        selected = dual_input_field(field_name, col_options, key_prefix=f"optional_dropdown_{field_name}_optional")
                    else:
                        selected = st.selectbox(
                            f"{field_name}",
                            options=[""] + col_options,
                            index=col_options.index(default_label) + 1 if default_label in col_options else 0,
                            key=f"optional_dropdown_{field_name}_optional"
                        )
                        selected_clean = selected.replace(f" (AI: {suggestion_score}%)", "").replace(" (AI Suggested)", "") if selected else None

                    if selected_clean:
                        final_mapping[field_name] = {
                            "mode": "manual" if selected_clean != suggested_column else "auto",
                            "value": selected_clean
                        }

    # --- After ALL mappings, refresh transformed_df ---
    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})

    if claims_df is not None and final_mapping:
        st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping)
        st.session_state.final_mapping = final_mapping

    if st.session_state.get("final_mapping"):
        generate_all_outputs()

def calculate_mapping_progress(layout_df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> Tuple[int, int, int]:
    """Calculates progress stats for required fields mapping."""
    required_fields = get_required_fields(layout_df)["Internal Field"].tolist()
    mapped_fields = [field for field in required_fields if field in final_mapping and final_mapping[field]["value"]]
    total_required = len(required_fields)
    mapped_required = len(mapped_fields)
    percent_complete = int((mapped_required / total_required) * 100) if total_required > 0 else 0

    return mapped_required, total_required, percent_complete

def generate_all_outputs():
    """
    Generates YAML, anonymized claims file, and mapping table outputs
    based on the latest field mappings.
    """
    final_mapping = st.session_state.get("final_mapping")
    claims_df = st.session_state.get("claims_df")
    layout_df = st.session_state.get("layout_df")

    if final_mapping and claims_df is not None and layout_df is not None:
        # --- Extract basic filename (placeholders removed) ---

        # --- Generate outputs ---
        anonymized_df = anonymize_claims_data(claims_df, final_mapping)
        mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)  # <-- Fixed this line

        # --- Save in session_state
        st.session_state.anonymized_df = anonymized_df
        st.session_state.mapping_table = mapping_table
    else:
        st.session_state.anonymized_df = None
        st.session_state.mapping_table = None

def render_claims_file_deep_dive():
    """
    Displays the deep dive summary of the claims file after mapping:
    showing all internal fields, mapped columns, data types, fill rates, required flag, and pass/fail status.
    """
    st.markdown("#### Claims File Deep Dive (Mapped Columns Analysis)")

    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})
    layout_df = st.session_state.get("layout_df")
    transformed_df = st.session_state.get("transformed_df")

    if claims_df is None or final_mapping is None or layout_df is None or transformed_df is None:
        st.info("Upload claims file, complete mappings, and preview transformed data first.")
        return

    deep_dive_rows: List[Dict[str, Any]] = []

    internal_fields = layout_df["Internal Field"].tolist()

    for internal_field in internal_fields:
        source_column = final_mapping.get(internal_field, {}).get("value", None)

        if source_column and source_column in transformed_df.columns:
            col_dtype = str(transformed_df[source_column].dtype)
            fill_rate = 100 * transformed_df[source_column].notnull().sum() / len(transformed_df)

            if fill_rate == 0:
                status_icon = "❌ Fail"
            elif fill_rate < 95:
                status_icon = "⚠️ Warning"
            else:
                status_icon = "✅ Pass"
        else:
            col_dtype = "N/A"
            fill_rate = 0.0
            status_icon = "❌ Fail"

        # Check if field is required
        usage = layout_df[layout_df["Internal Field"] == internal_field]["Usage"].values
        is_required = usage[0].lower() == "required" if len(usage) > 0 else False

        deep_dive_rows.append({
            "Internal Field": internal_field,
            "Mapped Claims Column": source_column if source_column else "Not Mapped",
            "Data Type": col_dtype,
            "Fill Rate %": f"{fill_rate:.1f}",
            "Required": "Yes" if is_required else "No",
            "Status": status_icon
        })

    deep_dive_df = pd.DataFrame(deep_dive_rows)

    st.dataframe(deep_dive_df, use_container_width=True)  # type: ignore[no-untyped-call]

    deep_dive_csv = deep_dive_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Deep Dive CSV",
        data=deep_dive_csv,
        file_name="deep_dive_report.csv",
        mime="text/csv",
        key="download_deep_dive_csv"
    )

# --- App Layout ---
render_title()
tab1, tab2, tab3, tab4 = st.tabs(["Setup", "Field Mapping", "Preview & Validate", "Downloads Tab"])

with tab1:
    render_upload_and_claims_preview()
    render_layout_summary_section()
    render_lookup_summary_section()
    render_claims_file_summary()

with tab2:
    layout_df = st.session_state.get("layout_df")
    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})

    if layout_df is None or claims_df is None:
        st.info("Upload both layout and claims files to begin mapping.")
        st.stop()

    # --- Sticky Mapping Progress Bar ---
    # Guard layout_df and string operations
    required_fields = layout_df[layout_df["Usage"].astype(str).str.lower() == "required"]["Internal Field"].tolist()  # type: ignore[no-untyped-call]
    mapped_required = [f for f in required_fields if f in final_mapping and final_mapping[f].get("value")]
    percent_complete = int((len(mapped_required) / len(required_fields)) * 100) if required_fields else 0

    st.markdown(
        f"""
        <div style="position: sticky; top: 0; background-color: #f8f9fa; z-index: 999; padding: 10px 16px; border-bottom: 1px solid #ddd;">
            <b>📌 Required Field Mapping Progress:</b>
            <div style="height: 8px; background: #e0e0e0; border-radius: 4px; margin-top: 4px;">
                <div style="width: {percent_complete}%; background: #4caf50; height: 100%; border-radius: 4px;"></div>
            </div>
            <small>{len(mapped_required)} / {len(required_fields)} fields mapped ({percent_complete}%)</small>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Main Mapping Section ---
    st.markdown("## Manual Field Mapping")
    # Gate heavy mapping updates behind a form submit to avoid recomputation on every rerun
    with st.form("mapping_form"):
        render_field_mapping_tab()
        apply_mappings = st.form_submit_button("Apply Mappings")
        if apply_mappings:
            st.session_state["mappings_ready"] = True

    st.divider()

    # --- AI Suggestions Section ---
    st.markdown("## AI Auto-Mapping Suggestions")

    # Compute AI suggestions only when needed
    if "auto_mapping" not in st.session_state and st.session_state.get("mappings_ready"):
        with st.spinner("Running AI mapping suggestions..."):
            st.session_state.auto_mapping = get_enhanced_automap(layout_df, claims_df)

    ai_suggestions = st.session_state.get("auto_mapping", {})
    auto_mapped_fields = st.session_state.get("auto_mapped_fields", [])

    if ai_suggestions:
        st.info("Fields with AI confidence ≥ 80% have already been auto-mapped. You can override them manually below.")

        with st.expander("🔍 View and Commit Additional Suggestions", expanded=False):
            selected_fields: List[str] = []

            for field, info in ai_suggestions.items():
                if field in auto_mapped_fields:
                    continue

                col1, col2, col3 = st.columns([3, 3, 1])
                with col1:
                    st.markdown(f"**{field}**")
                with col2:
                    st.code(info["value"], language="plaintext")
                    if "score" in info:
                        st.caption(f"Confidence: {info['score']}%")
                with col3:
                    selected = st.checkbox("Accept", key=f"ai_accept_{field}")
                    if selected:
                        selected_fields.append(field)

                if selected_fields and st.button("✅ Commit Selected Suggestions"):
                    for field in selected_fields:
                        st.session_state.final_mapping[field] = {
                            "mode": "auto",
                            "value": ai_suggestions[field]["value"]
                        }

                    with st.spinner("Applying selected suggestions..."):
                        st.success(f"Committed {len(selected_fields)} suggestion(s).")
                        generate_all_outputs()

                        # --- Refresh transformed dataframe ---
                        claims_df = st.session_state.get("claims_df")
                        final_mapping = st.session_state.get("final_mapping", {})
                        if claims_df is not None and final_mapping:
                            st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping)
                            st.session_state["transformed_ready"] = True

    else:
        st.info("No additional AI mapping suggestions available.")

with tab3:
    transformed_df = st.session_state.get("transformed_df")
    final_mapping = st.session_state.get("final_mapping", {})

    if transformed_df is None or not final_mapping:
        st.info("Please complete field mappings and preview transformed data first.")
        st.stop()

    # --- Validation gating ---
    run_val = st.button("Run Validation")
    if run_val:
        st.session_state["validation_ready"] = True

    if st.session_state.get("validation_ready"):
        with st.spinner("Running validation checks..."):
            required_fields = [field for field, mapping in final_mapping.items() if mapping.get("mode")]
            mapped_fields = [mapping["value"] for mapping in final_mapping.values() if mapping.get("value")]
            validation_results = run_validations(transformed_df, required_fields, mapped_fields)
            st.session_state.validation_results = validation_results
    else:
        validation_results = st.session_state.get("validation_results", [])

    # --- Validation Metrics Summary ---
    st.markdown("### Validation Summary")

    fails = [r for r in validation_results if r["status"] == "Fail"]
    warnings = [r for r in validation_results if r["status"] == "Warning"]
    passes = [r for r in validation_results if r["status"] == "Pass"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Total Checks", value=len(validation_results))
    with col2:
        st.metric(label="✅ Passes", value=len(passes))
    with col3:
        st.metric(label="⚠️ Warnings / ❌ Fails", value=len(warnings) + len(fails))

    st.divider()

    # --- Detailed Validation Table ---
    st.markdown("### Detailed Validation Results")
    validation_df = pd.DataFrame(validation_results)
    st.dataframe(validation_df, use_container_width=True)  # type: ignore[no-untyped-call]

    val_csv = validation_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Validation Report",
        data=val_csv,
        file_name="validation_report.csv",
        mime="text/csv",
        on_click=lambda: _notify("✅ Validation Report Ready!")
    )

    st.divider()

    # --- Final Verdict Block ---
    st.markdown("### Final Verdict")

    if not validation_results:
        st.info("No validations have been run yet.")
    else:
        if fails:
            st.markdown(
                """
                <div style='background-color:#fdecea; padding: 1rem; border-radius: 8px;'>
                <strong style='color: #b02a37;'>❌ File Status: Rejected — Critical issues found.</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif warnings:
            st.markdown(
                """
                <div style='background-color:#fff3cd; padding: 1rem; border-radius: 8px;'>
                <strong style='color: #8a6d3b;'>⚠️ File Status: Warning — Minor issues detected.</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style='background-color:#d4edda; padding: 1rem; border-radius: 8px;'>
                <strong style='color: #155724;'>✅ File Status: Approved — All checks passed.</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

    # --- Rejection Reason Generator (only if Rejected) ---
    if fails:
        st.markdown("### Rejection Reason for Client Success Team")
        st.caption("Copy this paragraph to explain rejection to the client")

        layout_df = st.session_state.get("layout_df")
        final_mapping = st.session_state.get("final_mapping", {})

        # Extract required fields from layout (guard None and typing)
        if layout_df is None:
            required_fields: List[str] = []
        else:
            required_fields = layout_df[layout_df["Usage"].astype(str).str.lower() == "required"]["Internal Field"].tolist()  # type: ignore[no-untyped-call]

        # Recompute unmapped fields accurately
        unmapped_required_fields: List[str] = []
        for field in required_fields:
            mapping = final_mapping.get(field)
            if not mapping or not mapping.get("value") or str(mapping.get("value")).strip() == "":
                unmapped_required_fields.append(field)

        # --- Generate rejection reason ---
        if unmapped_required_fields:
            field_list = ", ".join(f"`{f}`" for f in unmapped_required_fields)
            reason_text = (
                "This file cannot be approved for automated processing because the following mandatory fields "
                f"required for Targeted Marketing setup are missing: {field_list}. "
                "Please ensure these fields are present and reupload the file."
            )
        else:
            reason_text = (
                "This file cannot be approved due to failed validation checks. "
                "Please review and correct the issues."
            )

        st.code(reason_text, language="markdown")

with tab4:
    st.markdown("## Final Outputs and Downloads")

    if "final_mapping" not in st.session_state or not st.session_state.final_mapping:
        st.info("Complete required field mappings to generate outputs.")
    else:
        final_mapping = st.session_state.get("final_mapping", {})
        layout_df = st.session_state.get("layout_df")
        claims_df = st.session_state.get("claims_df")
        anonymized_df = st.session_state.get("anonymized_df")
        mapping_table = st.session_state.get("mapping_table")
        transformed_df = st.session_state.get("transformed_df")

        if any(x is None for x in [anonymized_df, mapping_table, transformed_df]):
            st.warning("Outputs not fully generated yet. Please complete mapping and preview steps.")
        else:
            # --- Anonymized Claims File Section ---
            with st.expander("Anonymized Claims Preview", expanded=True):
                anonymized_df = st.session_state.get("anonymized_df")
                st.dataframe(anonymized_df.head(), use_container_width=True)  # type: ignore[no-untyped-call]

                st.markdown("**Customize Anonymized File Output**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    file_name_input = st.text_input("File Name (without extension)", value="anonymized_claims")
                with col2:
                    file_type = st.selectbox("File Type", options=[".csv", ".txt", ".xlsx"], index=0)
                with col3:
                    delimiter = st.selectbox("Delimiter", options=["Comma", "Tab", "Pipe"], index=0)

                delim_char = {
                    "Comma": ",",
                    "Tab": "\t",
                    "Pipe": "|"
                }[delimiter]

                if file_type == ".xlsx":
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        anonymized_df.to_excel(writer, index=False)  # type: ignore[no-untyped-call]
                    anonymized_data = output.getvalue()
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else:
                    anonymized_data = anonymized_df.to_csv(index=False, sep=delim_char).encode('utf-8')  # type: ignore[no-untyped-call]
                    mime = "text/plain" if file_type == ".txt" else "text/csv"

                full_filename = f"{file_name_input.strip() or 'anonymized_claims'}{file_type}"

                # ✅ Save to session state for ZIP bundling
                st.session_state.anonymized_data = anonymized_data
                st.session_state.anonymized_filename = full_filename

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label=f"Download {file_type.upper()}",
                        data=anonymized_data,
                        file_name=full_filename,
                        mime=mime,
                        key="download_anon",
                        on_click=lambda: _notify("✅ Anonymized File Ready!")
                    )
                with col2:
                    if st.button("Regenerate Anonymized File"):
                        with st.spinner("Regenerating anonymized data..."):
                            claims_df_local = st.session_state.get("claims_df")
                            final_mapping_local = st.session_state.get("final_mapping", {})
                            if claims_df_local is not None:
                                st.session_state.anonymized_df = anonymize_claims_data(
                                    claims_df_local,
                                    final_mapping_local
                                )
                            _notify("✅ Anonymized file regenerated!")

            # --- Field Mapping Table Section ---
            with st.expander("Field Mapping Table Preview", expanded=True):
                mapping_table = st.session_state.get("mapping_table")
                st.dataframe(mapping_table, use_container_width=True)  # type: ignore[no-untyped-call]
                mapping_csv = mapping_table.to_csv(index=False).encode('utf-8')  # type: ignore[no-untyped-call]
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Mapping Table",
                        data=mapping_csv,
                        file_name="field_mapping_table.csv",
                        mime="text/csv",
                        key="download_mapping",
                        on_click=lambda: _notify("✅ Field Mapping Table Ready!")
                    )
                with col2:
                    if st.button("Regenerate Mapping Table"):
                        with st.spinner("Regenerating mapping table..."):
                            layout_df_local = st.session_state.get("layout_df")
                            claims_df_local = st.session_state.get("claims_df")
                            final_mapping_local = st.session_state.get("final_mapping", {})
                            if layout_df_local is not None and claims_df_local is not None:
                                st.session_state.mapping_table = generate_mapping_table(
                                    layout_df_local,
                                    final_mapping_local,
                                    claims_df_local
                                )
                            _notify("✅ Mapping table regenerated!")

            # --- Optional Attachments Section ---
            st.markdown("### Optional Attachments to Include in ZIP")
            uploaded_attachments = st.file_uploader(
                "Attach any additional files (e.g., header file, original claims, notes)",
                accept_multiple_files=True,
                key="zip_attachments"
            )

            # --- Custom Notes Section ---
            st.markdown("### Add Custom Notes (Optional)")
            notes_text = st.text_area("Include any notes or instructions to be added in the README file:", key="readme_notes")

            # --- Download All as ZIP ---
            st.divider()
            st.markdown("### Download All Outputs as ZIP")

            readme_text = notes_text.strip() if notes_text else "No additional notes provided."
            anon_file_name = st.session_state.get("anonymized_filename", "anonymized_claims.csv")
            anonymized_data = st.session_state.get("anonymized_data", b"")

            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as zip_file:
                zip_file.writestr(anon_file_name, anonymized_data)
                zip_file.writestr("field_mapping_table.csv", mapping_csv)
                zip_file.writestr("readme.txt", readme_text)
                for attachment in uploaded_attachments or []:  # type: ignore[var-annotated]
                    att_name: Any = attachment.name  # type: ignore[attr-defined]
                    att_bytes: Any = attachment.getvalue()  # type: ignore[call-arg]
                    zip_file.writestr(att_name, att_bytes)  # type: ignore[arg-type]

            buffer.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download All Files (ZIP)",
                    data=buffer,
                    file_name="all_outputs.zip",
                    mime="application/zip",
                    key="download_zip"
                )
            with col2:
                if st.button("Regenerate All Outputs"):
                    with st.spinner("Regenerating all outputs..."):
                        if claims_df is not None:
                            st.session_state.anonymized_df = anonymize_claims_data(claims_df, final_mapping)
                        if layout_df is not None and claims_df is not None:
                            st.session_state.mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)
                        _notify("All outputs regenerated.")
