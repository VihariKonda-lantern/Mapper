# --- tab_downloads.py ---
"""Downloads tab handler."""
import streamlit as st
from typing import Any, List, Dict
from datetime import datetime
import io
import zipfile
import pandas as pd
import re
from core.state_manager import SessionStateManager
from ui.ui_components import render_sortable_table, show_toast, show_confirmation_dialog
from core.error_handling import get_user_friendly_error
from data.output_generator import generate_mapping_table
from data.anonymizer import anonymize_claims_data
from utils.batch_processor import process_multiple_claims_files
from ui.ui_components import _notify
from utils.audit_logger import log_event
from utils.improvements_utils import render_empty_state
from ui.ux_enhancements import (
    render_empty_state as render_enhanced_empty_state,
    render_success_with_next_steps,
    render_data_preview_comparison,
    render_validation_feedback
)

st: Any = st


def render_downloads_tab() -> None:
    """Render the Downloads tab content."""
    # Inject tight spacing CSS
    from ui.design_system import inject_tight_spacing_css
    inject_tight_spacing_css()
    
    # Check for files first
    layout_df = SessionStateManager.get_layout_df()
    claims_df = SessionStateManager.get_claims_df()
    
    if layout_df is None or claims_df is None:
        render_enhanced_empty_state(
            title="Files Required",
            description="Please start from the Setup tab to upload both layout and claims files before generating outputs.",
            action_label="Go to Setup Tab",
            action_func=lambda: SessionStateManager.set("active_tab", "Setup"),
            icon="📁"
        )
        st.stop()
    
    # Check for mappings and outputs
    final_mapping = SessionStateManager.get_final_mapping()
    anonymized_df = SessionStateManager.get("anonymized_df")
    mapping_table = SessionStateManager.get("mapping_table")
    
    if not final_mapping or (anonymized_df is None and mapping_table is None):
        render_enhanced_empty_state(
            title="Mapping Required",
            description="Please complete field mappings to generate downloadable outputs. Map at least the required fields in the Field Mapping tab.",
            action_label="Go to Field Mapping Tab",
            action_func=lambda: SessionStateManager.set("active_tab", "Field Mapping"),
            icon="📋"
        )
        st.stop()
    
    # --- Main Content Tabs ---
    st.markdown("""
        <div style='margin-bottom: 0; margin-top: 0; padding-bottom: 0; padding-top: 0;'>
            <h2 style='color: #111827; font-size: 1.25rem; font-weight: 600; margin-bottom: 0; margin-top: 0; padding-bottom: 0; padding-top: 0; letter-spacing: -0.025em;'>Downloads & Outputs</h2>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Data Generation", "Output Previews", "Onboarding & Setup", "Download Package"])
    
    # Tab 1: Data Generation
    with tab1:
        st.markdown("""
            <div style='margin-bottom: 0; margin-top: 0;'>
                <h3 style='color: #111827; font-size: 1.1rem; font-weight: 600; margin-bottom: 0; margin-top: 0; letter-spacing: -0.025em;'>Test Data Generation</h3>
            </div>
        """, unsafe_allow_html=True)
        with st.expander("Generate Test Data with Scenarios", expanded=False):
            from data.output_generator import generate_test_data_outputs
            
            test_records_per_scenario = st.number_input("Records per Scenario", min_value=1, max_value=1000, value=30, key="test_records_per_scenario")
            
            st.markdown("**Select Scenarios:**")
            col1, col2 = st.columns(2)
            with col1:
                test_scenario_happy = st.checkbox("Happy Path", value=True, key="test_scenario_happy")
                test_scenario_headers = st.checkbox("Headers Only", value=True, key="test_scenario_headers")
                test_scenario_dates = st.checkbox("Messed Up Date Formats", value=True, key="test_scenario_dates")
                test_scenario_nulls = st.checkbox("Nulls in Required Fields", value=True, key="test_scenario_nulls")
            with col2:
                test_scenario_duplicates = st.checkbox("Duplicates", value=True, key="test_scenario_duplicates")
                test_scenario_demo = st.checkbox("Demo Mismatch", value=True, key="test_scenario_demo")
                test_scenario_duplicates_recent = st.checkbox("Duplicates with Recent Service", value=True, key="test_scenario_duplicates_recent")
                test_scenario_validation = st.checkbox("Validation Edge Cases", value=True, key="test_scenario_validation")
            
            test_include_scenarios = []
            if test_scenario_happy:
                test_include_scenarios.append("happy_path")
            if test_scenario_headers:
                test_include_scenarios.append("headers_only")
            if test_scenario_dates:
                test_include_scenarios.append("messed_up_date_formats")
            if test_scenario_nulls:
                test_include_scenarios.append("nulls_in_required_fields")
            if test_scenario_duplicates:
                test_include_scenarios.append("duplicates")
            if test_scenario_demo:
                test_include_scenarios.append("demo_mismatch")
            if test_scenario_duplicates_recent:
                test_include_scenarios.append("duplicates_with_recent_service")
            if test_scenario_validation:
                test_include_scenarios.append("validation_edge_cases")
            
            test_include_in_zip = st.checkbox("Include in ZIP file", value=False, key="test_include_in_zip")
            
            if st.button("Generate Test Data", key="generate_test_data_scenarios"):
                try:
                    final_mapping = SessionStateManager.get_final_mapping()
                    layout_df = SessionStateManager.get_layout_df()
                    if layout_df is None or final_mapping is None:
                        st.error("Please ensure layout and mapping are available before generating test data.")
                    else:
                        # Validate that we have at least some mappings
                        if not final_mapping or not any(m.get("value") for m in final_mapping.values() if isinstance(m, dict)):
                            st.error("No field mappings found. Please complete field mappings in the Field Mapping tab before generating test data.")
                        else:
                            test_data_dict = generate_test_data_outputs(
                                layout_df=layout_df,
                                final_mapping=final_mapping,
                                records_per_scenario=test_records_per_scenario,
                                include_scenarios=test_include_scenarios if test_include_scenarios else None
                            )
                            if not test_data_dict:
                                st.warning("No test data was generated. Please check your mappings and try again.")
                            else:
                                st.session_state.test_data_dict = test_data_dict
                                _notify(f"✅ Generated {len(test_data_dict)} test data scenarios!")
                except ValueError as e:
                    st.error(f"Validation error: {str(e)}")
                except ImportError as e:
                    st.error(f"Missing dependency: {str(e)}")
                except Exception as e:
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error generating test data: {error_msg}")
                    if st.session_state.get("debug_mode", False):
                        import traceback
                        st.exception(e)
            
            if st.session_state.get("test_data_dict"):
                st.markdown("**Preview Test Data:**")
                scenario_to_preview = st.selectbox("Select Scenario to Preview", options=list(st.session_state.test_data_dict.keys()), key="test_preview_scenario")
                if scenario_to_preview:
                    preview_data = st.session_state.test_data_dict[scenario_to_preview]
                    
                    # Handle different data types
                    if isinstance(preview_data, pd.DataFrame):
                        st.dataframe(preview_data.head(5), use_container_width=True)
                        preview_df = preview_data
                    elif isinstance(preview_data, bytes):
                        # Try to read as DataFrame if possible
                        try:
                            file_metadata = st.session_state.get("claims_file_metadata", {})
                            file_format = file_metadata.get("format", "csv")
                            if file_format.lower() == 'xlsx':
                                preview_df = pd.read_excel(io.BytesIO(preview_data), dtype=str)
                            elif file_format.lower() == 'json':
                                import json
                                preview_df = pd.read_json(io.BytesIO(preview_data), dtype=str)
                            elif file_format.lower() == 'parquet':
                                import pyarrow.parquet as pq
                                preview_df = pd.read_parquet(io.BytesIO(preview_data))
                            else:
                                preview_df = pd.read_csv(io.BytesIO(preview_data), dtype=str)
                            st.dataframe(preview_df.head(5), use_container_width=True)
                        except Exception as e:
                            st.info(f"Preview not available for this format. File size: {len(preview_data)} bytes")
                            preview_df = None
                    else:
                        st.info("Preview not available for this data type")
                        preview_df = None
                    
                    if preview_df is not None and not preview_df.empty:
                        # Download button for individual scenario
                        file_metadata = st.session_state.get("claims_file_metadata", {})
                        file_format = file_metadata.get("format", "csv")
                        file_ext = file_format.lower() if file_format else "csv"
                        
                        if file_ext == "csv":
                            download_data = preview_df.to_csv(index=False).encode('utf-8')
                            mime_type = "text/csv"
                        elif file_ext in ["xlsx", "excel"]:
                            output = io.BytesIO()
                            preview_df.to_excel(output, index=False, engine='openpyxl')
                            download_data = output.getvalue()
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        elif file_ext == "json":
                            download_data = preview_df.to_json(orient='records').encode('utf-8')
                            mime_type = "application/json"
                        elif file_ext == "parquet":
                            output = io.BytesIO()
                            preview_df.to_parquet(output, index=False)
                            download_data = output.getvalue()
                            mime_type = "application/octet-stream"
                        else:
                            download_data = preview_df.to_csv(index=False).encode('utf-8')
                            mime_type = "text/csv"
                        
                        st.download_button(
                            f"Download {scenario_to_preview}",
                            download_data,
                            f"test_data_{scenario_to_preview}.{file_ext}",
                            mime_type,
                            key=f"download_test_scenario_{scenario_to_preview}"
                        )

    # Tab 2: Output Previews
    with tab2:
        st.markdown("""
            <div style='margin-bottom: 0; margin-top: 0;'>
                <h3 style='color: #111827; font-size: 1.1rem; font-weight: 600; margin-bottom: 0; margin-top: 0; letter-spacing: -0.025em;'>Output Previews</h3>
            </div>
        """, unsafe_allow_html=True)
        final_mapping = SessionStateManager.get_final_mapping()
        if not final_mapping:
            st.info("Complete required field mappings to generate outputs.")
        else:
            layout_df = SessionStateManager.get_layout_df()
            claims_df = SessionStateManager.get_claims_df()
            anonymized_df = st.session_state.get("anonymized_df")
            mapping_table = st.session_state.get("mapping_table")
            transformed_df = SessionStateManager.get_transformed_df()

            if any(x is None for x in [anonymized_df, mapping_table, transformed_df]):
                st.warning("Outputs not fully generated yet. Please complete mapping and preview steps.")
            else:
                # Generate mapping_csv early (needed for ZIP creation)
                mapping_csv = mapping_table.to_csv(index=False).encode('utf-8') if mapping_table is not None else b""
                
                # --- Field Mapping Table Section ---
                with st.expander("Field Mapping Table Preview", expanded=False):
                    # mapping_csv already defined above for ZIP creation
                    mapping_table = st.session_state.get("mapping_table")
                    if mapping_table is not None and len(mapping_table) > 100:
                        table_page_size = st.slider("Rows per page:", 25, min(500, len(mapping_table)), 100, key="mapping_table_page_size")
                        page_num = st.session_state.get("mapping_table_page", 1)
                        start_idx = (page_num - 1) * table_page_size
                        end_idx = start_idx + table_page_size
                        paginated_table = mapping_table.iloc[start_idx:end_idx]
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col1:
                            if st.button("← Previous", key="prev_mapping_table", disabled=page_num == 1):
                                st.session_state.mapping_table_page = max(1, page_num - 1)
                            if st.button("Next →", key="next_mapping_table", disabled=page_num * table_page_size >= len(mapping_table)):
                                st.session_state.mapping_table_page = page_num + 1
                        render_sortable_table(paginated_table, key="mapping_table_paginated")
                    else:
                        render_sortable_table(mapping_table, key="mapping_table_full")
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
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                try:
                                    status_text.text("Regenerating mapping table...")
                                    progress_bar.progress(0.5)
                                    if layout_df is not None and claims_df is not None:
                                        st.session_state.mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)
                                    progress_bar.progress(1.0)
                                    status_text.empty()
                                    progress_bar.empty()
                                    _notify("✅ Mapping table regenerated!")
                                except Exception as e:
                                    progress_bar.empty()
                                    status_text.empty()
                                    error_msg = get_user_friendly_error(e)
                                    st.error(f"Error regenerating mapping table: {error_msg}")
                
                # --- Anonymized Claims File Section ---
                with st.expander("Anonymized Claims Preview", expanded=False):
                    render_sortable_table(anonymized_df.head(), key="anonymized_preview_table")

                    st.markdown("**Customize Anonymized File Output**")
                    
                    # Get file information from uploaded file
                    claims_file_obj = st.session_state.get("claims_file_obj")
                    file_metadata = st.session_state.get("claims_file_metadata", {})
                    
                    # Extract file name without extension
                    import os
                    if claims_file_obj and hasattr(claims_file_obj, "name"):
                        original_filename = claims_file_obj.name
                        # Remove extension
                        file_name_without_ext = os.path.splitext(original_filename)[0]
                        # Remove .gz if present (for decompressed files)
                        if file_name_without_ext.lower().endswith('.gz'):
                            file_name_without_ext = os.path.splitext(file_name_without_ext)[0]
                    else:
                        file_name_without_ext = "anonymized_claims"
                    
                    # Determine file type from metadata or file extension
                    file_format = file_metadata.get("format", "csv")
                    if claims_file_obj and hasattr(claims_file_obj, "name"):
                        file_ext = os.path.splitext(claims_file_obj.name.lower())[1]
                        # Handle .gz files
                        if file_ext == ".gz":
                            # Get the extension before .gz
                            name_without_gz = os.path.splitext(claims_file_obj.name)[0]
                            file_ext = os.path.splitext(name_without_gz.lower())[1]
                    else:
                        file_ext = ".csv"
                    
                    # Map file format/extension to selectbox options
                    file_type_map = {
                        "csv": ".csv",
                        "excel": ".xlsx",
                        "json": ".json",
                        "parquet": ".parquet",
                        ".csv": ".csv",
                        ".txt": ".txt",
                        ".tsv": ".txt",
                        ".xlsx": ".xlsx",
                        ".xls": ".xlsx",
                        ".json": ".json",
                        ".parquet": ".parquet"
                    }
                    default_file_type = file_type_map.get(file_format, file_type_map.get(file_ext, ".csv"))
                    file_type_options = [".csv", ".txt", ".xlsx", ".json", ".parquet"]
                    default_file_type_index = file_type_options.index(default_file_type) if default_file_type in file_type_options else 0
                    
                    # Determine delimiter from metadata
                    detected_sep = file_metadata.get("sep", ",")
                    delimiter_map = {
                        ",": "Comma",
                        "\t": "Tab",
                        "|": "Pipe"
                    }
                    default_delimiter = delimiter_map.get(detected_sep, "Comma")
                    delimiter_options = ["Comma", "Tab", "Pipe"]
                    default_delimiter_index = delimiter_options.index(default_delimiter) if default_delimiter in delimiter_options else 0
                    
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        file_name_input = st.text_input("File Name (without extension)", value=file_name_without_ext)
                    with col2:
                        file_type = st.selectbox("File Type", options=file_type_options, index=default_file_type_index)
                    with col3:
                        delimiter = st.selectbox("Delimiter", options=delimiter_options, index=default_delimiter_index, disabled=file_type in [".xlsx", ".json", ".parquet"])

                    delim_char = {
                        "Comma": ",",
                        "Tab": "\t",
                        "Pipe": "|"
                    }[delimiter]

                    try:
                        if file_type == ".xlsx":
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                                anonymized_df.to_excel(writer, sheet_name="Anonymized Claims", index=False)
                                if mapping_table is not None:
                                    mapping_table.to_excel(writer, sheet_name="Field Mapping", index=False)
                            anonymized_data = output.getvalue()
                            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        elif file_type == ".json":
                            anonymized_data = anonymized_df.to_json(orient="records", indent=2).encode('utf-8')
                            mime = "application/json"
                        elif file_type == ".parquet":
                            output = io.BytesIO()
                            anonymized_df.to_parquet(output, index=False, engine='pyarrow')
                            anonymized_data = output.getvalue()
                            mime = "application/octet-stream"
                        else:
                            anonymized_data = anonymized_df.to_csv(index=False, sep=delim_char).encode('utf-8')
                            mime = "text/plain" if file_type == ".txt" else "text/csv"
                    except Exception as e:
                        error_msg = get_user_friendly_error(e)
                        st.error(f"Error generating {file_type} file: {error_msg}")
                        anonymized_data = b""
                        mime = "text/plain"

                    full_filename = f"{file_name_input.strip() or 'anonymized_claims'}{file_type}"
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
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            try:
                                status_text.text("Regenerating anonymized data...")
                                progress_bar.progress(0.5)
                                if claims_df is not None and final_mapping is not None:
                                    # Import here to ensure it's in scope
                                    from data.anonymizer import anonymize_claims_data
                                    st.session_state.anonymized_df = anonymize_claims_data(claims_df, final_mapping)
                                progress_bar.progress(1.0)
                                status_text.empty()
                                progress_bar.empty()
                                _notify("✅ Anonymized file regenerated!")
                                st.rerun()
                            except Exception as e:
                                progress_bar.empty()
                                status_text.empty()
                                error_msg = get_user_friendly_error(e)
                                st.error(f"Error regenerating anonymized file: {error_msg}")
                
                # --- Data Preview: Source vs Transformed ---
                with st.expander("📊 Data Preview: Source vs Transformed", expanded=True):
                    render_data_preview_comparison(claims_df, transformed_df, max_rows=10)
                
                # --- Batch Processing Section ---
                with st.expander("📦 Batch Processing (Multiple Files)", expanded=False):
                    st.markdown("Process multiple claims files with the same mapping configuration")
                    batch_files = st.file_uploader(
                        "Upload multiple claims files:",
                        accept_multiple_files=True,
                        key="batch_files",
                        help="Select multiple files to process with the current mapping"
                    )
                    final_mapping = SessionStateManager.get_final_mapping()
                    layout_df = SessionStateManager.get_layout_df()
                    if batch_files and final_mapping:
                        if st.button("Process Batch Files", key="process_batch"):
                            with st.spinner("Processing batch files..."):
                                results = process_multiple_claims_files(
                                    batch_files,
                                    layout_df,
                                    final_mapping,
                                    st.session_state.get("lookup_df")
                                )
                                st.success(f"Processed {len(batch_files)} file(s)")
                                for file_name, result in results.items():
                                    if result.get("status") == "processed":
                                        st.info(f"✅ {file_name}: {result.get('rows', 0)} rows processed")
                                    else:
                                        st.error(f"❌ {file_name}: {result.get('error', 'Unknown error')}")
                    elif batch_files and not final_mapping:
                        st.warning("Please complete field mappings first before batch processing")

    # Tab 3: Onboarding & Setup
    with tab3:
        st.markdown("""
            <div style='margin-bottom: 0; margin-top: 0;'>
                <h3 style='color: #111827; font-size: 1.1rem; font-weight: 600; margin-bottom: 0; margin-top: 0; letter-spacing: -0.025em;'>Onboarding & Setup</h3>
            </div>
        """, unsafe_allow_html=True)
        final_mapping = SessionStateManager.get_final_mapping()
        if not final_mapping:
            st.info("Complete required field mappings to generate onboarding scripts.")
        else:
            layout_df = SessionStateManager.get_layout_df()
            claims_df = SessionStateManager.get_claims_df()
            file_metadata = st.session_state.get("claims_file_metadata", {})
            claims_file_obj = st.session_state.get("claims_file_obj")
            
            with st.expander("Generate Onboarding SQL Script", expanded=False):
                from data.output_generator import generate_onboarding_script_output
                
                # ===== Intelligent Auto-Population =====
                
                # Helper function to get value from mapping (handles both column names and manual inputs)
                def get_mapping_value(field_name: str, claims_df: Any = None) -> str:
                    """Get value from mapping, extracting from claims_df if it's a column name."""
                    if not final_mapping:
                        return ""
                    
                    mapping_info = final_mapping.get(field_name, {})
                    value = mapping_info.get("value", "")
                    
                    if not value:
                        return ""
                    
                    # Check if it's a column name in claims_df
                    if claims_df is not None and value in claims_df.columns:
                        # Get first non-null value from that column
                        col_data = claims_df[value].dropna()
                        if len(col_data) > 0:
                            return str(col_data.iloc[0]).strip()
                        # If all null, return column name
                        return value
                    
                    # Otherwise, it's a manual input or direct value
                    return value
                
                # 1. Client Name: From client_name mapping (correct mapping)
                client_name_from_mapping = get_mapping_value("client_name", claims_df)
                # If manual input was provided, use that; otherwise use mapping
                default_client = st.session_state.get("onboarding_client_name") or client_name_from_mapping
                
                # 2. Plan Sponsor Name: From plan_sponsor_name mapping (correct mapping)
                plan_sponsor_from_mapping = get_mapping_value("plan_sponsor_name", claims_df)
                default_sponsor = st.session_state.get("onboarding_sponsor") or plan_sponsor_from_mapping
                
                # 3. CH Client Name: Separate from DAPClientName, used in config parameters
                # Defaults to Client Name if not provided separately
                ch_client_name_from_mapping = get_mapping_value("client_name", claims_df)  # Can be different from DAPClientName
                default_ch_client = st.session_state.get("onboarding_ch_client_name") or ch_client_name_from_mapping or default_client
                
                # 3. Domain Name: Default to "PlanSponsorClaims"
                default_domain = st.session_state.get("onboarding_domain", "PlanSponsorClaims")
                
                # 5. Preprocessor Name: Default to "common_PlanSponsorClaims_prep"
                default_preprocessor = st.session_state.get("onboarding_preprocessor", "common_PlanSponsorClaims_prep")
                
                # 6. File Name Date Format: Infer from file name or use default
                default_file_date_format = st.session_state.get("onboarding_file_date_format", "yyyyMMdd")
                if claims_file_obj:
                    filename = claims_file_obj.name
                    # Try to detect date format from filename (e.g., 20251205, 2025-12-05, etc.)
                    if re.search(r'\d{8}', filename):  # yyyyMMdd
                        default_file_date_format = "yyyyMMdd"
                    elif re.search(r'\d{4}-\d{2}-\d{2}', filename):  # yyyy-MM-dd
                        default_file_date_format = "yyyy-MM-dd"
                    elif re.search(r'\d{2}/\d{2}/\d{4}', filename):  # MM/dd/yyyy
                        default_file_date_format = "MM/dd/yyyy"
                
                # 7. File Name Regex Pattern: Infer from file name pattern
                default_regex_pattern = st.session_state.get("onboarding_regex_pattern", "")
                if not default_regex_pattern and claims_file_obj:
                    filename = claims_file_obj.name
                    # Create a simple regex pattern based on filename
                    # Replace date patterns with regex
                    pattern = re.sub(r'\d{8}', r'\\d{8}', filename)  # Replace 8-digit dates
                    pattern = re.sub(r'\d{4}-\d{2}-\d{2}', r'\\d{4}-\\d{2}-\\d{2}', pattern)  # Replace date with dashes
                    if pattern != filename:
                        default_regex_pattern = pattern
                
                # 8. Primary Key Columns: Default to "Claim ID, Claim Line ID" or infer from layout_df
                default_primary_key = st.session_state.get("onboarding_primary_key", "")
                if not default_primary_key:
                    # First, try to find Claim ID and Claim Line ID from mappings
                    claim_id_value = None
                    claim_line_id_value = None
                    
                    if final_mapping:
                        # Look for Claim_ID or Claim ID
                        for field_name in ["claim_id","Claim_ID", "Claim ID", "ClaimID"]:
                            if field_name in final_mapping:
                                mapped_value = final_mapping[field_name].get("value", "")
                                if mapped_value:
                                    claim_id_value = mapped_value
                                    break
                        
                        # Look for Claim_Line_ID or Claim Line ID
                        for field_name in ["claim_line","Claim_Line_ID", "Claim Line ID", "ClaimLineID", "Claim_LineID"]:
                            if field_name in final_mapping:
                                mapped_value = final_mapping[field_name].get("value", "")
                                if mapped_value:
                                    claim_line_id_value = mapped_value
                                    break
                    
                    # If both found, use them as default
                    if claim_id_value and claim_line_id_value:
                        default_primary_key = f"{claim_id_value},{claim_line_id_value}"
                    elif claim_id_value:
                        default_primary_key = claim_id_value
                    elif layout_df is not None:
                        # Fallback: Look for fields with "ID", "Key", "Number" in internal field name
                        primary_key_candidates = []
                        for _, row in layout_df.iterrows():
                            internal_field = str(row.get("Internal Field", "")).lower()
                            if any(keyword in internal_field for keyword in ["id", "key", "number", "claim_id", "member_id"]):
                                mapped_value = final_mapping.get(row.get("Internal Field", ""), {}).get("value", "")
                                if mapped_value:
                                    primary_key_candidates.append(mapped_value)
                        if primary_key_candidates:
                            default_primary_key = ",".join(primary_key_candidates[:2])  # Limit to 2 columns
                
                # 9. Preprocessing Primary Key: Default to "Claim Line ID" or first primary key
                default_prep_primary_key = st.session_state.get("onboarding_prep_primary_key", "")
                if not default_prep_primary_key:
                    # First, try to find Claim Line ID from mappings
                    claim_line_id_value = None
                    if final_mapping:
                        for field_name in ["Claim_Line_ID", "Claim Line ID", "ClaimLineID", "Claim_LineID"]:
                            if field_name in final_mapping:
                                mapped_value = final_mapping[field_name].get("value", "")
                                if mapped_value:
                                    claim_line_id_value = mapped_value
                                    break
                    
                    if claim_line_id_value:
                        default_prep_primary_key = claim_line_id_value
                    elif default_primary_key:
                        default_prep_primary_key = default_primary_key.split(",")[0].strip()
                
                # 10. Sort Column Name: Infer from date fields (Service Date, Claim Date, etc.)
                default_sort_col = st.session_state.get("onboarding_sort_col", "")
                if not default_sort_col and final_mapping:
                    # Look for date fields that might be used for sorting
                    date_field_candidates = ["Service_Date", "Claim_Date", "Date_of_Service", "ServiceDate", "ClaimDate"]
                    for field_name in date_field_candidates:
                        if field_name in final_mapping:
                            mapped_value = final_mapping[field_name].get("value", "")
                            if mapped_value:
                                default_sort_col = mapped_value
                                break
                
                # 11. Entity Type: Default "Medical"
                default_entity_type = st.session_state.get("onboarding_entity_type", "Medical")
                
                # 12. Demographic Match Tier Config: Default "tier1,tier2"
                default_demo_tier = st.session_state.get("onboarding_demo_tier", "tier1,tier2")
                
                # 13. Null Threshold Percentage: Default 15
                default_null_threshold = st.session_state.get("onboarding_null_threshold", 15)
                
                # 14. Process Curation: Default True
                default_process_curation = st.session_state.get("onboarding_process_curation", True)
                
                # 15. Tagging Flag: Default True
                default_tagging_flag = st.session_state.get("onboarding_tagging_flag", True)
                
                col1, col2 = st.columns(2)
                with col1:
                    onboarding_client_name = st.text_input("Client Name", value=default_client, key="onboarding_client_name", help="Auto-filled from Client_Name mapping if available. Used for DAPClientName: {client}_{plansponsor}")
                    onboarding_ch_client_name = st.text_input("CH Client Name (optional)", value=default_ch_client, key="onboarding_ch_client_name", help="CH client name used in config parameters. Defaults to Client Name if not provided.")
                    onboarding_domain = st.text_input("Domain Name", value=default_domain, key="onboarding_domain")
                    onboarding_file_date_format = st.selectbox(
                        "File Name Date Format",
                        options=["yyyyMMdd", "yyyy-MM-dd", "MMddyyyy", "MM/dd/yyyy", "ddMMyyyy"],
                        index=["yyyyMMdd", "yyyy-MM-dd", "MMddyyyy", "MM/dd/yyyy", "ddMMyyyy"].index(default_file_date_format) if default_file_date_format in ["yyyyMMdd", "yyyy-MM-dd", "MMddyyyy", "MM/dd/yyyy", "ddMMyyyy"] else 0,
                        key="onboarding_file_date_format"
                    )
                    onboarding_primary_key = st.text_input("Primary Key Columns (comma-separated)", value=default_primary_key, key="onboarding_primary_key", help="Defaults to 'Claim ID, Claim Line ID' if available. Auto-detected from ID/Key fields in layout otherwise.")
                    onboarding_entity_type = st.text_input("Entity Type", value=default_entity_type, key="onboarding_entity_type")
                    onboarding_null_threshold = st.number_input("Null Threshold Percentage", min_value=0, max_value=100, value=default_null_threshold, key="onboarding_null_threshold")
                
                with col2:
                    onboarding_sponsor = st.text_input("Plan Sponsor Name", value=default_sponsor, key="onboarding_sponsor", help="Auto-filled from Plan_Sponsor_Name mapping if available")
                    onboarding_preprocessor = st.text_input("Preprocessor Name", value=default_preprocessor, key="onboarding_preprocessor", help="Defaults to 'common_PlanSponsorClaims_prep'")
                    onboarding_regex_pattern = st.text_input("File Name Regex Pattern (optional)", value=default_regex_pattern, key="onboarding_regex_pattern", help="Auto-inferred from file name pattern if available")
                    onboarding_prep_primary_key = st.text_input("Preprocessing Primary Key (optional)", value=default_prep_primary_key, key="onboarding_prep_primary_key", help="Defaults to 'Claim Line ID' if available. Auto-filled from primary key otherwise.")
                    onboarding_demo_tier = st.text_input("Demographic Match Tier Config", value=default_demo_tier, key="onboarding_demo_tier")
                    onboarding_sort_col = st.text_input("Sort Column Name (mandatory)", value=default_sort_col, key="onboarding_sort_col", help="Auto-detected from Service_Date/Claim_Date fields if available")
                    onboarding_process_curation = st.checkbox("Process Curation", value=default_process_curation, key="onboarding_process_curation")
                    onboarding_tagging_flag = st.checkbox("Tagging Flag", value=default_tagging_flag, key="onboarding_tagging_flag", help="Enable tagging in curation configurations")
                
                onboarding_include_in_zip = st.checkbox("Include in ZIP file", value=False, key="onboarding_include_in_zip")
                
                if st.button("Generate SQL Script", key="generate_onboarding_script"):
                    if not onboarding_client_name or not onboarding_sponsor:
                        st.error("Please provide Client Name and Plan Sponsor Name")
                    elif not onboarding_sort_col or not onboarding_sort_col.strip():
                        st.error("Please provide Sort Column Name (mandatory field)")
                    else:
                        try:
                            # Use default if empty
                            preprocessor_name = onboarding_preprocessor.strip() if onboarding_preprocessor and onboarding_preprocessor.strip() else "common_PlanSponsorClaims_prep"
                            sql_script = generate_onboarding_script_output(
                                client_name=onboarding_client_name,
                                plan_sponsor_name=onboarding_sponsor,
                                domain_name=onboarding_domain,
                                preprocessor_name=preprocessor_name,
                                file_name_date_format=onboarding_file_date_format,
                                file_name_regex_pattern=onboarding_regex_pattern if onboarding_regex_pattern and onboarding_regex_pattern.strip() else None,
                                primary_key=onboarding_primary_key if onboarding_primary_key and onboarding_primary_key.strip() else None,
                                preprocessing_primary_key=onboarding_prep_primary_key if onboarding_prep_primary_key and onboarding_prep_primary_key.strip() else None,
                                entity_type=onboarding_entity_type,
                                demographic_match_tier_config=onboarding_demo_tier,
                                sort_col_name=onboarding_sort_col if onboarding_sort_col and onboarding_sort_col.strip() else "",
                                null_threshold_percentage=onboarding_null_threshold,
                                process_curation=onboarding_process_curation,
                                layout_df=layout_df,
                                final_mapping=final_mapping,
                                ch_client_name=onboarding_ch_client_name if onboarding_ch_client_name and onboarding_ch_client_name.strip() else None,
                                tagging_flag=onboarding_tagging_flag,
                                claims_df=claims_df  # Source file DataFrame for raw zone columns
                            )
                            st.session_state.onboarding_sql_script = sql_script
                            render_success_with_next_steps(
                                "SQL script generated successfully!",
                                "Review the generated SQL script below. You can download it individually or include it in the ZIP package.",
                                next_step_label="Include in ZIP Package",
                                next_step_action=lambda: SessionStateManager.set("onboarding_include_in_zip", True)
                            )
                        except Exception as e:
                            error_msg = get_user_friendly_error(e)
                            st.error(f"Error generating SQL script: {error_msg}")
                
                if st.session_state.get("onboarding_sql_script"):
                    st.text_area("Generated SQL Script", value=st.session_state.onboarding_sql_script, height=300, key="onboarding_sql_preview")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    sql_filename = f"CDAP_Onboarding_{onboarding_client_name}_{timestamp}.sql"
                    st.download_button(
                        label="Download SQL Script",
                        data=st.session_state.onboarding_sql_script,
                        file_name=sql_filename,
                        mime="text/plain",
                        key="download_onboarding_sql"
                    )

    # Tab 4: Download Package
    with tab4:
        st.markdown("""
            <div style='margin-bottom: 0; margin-top: 0;'>
                <h3 style='color: #111827; font-size: 1.1rem; font-weight: 600; margin-bottom: 0; margin-top: 0; letter-spacing: -0.025em;'>Download Package</h3>
            </div>
        """, unsafe_allow_html=True)
        final_mapping = SessionStateManager.get_final_mapping()
        if not final_mapping:
            st.info("Complete required field mappings to generate download package.")
        else:
            layout_df = SessionStateManager.get_layout_df()
            claims_df = SessionStateManager.get_claims_df()
            anonymized_df = st.session_state.get("anonymized_df")
            mapping_table = st.session_state.get("mapping_table")
            transformed_df = SessionStateManager.get_transformed_df()

            if any(x is None for x in [anonymized_df, mapping_table, transformed_df]):
                st.warning("Outputs not fully generated yet. Please complete mapping and preview steps.")
            else:
                # Generate mapping_csv early (needed for ZIP creation)
                mapping_csv = mapping_table.to_csv(index=False).encode('utf-8') if mapping_table is not None else b""

            # --- Optional Attachments Section ---
            uploaded_attachments = st.file_uploader(
                "Attach any additional files (e.g., header file, original claims, notes)",
                accept_multiple_files=True,
                key="zip_attachments"
            )

            # --- Custom Notes Section ---
            notes_text = st.text_area(
                "Add Custom Notes (Optional)", 
                value="",
                help="Include any notes or instructions to be added in the README file",
                key="readme_notes"
            )

            # --- Download All as ZIP ---
            st.markdown("""
                <div style='margin-top: 0; margin-bottom: 0;'>
                    <h4 style='margin: 0; padding: 0;'>Download All Outputs as ZIP</h4>
                </div>
            """, unsafe_allow_html=True)

            # Regenerate All Outputs button (moved above download button)
            if st.button("Regenerate All Outputs"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    status_text.text("Regenerating all outputs...")
                    progress_bar.progress(0.2)
                    
                    # Regenerate anonymized data
                    if claims_df is not None:
                        from data.anonymizer import anonymize_claims_data
                        st.session_state.anonymized_df = anonymize_claims_data(claims_df, final_mapping)
                    progress_bar.progress(0.4)
                    
                    # Regenerate mapping table
                    if layout_df is not None and claims_df is not None:
                        from ui.mapping_ui import generate_mapping_table
                        st.session_state.mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)
                    progress_bar.progress(0.6)
                    
                    # Regenerate transformed data
                    if claims_df is not None:
                        from data.transformer import transform_claims_data
                        st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping, layout_df)
                    progress_bar.progress(0.8)
                    
                    # Regenerate anonymized file output
                    file_metadata = st.session_state.get("claims_file_metadata", {})
                    file_format = file_metadata.get("format", "csv")
                    if file_format == "csv":
                        anonymized_data = st.session_state.anonymized_df.to_csv(index=False).encode('utf-8')
                        st.session_state.anonymized_data = anonymized_data
                        st.session_state.anonymized_filename = "anonymized_claims.csv"
                    progress_bar.progress(1.0)
                    status_text.empty()
                    progress_bar.empty()
                    _notify("✅ All outputs regenerated!")
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error regenerating outputs: {error_msg}")

            readme_text = notes_text.strip() if notes_text else "No additional notes provided."
            anon_file_name = st.session_state.get("anonymized_filename", "anonymized_claims.csv")
            anonymized_data = st.session_state.get("anonymized_data", b"")

            # Enhanced README with onboarding, test data, and preprocessing sections
            enhanced_readme = readme_text
            has_additional_content = (
                st.session_state.get("onboarding_include_in_zip") or 
                st.session_state.get("test_include_in_zip") or
                st.session_state.get("preprocessing_steps")
            )
            if has_additional_content:
                enhanced_readme += "\n\n"
                enhanced_readme += "=" * 50 + "\n"
                enhanced_readme += "ADDITIONAL FILES AND SCRIPTS\n"
                enhanced_readme += "=" * 50 + "\n\n"
                
                if st.session_state.get("onboarding_include_in_zip"):
                    enhanced_readme += "ONBOARDING SCRIPTS:\n"
                    enhanced_readme += "- SQL script for CDAP database setup is included in the onboarding/ folder.\n\n"
                
                if st.session_state.get("test_include_in_zip"):
                    enhanced_readme += "TEST DATA SCENARIOS:\n"
                    enhanced_readme += "- Test data files are included in the test_data/ folder.\n\n"
                    
                    if st.session_state.get("preprocessing_steps"):
                        enhanced_readme += "PREPROCESSING SCRIPT:\n"
                        enhanced_readme += "- Python script (preprocess_file.py) is included in the preprocessing/ folder.\n\n"

            # Get uploaded file name for ZIP file naming
            claims_file_obj = st.session_state.get("claims_file_obj")
            import os
            if claims_file_obj and hasattr(claims_file_obj, "name"):
                original_filename = claims_file_obj.name
                # Remove extension
                zip_file_name = os.path.splitext(original_filename)[0]
                # Remove .gz if present (for decompressed files)
                if zip_file_name.lower().endswith('.gz'):
                    zip_file_name = os.path.splitext(zip_file_name)[0]
                # Add .zip extension
                zip_file_name = f"{zip_file_name}.zip"
            else:
                zip_file_name = "all_outputs.zip"

            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as zip_file:
                zip_file.writestr(anon_file_name, anonymized_data)
                zip_file.writestr("field_mapping_table.csv", mapping_csv)
                zip_file.writestr("readme.txt", enhanced_readme)
                
                # Add onboarding script if requested
                if st.session_state.get("onboarding_include_in_zip") and st.session_state.get("onboarding_sql_script"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    client_name = st.session_state.get("onboarding_client_name") or "client"
                    sql_filename = f"CDAP_Onboarding_{client_name}_{timestamp}.sql"
                    zip_file.writestr(f"onboarding/{sql_filename}", st.session_state.onboarding_sql_script)
                
                # Add test data if requested
                if st.session_state.get("test_include_in_zip") and st.session_state.get("test_data_dict"):
                    file_metadata = st.session_state.get("claims_file_metadata", {})
                    file_format = file_metadata.get("format", "csv")
                    file_separator = file_metadata.get("sep", "\t")
                    file_has_header = file_metadata.get("header", False)
                    
                    # Determine file extension based on format
                    file_ext_map = {
                        'csv': '.csv',
                        'txt': '.txt',
                        'tsv': '.tsv',
                        'xlsx': '.xlsx',
                        'json': '.json',
                        'parquet': '.parquet',
                        'fixed-width': '.txt'
                    }
                    file_ext = file_ext_map.get(file_format.lower(), '.csv')
                    
                    # Separate headers_only from other scenarios
                    headers_only_data = None
                    other_scenarios_dfs = []
                    
                    for scenario_name, scenario_data in st.session_state.test_data_dict.items():
                        if scenario_name == "headers_only":
                            headers_only_data = scenario_data
                        else:
                            # For combining, we need DataFrames
                            # If already converted to bytes/str, we'll handle it separately
                            if isinstance(scenario_data, pd.DataFrame) and not scenario_data.empty:
                                other_scenarios_dfs.append(scenario_data)
                    
                    # Write headers_only file if it exists
                    if headers_only_data is not None:
                        if isinstance(headers_only_data, pd.DataFrame):
                                # Convert to appropriate format
                                if file_format.lower() == 'xlsx':
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                        headers_only_data.to_excel(writer, sheet_name='headers_only', index=False, header=file_has_header)
                                    zip_file.writestr(f"test_data/test_data_headers_only{file_ext}", output.getvalue())
                                elif file_format.lower() == 'json':
                                    json_str = headers_only_data.to_json(orient='records', indent=2, date_format='iso')
                                    zip_file.writestr(f"test_data/test_data_headers_only{file_ext}", json_str.encode('utf-8'))
                                elif file_format.lower() == 'parquet':
                                    output = io.BytesIO()
                                    headers_only_data.to_parquet(output, index=False, engine='pyarrow')
                                    zip_file.writestr(f"test_data/test_data_headers_only{file_ext}", output.getvalue())
                                elif file_format.lower() == 'fixed-width':
                                    from data.test_data_generator import _convert_to_fixed_width
                                    source_columns = list(headers_only_data.columns) if not headers_only_data.empty else []
                                    fixed_width_str = _convert_to_fixed_width(headers_only_data, source_columns, file_has_header)
                                    zip_file.writestr(f"test_data/test_data_headers_only{file_ext}", fixed_width_str.encode('utf-8'))
                                else:
                                    # CSV/delimited format
                                    csv_data = headers_only_data.to_csv(index=False, sep=file_separator, header=file_has_header).encode('utf-8')
                                    zip_file.writestr(f"test_data/test_data_headers_only{file_ext}", csv_data)
                        elif isinstance(headers_only_data, bytes):
                            zip_file.writestr(f"test_data/test_data_headers_only{file_ext}", headers_only_data)
                        elif isinstance(headers_only_data, str):
                            zip_file.writestr(f"test_data/test_data_headers_only{file_ext}", headers_only_data.encode('utf-8'))
                        
                        # Combine all other scenarios into one file
                        if other_scenarios_dfs:
                            combined_df = pd.concat(other_scenarios_dfs, ignore_index=True)
                            
                            # Convert to appropriate format
                            if file_format.lower() == 'xlsx':
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                    combined_df.to_excel(writer, sheet_name='combined_scenarios', index=False, header=file_has_header)
                                zip_file.writestr(f"test_data/test_data_combined{file_ext}", output.getvalue())
                            elif file_format.lower() == 'json':
                                json_str = combined_df.to_json(orient='records', indent=2, date_format='iso')
                                zip_file.writestr(f"test_data/test_data_combined{file_ext}", json_str.encode('utf-8'))
                            elif file_format.lower() == 'parquet':
                                output = io.BytesIO()
                                combined_df.to_parquet(output, index=False, engine='pyarrow')
                                zip_file.writestr(f"test_data/test_data_combined{file_ext}", output.getvalue())
                            elif file_format.lower() == 'fixed-width':
                                from data.test_data_generator import _convert_to_fixed_width
                                source_columns = list(combined_df.columns)
                                fixed_width_str = _convert_to_fixed_width(combined_df, source_columns, file_has_header)
                                zip_file.writestr(f"test_data/test_data_combined{file_ext}", fixed_width_str.encode('utf-8'))
                            else:
                                # CSV/delimited format
                                csv_data = combined_df.to_csv(index=False, sep=file_separator, header=file_has_header).encode('utf-8')
                                zip_file.writestr(f"test_data/test_data_combined{file_ext}", csv_data)
                        
                        # Handle scenarios that were already converted to bytes/str (shouldn't happen with current flow, but handle for safety)
                        for scenario_name, scenario_data in st.session_state.test_data_dict.items():
                            if scenario_name != "headers_only" and not isinstance(scenario_data, pd.DataFrame):
                                # These are already converted, write them separately as fallback
                                if isinstance(scenario_data, bytes):
                                    zip_file.writestr(f"test_data/test_data_{scenario_name}{file_ext}", scenario_data)
                                elif isinstance(scenario_data, str):
                                    zip_file.writestr(f"test_data/test_data_{scenario_name}{file_ext}", scenario_data.encode('utf-8'))
                
                for attachment in uploaded_attachments or []:
                    att_name: Any = attachment.name
                    att_bytes: Any = attachment.getvalue()
                    zip_file.writestr(att_name, att_bytes)
                
                # Add preprocessing script if preprocessing steps were tracked
                if st.session_state.get("preprocessing_steps"):
                    try:
                        from data.preprocessing_tracker import generate_preprocessing_script
                        # Use the same claims_file_obj from above
                        original_filename = claims_file_obj.name if claims_file_obj and hasattr(claims_file_obj, "name") else "input_file.csv"
                        
                        preprocessing_script = generate_preprocessing_script(
                            file_path="raw_file.csv",
                            output_path="processed_file.csv",
                            filename=original_filename
                        )
                        
                        zip_file.writestr("preprocessing/preprocess_file.py", preprocessing_script.encode('utf-8'))
                    except ImportError:
                        pass  # Preprocessing tracker not available
                    except Exception:
                        pass  # Don't fail if script generation fails

            buffer.seek(0)

            def on_zip_download():
                try:
                    log_event("output", f"ZIP file generated and downloaded ({zip_file_name})")
                except NameError:
                    pass
                _notify("✅ ZIP file ready!")
            st.download_button(
                label="Download All Files (ZIP)",
                data=buffer,
                file_name=zip_file_name,
                mime="application/zip",
                key="download_zip",
                on_click=on_zip_download
            )
