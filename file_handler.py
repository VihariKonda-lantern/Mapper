# --- file_handler.py ---
# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
import csv
import json
import os
import io
from typing import Tuple, List, Any, Optional, IO
import streamlit as st  # type: ignore[import-not-found]
from typing import cast

st = cast(Any, st)
pd = cast(Any, pd)

SUPPORTED_FORMATS = ('.csv', '.txt', '.tsv', '.xlsx', '.xls', '.json', '.parquet')

def clean_header_row(header_list: List[str]) -> List[str]:
    """
    Cleans the header row: removes NaNs, trims spaces, fills missing values.
    De-duplicates columns by adding suffixes if needed.
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
    file.seek(0)
    try:
        sniffer = csv.Sniffer()
        sample = file.read(sample_size).decode("utf-8", errors="ignore")
        file.seek(0)
        return sniffer.has_header(sample)
    except Exception:
        file.seek(0)
        return False

@st.cache_data(show_spinner=False)
def _detect_delimiter_cached(sample: str) -> str:
    delimiters = [',', '\t', ';', '|', '~']
    delimiter_counts = {delim: sample.count(delim) for delim in delimiters}
    return max(delimiter_counts, key=lambda k: delimiter_counts.get(k, 0))

def detect_delimiter(file_obj: IO[bytes], num_bytes: int = 2048) -> str:
    try:
        sample = file_obj.read(num_bytes).decode("utf-8", errors="ignore")
        file_obj.seek(0)
        return _detect_delimiter_cached(sample)
    except Exception:
        file_obj.seek(0)
        return ','

@st.cache_data(show_spinner=False)
def _load_claims_df_cached(ext: str, content: bytes, delimiter: Optional[str], has_hdr: Optional[bool]) -> Tuple[Any, bool]:
    file_like = io.BytesIO(content)
    if ext in ['.csv', '.tsv', '.txt']:
        d = delimiter or ','
        h = 0 if (has_hdr is True) else None
        df = pd.read_csv(file_like, delimiter=d, header=h, dtype=str)  # type: ignore[no-untyped-call]
        return df, bool(has_hdr)
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
    file_like = io.BytesIO(content)
    header_df = pd.read_excel(file_like, nrows=1, header=None)  # type: ignore[no-untyped-call]
    return extract_merged_header(header_df)

def load_header_file(header_file: Any) -> List[str]:
    header_file.seek(0)
    content = header_file.read()
    header_file.seek(0)
    return _load_header_row_cached(content)

def extract_merged_header(header_df: Any) -> List[str]:
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
    if len(header_list) != df.shape[1]:
        return df, False
    df.columns = header_list
    return df, True

@st.cache_data(show_spinner=False)
def _read_claims_with_header_option_cached(ext: str, content: bytes, headerless: bool, header_bytes: Optional[bytes], delimiter: Optional[str]) -> Any:
    file_like = io.BytesIO(content)
    try:
        if ext.endswith(('.csv', '.txt', '.tsv')):
            if headerless:
                claims_df = pd.read_csv(file_like, delimiter=delimiter or ',', header=None, on_bad_lines="skip")  # type: ignore[no-untyped-call]
            else:
                claims_df = pd.read_csv(file_like, delimiter=delimiter or ',', on_bad_lines="skip")  # type: ignore[no-untyped-call]
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


