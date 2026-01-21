# --- tab_mapping.py ---
"""Field Mapping tab handler."""
import streamlit as st
import pandas as pd
from typing import Any, List, Dict, Optional
import json
import os
import time
from core.state_manager import SessionStateManager
from core.config_loader import AI_CONFIDENCE_THRESHOLD
from utils.improvements_utils import render_empty_state, get_user_friendly_error, DEBOUNCE_DELAY_SECONDS
from ui.ui_components import show_toast, show_confirmation_dialog, show_undo_redo_feedback
from ui.mapping_ui import render_field_mapping_tab
from mapping.manual_llm_workflow import generate_batch_payload, parse_llm_response
from ui.ui_components import render_progress_bar
from core.state_manager import initialize_undo_redo, save_to_history, undo_mapping, redo_mapping
from data.transformer import transform_claims_data
from data.output_generator import generate_all_outputs
# Testing QA removed - optional feature
from mapping.mapping_engine import get_enhanced_automap
from mapping.mapping_enhancements import (
    get_mapping_confidence_score,
    validate_mapping_before_processing,
    get_mapping_version,
    export_mapping_template_for_sharing,
    import_mapping_template_from_shareable
)
from advanced_features import save_mapping_template, load_mapping_template, list_saved_templates
from data.layout_loader import get_required_fields
from utils.audit_logger import log_event

st: Any = st


def render_mapping_tab() -> None:
    """Render the Field Mapping tab content."""
    # Inject tight spacing CSS
    from ui.design_system import inject_tight_spacing_css
    inject_tight_spacing_css()
    
    # Cache frequently accessed session state values
    layout_df = SessionStateManager.get_layout_df()
    claims_df = SessionStateManager.get_claims_df()
    final_mapping = SessionStateManager.get_final_mapping()

    if layout_df is None or claims_df is None:
        render_empty_state(
            icon="📁",
            title="Files Required",
            message="Please start from the Setup tab to upload both layout and claims files before mapping.",
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

    # --- Manual LLM Workflow Section (outside form to allow buttons) ---
    with st.expander("🤖 Manual LLM Mapping (Copy & Paste Workflow)", expanded=False):
        st.markdown("""
        **How to use:**
        1. Click "Generate Payload" to create the JSON payload
        2. Copy the generated payload
        3. Paste it into your Copilot Studio agent
        4. Copy the response from Copilot Studio
        5. Paste it in the response box below and click "Apply Mappings"
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            generate_minimal = st.checkbox("Generate minimal payload (smaller size)", key="minimal_payload_check", value=True, help="Reduces payload size by limiting sample values and removing optional fields")
            st.caption("ℹ️ Only mandatory fields will be included in the payload")
            if st.button("📋 Generate Payload", key="generate_payload_btn"):
                try:
                    existing_mappings = {
                        field: info.get("value") 
                        for field, info in final_mapping.items()
                        if info.get("value")
                    }
                    minimal_mode = st.session_state.get("minimal_payload_check", True)
                    payload = generate_batch_payload(layout_df, claims_df, existing_mappings, minimal=minimal_mode)
                    
                    # Count mandatory fields included
                    mandatory_count = len(payload.get("internal_fields", []))
                    total_cols = len(payload.get("source_columns", []))
                    
                    payload_json = json.dumps(payload, indent=2)
                    payload_size_kb = len(payload_json.encode('utf-8')) / 1024
                    st.session_state.llm_payload = payload_json
                    st.session_state.llm_payload_size = payload_size_kb
                    st.success(f"✅ Payload generated! Size: {payload_size_kb:.1f} KB ({mandatory_count} mandatory fields, {total_cols} source columns). Copy it from the box below.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating payload: {e}")
        
        with col2:
            if st.button("🔄 Clear Payload", key="clear_payload_btn"):
                if "llm_payload" in st.session_state:
                    del st.session_state.llm_payload
                if "llm_response_text" in st.session_state:
                    del st.session_state.llm_response_text
                st.success("Cleared!")
                st.rerun()
        
        # Show payload if generated (collapsible using details/summary HTML)
        if "llm_payload" in st.session_state:
            st.markdown("---")
            payload_size = st.session_state.get("llm_payload_size", 0)
            size_info = f" ({payload_size:.1f} KB)" if payload_size > 0 else ""
            st.markdown(f"""
            <details open style="margin: 0.5rem 0;">
                <summary style="cursor: pointer; font-weight: 600; padding: 0.5rem 0; user-select: none; font-size: 14px;">
                    📋 Generated Payload{size_info} (Click to expand/collapse)
                </summary>
            </details>
            """, unsafe_allow_html=True)
            
            # Show warning if payload is too large
            if payload_size > 50:  # More than 50 KB
                st.warning(f"⚠️ Payload size is {payload_size:.1f} KB. If Copilot Studio has paste limits, try reducing sample values or splitting the request.")
            
            # Copy button and payload display
            col_copy, col_info = st.columns([1, 4])
            with col_copy:
                copy_clicked = st.button("📋 Copy Payload", key="copy_payload_btn", use_container_width=True)
                if copy_clicked:
                    st.session_state.copy_payload_clicked = True
                    st.rerun()
            
            with col_info:
                st.caption("💡 Click 'Copy Payload' button or select all text in the box below (Ctrl/Cmd+A) and copy (Ctrl/Cmd+C)")
            
            # Display payload in a text area for easy selection and copying
            st.text_area(
                "Payload JSON (Select all and copy)",
                value=st.session_state.llm_payload,
                height=300,
                key="payload_display_textarea",
                help="Select all text (Ctrl/Cmd+A) and copy (Ctrl/Cmd+C). The copy button above also works.",
                label_visibility="visible"
            )
            
            # Handle copy button click with JavaScript
            if st.session_state.get("copy_payload_clicked", False):
                payload_escaped = json.dumps(st.session_state.llm_payload)
                st.markdown(
                    f"""
                    <script>
                        (function() {{
                            const text = {payload_escaped};
                            const textarea = document.createElement('textarea');
                            textarea.value = text;
                            textarea.style.position = 'fixed';
                            textarea.style.opacity = '0';
                            document.body.appendChild(textarea);
                            textarea.select();
                            textarea.setSelectionRange(0, 99999); // For mobile devices
                            
                            try {{
                                const successful = document.execCommand('copy');
                                if (successful) {{
                                    console.log('Payload copied to clipboard');
                                }} else {{
                                    // Fallback to modern API
                                    navigator.clipboard.writeText(text).then(function() {{
                                        console.log('Payload copied via clipboard API');
                                    }}).catch(function(err) {{
                                        console.error('Failed to copy: ', err);
                                    }});
                                }}
                            }} catch (err) {{
                                // Try modern API
                                navigator.clipboard.writeText(text).then(function() {{
                                    console.log('Payload copied via clipboard API');
                                }}).catch(function(err) {{
                                    console.error('Failed to copy: ', err);
                                }});
                            }}
                            
                            document.body.removeChild(textarea);
                        }})();
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                st.session_state.copy_payload_clicked = False
                st.success("✅ Payload copied to clipboard!")
        
        st.divider()
        
        # Response input
        st.markdown("**Paste Copilot Studio Response:**")
        response_text = st.text_area(
            "LLM Response",
            value=st.session_state.get("llm_response_text", ""),
            height=200,
            key="llm_response_text",
            placeholder="Paste the JSON response from Copilot Studio here...",
            help="Paste the complete response from your Copilot Studio agent"
        )
        
        if st.button("✅ Apply Mappings", key="apply_llm_mappings_btn", type="primary"):
            if not response_text.strip():
                st.warning("Please paste the response from Copilot Studio first.")
            else:
                try:
                    # Parse the response
                    parsed_mappings = parse_llm_response(response_text)
                    
                    if not parsed_mappings:
                        st.warning("No mappings found in the response. Please check the format.")
                    else:
                        # Apply mappings to final_mapping
                        if "final_mapping" not in st.session_state:
                            st.session_state.final_mapping = {}
                        
                        applied_count = 0
                        for field, mapping_info in parsed_mappings.items():
                            column = mapping_info.get("value")
                            if column and column in claims_df.columns:
                                st.session_state.final_mapping[field] = {
                                    "mode": "llm_manual",
                                    "value": column,
                                    "confidence": mapping_info.get("confidence", 1.0),
                                    "source": "llm"
                                }
                                applied_count += 1
                        
                        # Clear the response text after successful application
                        st.session_state.llm_response_text = ""
                        
                        # Refresh auto-mapping to reflect new mappings
                        if "auto_mapping" in st.session_state:
                            del st.session_state.auto_mapping
                        
                        st.success(f"✅ Applied {applied_count} mapping(s) from LLM response!")
                        st.rerun()
                        
                except ValueError as e:
                    st.error(f"Error parsing response: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
    
    # --- Main Mapping Section ---
    st.markdown("""
        <div style='margin-top: 0.5rem; margin-bottom: 0.125rem;'>
            <h4 style='margin: 0; padding: 0;'>Field Mapping</h4>
        </div>
    """, unsafe_allow_html=True)
    
    # Render mapping UI (no form wrapper - mappings update automatically)
    render_field_mapping_tab()
    
    # Auto-save mappings and generate outputs when mappings change
    current_mapping = SessionStateManager.get_final_mapping()
    if current_mapping:
        # Set mappings_ready flag
        st.session_state["mappings_ready"] = True
        
        # Save to history (debounced to avoid too many saves)
        mapping_hash = str(hash(str(current_mapping)))
        last_saved_hash = st.session_state.get("last_saved_mapping_hash")
        if last_saved_hash != mapping_hash:
            save_to_history(current_mapping)
            st.session_state.last_saved_mapping_hash = mapping_hash
            
            # Log event
            manual_mapped_count = len([f for f in current_mapping.keys() 
                                     if f in current_mapping and current_mapping[f].get("value") and current_mapping[f].get("mode") == "manual"])
            if manual_mapped_count > 0:
                try:
                    log_event("mapping", f"Field mappings updated ({manual_mapped_count} manual fields mapped)")
                except NameError:
                    pass

    # --- Test Mapping Section (silent, no UI) ---
    if st.session_state.get("mappings_ready") and current_mapping:
        mapping_hash = str(hash(str(final_mapping)))
        last_hash = st.session_state.get("last_mapping_hash")
        if last_hash != mapping_hash or not st.session_state.get("unit_test_results"):
            # Testing QA removed - optional feature
            st.session_state.last_mapping_hash = mapping_hash

