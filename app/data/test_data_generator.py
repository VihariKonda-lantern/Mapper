# --- test_data_generator.py ---
"""Generate test data with different scenarios."""
from typing import Any, Dict, List, Optional
import pandas as pd  # type: ignore[import-not-found]
import random
import io
from datetime import datetime, timedelta

try:
    from faker import Faker  # type: ignore[import-not-found]
    fake = Faker()
except ImportError:
    fake = None
    Faker = None


def generate_test_data_with_scenarios(
    layout_df: Any,
    final_mapping: Dict[str, Dict[str, Any]],
    claims_df: Optional[Any] = None,
    records_per_scenario: int = 30,
    include_scenarios: Optional[List[str]] = None,
    file_format: Optional[str] = None,
    file_separator: Optional[str] = None,
    file_has_header: Optional[bool] = None,
    file_date_format: Optional[str] = None,
    apply_reverse_mappings: bool = True
) -> Dict[str, Any]:
    """
    Generate test data with different scenarios.
    
    Args:
        layout_df: Layout DataFrame
        final_mapping: Field mapping dictionary
        claims_df: Claims DataFrame (for format detection)
        records_per_scenario: Number of records per scenario
        include_scenarios: List of scenarios to include (None = all)
        file_format: File format (csv, txt, xlsx, json, parquet, fixed-width)
        file_separator: File separator
        file_has_header: Whether file has header
        file_date_format: Date format in file
        apply_reverse_mappings: Whether to apply reverse value mappings
        
    Returns:
        Dictionary mapping scenario names to DataFrames or file data (bytes for binary formats)
    """
    if include_scenarios is None:
        include_scenarios = [
            "happy_path", "headers_only", "messed_up_date_formats",
            "nulls_in_required_fields", "duplicates", "demo_mismatch",
            "duplicates_with_recent_service", "validation_edge_cases"
        ]
    
    # Check if faker is installed
    if fake is None or Faker is None:
        raise ImportError(
            "The 'faker' package is required for test data generation. "
            "Please install it by running: pip install faker>=20.0.0"
        )
    
    scenarios = {}
    
    # Validate inputs
    if layout_df is None or layout_df.empty:
        raise ValueError("Layout DataFrame is required and cannot be empty")
    
    if not final_mapping:
        raise ValueError("Field mapping is required. Please complete field mappings first.")
    
    # Get internal fields and their data types
    from core.domain_config import get_domain_config
    config = get_domain_config()
    internal_field_col = config.internal_field_name
    data_type_col = config.layout_columns.get("data_type", "Data Type")
    usage_col = config.internal_usage_name
    
    internal_fields = []
    field_types = {}
    field_usage = {}
    required_fields = []
    
    try:
        for idx, row in layout_df.iterrows():
            field = str(row.get(internal_field_col, '')).strip()
            if not field or field.lower() == 'nan':
                continue
            internal_fields.append(field)
            data_type = str(row.get(data_type_col, 'string')).lower()
            field_types[field] = data_type
            usage = str(row.get(usage_col, '')).strip()
            field_usage[field] = usage
            if usage.lower() == 'mandatory':
                required_fields.append(field)
    except Exception as e:
        # If layout parsing fails, raise a more informative error
        raise ValueError(f"Error parsing layout file: {str(e)}. Please check that the layout file has the required columns.")
    
    # Get source columns from final_mapping
    source_columns = []
    field_mapping = {}  # internal_field -> source_column
    for internal_field, mapping_info in final_mapping.items():
        if isinstance(mapping_info, dict) and 'value' in mapping_info:
            source_col = mapping_info['value']
            if source_col:
                if source_col not in source_columns:
                    source_columns.append(source_col)
                field_mapping[internal_field] = source_col
    
    # If no source columns, use internal fields
    if not source_columns:
        source_columns = internal_fields
    
    # Validate we have columns to work with
    if not source_columns:
        raise ValueError("No source columns or internal fields found. Please ensure layout and mapping are properly configured.")
    
    # Detect file format from claims_df or use defaults
    if file_format is None:
        file_format = "csv"
    if file_separator is None:
        file_separator = "\t"
    if file_has_header is None:
        file_has_header = True
    if file_date_format is None:
        file_date_format = "yyyyMMdd"
    
    # Date format mapping
    PYSPARK_TO_PANDAS_DATE_FORMAT = {
        "yyyyMMdd": "%Y%m%d",
        "yyyy-MM-dd": "%Y-%m-%d",
        "yyyy/MM/dd": "%Y/%m/%d",
        "MMddyyyy": "%m%d%Y",
        "MM/dd/yyyy": "%m/%d/%Y",
        "MMddyy": "%m%d%y",
        "MM/dd/yy": "%m/%d/%y",
        "dd-MM-yyyy": "%d-%m-%Y",
        "dd/MM/yyyy": "%d/%m/%Y",
        "ddMMyyyy": "%d%m%Y",
        "ddMMyy": "%d%m%y",
        "dd/MM/yy": "%d/%m/%y",
        "yyyyMM": "%Y%m",
        "MM-yyyy": "%m-%Y",
        "MM/yyyy": "%m/%Y",
        "yyyyMd": "%Y%m%d",
    }
    
    pandas_date_format = PYSPARK_TO_PANDAS_DATE_FORMAT.get(file_date_format, "%Y%m%d")
    
    # Build reverse value mappings if needed
    reverse_mappings = {}
    if apply_reverse_mappings:
        reverse_mappings = _build_reverse_value_mappings(final_mapping, layout_df)
    
    # Scenario 1: Happy Path
    if "happy_path" in include_scenarios:
        df = _generate_happy_path_data(
            source_columns, field_types, field_mapping, field_usage,
            records_per_scenario, pandas_date_format
        )
        if apply_reverse_mappings:
            df = _apply_reverse_mappings(df, reverse_mappings, source_columns)
        scenarios["happy_path"] = df
    
    # Scenario 2: Headers Only
    if "headers_only" in include_scenarios:
        scenarios["headers_only"] = pd.DataFrame(columns=source_columns)
    
    # Scenario 3: Messed Up Date Formats
    if "messed_up_date_formats" in include_scenarios:
        df = _generate_messed_up_dates_data(
            source_columns, field_types, field_mapping, field_usage,
            records_per_scenario, pandas_date_format
        )
        if apply_reverse_mappings:
            df = _apply_reverse_mappings(df, reverse_mappings, source_columns)
        scenarios["messed_up_date_formats"] = df
    
    # Scenario 4: Nulls in Required Fields
    if "nulls_in_required_fields" in include_scenarios:
        df = _generate_nulls_in_required_data(
            source_columns, field_types, field_mapping, field_usage,
            required_fields, records_per_scenario, pandas_date_format
        )
        if apply_reverse_mappings:
            df = _apply_reverse_mappings(df, reverse_mappings, source_columns)
        scenarios["nulls_in_required_fields"] = df
    
    # Scenario 5: Duplicates
    if "duplicates" in include_scenarios:
        df = _generate_duplicates_data(
            source_columns, field_types, field_mapping, field_usage,
            records_per_scenario, pandas_date_format
        )
        if apply_reverse_mappings:
            df = _apply_reverse_mappings(df, reverse_mappings, source_columns)
        scenarios["duplicates"] = df
    
    # Scenario 6: Demo Mismatch
    if "demo_mismatch" in include_scenarios:
        df = _generate_demo_mismatch_data(
            source_columns, field_types, field_mapping, field_usage,
            records_per_scenario, pandas_date_format
        )
        if apply_reverse_mappings:
            df = _apply_reverse_mappings(df, reverse_mappings, source_columns)
        scenarios["demo_mismatch"] = df
    
    # Scenario 7: Duplicates with Recent Service
    if "duplicates_with_recent_service" in include_scenarios:
        df = _generate_duplicates_recent_service_data(
            source_columns, field_types, field_mapping, field_usage,
            pandas_date_format
        )
        if apply_reverse_mappings:
            df = _apply_reverse_mappings(df, reverse_mappings, source_columns)
        scenarios["duplicates_with_recent_service"] = df
    
    # Scenario 8: Validation Edge Cases
    if "validation_edge_cases" in include_scenarios:
        df = _generate_validation_edge_cases_data(
            source_columns, field_types, field_mapping, field_usage,
            pandas_date_format
        )
        if apply_reverse_mappings:
            df = _apply_reverse_mappings(df, reverse_mappings, source_columns)
        scenarios["validation_edge_cases"] = df
    
    # Convert DataFrames to appropriate format based on file_format (after all scenarios generated)
    if file_format and file_format.lower() in ['xlsx', 'json', 'parquet', 'fixed-width']:
        scenarios = _convert_dataframes_to_format(scenarios, file_format, file_separator, file_has_header, source_columns)
    
    return scenarios


def _generate_happy_path_data(
    source_columns: List[str],
    field_types: Dict[str, str],
    field_mapping: Dict[str, str],
    field_usage: Dict[str, str],
    n_rows: int,
    date_format: str
) -> pd.DataFrame:
    """Generate normal, valid test data."""
    if not source_columns:
        return pd.DataFrame()
    
    data = {}
    
    for col in source_columns:
        # Find corresponding internal field
        internal_field = None
        for int_field, src_col in field_mapping.items():
            if src_col == col:
                internal_field = int_field
                break
        
        if internal_field is None:
            # Use column name directly
            field_lower = col.lower()
        else:
            field_lower = internal_field.lower()
        
        dtype = field_types.get(internal_field, "string") if internal_field else "string"
        
        if "date" in field_lower or "dob" in field_lower:
            # DOB: 18-80 years ago
            dates = []
            for _ in range(n_rows):
                dob = fake.date_between(start_date='-80y', end_date='-18y')
                dates.append(dob.strftime(date_format))
            data[col] = dates
        elif "service" in field_lower and "date" in field_lower:
            # Service dates: last 6 months
            dates = []
            for _ in range(n_rows):
                service_date = fake.date_between(start_date='-6m', end_date='today')
                dates.append(service_date.strftime(date_format))
            data[col] = dates
        elif "name" in field_lower and "first" in field_lower:
            data[col] = [fake.first_name() for _ in range(n_rows)]
        elif "name" in field_lower and "last" in field_lower:
            data[col] = [fake.last_name() for _ in range(n_rows)]
        elif "sex" in field_lower or "gender" in field_lower:
            data[col] = [random.choice(["M", "F"]) for _ in range(n_rows)]
        elif "ssn" in field_lower:
            data[col] = [fake.ssn().replace("-", "") for _ in range(n_rows)]
        elif "npi" in field_lower:
            data[col] = [fake.numerify(text="##########") for _ in range(n_rows)]
        elif "cpt" in field_lower:
            data[col] = [fake.numerify(text="#####") for _ in range(n_rows)]
        elif "icd" in field_lower:
            # ICD codes: format like A12.34
            data[col] = [f"{fake.lexify(text='???').upper()}.{fake.numerify(text='##')}" for _ in range(n_rows)]
        elif dtype == "date":
            dates = []
            for _ in range(n_rows):
                date_val = fake.date_between(start_date='-2y', end_date='today')
                dates.append(date_val.strftime(date_format))
            data[col] = dates
        else:
            # Default: random alphanumeric
            data[col] = [fake.bothify(text="??###") for _ in range(n_rows)]
    
    return pd.DataFrame(data)


def _generate_messed_up_dates_data(
    source_columns: List[str],
    field_types: Dict[str, str],
    field_mapping: Dict[str, str],
    field_usage: Dict[str, str],
    n_rows: int,
    date_format: str
) -> pd.DataFrame:
    """Generate data with messed up date formats."""
    if not source_columns:
        return pd.DataFrame()
    
    df = _generate_happy_path_data(source_columns, field_types, field_mapping, field_usage, n_rows, date_format)
    
    # Find date columns
    date_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if "date" in col_lower or "dob" in col_lower:
            date_cols.append(col)
    
    # Mess up some dates
    for col in date_cols:
        for idx in range(min(10, len(df))):  # Mess up first 10 rows
            if random.random() < 0.5:
                # Wrong format
                if "/" in date_format:
                    df.at[idx, col] = "2024-12-25"  # Wrong separator
                elif "-" in date_format:
                    df.at[idx, col] = "12/25/2024"  # Wrong separator
                else:
                    df.at[idx, col] = "12-25-2024"  # Wrong format
            else:
                # Text in date field
                df.at[idx, col] = "INVALID_DATE"
    
    return df


def _generate_nulls_in_required_data(
    source_columns: List[str],
    field_types: Dict[str, str],
    field_mapping: Dict[str, str],
    field_usage: Dict[str, str],
    required_fields: List[str],
    n_rows: int,
    date_format: str
) -> pd.DataFrame:
    """Generate data with nulls in required fields."""
    if not source_columns:
        return pd.DataFrame()
    
    df = _generate_happy_path_data(source_columns, field_types, field_mapping, field_usage, n_rows, date_format)
    
    # Find required source columns
    required_source_cols = []
    for req_field in required_fields:
        if req_field in field_mapping:
            required_source_cols.append(field_mapping[req_field])
    
    # Set some required fields to null
    for col in required_source_cols:
        if col in df.columns:
            null_indices = random.sample(range(len(df)), min(5, len(df) // 2))
            for idx in null_indices:
                df.at[idx, col] = None
    
    return df


def _generate_duplicates_data(
    source_columns: List[str],
    field_types: Dict[str, str],
    field_mapping: Dict[str, str],
    field_usage: Dict[str, str],
    n_rows: int,
    date_format: str
) -> pd.DataFrame:
    """Generate data with duplicate records."""
    if not source_columns:
        return pd.DataFrame()
    
    # Generate fewer unique records, then duplicate them
    unique_rows = max(5, n_rows // 3)
    df_unique = _generate_happy_path_data(source_columns, field_types, field_mapping, field_usage, unique_rows, date_format)
    
    # Duplicate rows to reach n_rows
    df_duplicated = df_unique.copy()
    while len(df_duplicated) < n_rows:
        df_duplicated = pd.concat([df_duplicated, df_unique.head(n_rows - len(df_duplicated))], ignore_index=True)
    
    return df_duplicated


def _generate_demo_mismatch_data(
    source_columns: List[str],
    field_types: Dict[str, str],
    field_mapping: Dict[str, str],
    field_usage: Dict[str, str],
    n_rows: int,
    date_format: str
) -> pd.DataFrame:
    """Generate data with demographic mismatches."""
    if not source_columns:
        return pd.DataFrame()
    
    df = _generate_happy_path_data(source_columns, field_types, field_mapping, field_usage, n_rows, date_format)
    
    # Find demographic columns
    sex_col = None
    name_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if "sex" in col_lower or "gender" in col_lower:
            sex_col = col
        elif "name" in col_lower:
            name_cols.append(col)
    
    # Create mismatches
    for idx in range(min(10, len(df))):
        if sex_col and sex_col in df.columns:
            # Invalid sex code
            df.at[idx, sex_col] = random.choice(["X", "U", "INVALID", "99"])
        
        for name_col in name_cols:
            if name_col in df.columns:
                # Mismatched name format (numbers in name)
                df.at[idx, name_col] = f"{fake.numerify(text='####')} {fake.word()}"
    
    return df


def _generate_duplicates_recent_service_data(
    source_columns: List[str],
    field_types: Dict[str, str],
    field_mapping: Dict[str, str],
    field_usage: Dict[str, str],
    date_format: str
) -> pd.DataFrame:
    """Generate 3 duplicate records, one with recent service date."""
    if not source_columns:
        return pd.DataFrame()
    
    # Generate one base record
    base_df = _generate_happy_path_data(source_columns, field_types, field_mapping, field_usage, 1, date_format)
    
    # Find service date column
    service_date_col = None
    for col in base_df.columns:
        if "service" in col.lower() and "date" in col.lower():
            service_date_col = col
            break
    
    # Create 3 duplicates
    df = pd.concat([base_df, base_df.copy(), base_df.copy()], ignore_index=True)
    
    # Set service dates: one recent, two old
    if service_date_col:
        recent_date = datetime.now() - timedelta(days=random.randint(1, 30))
        old_date1 = datetime.now() - timedelta(days=random.randint(400, 600))
        old_date2 = datetime.now() - timedelta(days=random.randint(400, 600))
        
        df.at[0, service_date_col] = recent_date.strftime(date_format)
        df.at[1, service_date_col] = old_date1.strftime(date_format)
        df.at[2, service_date_col] = old_date2.strftime(date_format)
    
    return df


def _generate_validation_edge_cases_data(
    source_columns: List[str],
    field_types: Dict[str, str],
    field_mapping: Dict[str, str],
    field_usage: Dict[str, str],
    date_format: str
) -> pd.DataFrame:
    """Generate 3 rows with specific validation issues."""
    if not source_columns:
        return pd.DataFrame()
    
    # Generate 3 base records
    base_df = _generate_happy_path_data(source_columns, field_types, field_mapping, field_usage, 3, date_format)
    
    # Find DOB and service date columns
    dob_col = None
    service_date_col = None
    for col in base_df.columns:
        col_lower = col.lower()
        if "dob" in col_lower and "date" in col_lower:
            dob_col = col
        elif "service" in col_lower and "date" in col_lower:
            service_date_col = col
    
    # Row 1: DOB < 18 years ago (invalid age)
    if dob_col:
        invalid_dob = datetime.now() - timedelta(days=random.randint(365 * 10, 365 * 15))  # 10-15 years ago
        base_df.at[0, dob_col] = invalid_dob.strftime(date_format)
    
    # Row 2: Service date > 18 months ago (too old)
    if service_date_col:
        old_service_date = datetime.now() - timedelta(days=random.randint(550, 600))  # ~18+ months ago
        base_df.at[1, service_date_col] = old_service_date.strftime(date_format)
    
    # Row 3: Normal valid data (already generated)
    
    return base_df


def _build_reverse_value_mappings(
    final_mapping: Dict[str, Dict[str, Any]],
    layout_df: Any
) -> Dict[str, Dict[str, str]]:
    """
    Build reverse value mappings from final_mapping.
    
    Args:
        final_mapping: Field mapping dictionary
        layout_df: Layout DataFrame
        
    Returns:
        Dictionary mapping source column names to reverse value mappings
        {source_col: {target_value: source_value}}
    """
    reverse_mappings = {}
    
    # Check if there are value mapping rules in the mapping
    # This is a basic implementation - can be extended if value mapping rules are stored
    for internal_field, mapping_info in final_mapping.items():
        if isinstance(mapping_info, dict):
            source_col = mapping_info.get('value')
            # If there are value mapping rules, parse them
            # For now, return empty dict as value mappings are not currently stored in final_mapping
            if source_col and source_col not in reverse_mappings:
                reverse_mappings[source_col] = {}
    
    return reverse_mappings


def _apply_reverse_mappings(
    df: pd.DataFrame,
    reverse_mappings: Dict[str, Dict[str, str]],
    source_columns: List[str]
) -> pd.DataFrame:
    """
    Apply reverse value mappings to DataFrame.
    
    Args:
        df: DataFrame to apply mappings to
        reverse_mappings: Reverse mapping dictionary
        source_columns: List of source column names
        
    Returns:
        DataFrame with reverse mappings applied
    """
    df = df.copy()
    
    for col in source_columns:
        if col in df.columns and col in reverse_mappings:
            mapping = reverse_mappings[col]
            if mapping:
                # Apply reverse mapping: replace target values with source values
                df[col] = df[col].replace(mapping)
    
    return df


def _convert_dataframes_to_format(
    scenarios: Dict[str, pd.DataFrame],
    file_format: str,
    file_separator: str,
    file_has_header: bool,
    source_columns: List[str]
) -> Dict[str, Any]:
    """
    Convert DataFrames to the specified file format.
    
    Args:
        scenarios: Dictionary of scenario names to DataFrames
        file_format: Target file format (xlsx, json, parquet, fixed-width)
        file_separator: File separator (for fixed-width, not used)
        file_has_header: Whether to include header
        source_columns: List of source column names
        
    Returns:
        Dictionary mapping scenario names to file data (bytes for binary, str for text)
    """
    converted = {}
    file_format_lower = file_format.lower()
    
    for scenario_name, df in scenarios.items():
        # Skip if DataFrame is empty
        if isinstance(df, pd.DataFrame) and df.empty:
            converted[scenario_name] = df
            continue
        
        try:
            if file_format_lower == 'xlsx':
                # Excel format
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore[no-untyped-call]
                    df.to_excel(writer, sheet_name=scenario_name, index=False, header=file_has_header)  # type: ignore[no-untyped-call]
                converted[scenario_name] = output.getvalue()
            
            elif file_format_lower == 'json':
                # JSON format
                json_str = df.to_json(orient='records', indent=2, date_format='iso')  # type: ignore[no-untyped-call]
                converted[scenario_name] = json_str.encode('utf-8')
            
            elif file_format_lower == 'parquet':
                # Parquet format
                output = io.BytesIO()
                df.to_parquet(output, index=False, engine='pyarrow')  # type: ignore[no-untyped-call]
                converted[scenario_name] = output.getvalue()
            
            elif file_format_lower == 'fixed-width':
                # Fixed-width format
                fixed_width_str = _convert_to_fixed_width(df, source_columns, file_has_header)
                converted[scenario_name] = fixed_width_str.encode('utf-8')
            
            else:
                # Keep as DataFrame for CSV/delimited formats
                converted[scenario_name] = df
        except Exception:
            # If conversion fails, keep as DataFrame (fallback to CSV)
            converted[scenario_name] = df
    
    return converted


def _convert_to_fixed_width(
    df: pd.DataFrame,
    source_columns: List[str],
    file_has_header: bool
) -> str:
    """
    Convert DataFrame to fixed-width format.
    
    Args:
        df: DataFrame to convert
        source_columns: List of source column names (for order)
        file_has_header: Whether to include header
        
    Returns:
        Fixed-width formatted string
    """
    lines = []
    
    # Calculate column widths
    col_widths = {}
    for col in source_columns:
        if col in df.columns:
            # Calculate max width needed for this column
            if len(df) > 0:
                max_width = max(
                    len(str(val)) if pd.notna(val) else 0
                    for val in df[col]
                )
            else:
                max_width = 0
            # Also consider column name length
            max_width = max(max_width, len(str(col)))
            col_widths[col] = max(max_width, 10)  # Minimum 10 chars
        else:
            col_widths[col] = max(len(str(col)), 10)
    
    # Generate header if needed
    if file_has_header:
        header_line = ""
        for col in source_columns:
            width = col_widths.get(col, 10)
            header_line += str(col).ljust(width)
        lines.append(header_line)
    
    # Generate data rows (skip if empty DataFrame)
    if len(df) > 0:
        for _, row in df.iterrows():
            data_line = ""
            for col in source_columns:
                if col in df.columns:
                    width = col_widths.get(col, 10)
                    val = str(row[col]) if pd.notna(row[col]) else ""
                    data_line += val.ljust(width)
                else:
                    width = col_widths.get(col, 10)
                    data_line += "".ljust(width)
            lines.append(data_line)
    
    return "\n".join(lines) if lines else ""
