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
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

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
    """Heuristically select the most common delimiter from a text sample.

    Args:
        sample: Text content to analyze.

    Returns:
        The delimiter with the highest frequency among common candidates.
    """
    delimiters = [',', '\t', ';', '|', '~']
    delimiter_counts = {delim: sample.count(delim) for delim in delimiters}
    return max(delimiter_counts, key=lambda k: delimiter_counts.get(k, 0))

def detect_encoding(content: bytes, sample_size: int = 10000) -> str:
    """Detect file encoding using chardet, with fallback to common encodings.
    
    Args:
        content: Raw file bytes.
        sample_size: Number of bytes to sample for detection.
        
    Returns:
        Detected encoding string.
    """
    # Try chardet first if available
    if HAS_CHARDET:
        try:
            sample = content[:min(sample_size, len(content))]
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
                return encoding
        except Exception:
            pass
    
    # Fallback: try each encoding until one works
    for encoding in ENCODING_FALLBACKS:
        try:
            sample = content[:min(sample_size, len(content))]
            sample.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Last resort: latin-1 can decode any byte sequence
    return 'latin-1'

def detect_delimiter(file_obj: IO[bytes], num_bytes: int = 2048) -> str:
    """Read a short sample from a file and infer the delimiter.

    Args:
        file_obj: Binary file-like object to read from.
        num_bytes: Number of bytes to read for analysis.

    Returns:
        Detected delimiter, falling back to comma on errors.
    """
    try:
        content = file_obj.read(num_bytes)
        file_obj.seek(0)
        encoding = detect_encoding(content, num_bytes)
        sample = content.decode(encoding, errors="ignore")
        return _detect_delimiter_cached(sample)
    except Exception:
        file_obj.seek(0)
        return ','

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

@st.cache_data(show_spinner=False)
def _read_claims_with_header_option_cached(ext: str, content: bytes, headerless: bool, header_bytes: Optional[bytes], delimiter: Optional[str]) -> Any:
    """Parse claims data with optional header handling and caching.

    Reads the claims file according to its extension and applies an external
    header when provided and `headerless` is True.

    Args:
        ext: Lowercased filename or extension.
        content: Raw claims file bytes.
        headerless: Whether the claims file lacks a header row.
        header_bytes: Raw bytes of the external header file, if any.
        delimiter: Delimiter for delimited text formats.

    Returns:
        Parsed DataFrame-like object, or empty DataFrame on error.
    """
    file_like = io.BytesIO(content)
    try:
        if ext.endswith(('.csv', '.txt', '.tsv')):
            # Detect encoding and try multiple encodings if needed
            encoding = detect_encoding(content)
            encodings_to_try = [encoding] + [e for e in ENCODING_FALLBACKS if e != encoding]
            last_error = None
            
            for enc in encodings_to_try:
                try:
                    file_like.seek(0)
                    if headerless:
                        claims_df = pd.read_csv(file_like, delimiter=delimiter or ',', header=None, on_bad_lines="skip", encoding=enc)  # type: ignore[no-untyped-call]
                    else:
                        claims_df = pd.read_csv(file_like, delimiter=delimiter or ',', on_bad_lines="skip", encoding=enc)  # type: ignore[no-untyped-call]
                    break  # Success, exit loop
                except (UnicodeDecodeError, UnicodeError) as e:
                    last_error = e
                    file_like.seek(0)
                    continue
                except Exception as e:
                    # For other errors, try next encoding
                    last_error = e
                    file_like.seek(0)
                    continue
            else:
                # If loop completed without break, all encodings failed
                if last_error:
                    error_msg = str(last_error)
                    if "codec can't decode" in error_msg:
                        st.error(
                            "❌ Encoding Error: The file appears to be in an unsupported encoding. "
                            "Please try saving the file as UTF-8 or contact support."
                        )
                    else:
                        st.error(f"Error reading claims file: {error_msg}")
                else:
                    st.error("Error reading claims file: Could not determine file encoding")
                return pd.DataFrame()
        elif ext.endswith(('.xlsx', '.xls')):
            claims_df = pd.read_excel(file_like, header=None if headerless else 0)  # type: ignore[no-untyped-call]
        else:
            st.error("Unsupported file format for claims file.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error reading claims file: {e}")
        return pd.DataFrame()

    if headerless and header_bytes:
        header_like = io.BytesIO(header_bytes)
        try:
            header_df = pd.read_excel(header_like, header=None)  # type: ignore[no-untyped-call]
            header_list = header_df.iloc[0].dropna().tolist()
            if not header_list:
                st.error("❌ Uploaded header file is empty or unreadable.")
                st.stop()
            if len(header_list) != claims_df.shape[1]:
                st.warning(
                    f"⚠️ Mismatch: Header file has {len(header_list)} columns, "
                    f"but claims file has {claims_df.shape[1]} columns."
                )
                st.stop()
            claims_df.columns = header_list
            st.toast("✅ Header applied successfully!", icon="✅")
        except Exception as e:
            st.error(f"Error reading external header file: {e}")
            return pd.DataFrame()

    return claims_df

def read_claims_with_header_option(file: Any, headerless: bool = False, header_file: Optional[Any] = None, delimiter: Optional[str] = None) -> Any:
    """Read claims file, optionally applying an external header.

    Convenience wrapper that reads the file and forwards to the cached parser.

    Args:
        file: Streamlit-uploaded claims file.
        headerless: If True, treat the claims file as having no header row.
        header_file: Optional external header Excel file.
        delimiter: Optional delimiter override for text formats.

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
    if header_file is not None:
        header_file.seek(0)
        header_bytes = header_file.read()
        header_file.seek(0)
    return _read_claims_with_header_option_cached(ext, content, headerless, header_bytes, delimiter)


