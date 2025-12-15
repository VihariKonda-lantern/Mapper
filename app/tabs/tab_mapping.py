# --- tab_mapping.py ---
"""Field Mapping tab handler."""
import streamlit as st
from typing import Any, List, Dict, Optional
import json
import os
import time
from core.state_manager import SessionStateManager
from core.config import AI_CONFIDENCE_THRESHOLD
from utils.improvements_utils import render_empty_state, get_user_friendly_error, DEBOUNCE_DELAY_SECONDS
from ui.ui_improvements import show_toast, show_confirmation_dialog, show_undo_redo_feedback
from ui.mapping_ui import render_field_mapping_tab
from ui.ui_components import render_progress_bar
from core.session_state import initialize_undo_redo, save_to_history, undo_mapping, redo_mapping
from data.transformer import transform_claims_data
from data.output_generator import generate_all_outputs
from testing_qa import create_mapping_unit_tests, run_unit_tests
from mapping.mapping_engine import get_enhanced_automap
from mapping.mapping_enhancements import (
    get_mapping_confidence_score,
    validate_mapping_before_processing,
    get_mapping_version,
    export_mapping_template_for_sharing,
    import_mapping_template_from_shareable
)
from advanced_features import save_mapping_template, load_mapping_template, list_saved_templates
from file.layout_loader import get_required_fields
from monitoring.audit_logger import log_event

st: Any = st


def render_mapping_tab() -> None:
    """Render the Field Mapping tab content."""
    # Cache frequently accessed session state values
    layout_df = SessionStateManager.get_layout_df()
    claims_df = SessionStateManager.get_claims_df()
    final_mapping = SessionStateManager.get_final_mapping()

    if layout_df is None or claims_df is None:
        render_empty_state(
            icon="📁",
            title="Files Required",
            message="Please upload both layout and claims files to begin mapping.",
            action_label="Go to Setup Tab",
            action_callback=lambda: SessionStateManager.set("active_tab", "Setup")
        )
        st.stop()
    
    # --- Sticky Mapping Progress Bar ---
    # Cache required fields calculation to avoid recomputing on every rerun
    if layout_df is not None:
        cache_key = f"required_fields_{id(layout_df)}"
        if cache_key not in st.session_state:
            usage_normalized = layout_df["Usage"].astype(str).str.strip().str.lower()
            required_fields = layout_df[usage_normalized == "mandatory"]["Internal Field"].tolist()
            st.session_state[cache_key] = required_fields
        else:
            required_fields = st.session_state[cache_key]
    else:
        required_fields = []
    
    total_required = len(required_fields) if required_fields else 0
    mapped_required: List[str] = [str(f) for f in required_fields if f in final_mapping and final_mapping[f].get("value")]
    mapped_count = len(mapped_required)
    percent_complete = int((mapped_count / total_required) * 100) if total_required > 0 else 0

    progress_html = render_progress_bar(percent_complete, f"{mapped_count} / {total_required} fields mapped ({percent_complete}%)")
    st.markdown(
        f'<div style="position: sticky; top: 0; background: #f5f5f5; color: #000000; z-index: 999; padding: 0.5rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; box-shadow: 0 1px 2px rgba(0,0,0,0.1); border: 1px solid #ddd;"><b style="font-size: 0.875rem; color: #000000;">📌 Required Field Mapping Progress</b>{progress_html}</div>',
        unsafe_allow_html=True
    )

    # --- UX Tools (Collapsible Container) ---
    with st.expander("⚙️ Tools & Actions", expanded=False):
        # Search field at the top of the container with debouncing
        raw_search_tools = st.text_input("🔍 Search Fields", placeholder="Type to filter fields... (Ctrl+F)", key="field_search_tools_raw")
        # Debounce search input
        current_time = time.time()
        last_search_time = st.session_state.get("field_search_tools_last_time", 0)
        debounced_search = st.session_state.get("field_search_tools", "")
        if raw_search_tools != st.session_state.get("field_search_tools_raw_prev", ""):
            st.session_state.field_search_tools_raw_prev = raw_search_tools
            if current_time - last_search_time >= DEBOUNCE_DELAY_SECONDS:
                debounced_search = raw_search_tools
                st.session_state.field_search_tools = debounced_search
                st.session_state.field_search_tools_last_time = current_time
            else:
                st.session_state.field_search_tools_pending = raw_search_tools
        if "field_search_tools_pending" in st.session_state:
            if current_time - last_search_time >= DEBOUNCE_DELAY_SECONDS:
                debounced_search = st.session_state.field_search_tools_pending
                st.session_state.field_search_tools = debounced_search
                st.session_state.field_search_tools_last_time = current_time
                del st.session_state.field_search_tools_pending
        search_query = debounced_search
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**History**")
            initialize_undo_redo()
            if len(st.session_state.mapping_history) == 0:
                if final_mapping:
                    save_to_history(final_mapping)
                else:
                    save_to_history({})
            can_undo = st.session_state.history_index > 0
            can_redo = st.session_state.history_index < len(st.session_state.mapping_history) - 1
            if st.button("↶ Undo", key="undo_btn", use_container_width=True, disabled=not can_undo, help="Undo last mapping change (Ctrl+Z)"):
                undone = undo_mapping()
                if undone is not None:
                    st.session_state.final_mapping = {k: dict(v) for k, v in undone.items()}
                    if "auto_mapping" in st.session_state:
                        del st.session_state.auto_mapping
                    undone_field_name: Optional[str] = list(undone.keys())[0] if undone else None
                    show_undo_redo_feedback("Undone", undone_field_name or "")
                    st.session_state.needs_refresh = True
            if st.button("↷ Redo", key="redo_btn", use_container_width=True, disabled=not can_redo, help="Redo last undone change (Ctrl+Y)"):
                redone = redo_mapping()
                if redone is not None:
                    st.session_state.final_mapping = {k: dict(v) for k, v in redone.items()}
                    if "auto_mapping" in st.session_state:
                        del st.session_state.auto_mapping
                    redone_field_name: Optional[str] = list(redone.keys())[0] if redone else None
                    show_undo_redo_feedback("Redone", redone_field_name or "")
                    st.session_state.needs_refresh = True
        with col2:
            st.markdown("**Bulk Actions**")
            ai_suggestions = st.session_state.get("auto_mapping", {})
            if st.button("✅ Accept All AI (≥80%)", key="bulk_accept_ai", use_container_width=True):
                accepted = 0
                for field, info in ai_suggestions.items():
                    score = info.get("score", 0)
                    if score >= AI_CONFIDENCE_THRESHOLD and (field not in final_mapping or not final_mapping[field].get("value")):
                        final_mapping[field] = {"mode": "auto", "value": info["value"]}
                        accepted += 1
                if accepted > 0:
                    st.session_state.final_mapping = final_mapping
                    save_to_history(final_mapping)
                    show_toast(f"Accepted {accepted} AI suggestions!", "✅")
                    st.session_state.needs_refresh = True
            if st.button("🔄 Clear All", key="bulk_clear", use_container_width=True):
                if show_confirmation_dialog(
                    "Clear All Mappings",
                    "⚠️ Are you sure you want to clear all mappings? This action cannot be undone.",
                    confirm_label="Yes, Clear All",
                    cancel_label="Cancel",
                    key="clear_all_confirm"
                ):
                    final_mapping.clear()
                    st.session_state.final_mapping = {}
                    save_to_history({})
                    show_toast("All mappings cleared!", "🔄")
                    log_event("mapping", "Cleared all mappings")
                    st.session_state.needs_refresh = True
        with col3:
            st.markdown("**Utilities**")
            if st.button("📋 Copy Mapping", key="bulk_copy", use_container_width=True):
                mapping_str = json.dumps(final_mapping, indent=2)
                st.code(mapping_str, language="json")
                st.info("Right-click and copy the JSON above")
            if final_mapping:
                mapping_json = json.dumps(final_mapping, indent=2).encode('utf-8')
                st.download_button(
                    label="💾 Export Mapping (JSON)",
                    data=mapping_json,
                    file_name="mapping_template.json",
                    mime="application/json",
                    key="export_mapping_json",
                    use_container_width=True,
                    help="Download current mapping as JSON template"
                )
            st.markdown("**Mapping Templates**")
            template_col1, template_col2 = st.columns(2)
            with template_col1:
                if st.button("💾 Save Template", key="save_template", use_container_width=True):
                    if final_mapping:
                        filename = save_mapping_template(final_mapping)
                        st.success(f"Template saved: {os.path.basename(filename)}")
                        log_event("template", f"Saved mapping template: {os.path.basename(filename)}")
                    else:
                        st.warning("No mapping to save")
            with template_col2:
                saved_templates = list_saved_templates()
                if saved_templates:
                    template_names = [os.path.basename(t) for t in saved_templates]
                    selected_template = st.selectbox(
                        "Load Template",
                        options=[""] + template_names,
                        key="load_template_select",
                        help="Select a saved template to load"
                    )
                    if selected_template and selected_template != "":
                        template_path = os.path.join("templates", selected_template)
                        loaded_mapping = load_mapping_template(template_path)
                        if loaded_mapping:
                            st.session_state.final_mapping = loaded_mapping
                            save_to_history(loaded_mapping)
                            show_toast(f"Template loaded: {selected_template}", "✅")
                            log_event("template", f"Loaded mapping template: {selected_template}")
                            st.session_state.needs_refresh = True
                else:
                    st.info("No saved templates")

    # --- Mapping Enhancements Section ---
    with st.expander("🔧 Mapping Tools & Enhancements", expanded=False):
        if st.button("Validate Mapping Before Processing", key="validate_mapping_btn"):
            is_valid, errors = validate_mapping_before_processing(final_mapping, layout_df, claims_df)
            if is_valid:
                st.success("✅ Mapping is valid and ready for processing!")
            else:
                st.error("❌ Mapping validation failed:")
                for error in errors:
                    st.error(f"- {error}")
        ai_suggestions_tab2 = st.session_state.get("auto_mapping", {})
        if ai_suggestions_tab2:
            confidence_scores = get_mapping_confidence_score(final_mapping, ai_suggestions_tab2)
            st.markdown("#### Mapping Confidence Scores")
            import pandas as pd
            confidence_df = pd.DataFrame(list(confidence_scores.items()), columns=["Field", "Confidence"])
            confidence_df["Confidence"] = (confidence_df["Confidence"] * 100).round(1)
            if confidence_df.empty:
                render_empty_state(
                    icon="🎯",
                    title="No Confidence Scores",
                    message="AI mapping suggestions will appear here once available."
                )
            else:
                from ui_improvements import render_tooltip, render_sortable_table
                render_tooltip(
                    "AI mapping confidence scores",
                    "Higher scores indicate better matches. Scores above 80% are considered high confidence."
                )
                render_sortable_table(confidence_df, key="confidence_table")
        st.markdown("#### Mapping Version Control")
        mapping_version = get_mapping_version(final_mapping)
        st.code(f"Current Version: {mapping_version}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Mapping for Sharing", key="export_mapping_share"):
                shareable = export_mapping_template_for_sharing(final_mapping, {
                    "name": "Current Mapping",
                    "description": "Exported mapping",
                    "author": "User"
                })
                st.download_button("Download Shareable Template",
                                 json.dumps(shareable, indent=2).encode('utf-8'),
                                 "mapping_template_shareable.json",
                                 "application/json",
                                 key="download_shareable")
        with col2:
            uploaded_template = st.file_uploader("Import Shareable Template",
                                                type=["json"],
                                                key="import_shareable_template")
            if uploaded_template:
                try:
                    template_data = json.load(uploaded_template)
                    imported_mapping, metadata = import_mapping_template_from_shareable(template_data)
                    if st.button("Apply Imported Mapping", key="apply_imported"):
                        st.session_state.final_mapping = imported_mapping
                        show_toast(f"Imported mapping from: {metadata.get('name', 'Unknown')}", "✅")
                        st.session_state.needs_refresh = True
                except Exception as e:
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error importing template: {error_msg}")
    
    # --- Main Mapping Section ---
    st.markdown("#### Manual Field Mapping")
    with st.form("mapping_form"):
        render_field_mapping_tab()
        apply_mappings = st.form_submit_button("Apply Mappings")
        if apply_mappings:
            st.session_state["mappings_ready"] = True
            if final_mapping:
                save_to_history(final_mapping)
                manual_mapped_count = len([f for f in final_mapping.keys() 
                                         if final_mapping[f].get("value") and final_mapping[f].get("mode") == "manual"])
                if manual_mapped_count > 0:
                    try:
                        log_event("mapping", f"Manual field mappings committed via form ({manual_mapped_count} fields mapped)")
                    except NameError:
                        pass
                try:
                    tests = create_mapping_unit_tests(final_mapping, claims_df, layout_df)
                    test_results = run_unit_tests(tests)
                    st.session_state.unit_test_results = test_results
                except Exception:
                    pass

    st.divider()
    
    # --- Test Mapping Section ---
    if st.session_state.get("mappings_ready") and final_mapping:
        mapping_hash = str(hash(str(final_mapping)))
        last_hash = st.session_state.get("last_mapping_hash")
        if last_hash != mapping_hash or not st.session_state.get("unit_test_results"):
            try:
                tests = create_mapping_unit_tests(final_mapping, claims_df, layout_df)
                test_results = run_unit_tests(tests)
                st.session_state.unit_test_results = test_results
                st.session_state.last_mapping_hash = mapping_hash
            except Exception:
                pass

    # --- Review & Adjust Mappings Section ---
    if st.session_state.get("mappings_ready") and final_mapping:
        st.markdown("#### Review & Adjust Mappings")
        st.caption("Review and edit your mappings in the table below. Click 'Apply Edited Mappings' to save changes.")
        all_internal_fields = layout_df["Internal Field"].dropna().unique().tolist()
        required_fields_df = get_required_fields(layout_df)
        required_fields_list: List[str] = required_fields_df["Internal Field"].tolist() if isinstance(required_fields_df, pd.DataFrame) else []
        required_fields_set: set = set(required_fields_list)
        available_source_columns = claims_df.columns.tolist()
        review_data: List[Dict[str, Any]] = []
        for field in all_internal_fields:
            mapping_info = final_mapping.get(field, {})
            source_col = mapping_info.get("value", "")
            is_required = "Yes" if field in required_fields_set else "No"
            review_data.append({
                "Internal Field": field,
                "Source Column": source_col,
                "Is Required": is_required
            })
        import pandas as pd
        review_df = pd.DataFrame(review_data)
        review_df["_sort_key"] = review_df["Is Required"].apply(lambda x: 0 if x == "Yes" else 1)
        review_df = review_df.sort_values(by=["_sort_key", "Internal Field"]).drop(columns=["_sort_key"])
        column_config = {
            "Internal Field": st.column_config.TextColumn("Internal Field", disabled=True, help="Internal field name (cannot be edited)"),
            "Source Column": st.column_config.TextColumn("Source Column", help="Type or edit the source column name. Available columns: " + ", ".join(available_source_columns[:10]) + ("..." if len(available_source_columns) > 10 else ""), required=False),
            "Is Required": st.column_config.TextColumn("Is Required", disabled=True, help="Whether this field is mandatory")
        }
        edited_df = st.data_editor(review_df, column_config=column_config, use_container_width=True, num_rows="fixed", key="mapping_review_editor", hide_index=True)
        if st.button("Apply Edited Mappings", key="apply_edited_mappings", use_container_width=True, type="primary"):
            updated_mapping: Dict[str, Dict[str, Any]] = dict(final_mapping)
            for row in edited_df.itertuples(index=False):
                internal_field = str(row[0])
                source_col = str(row[1]).strip() if pd.notna(row[1]) else ""
                if source_col and source_col != "":
                    existing_mapping = updated_mapping.get(internal_field, {})
                    mode = existing_mapping.get("mode", "manual")
                    if existing_mapping.get("value") != source_col:
                        mode = "manual"
                    updated_mapping[internal_field] = {"mode": mode, "value": source_col}
                elif internal_field in updated_mapping:
                    del updated_mapping[internal_field]
            st.session_state.final_mapping = updated_mapping
            if updated_mapping:
                save_to_history(updated_mapping)
            if claims_df is not None and updated_mapping:
                st.session_state.transformed_df = transform_claims_data(claims_df, updated_mapping)
                generate_all_outputs()
                try:
                    tests = create_mapping_unit_tests(updated_mapping, claims_df, layout_df)
                    test_results = run_unit_tests(tests)
                    st.session_state.unit_test_results = test_results
                    st.session_state.last_mapping_hash = str(hash(str(updated_mapping)))
                except Exception:
                    pass
            st.success("✅ Mappings updated successfully!")
            manual_mapped_count = len([f for f in updated_mapping.keys() 
                                     if updated_mapping[f].get("value") and updated_mapping[f].get("mode") == "manual"])
            if manual_mapped_count > 0:
                try:
                    log_event("mapping", f"Manual mappings updated via review table ({manual_mapped_count} fields mapped)")
                except NameError:
                    pass
            show_toast("Mappings updated successfully!", "✅")
            st.session_state.needs_refresh = True

    st.divider()

    # --- AI Suggestions Section ---
    st.markdown("#### AI Auto-Mapping Suggestions")
    if "auto_mapping" not in st.session_state and st.session_state.get("mappings_ready"):
        with st.spinner("Running AI mapping suggestions..."):
            st.session_state.auto_mapping = get_enhanced_automap(layout_df, claims_df)

    ai_suggestions = st.session_state.get("auto_mapping", {})
    auto_mapped_fields = st.session_state.get("auto_mapped_fields", [])

    if ai_suggestions:
        auto_mapped_high_confidence = [
            (field, info) for field, info in ai_suggestions.items()
            if field in auto_mapped_fields and info.get("score", 0) >= 80
        ]
        if auto_mapped_high_confidence:
            st.info("Fields with AI confidence ≥ 80% have already been auto-mapped. You can override them manually below.")
            with st.expander("📋 Auto-Mapped Fields (≥80% confidence) - Click to Override", expanded=False):
                st.caption("These fields were automatically mapped. You can change them in the mapping form below.")
                for field, info in auto_mapped_high_confidence:
                    col1, col2, col3 = st.columns([3, 3, 2])
                    with col1:
                        st.markdown(f"**{field}**")
                    with col2:
                        mapped_value = final_mapping.get(field, {}).get("value", "")
                        st.code(mapped_value if mapped_value else "Not mapped", language="plaintext")
                        if "score" in info:
                            st.caption(f"AI Confidence: {info['score']}%")
                    with col3:
                        if st.button("Override", key=f"override_{field}", use_container_width=True):
                            if field in final_mapping:
                                final_mapping[field] = {"mode": "manual", "value": ""}
                                st.session_state.final_mapping = final_mapping
                                show_toast(f"Override applied for {field}", "✅")
                                st.session_state.needs_refresh = True
                st.divider()

        with st.expander("🔍 View and Commit Additional Suggestions", expanded=False):
            selected_fields_tab2: List[str] = []
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
                        selected_fields_tab2.append(field)

            if selected_fields_tab2 and st.button("✅ Commit Selected Suggestions"):
                for field in selected_fields_tab2:
                    st.session_state.final_mapping[field] = {
                        "mode": "auto",
                        "value": ai_suggestions[field]["value"]
                    }
                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    status_text.text("Applying selected suggestions...")
                    progress_bar.progress(0.3)
                    generate_all_outputs()
                    progress_bar.progress(1.0)
                    status_text.empty()
                    progress_bar.empty()
                    st.success(f"Committed {len(selected_fields_tab2)} suggestion(s).")
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error applying suggestions: {error_msg}")
                    if claims_df is not None and final_mapping:
                        st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping)
                        st.session_state["transformed_ready"] = True
    else:
        render_empty_state(
            icon="🤖",
            title="No AI Suggestions",
            message="No additional AI mapping suggestions available. All fields may already be mapped or AI confidence is below threshold."
        )

