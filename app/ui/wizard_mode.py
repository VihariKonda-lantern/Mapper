# --- wizard_mode.py ---
"""Wizard mode for first-time users with step-by-step guidance."""
import streamlit as st
from typing import Any, Optional, Callable, Dict, List
from core.state_manager import SessionStateManager

st: Any = st


class WizardMode:
    """Step-by-step wizard for first-time users."""
    
    STEPS = [
        {
            "id": "setup",
            "title": "Step 1: Upload Files",
            "description": "Upload your Layout, Lookup, and Claims files",
            "tab": "Setup",
            "check_complete": lambda: (
                SessionStateManager.get_layout_df() is not None and
                SessionStateManager.get_claims_df() is not None
            )
        },
        {
            "id": "mapping",
            "title": "Step 2: Map Fields",
            "description": "Map your source columns to required fields",
            "tab": "Field Mapping",
            "check_complete": lambda: (
                SessionStateManager.get_final_mapping() is not None and
                len(SessionStateManager.get_final_mapping()) > 0
            )
        },
        {
            "id": "validation",
            "title": "Step 3: Preview & Validate",
            "description": "Review validation results and data quality",
            "tab": "Preview & Validate",
            "check_complete": lambda: (
                SessionStateManager.get_transformed_df() is not None
            )
        },
        {
            "id": "download",
            "title": "Step 4: Download Results",
            "description": "Download your processed files",
            "tab": "Downloads Tab",
            "check_complete": lambda: (
                SessionStateManager.get_transformed_df() is not None
            )
        }
    ]
    
    @classmethod
    def should_show_wizard(cls) -> bool:
        """Check if wizard should be shown."""
        if "wizard_enabled" not in st.session_state:
            st.session_state.wizard_enabled = True
        
        if "wizard_completed" not in st.session_state:
            st.session_state.wizard_completed = False
        
        return st.session_state.wizard_enabled and not st.session_state.wizard_completed
    
    @classmethod
    def get_current_step(cls) -> int:
        """Get current wizard step based on progress."""
        if "wizard_current_step" not in st.session_state:
            st.session_state.wizard_current_step = 0
        
        # Check which steps are complete
        for i, step in enumerate(cls.STEPS):
            if not step["check_complete"]():
                st.session_state.wizard_current_step = i
                return i
        
        # All steps complete
        st.session_state.wizard_current_step = len(cls.STEPS)
        return len(cls.STEPS)
    
    @classmethod
    def render_wizard_header(cls) -> None:
        """Render wizard header with progress."""
        if not cls.should_show_wizard():
            return
        
        current_step = cls.get_current_step()
        total_steps = len(cls.STEPS)
        
        st.markdown("### 🧙 Wizard Mode - Step-by-Step Guide")
        st.markdown(f"**Progress: {current_step}/{total_steps} steps completed**")
        
        # Progress bar
        progress = int((current_step / total_steps) * 100)
        st.progress(progress)
        
        # Show current step info
        if current_step < len(cls.STEPS):
            step_info = cls.STEPS[current_step]
            st.info(f"**Current Step:** {step_info['title']}\n\n{step_info['description']}")
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if current_step > 0:
                    if st.button("← Previous Step", key="wizard_prev"):
                        st.session_state.wizard_current_step = current_step - 1
                        st.session_state.active_tab = cls.STEPS[current_step - 1]["tab"]
                        st.rerun()
            
            with col2:
                if current_step < len(cls.STEPS) - 1:
                    if st.button("Next Step →", key="wizard_next"):
                        st.session_state.wizard_current_step = current_step + 1
                        st.session_state.active_tab = cls.STEPS[current_step + 1]["tab"]
                        st.rerun()
            
            with col3:
                if st.button("Exit Wizard Mode", key="wizard_exit"):
                    st.session_state.wizard_enabled = False
                    st.session_state.wizard_completed = True
                    st.rerun()
        else:
            st.success("🎉 Congratulations! You've completed all steps!")
            if st.button("Exit Wizard Mode", key="wizard_complete_exit"):
                st.session_state.wizard_enabled = False
                st.session_state.wizard_completed = True
                st.rerun()
    
    @classmethod
    def render_step_guidance(cls, step_id: str) -> None:
        """Render guidance for a specific step."""
        step = next((s for s in cls.STEPS if s["id"] == step_id), None)
        if not step:
            return
        
        with st.expander(f"💡 {step['title']} - Tips & Guidance", expanded=True):
            if step_id == "setup":
                st.markdown("""
                **Upload Files:**
                1. **Layout File**: This defines the structure of your output file
                   - Must be an Excel (.xlsx) file
                   - Contains field definitions and requirements
                
                2. **Lookup File**: Contains reference data for validation
                   - Must be an Excel (.xlsx) file
                   - Used for diagnosis code validation
                
                3. **Claims File**: Your source data to be processed
                   - Supports CSV, TXT, TSV, XLSX, JSON, Parquet formats
                   - Can have headers or be headerless (with external header file)
                
                **Tips:**
                - Ensure all files are properly formatted
                - Check file sizes (max 500MB recommended)
                - Verify file encoding is correct
                """)
            
            elif step_id == "mapping":
                st.markdown("""
                **Map Fields:**
                1. Review AI suggestions (≥80% confidence auto-applied)
                2. Manually map remaining required fields
                3. Use search to quickly find fields
                4. Check mapping progress indicator
                
                **Tips:**
                - AI suggestions are based on field name similarity
                - You can override any auto-mapped field
                - Save mapping templates for future use
                - Use undo/redo (Ctrl+Z/Ctrl+Y) if needed
                """)
            
            elif step_id == "validation":
                st.markdown("""
                **Preview & Validate:**
                1. Review validation results
                2. Check data quality scores
                3. Address any errors or warnings
                4. Review transformed data preview
                
                **Tips:**
                - Green = Pass, Red = Error, Yellow = Warning
                - Click on validation results for details
                - Custom validation rules can be added
                - Data quality score should be ≥85%
                """)
            
            elif step_id == "download":
                st.markdown("""
                **Download Results:**
                1. Choose output format
                2. Select files to download
                3. Download individual files or ZIP archive
                4. Save mapping template for reuse
                
                **Tips:**
                - Anonymized file removes sensitive data
                - Mapping table shows all mappings
                - ZIP contains all outputs together
                - Templates can be shared with team
                """)
    
    @classmethod
    def check_step_completion(cls, step_id: str) -> bool:
        """Check if a specific step is complete."""
        step = next((s for s in cls.STEPS if s["id"] == step_id), None)
        if not step:
            return False
        return step["check_complete"]()


def render_quick_actions() -> None:
    """Render quick action buttons for common tasks."""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📁 Load Template", key="quick_load_template", use_container_width=True):
            st.session_state.active_tab = "Field Mapping"
            st.info("💡 Go to Field Mapping tab to load a saved template")
    
    with col2:
        if st.button("💾 Save Mapping", key="quick_save_mapping", use_container_width=True):
            mapping = SessionStateManager.get_final_mapping()
            if mapping:
                from ui.ui_improvements import show_toast
                show_toast("Mapping saved!", "💾")
            else:
                st.warning("No mapping to save. Complete field mapping first.")
    
    with col3:
        if st.button("📊 View Quality", key="quick_view_quality", use_container_width=True):
            st.session_state.active_tab = "Data Quality"
            st.rerun()
    
    with col4:
        if st.button("🔄 Reset All", key="quick_reset", use_container_width=True):
            from ui.ui_improvements import show_confirmation_dialog
            if show_confirmation_dialog(
                "Reset All Data",
                "Are you sure you want to reset all data? This will clear all uploaded files and mappings.",
                confirm_label="Yes, Reset",
                cancel_label="Cancel",
                key="reset_confirm"
            ):
                # Clear session state
                for key in list(st.session_state.keys()):
                    if key not in ["wizard_enabled", "wizard_completed", "wizard_current_step"]:
                        del st.session_state[key]
                st.session_state.active_tab = "Setup"
                from ui.ui_improvements import show_toast
                show_toast("All data reset", "🔄")
                st.rerun()

