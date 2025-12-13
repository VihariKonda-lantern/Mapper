# --- tab_downloads.py ---
"""Downloads tab handler."""
import streamlit as st
from typing import Any, List, Dict
import io
import zipfile
import pandas as pd
from state_manager import SessionStateManager
from ui_improvements import render_sortable_table
from error_handling import get_user_friendly_error
from ui_improvements import show_toast, show_confirmation_dialog
from output_generator import generate_mapping_table, anonymize_claims_data
from batch_processor import process_multiple_claims_files
from ui_components import _notify
from audit_logger import log_event
from datetime import datetime

st: Any = st


def render_downloads_tab() -> None:
    """Render the Downloads tab content."""
    st.markdown("#### Final Outputs and Downloads")
    
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

    # --- Activity Log Section ---
    st.markdown("### 📋 Activity Log")
    audit_log = SessionStateManager.get_audit_log()
    if audit_log:
        recent_events = audit_log[-20:][::-1]
        log_data_list: List[Dict[str, str]] = []
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            message = event.get("message", "")
            timestamp = event.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                time_str = timestamp
            log_data_list.append({
                "Time": time_str,
                "Type": event_type.upper(),
                "Message": message
            })
        log_df = pd.DataFrame(log_data_list)
        render_sortable_table(log_df, key="audit_log_table")
        if st.button("Clear Activity Log", key="clear_activity_log_tab4"):
            if show_confirmation_dialog(
                "Clear Activity Log",
                "Are you sure you want to clear the activity log? This action cannot be undone.",
                confirm_label="Yes, Clear",
                cancel_label="Cancel",
                key="clear_activity_confirm"
            ):
                SessionStateManager.clear_audit_log()
                show_toast("Activity log cleared", "🗑️")
                st.session_state.needs_refresh = True
    else:
        st.info("No activity logged yet. Events will appear here as you use the app.")
    st.divider()

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
            # --- Anonymized Claims File Section ---
            with st.expander("Anonymized Claims Preview", expanded=False):
                render_sortable_table(anonymized_df.head(), key="anonymized_preview_table")

                st.markdown("**Customize Anonymized File Output**")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    file_name_input = st.text_input("File Name (without extension)", value="anonymized_claims")
                with col2:
                    file_type = st.selectbox("File Type", options=[".csv", ".txt", ".xlsx", ".json", ".parquet"], index=0)
                with col3:
                    delimiter = st.selectbox("Delimiter", options=["Comma", "Tab", "Pipe"], index=0, disabled=file_type in [".xlsx", ".json", ".parquet"])

                delim_char = {
                    "Comma": ",",
                    "Tab": "\t",
                    "Pipe": "|"
                }[delimiter]

                try:
                    if file_type == ".xlsx":
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
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
                            if claims_df is not None:
                                st.session_state.anonymized_df = anonymize_claims_data(claims_df, final_mapping)
                            progress_bar.progress(1.0)
                            status_text.empty()
                            progress_bar.empty()
                            _notify("✅ Anonymized file regenerated!")
                        except Exception as e:
                            progress_bar.empty()
                            status_text.empty()
                            error_msg = get_user_friendly_error(e)
                            st.error(f"Error regenerating anonymized file: {error_msg}")

            # --- Field Mapping Table Section ---
            with st.expander("Field Mapping Table Preview", expanded=False):
                mapping_table = st.session_state.get("mapping_table")
                mapping_csv = mapping_table.to_csv(index=False).encode('utf-8')
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
                for attachment in uploaded_attachments or []:
                    att_name: Any = attachment.name
                    att_bytes: Any = attachment.getvalue()
                    zip_file.writestr(att_name, att_bytes)

            buffer.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                def on_zip_download():
                    try:
                        log_event("output", "ZIP file generated and downloaded (all_outputs.zip)")
                    except NameError:
                        pass
                    _notify("✅ ZIP file ready!")
                st.download_button(
                    label="Download All Files (ZIP)",
                    data=buffer,
                    file_name="all_outputs.zip",
                    mime="application/zip",
                    key="download_zip",
                    on_click=on_zip_download
                )
            with col2:
                if st.button("Regenerate All Outputs"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    try:
                        status_text.text("Regenerating all outputs...")
                        progress_bar.progress(0.3)
                        if claims_df is not None:
                            st.session_state.anonymized_df = anonymize_claims_data(claims_df, final_mapping)
                        progress_bar.progress(0.6)
                        if layout_df is not None and claims_df is not None:
                            st.session_state.mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)
                        progress_bar.progress(1.0)
                        status_text.empty()
                        progress_bar.empty()
                        _notify("✅ All outputs regenerated!")
                        show_toast("All outputs regenerated!", "✅")
                        st.session_state.needs_refresh = True
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        error_msg = get_user_friendly_error(e)
                        st.error(f"Error regenerating outputs: {error_msg}")

