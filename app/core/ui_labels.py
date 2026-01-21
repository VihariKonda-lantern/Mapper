"""Centralized UI labels that can be customized per domain."""
from typing import Dict, Any, Optional
from core.domain_config import get_domain_config, DomainConfig


class UILabels:
    """Centralized UI labels that adapt to domain configuration."""
    
    def __init__(self, domain_config: Optional[DomainConfig] = None):
        """Initialize UI labels with domain configuration.
        
        Args:
            domain_config: Domain configuration. If None, uses default claims config.
        """
        self.config = domain_config or get_domain_config()
    
    # App-level labels
    @property
    def app_title(self) -> str:
        """Application title."""
        return self.config.app_title
    
    @property
    def app_description(self) -> str:
        """Application description."""
        return self.config.app_description
    
    # File upload labels
    @property
    def source_file_label(self) -> str:
        """Source file upload label."""
        return self.config.source_file_label
    
    @property
    def source_file_help(self) -> str:
        """Source file upload help text."""
        return self.config.source_file_help
    
    @property
    def target_layout_label(self) -> str:
        """Target layout file upload label."""
        return self.config.target_layout_label
    
    @property
    def target_layout_help(self) -> str:
        """Target layout file upload help text."""
        return self.config.target_layout_help
    
    @property
    def lookup_file_label(self) -> str:
        """Lookup file upload label."""
        return self.config.lookup_file_label
    
    @property
    def lookup_file_help(self) -> str:
        """Lookup file upload help text."""
        return self.config.lookup_file_help
    
    # Tab labels
    @property
    def tab_setup(self) -> str:
        """Setup tab label."""
        return "Setup"
    
    @property
    def tab_mapping(self) -> str:
        """Mapping tab label."""
        return "Field Mapping"
    
    @property
    def tab_preview(self) -> str:
        """Preview tab label."""
        return "Preview & Validate"
    
    @property
    def tab_downloads(self) -> str:
        """Downloads tab label."""
        return "Downloads Tab"
    
    @property
    def tab_quality(self) -> str:
        """Data Quality tab label."""
        return "Data Quality"
    
    @property
    def tab_tools(self) -> str:  # Deprecated - tab removed
        """Tools tab label."""
        return "Tools & Analytics"
    
    # Section labels
    @property
    def section_upload_files(self) -> str:
        """Upload files section label."""
        return f"Upload {self.source_file_label}"
    
    @property
    def section_file_preview(self) -> str:
        """File preview section label."""
        return f"{self.source_file_label} Preview"
    
    @property
    def section_mapping_progress(self) -> str:
        """Mapping progress section label."""
        return "Field Mapping Progress"
    
    # Button labels
    @property
    def button_load_template(self) -> str:
        """Load template button label."""
        return "Load Template"
    
    @property
    def button_save_mapping(self) -> str:
        """Save mapping button label."""
        return "Save Mapping"
    
    @property
    def button_view_quality(self) -> str:
        """View quality button label."""
        return "View Quality"
    
    @property
    def button_reset_all(self) -> str:
        """Reset all button label."""
        return "Reset All"
    
    # Status messages
    @property
    def message_no_files_uploaded(self) -> str:
        """Message when no files are uploaded."""
        return f"Please upload {self.source_file_label.lower()} and {self.target_layout_label.lower()} to begin."
    
    @property
    def message_mapping_complete(self) -> str:
        """Message when mapping is complete."""
        return "Mapping saved!"
    
    @property
    def message_no_mapping(self) -> str:
        """Message when no mapping exists."""
        return "No mapping to save. Complete field mapping first."


# Global instance for easy access
_global_labels: Optional[UILabels] = None


def get_ui_labels(domain_config: Optional[DomainConfig] = None) -> UILabels:
    """Get UI labels instance.
    
    Args:
        domain_config: Domain configuration. If None, uses default.
    
    Returns:
        UILabels instance.
    """
    global _global_labels
    if _global_labels is None or domain_config is not None:
        _global_labels = UILabels(domain_config)
    return _global_labels


def set_domain(domain_name: str) -> None:
    """Set the current domain and update UI labels.
    
    Args:
        domain_name: Name of the domain to use.
    """
    from core.domain_config import get_domain_config
    config = get_domain_config(domain_name)
    global _global_labels
    _global_labels = UILabels(config)
