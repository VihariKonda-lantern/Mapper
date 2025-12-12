# --- file_handler.py ---
# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
import csv
import json
import os
import io
from typing import Tuple, List, Any, Optional, IO, cast
import streamlit as st  # type: ignore[import-not-found]

st = cast(Any, st)
pd = cast(Any, pd)

# Try to import chardet for encoding detection (optional)
try:
    import chardet  # type: ignore[import-not-found]
    HAS_CHARDET: bool = True
except ImportError:
    HAS_CHARDET = False  # type: ignore[assignment]

SUPPORTED_FORMATS = ('.csv', '.txt', '.tsv', '.xlsx', '.xls', '.json', '.parquet')

# Common encodings to try in order of preference
ENCODING_FALLBACKS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-16-le', 'utf-16-be']

def clean_header_row(header_list: List[str]) -> List[str]:
    """Normalize and de-duplicate a raw header row.

    Replaces missing/blank values with `Unknown_{i}`, trims whitespace, and
    appends numeric suffixes to duplicate column names to ensure uniqueness.

    Args:
        header_list: Raw header values as strings.

    Returns:
        Cleaned header list with unique, non-empty strings.
    """
    cleaned: List[str] = []
    for idx, val in enumerate(header_list):
        if pd.isna(val) or str(val).strip() == "":
            cleaned.append(f"Unknown_{idx+1}")
        else:
            cleaned.append(str(val).strip())

    # De-duplicate headers
    seen: dict[str, int] = {}
    final_headers: List[str] = []
    for h in cleaned:
        if h in seen:
            seen[h] += 1
            final_headers.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 0
            final_headers.append(h)

    return final_headers

def has_header(file: IO[bytes], delimiter: str = ",", sample_size: int = 2048) -> bool:
    """Detect if a delimited text file appears to have a header row.

    Uses `csv.Sniffer().has_header` on a sample of bytes read from the file.

    Args:
        file: Binary file-like object positioned anywhere; will be reset.
        delimiter: Expected delimiter for context (not strictly required).
        sample_size: Number of bytes to sample for detection.

    Returns:
        True if a header is likely present; False otherwise.
    """
    file.seek(0)
    try:
        sniffer = csv.Sniffer()
        content = file.read(sample_size)
        file.seek(0)
        encoding = detect_encoding(content, sample_size)
        sample = content.decode(encoding, errors="ignore")
        return sniffer.has_header(sample)
    except Exception:
        file.seek(0)
        return False

@st.cache_data(show_spinner=False)
def _detect_delimiter_cached(sample: str) -> str:
    """Intelligently detect delimiter using multiple strategies.

    Args:
        sample: Text content to analyze.

    Returns:
        The most likely delimiter based on multiple heuristics.
    """
    # Expanded delimiter list including less common ones
    delimiters = [',', '\t', ';', '|', '~', ':', ' ', '\x01', '\x02', '\x03']
    
    # Strategy 1: Count occurrences (simple frequency)
    delimiter_counts = {delim: sample.count(delim) for delim in delimiters}
    
    # Strategy 2: Count occurrences per line (more accurate for delimited files)
    lines = sample.splitlines()[:100]  # Analyze first 100 lines
    delimiter_per_line = {delim: 0 for delim in delimiters}
    line_count = 0
    
    for line in lines:
        if len(line.strip()) > 0:  # Skip empty lines
            line_count += 1
            for delim in delimiters:
                if delim in line:
                    delimiter_per_line[delim] += 1
    
    # Strategy 3: Consistency check - delimiter should appear in most lines
    delimiter_consistency = {}
    for delim in delimiters:
        if line_count > 0:
            consistency = delimiter_per_line[delim] / line_count
            delimiter_consistency[delim] = consistency
    
    # Strategy 4: Field count consistency - delimited files have consistent field counts
    delimiter_field_counts = {}
    for delim in delimiters:
        field_counts = []
        for line in lines[:20]:  # Check first 20 lines
            if len(line.strip()) > 0:
                fields = line.split(delim)
                field_counts.append(len(fields))
        
        if len(field_counts) > 1:
            # Calculate consistency (lower std dev = more consistent)
            import statistics
            try:
                std_dev = statistics.stdev(field_counts) if len(field_counts) > 1 else float('inf')
                avg_fields = statistics.mean(field_counts)
                # Prefer delimiters with consistent field counts and reasonable field count
                if avg_fields > 1 and std_dev < avg_fields * 0.1:  # Less than 10% variation
                    delimiter_field_counts[delim] = 1.0 / (1.0 + std_dev / avg_fields)
                else:
                    delimiter_field_counts[delim] = 0
            except:
                delimiter_field_counts[delim] = 0
        else:
            delimiter_field_counts[delim] = 0
    
    # Combine strategies with weighted scoring
    scores = {}
    for delim in delimiters:
        # Weight: frequency (30%), consistency (40%), field count consistency (30%)
        freq_score = delimiter_counts.get(delim, 0) / max(max(delimiter_counts.values()), 1)
        consistency_score = delimiter_consistency.get(delim, 0)
        field_score = delimiter_field_counts.get(delim, 0)
        
        # Penalize space delimiter if it's too common (likely not a delimiter)
        if delim == ' ' and freq_score > 0.3:
            freq_score *= 0.1
        
        combined_score = (freq_score * 0.3 + consistency_score * 0.4 + field_score * 0.3)
        scores[delim] = combined_score
    
    # Return delimiter with highest score, fallback to comma
    if scores:
        max_score = max(scores.values())
        if max_score > 0.1:
            def get_score(key: str) -> float:
                return scores[key]
            best_delim = max(scores, key=get_score)
        else:
            best_delim = ','
    else:
        best_delim = ','
    
    return best_delim

def detect_encoding(content: bytes, sample_size: int = 10000) -> str:
    """Intelligently detect file encoding with BOM handling and multiple strategies.
    
    Args:
        content: Raw file bytes.
        sample_size: Number of bytes to sample for detection.
        
    Returns:
        Detected encoding string.
    """
    sample = content[:min(sample_size, len(content))]
    
    # Strategy 1: Check for BOM (Byte Order Mark) - most reliable
    if len(sample) >= 3:
        # UTF-8 BOM: EF BB BF
        if sample[:3] == b'\xef\xbb\xbf':
            return 'utf-8-sig'  # utf-8 with BOM removal
        # UTF-16 LE BOM: FF FE
        if sample[:2] == b'\xff\xfe':
            return 'utf-16-le'
        # UTF-16 BE BOM: FE FF
        if sample[:2] == b'\xfe\xff':
            return 'utf-16-be'
        # UTF-32 LE BOM: FF FE 00 00
        if len(sample) >= 4 and sample[:4] == b'\xff\xfe\x00\x00':
            return 'utf-32-le'
        # UTF-32 BE BOM: 00 00 FE FF
        if len(sample) >= 4 and sample[:4] == b'\x00\x00\xfe\xff':
            return 'utf-32-be'
    
    # Strategy 2: Try chardet if available (good for most cases)
    if HAS_CHARDET:
        try:
            detected = chardet.detect(sample)  # type: ignore[possibly-undefined]
            if detected and detected.get('encoding') and detected.get('confidence', 0) > 0.7:
                encoding = detected['encoding'].lower()
                # Normalize common variations
                if encoding in ['windows-1252', 'cp1252']:
                    return 'cp1252'
                if encoding in ['iso-8859-1', 'latin-1', 'latin1']:
                    return 'latin-1'
                if encoding in ['utf-8', 'utf8']:
                    return 'utf-8'
                if encoding in ['utf-16', 'utf16']:
                    # Try to determine endianness
                    try:
                        sample.decode('utf-16-le')
                        return 'utf-16-le'
                    except:
                        return 'utf-16-be'
                return encoding
        except Exception:
            pass
    
    # Strategy 3: Try to decode with common encodings and check for errors
    # This is more reliable than just checking if decode works
    encoding_scores = {}
    for encoding in ENCODING_FALLBACKS:
        try:
            decoded = sample.decode(encoding, errors='strict')
            # Score based on valid characters and lack of replacement chars
            score = len(decoded) / len(sample) if len(sample) > 0 else 0
            # Bonus for common ASCII/printable characters
            printable_ratio = sum(1 for c in decoded[:1000] if c.isprintable() or c.isspace()) / min(1000, len(decoded))
            encoding_scores[encoding] = score * 0.7 + printable_ratio * 0.3
        except (UnicodeDecodeError, LookupError):
            encoding_scores[encoding] = 0
    
    # Return encoding with highest score
    if encoding_scores:
        max_score = max(encoding_scores.values())
        if max_score > 0.5:
            def get_encoding_score(key: str) -> float:
                return encoding_scores[key]
            best_encoding = max(encoding_scores, key=get_encoding_score)
            return best_encoding
    
    # Strategy 4: Fallback - try each encoding with error handling
    for encoding in ENCODING_FALLBACKS:
        try:
            sample.decode(encoding, errors='strict')
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Last resort: latin-1 can decode any byte sequence (but may produce garbage)
    return 'latin-1'

def detect_delimiter(file_obj: IO[bytes], num_bytes: int = 8192) -> str:
    """Intelligently detect delimiter with multiple fallback strategies.

    Args:
        file_obj: Binary file-like object to read from.
        num_bytes: Number of bytes to read for analysis (increased for better detection).

    Returns:
        Detected delimiter, falling back to comma on errors.
    """
    try:
        content = file_obj.read(num_bytes)
        file_obj.seek(0)
        
        # Try multiple encoding strategies
        encodings_to_try = []
        
        # First, try to detect encoding
        detected_encoding = detect_encoding(content, num_bytes)
        encodings_to_try.append(detected_encoding)
        
        # Add common fallbacks
        for enc in ENCODING_FALLBACKS:
            if enc not in encodings_to_try:
                encodings_to_try.append(enc)
        
        # Try each encoding
        for encoding in encodings_to_try:
            try:
                sample = content.decode(encoding, errors="ignore")
                if len(sample.strip()) > 0:  # Make sure we got valid content
                    delimiter = _detect_delimiter_cached(sample)
                    # Validate delimiter makes sense
                    if delimiter and len(sample) > 100:
                        # Quick sanity check: delimiter should appear in sample
                        if delimiter in sample[:1000]:
                            return delimiter
            except Exception:
                continue
        
        # Fallback to comma
        return ','
    except Exception:
        file_obj.seek(0)
        return ','

def is_fixed_width(file_obj: IO[bytes], num_bytes: int = 2048, min_lines: int = 3) -> bool:
    """Detect if a file appears to be fixed-width format.
    
    Fixed-width files have:
    - Consistent line lengths (within small tolerance)
    - No common delimiters (comma, tab, pipe, etc.)
    - Multiple lines with similar structure
    
    Args:
        file_obj: Binary file-like object to read from.
        num_bytes: Number of bytes to read for analysis.
        min_lines: Minimum number of lines needed for detection.
        
    Returns:
        True if file appears to be fixed-width, False otherwise.
    """
    try:
        content = file_obj.read(num_bytes)
        file_obj.seek(0)
        encoding = detect_encoding(content, num_bytes)
        sample = content.decode(encoding, errors="ignore")
        lines = sample.splitlines()
        
        if len(lines) < min_lines:
            return False
        
        # Check for common delimiters - if found, likely not fixed-width
        common_delimiters = [',', '\t', ';', '|', '~']
        delimiter_counts = {delim: sample.count(delim) for delim in common_delimiters}
        total_chars = len(sample.replace('\n', '').replace('\r', ''))
        
        # If delimiters are very common (>5% of characters), likely delimited
        if total_chars > 0:
            max_delim_ratio = max(delimiter_counts.values()) / total_chars if total_chars > 0 else 0
            if max_delim_ratio > 0.05:
                return False
        
        # Check line length consistency
        line_lengths = [len(line.rstrip('\r\n')) for line in lines if line.strip()]
        if len(line_lengths) < min_lines:
            return False
        
        # Calculate standard deviation of line lengths
        if len(line_lengths) > 1:
            avg_length = sum(line_lengths) / len(line_lengths)
            variance = sum((l - avg_length) ** 2 for l in line_lengths) / len(line_lengths)
            std_dev = variance ** 0.5
            
            # If standard deviation is small relative to average, likely fixed-width
            # Allow 5% variation
            if avg_length > 0 and std_dev / avg_length < 0.05:
                return True
        
        return False
    except Exception:
        file_obj.seek(0)
        return False

def infer_fixed_width_positions(file_obj: IO[bytes], num_bytes: int = 2048, num_lines: int = 100) -> List[Tuple[int, int]]:
    """Infer column positions for a fixed-width file by analyzing whitespace patterns.
    
    Uses a simple heuristic: identifies columns where most lines have non-whitespace
    content, separated by whitespace regions.
    
    Args:
        file_obj: Binary file-like object to read from.
        num_bytes: Number of bytes to read for analysis.
        num_lines: Maximum number of lines to analyze.
        
    Returns:
        List of (start, end) position tuples for each column.
    """
    try:
        content = file_obj.read(num_bytes)
        file_obj.seek(0)
        encoding = detect_encoding(content, num_bytes)
        sample = content.decode(encoding, errors="ignore")
        lines = [line.rstrip('\r\n') for line in sample.splitlines() if line.strip()][:num_lines]
        
        if not lines:
            return []
        
        max_length = max(len(line) for line in lines)
        if max_length == 0:
            return []
        
        # Create a matrix: for each position, count how many lines have non-whitespace
        non_whitespace_count = [0] * max_length
        for line in lines:
            for i, char in enumerate(line):
                if i < max_length and not char.isspace():
                    non_whitespace_count[i] += 1
        
        # Find column boundaries (regions with high non-whitespace density)
        # A column is a region where >50% of lines have non-whitespace
        threshold = len(lines) * 0.3  # At least 30% of lines should have content
        positions = []
        in_column = False
        start = 0
        
        for i in range(max_length):
            has_content = non_whitespace_count[i] > threshold
            if has_content and not in_column:
                # Start of a column
                start = i
                in_column = True
            elif not has_content and in_column:
                # End of a column
                positions.append((start, i))
                in_column = False
        
        # If we ended in a column, close it
        if in_column:
            positions.append((start, max_length))
        
        # Filter out very small columns (likely noise)
        positions = [(s, e) for s, e in positions if e - s >= 2]
        
        return positions
    except Exception:
        file_obj.seek(0)
        return []

@st.cache_data(show_spinner=False)
def _load_claims_df_cached(ext: str, content: bytes, delimiter: Optional[str], has_hdr: Optional[bool]) -> Tuple[Any, bool]:
    """Load a claims file buffer into a DataFrame with format-aware parsing.

    Supports CSV/TSV/TXT, Excel, JSON, and Parquet. Returns the DataFrame and
    a boolean indicating whether the data has headers applied.

    Args:
        ext: Lowercased file extension including dot (e.g., ".csv").
        content: Raw file bytes.
        delimiter: Delimiter for delimited text formats.
        has_hdr: Whether the source contains a header row.

    Returns:
        A tuple of (dataframe_like, has_header).

    Raises:
        ValueError: If JSON parsing fails or extension is unsupported.
    """
    file_like = io.BytesIO(content)
    if ext in ['.csv', '.tsv', '.txt']:
        d = delimiter or ','
        h = 0 if (has_hdr is True) else None
        
        # Detect encoding and try to read with it
        encoding = detect_encoding(content)
        last_error = None
        
        # Try detected encoding first, then fallbacks
        encodings_to_try = [encoding] + [e for e in ENCODING_FALLBACKS if e != encoding]
        
        for enc in encodings_to_try:
            try:
                file_like.seek(0)
                df = pd.read_csv(file_like, delimiter=d, header=h, dtype=str, encoding=enc, on_bad_lines="skip")  # type: ignore[no-untyped-call]
                return df, bool(has_hdr)
            except (UnicodeDecodeError, UnicodeError) as e:
                last_error = e
                file_like.seek(0)
                continue
            except Exception as e:
                # For other errors, try next encoding
                last_error = e
                file_like.seek(0)
                continue
        
        # If all encodings failed, raise the last error
        if last_error:
            raise ValueError(f"Failed to read file with any encoding. Last error: {last_error}")
        raise ValueError("Failed to read file - could not determine encoding")
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_like, dtype=str)  # type: ignore[no-untyped-call]
        return df, True
    elif ext == '.json':
        try:
            data = json.load(io.TextIOWrapper(file_like, encoding="utf-8"))
            df = pd.DataFrame(data) if isinstance(data, list) else pd.json_normalize(data)  # type: ignore[no-untyped-call]
            return df, True
        except Exception as e:
            raise ValueError("Error parsing JSON file") from e
    elif ext == '.parquet':
        df = pd.read_parquet(file_like)  # type: ignore[no-untyped-call]
        return df, True
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def load_claims_file(file: Any) -> Tuple[Any, bool]:
    """Load an uploaded claims file and return parsed data plus header flag.

    Detects delimiter and header when applicable, then delegates to a cached
    loader to parse the content.

    Args:
        file: Streamlit-uploaded file-like object.

    Returns:
        (dataframe_like, has_header_boolean).

    Raises:
        ValueError: If the file type is unsupported.
    """
    ext = os.path.splitext(file.name)[-1].lower()

    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported file type: {ext}")

    file.seek(0)
    content = file.read()
    file.seek(0)
    delimiter = None
    has_hdr = None
    if ext in ['.csv', '.tsv', '.txt']:
        delimiter = detect_delimiter(io.BytesIO(content))
        has_hdr = has_header(io.BytesIO(content), delimiter)
    return _load_claims_df_cached(ext, content, delimiter, has_hdr)

@st.cache_data(show_spinner=False)
def _load_header_row_cached(content: bytes) -> List[str]:
    """Read the first row of an Excel header file and return merged labels.

    Args:
        content: Raw bytes of the header Excel file.

    Returns:
        List of header labels derived from the first row.
    """
    file_like = io.BytesIO(content)
    header_df = pd.read_excel(file_like, nrows=1, header=None)  # type: ignore[no-untyped-call]
    return extract_merged_header(header_df)

def load_header_file(header_file: Any) -> List[str]:
    """Load an external header Excel file and return a header list.

    Args:
        header_file: Streamlit-uploaded file-like object.

    Returns:
        Cleaned list of header strings.
    """
    header_file.seek(0)
    content = header_file.read()
    header_file.seek(0)
    return _load_header_row_cached(content)

def extract_merged_header(header_df: Any) -> List[str]:
    """Merge and clean header labels from the first row of a DataFrame.

    Drops NaNs, trims whitespace, and removes duplicates while preserving order.

    Args:
        header_df: DataFrame-like object containing header data.

    Returns:
        List of unique, cleaned header labels.
    """
    first_row = header_df.iloc[0].tolist()
    merged: List[str] = []
    seen: set[str] = set()

    for col in first_row:
        if pd.isna(col):
            continue
        val = str(col).strip()
        if val and val not in seen:
            merged.append(val)
            seen.add(val)

    return merged

def apply_external_header(df: Any, header_list: List[str]) -> Tuple[Any, bool]:
    """Apply an external header list to a DataFrame if shapes match.

    Args:
        df: DataFrame-like object whose columns will be replaced.
        header_list: Header strings to apply.

    Returns:
        Tuple of (updated_df, applied_flag) where applied_flag is True on success.
    """
    if len(header_list) != df.shape[1]:
        return df, False
    df.columns = header_list
    return df, True

def parse_header_specification_file(header_bytes: bytes, header_ext: str) -> Tuple[List[str], List[Tuple[int, int]]]:
    """Parse a header specification file that contains column metadata.
    
    Expected format: A file with columns like:
    - Column Name / Field Name / Name
    - Start Position / Start / Start_Pos
    - End Position / End / End_Pos
    - Size / Width / Length (optional, can be calculated from start/end)
    
    Args:
        header_bytes: Raw bytes of the header specification file.
        header_ext: File extension (e.g., '.csv', '.xlsx').
        
    Returns:
        Tuple of (column_names_list, colspecs_list) where colspecs is list of (start, end) tuples.
        
    Raises:
        ValueError: If header spec file is empty, unreadable, or missing required columns.
    """
    header_like = io.BytesIO(header_bytes)
    
    try:
        # Read header spec file based on format
        if header_ext in ['.csv', '.txt', '.tsv']:
            encoding = detect_encoding(header_bytes)
            spec_df = pd.read_csv(header_like, encoding=encoding, on_bad_lines="skip")  # type: ignore[no-untyped-call]
        elif header_ext in ['.xlsx', '.xls']:
            spec_df = pd.read_excel(header_like)  # type: ignore[no-untyped-call]
        else:
            raise ValueError(f"Unsupported header specification file format: {header_ext}")
        
        if spec_df.empty:
            raise ValueError("Header specification file is empty")
        
        # Normalize column names (lowercase, strip, replace spaces/underscores)
        spec_df.columns = [str(col).lower().strip().replace(' ', '_').replace('-', '_') for col in spec_df.columns]
        
        # Find relevant columns (case-insensitive, flexible naming)
        name_col = None
        start_col = None
        end_col = None
        size_col = None
        
        # Common variations of column names
        name_variations = ['column_name', 'field_name', 'name', 'column', 'field', 'col_name', 'fieldname']
        start_variations = ['start_position', 'start_pos', 'start', 'startposition', 'begin', 'begin_pos']
        end_variations = ['end_position', 'end_pos', 'end', 'endposition', 'stop', 'stop_pos']
        size_variations = ['size', 'width', 'length', 'column_size', 'field_size', 'col_width']
        
        for col in spec_df.columns:
            col_lower = col.lower()
            if col_lower in name_variations and name_col is None:
                name_col = col
            elif col_lower in start_variations and start_col is None:
                start_col = col
            elif col_lower in end_variations and end_col is None:
                end_col = col
            elif col_lower in size_variations and size_col is None:
                size_col = col
        
        # Validate required columns
        if name_col is None:
            raise ValueError("Header specification file must contain a column name field (e.g., 'Column Name', 'Field Name', 'Name')")
        
        if start_col is None and end_col is None and size_col is None:
            raise ValueError("Header specification file must contain position information (Start/End positions or Size/Width)")
        
        # Extract column names
        column_names = []
        colspecs = []
        
        for _, row in spec_df.iterrows():
            # Get column name
            name_val = row[name_col]
            col_name: Optional[str] = None
            if pd.notna(name_val):  # type: ignore[arg-type]
                col_name = str(name_val).strip()
            if col_name is None or col_name == '' or col_name.lower() in ['nan', 'none']:
                continue
            
            # Get positions
            start_pos: Optional[int] = None
            end_pos: Optional[int] = None
            size: Optional[int] = None
            
            if start_col:
                start_raw = row[start_col] if start_col in row.index else None
                if start_raw is not None:
                    try:
                        if pd.notna(start_raw):  # type: ignore[arg-type]
                            start_pos = int(float(start_raw))
                    except (ValueError, TypeError):
                        pass
            
            if end_col:
                end_raw = row[end_col] if end_col in row.index else None
                if end_raw is not None:
                    try:
                        if pd.notna(end_raw):  # type: ignore[arg-type]
                            end_pos = int(float(end_raw))
                    except (ValueError, TypeError):
                        pass
            
            if size_col:
                size_raw = row[size_col] if size_col in row.index else None
                if size_raw is not None:
                    try:
                        if pd.notna(size_raw):  # type: ignore[arg-type]
                            size = int(float(size_raw))
                    except (ValueError, TypeError):
                        pass
            
            # Calculate missing values
            if start_pos is not None and end_pos is not None:
                # Both provided, use them
                pass
            elif start_pos is not None and size is not None:
                # Start and size provided, calculate end
                end_pos = start_pos + size
            elif end_pos is not None and size is not None:
                # End and size provided, calculate start
                start_pos = end_pos - size
            elif start_pos is not None:
                # Only start provided, try to infer from next column
                # This will be handled in the next iteration
                pass
            else:
                # Missing required information
                continue
            
            # Validate positions
            # After the calculations above, if we reach here, both should be set
            if start_pos is not None and end_pos is not None:  # type: ignore[comparison-overlap]
                # Type narrowing: both are int at this point
                start_final: int = start_pos  # type: ignore[assignment]
                end_final: int = end_pos  # type: ignore[assignment]
                if start_final < 0 or end_final < 0:
                    continue
                if start_final >= end_final:
                    continue
                
                column_names.append(col_name)
                colspecs.append((start_final, end_final))
        
        if not column_names:
            raise ValueError("No valid column specifications found in header file")
        
        # Sort by start position to ensure correct order
        def get_start_pos(item: Tuple[str, Tuple[int, int]]) -> int:
            return item[1][0]
        sorted_pairs = sorted(zip(column_names, colspecs), key=get_start_pos)
        column_names = [name for name, _ in sorted_pairs]
        colspecs = [spec for _, spec in sorted_pairs]
        
        return column_names, colspecs
        
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error reading header specification file: {e}") from e

def process_header_file(header_bytes: bytes, header_ext: str) -> List[str]:
    """Intelligently process header file in either one-column or one-row format.
    
    Supports CSV, TXT, TSV, and Excel files. Automatically detects if headers
    are arranged vertically (one column) or horizontally (one row).
    
    Args:
        header_bytes: Raw bytes of the header file.
        header_ext: File extension (e.g., '.csv', '.xlsx').
        
    Returns:
        List of header strings.
        
    Raises:
        ValueError: If header file is empty or unreadable.
    """
    header_like = io.BytesIO(header_bytes)
    
    try:
        # Read header file based on format
        if header_ext in ['.csv', '.txt', '.tsv']:
            encoding = detect_encoding(header_bytes)
            header_df = pd.read_csv(header_like, header=None, encoding=encoding, on_bad_lines="skip")  # type: ignore[no-untyped-call]
        elif header_ext in ['.xlsx', '.xls']:
            header_df = pd.read_excel(header_like, header=None)  # type: ignore[no-untyped-call]
        else:
            raise ValueError(f"Unsupported header file format: {header_ext}")
        
        if header_df.empty:
            raise ValueError("Header file is empty")
        
        # Detect format: one column (vertical) or one row (horizontal)
        rows, cols = header_df.shape
        
        if rows == 1:
            # One row format (horizontal) - most common
            header_list = header_df.iloc[0].dropna().tolist()
        elif cols == 1:
            # One column format (vertical) - convert to list
            header_list = header_df.iloc[:, 0].dropna().tolist()
        else:
            # Multiple rows and columns - try first row first, then first column
            # Check which has more non-null values
            first_row_count = header_df.iloc[0].notna().sum()
            first_col_count = header_df.iloc[:, 0].notna().sum()
            
            if first_row_count >= first_col_count:
                # Use first row
                header_list = header_df.iloc[0].dropna().tolist()
            else:
                # Use first column
                header_list = header_df.iloc[:, 0].dropna().tolist()
        
        # Clean and validate headers
        header_list = [str(h).strip() for h in header_list if str(h).strip()]
        
        if not header_list:
            raise ValueError("No valid headers found in header file")
        
        return header_list
        
    except Exception as e:
        raise ValueError(f"Error reading header file: {e}") from e

@st.cache_data(show_spinner=False)
def _read_claims_with_header_option_cached(ext: str, content: bytes, headerless: bool, header_bytes: Optional[bytes], delimiter: Optional[str], header_ext: Optional[str] = None, colspecs: Optional[List[Tuple[int, int]]] = None, header_names: Optional[List[str]] = None) -> Any:
    """Parse claims data with optional header handling and caching.

    Reads the claims file according to its extension and applies an external
    header when provided and `headerless` is True.

    Args:
        ext: Lowercased filename or extension.
        content: Raw claims file bytes.
        headerless: Whether the claims file lacks a header row.
        header_bytes: Raw bytes of the external header file, if any.
        delimiter: Delimiter for delimited text formats.
        header_ext: Extension of the header file (for format detection).
        colspecs: Optional list of (start, end) tuples for fixed-width files.
        header_names: Optional list of column names (from header spec file).

    Returns:
        Parsed DataFrame-like object, or empty DataFrame on error.
    """
    file_like = io.BytesIO(content)
    try:
        if ext.endswith(('.csv', '.txt', '.tsv')):
            # Intelligent reading with multiple fallback strategies
            encoding = detect_encoding(content)
            encodings_to_try = [encoding] + [e for e in ENCODING_FALLBACKS if e != encoding]
            last_error = None
            last_df = None
            
            # Check if this is a fixed-width file
            if colspecs is not None and len(colspecs) > 0:
                # Fixed-width file with provided column specifications
                encoding = detect_encoding(content)
                encodings_to_try = [encoding] + [e for e in ENCODING_FALLBACKS if e != encoding]
                last_error = None
                
                for enc in encodings_to_try:
                    try:
                        file_like.seek(0)
                        if headerless:
                            claims_df = pd.read_fwf(file_like, colspecs=colspecs, header=None, encoding=enc, dtype=str)  # type: ignore[no-untyped-call]
                        else:
                            claims_df = pd.read_fwf(file_like, colspecs=colspecs, header=0, encoding=enc, dtype=str)  # type: ignore[no-untyped-call]
                        break  # Success, exit loop
                    except (UnicodeDecodeError, UnicodeError) as e:
                        last_error = e
                        file_like.seek(0)
                        continue
                    except Exception as e:
                        last_error = e
                        file_like.seek(0)
                        continue
                else:
                    if last_error:
                        st.error(f"Error reading fixed-width file: {last_error}")
                    return pd.DataFrame()
            else:
                # Delimited file (CSV/TSV/TXT) - Intelligent reading with fallbacks
                # Strategy 1: Try with detected delimiter and encoding
                detected_delim = delimiter or ','
                delimiters_to_try = [detected_delim]
                
                # Add common alternatives if primary delimiter fails
                if detected_delim != ',':
                    delimiters_to_try.append(',')
                if detected_delim != '\t':
                    delimiters_to_try.append('\t')
                if detected_delim != ';':
                    delimiters_to_try.append(';')
                if detected_delim != '|':
                    delimiters_to_try.append('|')
                
                last_df = None
                last_error = None
                
                for delim in delimiters_to_try:
                    for enc in encodings_to_try:
                        try:
                            file_like.seek(0)
                            # Try with different pandas options for robustness
                            read_options = [
                                # Option 1: Standard read
                                {'delimiter': delim, 'header': None if headerless else 0, 'on_bad_lines': 'skip', 'encoding': enc, 'dtype': str},
                                # Option 2: With quote handling
                                {'delimiter': delim, 'header': None if headerless else 0, 'on_bad_lines': 'skip', 'encoding': enc, 'dtype': str, 'quotechar': '"', 'quoting': 1},
                                # Option 3: With different quote char
                                {'delimiter': delim, 'header': None if headerless else 0, 'on_bad_lines': 'skip', 'encoding': enc, 'dtype': str, 'quotechar': "'", 'quoting': 1},
                                # Option 4: Skip initial space
                                {'delimiter': delim, 'header': None if headerless else 0, 'on_bad_lines': 'skip', 'encoding': enc, 'dtype': str, 'skipinitialspace': True},
                            ]
                            
                            for options in read_options:
                                try:
                                    file_like.seek(0)
                                    claims_df = pd.read_csv(file_like, **options)  # type: ignore[no-untyped-call]
                                    
                                    # Validate DataFrame is reasonable
                                    if claims_df.shape[0] > 0 and claims_df.shape[1] > 0:
                                        # Check for reasonable column count (not too many, not too few)
                                        if 1 <= claims_df.shape[1] <= 1000:
                                            last_df = claims_df
                                            break  # Success!
                                except Exception:
                                    continue
                            
                            if last_df is not None:
                                break  # Success with this delimiter/encoding combo
                        except (UnicodeDecodeError, UnicodeError) as e:
                            last_error = e
                            file_like.seek(0)
                            continue
                        except Exception as e:
                            last_error = e
                            file_like.seek(0)
                            continue
                    
                    if last_df is not None:
                        break  # Success!
                
                # If we got a DataFrame, use it
                if last_df is not None:
                    claims_df = last_df
                else:
                    # All strategies failed
                    if last_error:
                        error_msg = str(last_error)
                        if "codec can't decode" in error_msg:
                            st.error(
                                "❌ Encoding Error: The file appears to be in an unsupported encoding. "
                                "Tried multiple encodings and delimiters. Please try saving the file as UTF-8 or contact support."
                            )
                        else:
                            st.error(f"Error reading claims file: {error_msg}")
                    else:
                        st.error("Error reading claims file: Could not determine file encoding or format. Please check the file format.")
                    return pd.DataFrame()
        elif ext.endswith(('.xlsx', '.xls')):
            claims_df = pd.read_excel(file_like, header=None if headerless else 0)  # type: ignore[no-untyped-call]
        else:
            st.error("Unsupported file format for claims file.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error reading claims file: {e}")
        return pd.DataFrame()

    # Apply header names if provided (from header spec file)
    if header_names is not None and len(header_names) > 0:
        if len(header_names) != claims_df.shape[1]:
            st.error(
                f"❌ Column Mismatch: Header specification has {len(header_names)} columns, "
                f"but claims file has {claims_df.shape[1]} columns. "
                f"Please ensure the header specification matches the number of columns in your claims file."
            )
            st.stop()
        claims_df.columns = header_names
        st.toast("✅ Header specification applied successfully!", icon="✅")
    elif headerless and header_bytes and header_ext:
        try:
            # Try to parse as header specification file first
            try:
                _header_names_from_spec, _colspecs_from_spec = parse_header_specification_file(header_bytes, header_ext)
                # If successful, we already have colspecs and names, so skip regular processing
                # This case is handled above with header_names parameter
                # But if we're here, it means header_names wasn't passed, so try regular processing
                pass
            except ValueError:
                # Not a header spec file, try regular header file processing
                pass
            
            # Use the new intelligent header processing
            header_list = process_header_file(header_bytes, header_ext)
            
            if not header_list:
                st.error("❌ Uploaded header file is empty or unreadable.")
                st.stop()
            if len(header_list) != claims_df.shape[1]:
                st.error(
                    f"❌ Column Mismatch: Header file has {len(header_list)} columns, "
                    f"but claims file has {claims_df.shape[1]} columns. "
                    f"Please ensure the header file matches the number of columns in your claims file."
                )
                st.stop()
            claims_df.columns = header_list
            st.toast("✅ Header applied successfully!", icon="✅")
        except ValueError as e:
            st.error(f"❌ {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"Error reading external header file: {e}")
            return pd.DataFrame()

    return claims_df

def read_claims_with_header_option(file: Any, headerless: bool = False, header_file: Optional[Any] = None, delimiter: Optional[str] = None, colspecs: Optional[List[Tuple[int, int]]] = None, header_names: Optional[List[str]] = None) -> Any:
    """Read claims file, optionally applying an external header.

    Convenience wrapper that reads the file and forwards to the cached parser.

    Args:
        file: Streamlit-uploaded claims file.
        headerless: If True, treat the claims file as having no header row.
        header_file: Optional external header file (CSV, TXT, TSV, or Excel).
        delimiter: Optional delimiter override for text formats.
        colspecs: Optional list of (start, end) tuples for fixed-width files.

    Args:
        file: Streamlit-uploaded claims file.
        headerless: If True, treat the claims file as having no header row.
        header_file: Optional external header file (CSV, TXT, TSV, or Excel).
        delimiter: Optional delimiter override for text formats.
        colspecs: Optional list of (start, end) tuples for fixed-width files.
        header_names: Optional list of column names (from header spec file).

    Returns:
        Parsed DataFrame-like object.
    """
    if not file:
        return pd.DataFrame()
    ext = file.name.lower()
    file.seek(0)
    content = file.read()
    file.seek(0)
    header_bytes = None
    header_ext = None
    if header_file is not None:
        header_file.seek(0)
        header_bytes = header_file.read()
        header_ext = os.path.splitext(header_file.name)[-1].lower()
        header_file.seek(0)
    return _read_claims_with_header_option_cached(ext, content, headerless, header_bytes, delimiter, header_ext, colspecs, header_names)


