# --- preprocessing_tracker.py ---
"""Track and generate preprocessing code for file processing."""
from typing import Dict, Any, Optional, List
import streamlit as st  # type: ignore[import-not-found]

st: Any = st  # type: ignore[assignment]


def track_preprocessing_step(step_name: str, parameters: Dict[str, Any]) -> None:
    """Track a preprocessing step that was applied to the file.
    
    Args:
        step_name: Name of the preprocessing step (e.g., "skip_rows", "detect_encoding")
        parameters: Dictionary of parameters used in this step
    """
    if "preprocessing_steps" not in st.session_state:
        st.session_state.preprocessing_steps = []
    
    st.session_state.preprocessing_steps.append({
        "step": step_name,
        "parameters": parameters
    })


def clear_preprocessing_steps() -> None:
    """Clear all tracked preprocessing steps."""
    if "preprocessing_steps" in st.session_state:
        st.session_state.preprocessing_steps = []


def get_preprocessing_steps() -> List[Dict[str, Any]]:
    """Get all tracked preprocessing steps.
    
    Returns:
        List of preprocessing step dictionaries
    """
    return st.session_state.get("preprocessing_steps", [])


def generate_preprocessing_script(
    file_path: str = "input_file.csv",
    output_path: str = "processed_file.csv",
    filename: Optional[str] = None
) -> str:
    """
    Generate a Python script that reproduces the preprocessing steps.
    
    Args:
        file_path: Path to the raw input file
        output_path: Path where processed file should be saved
        filename: Original filename (for reference)
        
    Returns:
        Python script as string
    """
    steps = st.session_state.get("preprocessing_steps", [])
    file_metadata = st.session_state.get("claims_file_metadata", {})
    
    script_lines = [
        "#!/usr/bin/env python3",
        '"""',
        f"Original file: {filename or 'N/A'}",
        '"""',
        "",
        "import pandas as pd",
        "import sys",
        "import os",
        "",
        "def preprocess_file(input_file: str, output_file: str = None) -> pd.DataFrame:",
        '    """',
        "    Preprocess the input file using the same steps applied during processing.",
        '    """',
        "    if not os.path.exists(input_file):",
        '        raise FileNotFoundError(f"Input file not found: {input_file}")',
        "",
        "    # File format and basic settings",
        f"    file_format = '{file_metadata.get('format', 'csv')}'",
        f"    delimiter = {repr(file_metadata.get('sep', ','))}",
        f"    has_header = {file_metadata.get('header', False)}",
        "",
    ]
    
    # Extract preprocessing parameters
    skiprows = None
    header_row = None
    encoding = None
    colspecs = None
    external_header = False
    headerless = False
    
    for step in steps:
        step_name = step.get("step")
        params = step.get("parameters", {})
        
        if step_name == "skip_rows":
            skiprows = params.get("num_rows", 0)
        elif step_name == "detect_encoding":
            encoding = params.get("encoding", "utf-8")
        elif step_name == "external_header":
            external_header = True
            headerless = True
        elif step_name == "headerless_file":
            headerless = True
        elif step_name == "fixed_width":
            colspecs = params.get("colspecs")
    
    # Add encoding detection if tracked
    if encoding:
        script_lines.append(f"    # Detected encoding: {encoding}")
        script_lines.append(f"    encoding = {repr(encoding)}")
    else:
        script_lines.append("    # Default encoding")
        script_lines.append("    encoding = 'utf-8'")
    
    script_lines.append("")
    
    # Build read statement based on file format
    if file_metadata.get("format") == "csv" or file_metadata.get("format") == "txt" or file_metadata.get("format") == "tsv":
        script_lines.append("    # Read CSV/delimited file")
        
        read_options = []
        if delimiter:
            read_options.append(f"delimiter={repr(delimiter)}")
        if encoding:
            read_options.append(f"encoding=encoding")
        if skiprows:
            read_options.append(f"skiprows={skiprows}")
        if headerless or not has_header:
            read_options.append("header=None")
        else:
            read_options.append("header=0")
        
        read_options.append("dtype=str")
        read_options.append("on_bad_lines='skip'")
        
        script_lines.append(f"    df = pd.read_csv(input_file, {', '.join(read_options)})")
        
    elif file_metadata.get("format") in ["xlsx", "excel"]:
        script_lines.append("    # Read Excel file")
        
        read_options = []
        if skiprows:
            read_options.append(f"skiprows={skiprows}")
        if headerless or not has_header:
            read_options.append("header=None")
        else:
            read_options.append("header=0")
        
        read_options.append("dtype=str")
        
        script_lines.append(f"    df = pd.read_excel(input_file, {', '.join(read_options)})")
        
    elif file_metadata.get("format") == "json":
        script_lines.append("    # Read JSON file")
        script_lines.append("    df = pd.read_json(input_file)")
        
    elif file_metadata.get("format") == "parquet":
        script_lines.append("    # Read Parquet file")
        script_lines.append("    df = pd.read_parquet(input_file)")
    
    # Add fixed-width handling
    if colspecs:
        script_lines.append("")
        script_lines.append("    # Fixed-width file processing")
        script_lines.append(f"    colspecs = {colspecs}")
        script_lines.append("    df = pd.read_fwf(input_file, colspecs=colspecs, header=0 if has_header else None, dtype=str)")
    
    # Add external header handling
    if external_header:
        script_lines.append("")
        script_lines.append("    # Apply external header")
        script_lines.append("    # NOTE: You need to provide the header file separately")
        script_lines.append("    # Example:")
        script_lines.append("    # header_file = 'header_file.csv'")
        script_lines.append("    # header_df = pd.read_csv(header_file, header=None)")
        script_lines.append("    # if len(header_df.columns) == df.shape[1]:")
        script_lines.append("    #     df.columns = header_df.iloc[0].tolist()")
        script_lines.append("    # else:")
        script_lines.append("    #     print(f'Warning: Header file has {len(header_df.columns)} columns, but data has {df.shape[1]} columns')")
    
    # Add row skipping documentation
    if skiprows:
        script_lines.append("")
        script_lines.append(f"    # Note: First {skiprows} rows were skipped (e.g., logos, stats, etc.)")
    
    script_lines.extend([
        "",
        "    # Additional cleaning steps",
        "    # Remove completely empty rows",
        "    df = df.dropna(how='all')",
        "",
        "    # Trim whitespace from string columns",
        "    for col in df.select_dtypes(include=['object']).columns:",
        "        df[col] = df[col].astype(str).str.strip()",
        "",
        "    # Remove rows where all values are empty strings",
        "    df = df[~(df.astype(str).apply(lambda x: x.str.strip() == '').all(axis=1))]",
        "",
        "    # Save processed file",
        "    if output_file:",
        "        if file_format in ['csv', 'txt', 'tsv']:",
        f"            df.to_csv(output_file, index=False, sep={repr(delimiter) if delimiter else repr(',')})",
        "        elif file_format in ['xlsx', 'excel']:",
        "            df.to_excel(output_file, index=False)",
        "        elif file_format == 'json':",
        "            df.to_json(output_file, orient='records', indent=2)",
        "        elif file_format == 'parquet':",
        "            df.to_parquet(output_file, index=False)",
        "        print(f'Processed file saved to: {output_file}')",
        "",
        "    return df",
        "",
        "",
        "if __name__ == '__main__':",
        "    if len(sys.argv) < 2:",
        '        print("Usage: python preprocess_file.py <input_file> [output_file]")',
        "        sys.exit(1)",
        "",
        "    input_file = sys.argv[1]",
        "    output_file = sys.argv[2] if len(sys.argv) > 2 else None",
        "",
        "    try:",
        "        df = preprocess_file(input_file, output_file)",
        '        print(f"Successfully processed {len(df)} rows, {len(df.columns)} columns")',
        "    except Exception as e:",
        '        print(f"Error processing file: {e}")',
        "        import traceback",
        "        traceback.print_exc()",
        "        sys.exit(1)",
    ])
    
    return "\n".join(script_lines)
