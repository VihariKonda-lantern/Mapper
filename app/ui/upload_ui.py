# --- upload_ui.py ---
"""Upload-related UI functions."""
import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
import io
import os
import gzip
from typing import Any, List, Dict, Set, Union, cast, Tuple

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]

from utils.cache_manager import load_layout_cached, load_lookups_cached
from data.file_handler import (
    read_claims_with_header_option,
    detect_delimiter,
    has_header,
    is_fixed_width,
    infer_fixed_width_positions,
    parse_header_specification_file,
)
from data.upload_handlers import capture_claims_file_metadata

# Import improvement utilities
try:
    from utils.improvements_utils import (
        validate_file_upload,
        get_user_friendly_error,
        show_progress_with_callback,
        render_empty_state,
        compress_dataframe,
        MAX_FILE_SIZE_MB,
    )
    from ui.ui_components import (
        render_file_preview,
        show_toast,
    )
except ImportError:
    # Fallback if modules not available
    def validate_file_upload(file_obj: Any, max_size_mb: int = 500) -> Tuple[bool, Any]:
        return True, None
    def get_user_friendly_error(error: Exception) -> str:
        return str(error)
    def show_progress_with_callback(total: int, callback: Any, *args: Any, **kwargs: Any) -> Any:
        return callback(*args, **kwargs)
    def render_empty_state(*args: Any, **kwargs: Any) -> None:
        pass
    def compress_dataframe(df: Any) -> Any:
        return df
    def render_file_preview(*args: Any, **kwargs: Any) -> None:
        pass
    def show_toast(message: str, icon: str = "✅") -> None:
        st.success(message)
    MAX_FILE_SIZE_MB = 500


def render_lookup_summary_section():
    """Preview summary for diagnosis lookup codes.

    Dynamically reads all code sets from session state and displays counts.
    Automatically detects all code categories (MSK, BAR, and any future categories).
    """
    # Dynamically find all code categories in session_state (anything ending with "_codes")
    code_categories: Dict[str, Union[Set[str], List[str]]] = {}
    for key in st.session_state.keys():
        if key.endswith("_codes") and isinstance(st.session_state[key], (set, list)):
            category_name = key.replace("_codes", "").upper()
            codes_value = st.session_state[key]
            if isinstance(codes_value, (set, list)):
                code_categories[category_name] = codes_value  # type: ignore[assignment]
    
    if code_categories:
        st.markdown("#### Diagnosis Lookup Summary")
        
        # Display total code categories count
        total_categories = len(code_categories)
        st.markdown(f"**Total Code Categories:** {total_categories}", unsafe_allow_html=True)
        
        # Display counts for each category dynamically
        for category_name, codes in sorted(code_categories.items()):
            codes_len = len(codes) if codes else 0
            st.markdown(f"**{category_name} Codes Loaded:** {codes_len}", unsafe_allow_html=True)

        # Create expanders for each category dynamically
        for category_name, codes in sorted(code_categories.items()):
            with st.expander(f"View Sample {category_name} Codes", expanded=False):
                code_list = list(codes) if isinstance(codes, set) else codes
                st.write(code_list[:10])  # type: ignore[no-untyped-call]
    elif st.session_state.get("lookup_upload_attempted", False):
        # Only show info if user has attempted to upload a file
        st.info("Upload a valid diagnosis lookup file to preview codes.")


def render_upload_and_claims_preview():
    """
    Upload Section for Layout, Lookup, Source, and Headerless detection.
    Allows proper external header upload if needed.
    """
    from core.ui_labels import get_ui_labels
    ui_labels = get_ui_labels()
    st.markdown("""
        <div style='margin-bottom: 0.5rem;'>
            <h2 style='color: #111827; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.125rem; letter-spacing: -0.025em;'>Step 1: Upload Files and Confirm {}</h2>
        </div>
    """.format(ui_labels.source_file_label), unsafe_allow_html=True)

    # Check if header file uploader should be shown (only when headerless file detected)
    show_header_uploader = False
    if "detected_has_header" in st.session_state:
        # Show uploader if file was detected as headerless
        if st.session_state.detected_has_header is False:
            show_header_uploader = True
        # Also show if user already uploaded a header file (to allow changes)
        if st.session_state.get("header_file_obj") is not None:
            show_header_uploader = True
    
    # --- All Upload Blocks Side by Side (Centered and Reduced Width) ---
    # Wrap in a centered container with reduced width (70% of original)
    st.markdown('<div class="upload-columns-container">', unsafe_allow_html=True)
    
    # Always create columns based on whether header uploader is needed
    col4 = None  # Initialize to avoid unbound error
    if show_header_uploader:
        # 4 columns: Layout, Lookup, Header, Claims - equal widths with gap
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="large")
    else:
        # 3 columns: Layout, Lookup, Claims - equal widths with gap
        col1, col2, col3 = st.columns([1, 1, 1], gap="large")
    
    # Initialize variables
    layout_file = None
    lookup_file = None
    header_file = None
    claims_file = None
    
    # Layout File Upload (always in col1)
    with col1:
        layout_file = st.file_uploader(
            f"📄 Upload {ui_labels.target_layout_label}", 
            type=["csv", "txt", "tsv", "xlsx", "xls", "json", "parquet"], 
            key="layout_file", 
            help=f"{ui_labels.target_layout_help}. Supports: CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET. Drag and drop or click to upload."
        )
        if layout_file:
            # Validate file
            is_valid, error_msg = validate_file_upload(layout_file, MAX_FILE_SIZE_MB)
            if not is_valid:
                st.error(error_msg)
            else:
                try:
                    st.session_state.layout_upload_attempted = True
                    with st.spinner("Loading layout file..."):
                        layout_df = load_layout_cached(layout_file)
                        st.session_state.layout_df = layout_df
                    st.success("✅ **Layout file loaded successfully!**")
                    # Track upload order if this is a new file
                    if "layout_file_obj" not in st.session_state or st.session_state.layout_file_obj.name != layout_file.name:
                        if "upload_order" not in st.session_state:
                            st.session_state.upload_order = []
                        upload_order_list = cast(List[str], st.session_state.upload_order)
                        if "layout" not in upload_order_list:
                            upload_order_list.append("layout")
                    st.session_state.layout_file_obj = layout_file
                except Exception as e:
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error loading layout file: {error_msg}")
                    st.session_state.layout_df = None
        elif layout_file is None and "layout_upload_attempted" not in st.session_state:
            # Track that user has interacted with uploader (even if no file selected)
            pass
        elif layout_file is None and "layout" in st.session_state.get("upload_order", []):
            # File was removed, remove from order
            if "upload_order" in st.session_state:
                upload_order_list = cast(List[str], st.session_state.upload_order)
                if "layout" in upload_order_list:
                    upload_order_list.remove("layout")

    # Lookup File Upload (always in col2)
    with col2:
        lookup_file = st.file_uploader(
            f"Upload {ui_labels.lookup_file_label}", 
            type=["csv", "txt", "tsv", "xlsx", "xls", "json", "parquet"], 
            key="lookup_file", 
            help=f"{ui_labels.lookup_file_help}. Supports: CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET. Drag and drop or click to upload."
        )
        if lookup_file:
            # Validate file
            is_valid, error_msg = validate_file_upload(lookup_file, MAX_FILE_SIZE_MB)
            if not is_valid:
                st.error(error_msg)
            else:
                try:
                    st.session_state.lookup_upload_attempted = True
                    with st.spinner("Loading lookup file..."):
                        msk_codes, bar_codes = load_lookups_cached(lookup_file)
                        st.session_state.msk_codes = msk_codes
                        st.session_state.bar_codes = bar_codes
                    st.success("✅ **Lookup file loaded successfully!**")
                    # Track upload order if this is a new file
                    if "lookup_file_obj" not in st.session_state or st.session_state.lookup_file_obj.name != lookup_file.name:
                        if "upload_order" not in st.session_state:
                            st.session_state.upload_order = []
                        upload_order_list = cast(List[str], st.session_state.upload_order)
                        if "lookup" not in upload_order_list:
                            upload_order_list.append("lookup")
                    st.session_state.lookup_file_obj = lookup_file
                except Exception as e:
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error loading lookup file: {error_msg}")
                    st.session_state.msk_codes = set()
                    st.session_state.bar_codes = set()
        elif lookup_file is None and "lookup_upload_attempted" not in st.session_state:
            # Track that user has interacted with uploader (even if no file selected)
            pass
        elif lookup_file is None and "lookup" in st.session_state.get("upload_order", []):
            # File was removed, remove from order
            if "upload_order" in st.session_state:
                upload_order_list = cast(List[str], st.session_state.upload_order)
                if "lookup" in upload_order_list:
                    upload_order_list.remove("lookup")

    # Header File Upload (only in col3 when needed)
    if show_header_uploader:
        with col3:
            header_file = st.file_uploader(
                "Upload Header File (Required)", 
                type=["csv", "txt", "tsv", "xlsx", "xls"], 
                key="external_header_upload", 
                help="Required for files without headers. Supports: (1) Simple format: one column (vertical) or one row (horizontal) with column names only. (2) Specification format: file with Column Name, Start Position, End Position, and Size columns (for fixed-width files)."
            )
            st.session_state.header_file_obj = header_file if header_file else None
        # Source File Upload (in col4 when header is shown)
        if col4 is not None:
            with col4:
                claims_file = st.file_uploader(
                    f"Upload {ui_labels.source_file_label}", 
                    type=["csv", "txt", "tsv", "xlsx", "xls", "json", "parquet", "gz"],
                    key="claims_file_upload",
                    help=f"{ui_labels.source_file_help}. Supports: CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET, GZ. Drag and drop or click to upload."
                )
                # Handle source file upload (inside column context)
                if claims_file:
                    # Validate file
                    is_valid, error_msg = validate_file_upload(claims_file, MAX_FILE_SIZE_MB)
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        st.session_state.claims_upload_attempted = True
                    # Reset session if file changed
                    if "claims_file_obj" in st.session_state and st.session_state.claims_file_obj.name != claims_file.name:
                        st.session_state.pop("claims_df", None)
                        st.session_state.pop("final_mapping", None)
                        st.session_state.pop("auto_mapping", None)
                        st.session_state.pop("auto_mapped_fields", None)
                        # Clear preprocessing steps for new file
                        try:
                            from data.preprocessing_tracker import clear_preprocessing_steps
                            clear_preprocessing_steps()
                        except ImportError:
                            pass
                        st.session_state.pop("preprocessing_skiprows", None)
                    # Track upload order if this is a new file
                        if "claims_file_obj" not in st.session_state or st.session_state.claims_file_obj.name != claims_file.name:
                            if "upload_order" not in st.session_state:
                                st.session_state.upload_order = []
                            upload_order_list = cast(List[str], st.session_state.upload_order)
                            if "claims" not in upload_order_list:
                                upload_order_list.append("claims")
                        st.session_state.claims_file_obj = claims_file
                        # Show success message - check if file is already loaded or just uploaded
                        claims_df_loaded = st.session_state.get("claims_df")
                        last_loaded = st.session_state.get("last_loaded_file")
                        if claims_df_loaded is not None and last_loaded == claims_file.name:
                            # File is already loaded
                            st.success(f"✅ **{ui_labels.source_file_label} loaded successfully!**")
                        else:
                            # File just uploaded, processing will happen
                            st.success(f"✅ **{ui_labels.source_file_label} uploaded successfully!** Processing...")
                elif claims_file is None and "claims_upload_attempted" not in st.session_state:
                    # Track that user has interacted with uploader (even if no file selected)
                    pass
                elif claims_file is None and "claims" in st.session_state.get("upload_order", []):
                    # File was removed, remove from order
                    if "upload_order" in st.session_state:
                        upload_order_list = cast(List[str], st.session_state.upload_order)
                        if "claims" in upload_order_list:
                            upload_order_list.remove("claims")
        else:
            claims_file = None
    else:
        # Source File Upload (in col3 when header is not shown)
        with col3:
            claims_file = st.file_uploader(
                f"📊 Upload {ui_labels.source_file_label}", 
                type=["csv", "txt", "tsv", "xlsx", "xls", "json", "parquet", "gz"],
                key="claims_file_upload",
                help=f"{ui_labels.source_file_help}. Supports: CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET. Drag and drop or click to upload."
            )
            # Handle claims file upload (inside column context)
            if claims_file:
                # Validate file
                is_valid, error_msg = validate_file_upload(claims_file, MAX_FILE_SIZE_MB)
                if not is_valid:
                    st.error(error_msg)
                else:
                    st.session_state.claims_upload_attempted = True
                    # Reset session if file changed
                    if "claims_file_obj" in st.session_state and st.session_state.claims_file_obj.name != claims_file.name:
                        st.session_state.pop("claims_df", None)
                        st.session_state.pop("final_mapping", None)
                        st.session_state.pop("auto_mapping", None)
                        st.session_state.pop("auto_mapped_fields", None)
                        # Clear preprocessing steps for new file
                        try:
                            from data.preprocessing_tracker import clear_preprocessing_steps
                            clear_preprocessing_steps()
                        except ImportError:
                            pass
                        st.session_state.pop("preprocessing_skiprows", None)
                    # Track upload order if this is a new file
                    if "claims_file_obj" not in st.session_state or st.session_state.claims_file_obj.name != claims_file.name:
                        if "upload_order" not in st.session_state:
                            st.session_state.upload_order = []
                        upload_order_list = cast(List[str], st.session_state.upload_order)
                        if "claims" not in upload_order_list:
                            upload_order_list.append("claims")
                    st.session_state.claims_file_obj = claims_file
                    # Show success message - check if file is already loaded or just uploaded
                    claims_df_loaded = st.session_state.get("claims_df")
                    last_loaded = st.session_state.get("last_loaded_file")
                    if claims_df_loaded is not None and last_loaded == claims_file.name:
                        # File is already loaded
                        st.success(f"✅ **{ui_labels.source_file_label} loaded successfully!**")
                    else:
                        # File just uploaded, processing will happen
                        st.success(f"✅ **{ui_labels.source_file_label} uploaded successfully!** Processing...")
            elif claims_file is None and "claims_upload_attempted" not in st.session_state:
                # Track that user has interacted with uploader (even if no file selected)
                pass
            elif claims_file is None and "claims" in st.session_state.get("upload_order", []):
                # File was removed, remove from order
                if "upload_order" in st.session_state:
                    upload_order_list = cast(List[str], st.session_state.upload_order)
                    if "claims" in upload_order_list:
                        upload_order_list.remove("claims")
    
    # Close the centered container
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Automatic File Loading ---
    # Check if all files are uploaded and claims_df hasn't been loaded yet
    all_files_uploaded = (
        "layout_file_obj" in st.session_state and 
        "lookup_file_obj" in st.session_state and 
        "claims_file_obj" in st.session_state
    )
    
    # Check if we need to load (either not loaded yet, or file changed)
    claims_file = st.session_state.get("claims_file_obj")
    last_loaded = st.session_state.get("last_loaded_file")
    claims_df_loaded = st.session_state.get("claims_df")
    needs_loading = (
        all_files_uploaded and 
        claims_file is not None and
        (claims_df_loaded is None or 
         last_loaded != claims_file.name)
    )
    
    if needs_loading:
        try:
            # Validate file before processing
            claims_file = st.session_state.get("claims_file_obj")
            if claims_file:
                is_valid, error_msg = validate_file_upload(claims_file, MAX_FILE_SIZE_MB)
                if not is_valid:
                    st.error(error_msg)
                    st.stop()
            
            # Show enhanced progress indicator
            from ui.progress_indicators import ProgressIndicator
            
            # Memory profiling (optional feature - not available, using dummy implementation)
            from contextlib import contextmanager
            
            @contextmanager
            def track_memory_usage(operation_name: str):
                """Dummy context manager for memory tracking (performance module not available)."""
                yield {"available": False}
            
            progress = ProgressIndicator(
                total_steps=100,
                message="Processing file...",
                show_time=True
            )
            
            with track_memory_usage("File Upload") as memory_track:
                progress.update(10, "Detecting file format...")
                
                # --- Intelligent File Format Detection ---
                claims_file.seek(0)
                ext = claims_file.name.lower()
                
                # Handle .gz decompression if user selected it in preprocessing options
                needs_decompression = ext.endswith('.gz') and st.session_state.get("preprocessing_type") == "Unzip .gz File"
                if needs_decompression:
                    progress.update(15, "Decompressing .gz file...")
                    try:
                        claims_file.seek(0)
                        decompressed_content = gzip.decompress(claims_file.read())
                        claims_file = io.BytesIO(decompressed_content)
                        # Update extension to remove .gz
                        ext = ext[:-3]  # Remove .gz extension
                        # Track decompression step
                        try:
                            from data.preprocessing_tracker import track_preprocessing_step
                            track_preprocessing_step("unzip_gz", {"compressed": True})
                        except ImportError:
                            pass
                    except Exception as e:
                        st.error(f"Error decompressing .gz file: {str(e)}")
                        st.stop()
                
                progress.update(20, "Analyzing file structure...")
            
                # Detect if file is fixed-width
                is_fw = False
                colspecs = None
                delimiter = None
                header_spec_names = None
                header_spec_colspecs = None
                
                if ext.endswith((".csv", ".txt", ".tsv")):
                    claims_file.seek(0)
                    file_content = claims_file.read()
                    claims_file.seek(0)
                    file_bytes = io.BytesIO(file_content)
                    
                    # Check if fixed-width
                    is_fw = is_fixed_width(file_bytes)
                    
                    if is_fw:
                        st.info("📏 **Detected:** Fixed-width file format")
                        # Check if header file is a specification file first (before auto-detection)
                        header_file = st.session_state.get("header_file_obj")
                        
                        if header_file:
                            # Try to parse as header specification file
                            try:
                                header_file.seek(0)
                                header_bytes = header_file.read()
                                header_file.seek(0)
                                header_ext = os.path.splitext(header_file.name)[-1].lower()
                                header_spec_names, header_spec_colspecs = parse_header_specification_file(header_bytes, header_ext)
                                if header_spec_colspecs:
                                    st.success(f"✅ **Header Specification File Detected:** Found {len(header_spec_names)} columns with position information")
                                    colspecs = header_spec_colspecs
                                    st.info("📏 Using column positions from header specification file")
                            except (ValueError, Exception):
                                # Not a header spec file, will try auto-detection
                                pass
                        
                        # If no header spec file or parsing failed, try auto-detection
                        if not colspecs:
                            colspecs = infer_fixed_width_positions(file_bytes)
                            if colspecs:
                                st.success(f"✅ Auto-detected {len(colspecs)} columns")
                                # Store in session state for potential manual override
                                st.session_state.fixed_width_colspecs = colspecs
                            else:
                                st.warning("⚠️ Could not auto-detect column positions. Please upload a header specification file or manual specification may be required.")
                    else:
                        # Delimited file
                        delimiter = detect_delimiter(claims_file)
                
                # Check if header file is a specification file (for delimited files - use names only)
                header_file = st.session_state.get("header_file_obj")
                if header_file and not is_fw and ext.endswith((".csv", ".txt", ".tsv")):
                    # For delimited files, check if header file is a spec file (unlikely but possible)
                    try:
                        header_file.seek(0)
                        header_bytes = header_file.read()
                        header_file.seek(0)
                        header_ext = os.path.splitext(header_file.name)[-1].lower()
                        temp_names, temp_colspecs = parse_header_specification_file(header_bytes, header_ext)
                        if temp_colspecs:
                            st.info(f"ℹ️ Header specification file detected (contains {len(temp_names)} columns), but file is delimited. Using column names only.")
                            # For delimited files, we only use the names, not positions
                            header_spec_names = temp_names
                            header_spec_colspecs = None
                    except (ValueError, Exception):
                        # Not a header spec file, will be handled as regular header file
                        pass
                
                # Auto-detect if file has headers (for CSV/TXT/TSV files)
                # Always detect, but require header file if no headers found
                detected_has_header = None
                
                # Auto-detect headers (always, to inform user)
                if ext.endswith((".csv", ".txt", ".tsv")):
                    if not is_fw:
                        # For delimited text files, use intelligent detection
                        claims_file.seek(0)
                        file_content = claims_file.read()
                        claims_file.seek(0)
                        file_bytes = io.BytesIO(file_content)
                        detected_has_header = has_header(file_bytes, delimiter=delimiter or ",")
                        st.session_state.detected_has_header = detected_has_header
                    else:
                        # For fixed-width, check first row
                        claims_file.seek(0)
                        file_content = claims_file.read()
                        claims_file.seek(0)
                        file_bytes = io.BytesIO(file_content)
                        detected_has_header = has_header(file_bytes, delimiter="")  # No delimiter for fixed-width
                        st.session_state.detected_has_header = detected_has_header
                elif ext.endswith((".xlsx", ".xls")):
                    # Excel files typically always have headers
                    detected_has_header = True
                    st.session_state.detected_has_header = True
                else:
                    # For other formats, assume headers exist
                    detected_has_header = True
                    st.session_state.detected_has_header = True
                
                # Skip preview since we're auto-detecting - preview will be shown after loading
                
                # Show fixed-width column positions if detected
                if is_fw and colspecs:
                    with st.expander("📏 View Detected Column Positions", expanded=False):
                        st.markdown("**Column Positions (start, end):**")
                        for i, (start, end) in enumerate(colspecs):
                            st.write(f"Column {i+1}: Positions {start}-{end} (width: {end-start})")
                
                # Show header detection result
                header_file = st.session_state.get("header_file_obj")
                if detected_has_header is not None:  # type: ignore[comparison-overlap]
                    if detected_has_header:  # type: ignore[comparison-overlap]
                        st.info("✅ **Auto-detected:** File appears to have headers. Using first row as column names.")
                    else:
                        st.error("❌ **Auto-detected:** File appears to have no headers. **Header file is required.**")
                        st.markdown("""
                        **Please upload a header file in one of these formats:**
                        - **One row format:** All field names in a single row (e.g., `claim_id,patient_name,date_of_service`)
                        - **One column format:** All field names in a single column (one per row)
                        """)
                        # Check if header file is provided
                        if not header_file:
                            st.warning("⚠️ **Please upload a header file to continue.**")
                            # Show header uploader without rerun
                            st.session_state.header_uploader_shown = True
                            st.stop()  # Stop processing until header file is uploaded

                # --- Read full source file (only if header detection is complete)
                if detected_has_header is not None:  # type: ignore[comparison-overlap]
                    progress.update(70, "Loading claims data...")
                    
                    with st.spinner(f"Loading {ui_labels.source_file_label.lower()}..."):
                        claims_file.seek(0)
                        header_file = st.session_state.get("header_file_obj")
                        # Use header file if provided (allows override), otherwise use detected status
                        # If no headers detected and no header file, we should have stopped earlier
                        use_header_file = header_file is not None
                        # Determine if we should use header spec file or regular header file
                        use_header_spec = header_spec_colspecs is not None and header_spec_names is not None
                        
                        skiprows_value = st.session_state.get("preprocessing_skiprows", 0) or None
                        if skiprows_value == 0:
                            skiprows_value = None
                        
                        claims_df = read_claims_with_header_option(
                            claims_file,
                            headerless=(use_header_file or (detected_has_header is False) or use_header_spec),
                            header_file=header_file if (use_header_file and not use_header_spec) else None,
                            delimiter=delimiter,
                            colspecs=colspecs if is_fw else None,
                            header_names=header_spec_names if use_header_spec else None,
                            skiprows=skiprows_value
                        )

                        # Fallback for junk columns
                        if claims_df.columns.isnull().any():
                            claims_df.columns = [f"col_{i}" if not col or pd.isna(col) else str(col) for i, col in enumerate(claims_df.columns)]

                        # Compress dataframe to save memory
                        claims_df = compress_dataframe(claims_df)

                        # Save to session
                        st.session_state.claims_df = claims_df
                        st.session_state.last_loaded_file = claims_file.name
                        # Use detected header status if available, otherwise fallback to logic
                        final_has_header = detected_has_header if detected_has_header is not None else (header_file is None)  # type: ignore[comparison-overlap]
                        capture_claims_file_metadata(claims_file, has_header=bool(final_has_header))

                    progress.update(90, "Finalizing...")
                    progress.complete(f"File loaded successfully! {len(claims_df):,} rows, {len(claims_df.columns)} columns")
                    
                    # Show memory usage if available
                    if memory_track.get("available") and "memory_delta_mb" in memory_track:
                        st.caption(f"💾 Memory used: {memory_track['memory_delta_mb']} MB | Duration: {memory_track.get('duration_seconds', 0):.1f}s")
                
                # Mark that processing is complete - success message will show above after refresh
                st.session_state.claims_processing_complete = True
                
                # Preview is handled by the file uploader's intelligent header detection
                # No need to show preview rows here - header detection already handled it
                
                st.session_state.needs_refresh = True

        except Exception as e:
            error_msg = get_user_friendly_error(e)
            st.error(f"Error processing {ui_labels.source_file_label.lower()}: {error_msg}")
            st.session_state.claims_df = None
            # Show retry option
            if st.button("🔄 Retry Loading File", key="retry_claims_load"):
                st.session_state.pop("claims_df", None)
                st.session_state.pop("last_loaded_file", None)
                st.session_state.needs_refresh = True
    
    # --- Preprocessing Options (Always show if file is uploaded, even after loading) ---
    claims_file_obj = st.session_state.get("claims_file_obj")
    if claims_file_obj is not None:
        with st.expander("⚙️ Preprocessing Options", expanded=True):
            # Show first 10 rows preview
            st.markdown("**📊 Data Preview (First 10 rows):**")
            try:
                # Read a preview of the file
                claims_file_obj.seek(0)
                preview_file = claims_file_obj
                
                # Check if file needs decompression
                file_ext = claims_file_obj.name.lower()
                actual_ext = file_ext
                if file_ext.endswith('.gz'):
                    preview_file = io.BytesIO(gzip.decompress(claims_file_obj.read()))
                    claims_file_obj.seek(0)
                    # Determine actual file type after decompression
                    actual_ext = file_ext[:-3]  # Remove .gz
                
                # Read preview based on file type
                if actual_ext.endswith(('.csv', '.txt', '.tsv')):
                    # Try to detect delimiter for text files
                    preview_file.seek(0)
                    delimiter = detect_delimiter(preview_file) if hasattr(preview_file, 'read') else ','
                    preview_file.seek(0)
                    preview_df = pd.read_csv(preview_file, nrows=10, dtype=str, delimiter=delimiter, on_bad_lines='skip')
                elif actual_ext.endswith(('.xlsx', '.xls')):
                    preview_file.seek(0)
                    preview_df = pd.read_excel(preview_file, nrows=10, dtype=str)
                elif actual_ext.endswith('.json'):
                    import json
                    preview_file.seek(0)
                    data = json.load(io.TextIOWrapper(preview_file, encoding='utf-8'))
                    if isinstance(data, list):
                        preview_df = pd.DataFrame(data[:10])
                    else:
                        preview_df = pd.json_normalize(data).head(10)
                elif actual_ext.endswith('.parquet'):
                    preview_file.seek(0)
                    preview_df = pd.read_parquet(preview_file).head(10)
                else:
                    preview_df = pd.DataFrame()
                
                if not preview_df.empty:
                    # Convert all columns to string to avoid PyArrow serialization issues
                    preview_df_display = preview_df.copy()
                    for col in preview_df_display.columns:
                        preview_df_display[col] = preview_df_display[col].astype(str).fillna("")
                    # Limit preview to avoid memory issues
                    preview_df_display = preview_df_display.head(10)
                    try:
                        st.dataframe(preview_df_display, use_container_width=True, height=300)
                    except Exception as display_error:
                        # Fallback: show as text if dataframe display fails
                        st.warning(f"Preview display issue: {str(display_error)}")
                        st.text(str(preview_df_display.head(5)))
                else:
                    st.info("Preview not available for this file type.")
            except Exception as e:
                st.warning(f"Could not preview file: {str(e)}")
                # Don't show full traceback to user, just log it
                import logging
                logging.exception("Preview error")
            
            # Preprocessing type selector - show options based on file type
            file_ext_for_preprocessing = claims_file_obj.name.lower()
            preprocessing_options = ["None", "Skip Rows"]
            
            # Add .gz option only if file is .gz
            if file_ext_for_preprocessing.endswith('.gz'):
                preprocessing_options.append("Unzip .gz File")
            
            # Initialize preprocessing_type in session state if not present
            if "preprocessing_type" not in st.session_state:
                st.session_state.preprocessing_type = "None"
            
            # Get current selection
            current_selection = st.session_state.get("preprocessing_type", "None")
            if current_selection not in preprocessing_options:
                current_selection = "None"
                st.session_state.preprocessing_type = "None"
            
            # Ensure we have a valid index
            try:
                current_index = preprocessing_options.index(current_selection)
            except ValueError:
                current_index = 0
                st.session_state.preprocessing_type = "None"
            
            preprocessing_type = st.selectbox(
                "Select Preprocessing Step",
                options=preprocessing_options,
                index=current_index,
                key="preprocessing_type",
                help="Select the type of preprocessing step needed for this file. Available options: " + ", ".join(preprocessing_options)
            )
            
            # Clear previous preprocessing steps when type changes to "None"
            if preprocessing_type == "None":
                try:
                    from data.preprocessing_tracker import clear_preprocessing_steps
                    clear_preprocessing_steps()
                    st.session_state.pop("preprocessing_skiprows", None)
                except ImportError:
                    pass
            
            # Show preprocessing options based on selection
            if preprocessing_type == "Skip Rows":
                skiprows_input = st.number_input(
                    "Skip first N rows (e.g., for logos, stats, or metadata)",
                    min_value=0,
                    value=st.session_state.get("preprocessing_skiprows", 0),
                    key="preprocessing_skiprows",
                    help="Use this if your file has logos, statistics, or other metadata at the top that should be skipped before the actual data starts."
                )
                
                # Track skiprows - clear previous skip_rows steps first, then add new one
                if skiprows_input > 0:
                    try:
                        from data.preprocessing_tracker import track_preprocessing_step, get_preprocessing_steps, clear_preprocessing_steps
                        # Remove any existing skip_rows steps
                        steps = get_preprocessing_steps()
                        clear_preprocessing_steps()
                        # Re-add other steps (excluding skip_rows)
                        for step in steps:
                            if step.get("step") != "skip_rows":
                                track_preprocessing_step(step.get("step"), step.get("parameters", {}))
                        # Add the new skip_rows step
                        track_preprocessing_step("skip_rows", {"num_rows": int(skiprows_input)})
                        # Don't manually set session state - widget manages its own state
                    except ImportError:
                        pass
                else:
                    # Clear skip_rows step if set to 0
                    try:
                        from data.preprocessing_tracker import get_preprocessing_steps, clear_preprocessing_steps, track_preprocessing_step
                        steps = get_preprocessing_steps()
                        clear_preprocessing_steps()
                        # Re-add other steps (excluding skip_rows)
                        for step in steps:
                            if step.get("step") != "skip_rows":
                                track_preprocessing_step(step.get("step"), step.get("parameters", {}))
                        # Don't manually set session state - widget manages its own state
                    except ImportError:
                        pass
            
            elif preprocessing_type == "Unzip .gz File":
                if not file_ext_for_preprocessing.endswith('.gz'):
                    st.info("ℹ️ This file doesn't appear to be a .gz compressed file.")
                else:
                    st.success("✅ .gz file detected. File will be automatically decompressed during processing.")
                    try:
                        from data.preprocessing_tracker import track_preprocessing_step, get_preprocessing_steps
                        # Check if unzip_gz step already exists
                        steps = get_preprocessing_steps()
                        has_unzip = any(step.get("step") == "unzip_gz" for step in steps)
                        if not has_unzip:
                            track_preprocessing_step("unzip_gz", {"compressed": True})
                    except ImportError:
                        pass
            
            # Show active preprocessing steps
            try:
                from data.preprocessing_tracker import get_preprocessing_steps
                active_steps = get_preprocessing_steps()
                if active_steps:
                    st.markdown("**✅ Active Preprocessing Steps:**")
                    for step in active_steps:
                        step_name = step.get("step", "")
                        params = step.get("parameters", {})
                        if step_name == "skip_rows":
                            st.info(f"📋 Skip Rows: {params.get('num_rows', 0)} rows will be skipped")
                        elif step_name == "unzip_gz":
                            st.info("📦 Unzip .gz: File will be decompressed")
                        else:
                            st.info(f"⚙️ {step_name}: {params}")
            except ImportError:
                pass


def render_claims_file_deep_dive():
    """
    Displays the deep dive summary of the source file after mapping:
    showing all internal fields, mapped columns, data types, fill rates, required flag, and pass/fail status.
    """
    from core.ui_labels import get_ui_labels
    ui_labels = get_ui_labels()
    st.markdown(f"#### {ui_labels.source_file_label} Deep Dive (Mapped Columns Analysis)")

    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})
    layout_df = st.session_state.get("layout_df")
    transformed_df = st.session_state.get("transformed_df")

    if claims_df is None or final_mapping is None or layout_df is None or transformed_df is None:
        st.info(f"Upload {ui_labels.source_file_label.lower()}, complete mappings, and preview transformed data first.")
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

