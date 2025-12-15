# --- view_models.py ---
"""View models/controllers for separating UI from business logic."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from core.state_manager import SessionStateManager


@dataclass
class TabViewModel(ABC):
    """Base view model for tab controllers."""
    tab_name: str
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from session state."""
        return SessionStateManager.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set value in session state."""
        SessionStateManager.set(key, value)
    
    def has_state(self, key: str) -> bool:
        """Check if key exists in session state."""
        return SessionStateManager.has(key)
    
    @abstractmethod
    def get_view_data(self) -> Dict[str, Any]:
        """Get data needed for rendering the view."""
        pass
    
    @abstractmethod
    def handle_action(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """Handle user actions."""
        pass


class SetupTabViewModel(TabViewModel):
    """View model for Setup tab."""
    
    def __init__(self):
        super().__init__(tab_name="setup")
    
    def get_view_data(self) -> Dict[str, Any]:
        """Get data for Setup tab view."""
        layout_df = SessionStateManager.get_layout_df()
        claims_df = SessionStateManager.get_claims_df()
        lookup_file_obj = SessionStateManager.get("lookup_file_obj")
        
        # Determine upload order
        upload_order = self.get_state("upload_order", [])
        
        # Check which files are uploaded
        has_layout = SessionStateManager.has("layout_file_obj")
        has_lookup = SessionStateManager.has("lookup_file_obj")
        has_claims = SessionStateManager.has("claims_file_obj")
        
        # File metadata
        layout_metadata = {}
        if has_layout:
            layout_file_obj = SessionStateManager.get("layout_file_obj")
            if layout_file_obj and hasattr(layout_file_obj, "name"):
                layout_metadata = {"filename": layout_file_obj.name}
        
        claims_metadata = {}
        if has_claims and claims_df is not None:
            claims_file_obj = SessionStateManager.get("claims_file_obj")
            if claims_file_obj and hasattr(claims_file_obj, "name"):
                claims_metadata = {
                    "filename": claims_file_obj.name,
                    "rows": len(claims_df),
                    "columns": len(claims_df.columns) if claims_df is not None else 0
                }
        
        lookup_metadata = {}
        if has_lookup:
            if lookup_file_obj and hasattr(lookup_file_obj, "name"):
                msk_codes = self.get_state("msk_codes", set())
                bar_codes = self.get_state("bar_codes", set())
                lookup_metadata = {
                    "filename": lookup_file_obj.name,
                    "msk_count": len(msk_codes),
                    "bar_count": len(bar_codes)
                }
        
        return {
            "layout_df": layout_df,
            "claims_df": claims_df,
            "has_layout": has_layout,
            "has_lookup": has_lookup,
            "has_claims": has_claims,
            "upload_order": upload_order,
            "layout_metadata": layout_metadata,
            "claims_metadata": claims_metadata,
            "lookup_metadata": lookup_metadata
        }
    
    def handle_action(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """Handle Setup tab actions."""
        if action == "log_file_upload":
            file_type = kwargs.get("file_type")
            file_name = kwargs.get("file_name")
            metadata = kwargs.get("metadata", {})
            
            # Track file upload
            try:
                from monitoring.audit_logger import log_event
                from monitoring.monitoring_logging import track_feature_usage
                from ui.user_experience import add_recent_file
                
                if file_type == "layout":
                    log_event("file_upload", f"Layout file loaded: {file_name}")
                    track_feature_usage("file_upload", "layout_file_uploaded", {"file": file_name})
                    self.set_state("last_logged_layout_file", file_name)
                    add_recent_file(file_name, "layout", {})
                
                elif file_type == "claims":
                    row_count = metadata.get("rows", 0)
                    col_count = metadata.get("columns", 0)
                    log_event("file_upload", f"Claims file loaded: {file_name} ({row_count:,} rows, {col_count} columns)")
                    track_feature_usage("file_upload", "claims_file_uploaded", {"file": file_name, "rows": row_count})
                    self.set_state("last_logged_claims_file", file_name)
                    add_recent_file(file_name, "claims", {"rows": row_count, "columns": col_count})
                
                elif file_type == "lookup":
                    msk_count = metadata.get("msk_count", 0)
                    bar_count = metadata.get("bar_count", 0)
                    log_event("file_upload", f"Lookup file loaded: {file_name} (MSK: {msk_count}, BAR: {bar_count})")
                    track_feature_usage("file_upload", "lookup_file_uploaded", {"file": file_name})
                    self.set_state("last_logged_lookup_file", file_name)
                    add_recent_file(file_name, "lookup", {"msk": msk_count, "bar": bar_count})
                
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": f"Unknown action: {action}"}


class MappingTabViewModel(TabViewModel):
    """View model for Mapping tab."""
    
    def __init__(self):
        super().__init__(tab_name="mapping")
    
    def get_view_data(self) -> Dict[str, Any]:
        """Get data for Mapping tab view."""
        layout_df = SessionStateManager.get_layout_df()
        claims_df = SessionStateManager.get_claims_df()
        final_mapping = SessionStateManager.get_final_mapping()
        
        # Calculate required fields
        required_fields = []
        if layout_df is not None:
            cache_key = f"required_fields_{id(layout_df)}"
            if cache_key not in SessionStateManager.get("_cache", {}):
                usage_normalized = layout_df["Usage"].astype(str).str.strip().str.lower()
                required_fields = layout_df[usage_normalized == "mandatory"]["Internal Field"].tolist()
                cache = SessionStateManager.get("_cache", {})
                cache[cache_key] = required_fields
                SessionStateManager.set("_cache", cache)
            else:
                cache = SessionStateManager.get("_cache", {})
                required_fields = cache.get(cache_key, [])
        
        # Calculate mapping progress
        total_required = len(required_fields) if required_fields else 0
        mapped_required = [f for f in required_fields if f in final_mapping and final_mapping[f].get("value")]
        mapped_count = len(mapped_required)
        percent_complete = int((mapped_count / total_required) * 100) if total_required > 0 else 0
        
        return {
            "layout_df": layout_df,
            "claims_df": claims_df,
            "final_mapping": final_mapping,
            "required_fields": required_fields,
            "total_required": total_required,
            "mapped_count": mapped_count,
            "percent_complete": percent_complete,
            "can_proceed": layout_df is not None and claims_df is not None
        }
    
    def handle_action(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """Handle Mapping tab actions."""
        if action == "save_mapping":
            mapping = kwargs.get("mapping")
            if mapping:
                SessionStateManager.set_final_mapping(mapping)
                from core.session_state import save_to_history
                save_to_history(mapping)
                return {"success": True}
            return {"success": False, "error": "No mapping provided"}
        
        elif action == "load_template":
            template_path = kwargs.get("template_path")
            try:
                from advanced_features import load_mapping_template
                template = load_mapping_template(template_path)
                if template:
                    SessionStateManager.set_final_mapping(template)
                    return {"success": True, "mapping": template}
                return {"success": False, "error": "Template not found"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif action == "auto_map":
            layout_df = SessionStateManager.get_layout_df()
            claims_df = SessionStateManager.get_claims_df()
            if layout_df is None or claims_df is None:
                return {"success": False, "error": "Layout and claims files required"}
            
            try:
                from mapping.mapping_engine import get_enhanced_automap
                automap_result = get_enhanced_automap(claims_df, layout_df)
                if automap_result:
                    SessionStateManager.set_final_mapping(automap_result)
                    from core.session_state import save_to_history
                    save_to_history(automap_result)
                    return {"success": True, "mapping": automap_result}
                return {"success": False, "error": "Auto-mapping failed"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif action == "undo":
            from core.session_state import undo_mapping
            result = undo_mapping()
            if result:
                SessionStateManager.set_final_mapping(result)
                return {"success": True, "mapping": result}
            return {"success": False, "error": "Nothing to undo"}
        
        elif action == "redo":
            from core.session_state import redo_mapping
            result = redo_mapping()
            if result:
                SessionStateManager.set_final_mapping(result)
                return {"success": True, "mapping": result}
            return {"success": False, "error": "Nothing to redo"}
        
        return {"success": False, "error": f"Unknown action: {action}"}


class ValidationTabViewModel(TabViewModel):
    """View model for Validation tab."""
    
    def __init__(self):
        super().__init__(tab_name="validation")
    
    def get_view_data(self) -> Dict[str, Any]:
        """Get data for Validation tab view."""
        transformed_df = SessionStateManager.get_transformed_df()
        validation_results = SessionStateManager.get_validation_results()
        final_mapping = SessionStateManager.get_final_mapping()
        
        return {
            "transformed_df": transformed_df,
            "validation_results": validation_results,
            "final_mapping": final_mapping,
            "has_data": transformed_df is not None
        }
    
    def handle_action(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """Handle Validation tab actions."""
        if action == "run_validation":
            transformed_df = SessionStateManager.get_transformed_df()
            if transformed_df is None:
                return {"success": False, "error": "No transformed data available"}
            
            try:
                from validation.validation_engine import run_validations
                from file.layout_loader import get_required_fields
                from core.state_manager import SessionStateManager
                
                layout_df = SessionStateManager.get_layout_df()
                if layout_df is None:
                    return {"success": False, "error": "Layout file required"}
                
                required_fields = get_required_fields(layout_df)
                all_mapped_fields = list(SessionStateManager.get_final_mapping().keys())
                
                results = run_validations(transformed_df, required_fields, all_mapped_fields)
                SessionStateManager.set_validation_results(results)
                return {"success": True, "results": results}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif action == "compare_validations":
            validation_id1 = kwargs.get("validation_id1")
            validation_id2 = kwargs.get("validation_id2")
            # Implementation for comparison
            return {"success": False, "error": "Not yet implemented"}
        
        return {"success": False, "error": f"Unknown action: {action}"}


# Factory function to get view models
def get_view_model(tab_name: str) -> Optional[TabViewModel]:
    """Get view model for a tab."""
    view_models = {
        "setup": SetupTabViewModel,
        "mapping": MappingTabViewModel,
        "validation": ValidationTabViewModel,
    }
    
    view_model_class = view_models.get(tab_name.lower())
    if view_model_class:
        return view_model_class()
    return None

