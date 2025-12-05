# --- file_handler.py ---
import pandas as pd
import csv
import json
import os
from typing import Tuple, List, Any, Optional, IO
import streamlit as st

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

def detect_delimiter(file_obj: IO[bytes], num_bytes: int = 2048) -> str:
    try:
        sample = file_obj.read(num_bytes).decode("utf-8", errors="ignore")
        file_obj.seek(0)
        delimiters = [',', '\t', ';', '|', '~']
        delimiter_counts = {delim: sample.count(delim) for delim in delimiters}
        best_delimiter = max(delimiter_counts, key=lambda k: delimiter_counts.get(k, 0))
        return best_delimiter
    except Exception:
        file_obj.seek(0)
        return ','

def load_claims_file(file: Any) -> Tuple[pd.DataFrame, bool]:
    ext = os.path.splitext(file.name)[-1].lower()

    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported file type: {ext}")

    file.seek(0)
    if ext in ['.csv', '.tsv', '.txt']:
        delimiter = detect_delimiter(file)
        has_hdr = has_header(file, delimiter)
        df = pd.read_csv(file, delimiter=delimiter, header=0 if has_hdr else None, dtype=str)  # type: ignore[no-untyped-call]
        return df, has_hdr

    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file, dtype=str)  # type: ignore[no-untyped-call]
        return df, True

    elif ext == '.json':
        try:
            data = json.load(file)
            df = pd.DataFrame(data) if isinstance(data, list) else pd.json_normalize(data)  # type: ignore[no-untyped-call]
            return df, True
        except Exception as e:
            raise ValueError("Error parsing JSON file") from e

    elif ext == '.parquet':
        df = pd.read_parquet(file)  # type: ignore[no-untyped-call]
        return df, True

    raise ValueError(f"Unsupported file extension: {ext}")

def load_header_file(header_file: Any) -> List[str]:
    header_df = pd.read_excel(header_file, nrows=1, header=None)  # type: ignore[no-untyped-call]
    return extract_merged_header(header_df)

def extract_merged_header(header_df: pd.DataFrame) -> List[str]:
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

def apply_external_header(df: pd.DataFrame, header_list: List[str]) -> Tuple[pd.DataFrame, bool]:
    if len(header_list) != df.shape[1]:
        return df, False
    df.columns = header_list
    return df, True

def read_claims_with_header_option(file: Any, headerless: bool = False, header_file: Optional[Any] = None, delimiter: Optional[str] = None) -> pd.DataFrame:
    if not file:
        return pd.DataFrame()

    ext = file.name.lower()
    claims_df = pd.DataFrame()

    try:
        if ext.endswith(('.csv', '.txt', '.tsv')):
            if headerless:
                claims_df = pd.read_csv(file, delimiter=delimiter or ',', header=None, on_bad_lines="skip")  # type: ignore[no-untyped-call]
            else:
                claims_df = pd.read_csv(file, delimiter=delimiter or ',', on_bad_lines="skip")  # type: ignore[no-untyped-call]
        elif ext.endswith(('.xlsx', '.xls')):
            claims_df = pd.read_excel(file, header=None if headerless else 0)  # type: ignore[no-untyped-call]
        else:
            st.error("Unsupported file format for claims file.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error reading claims file: {e}")
        return pd.DataFrame()

    # --- Apply external header if needed ---
    if headerless and header_file:
        header_ext = header_file.name.lower()
        try:
            if header_ext.endswith(('.csv', '.txt', '.tsv')):
                header_df = pd.read_csv(header_file, header=None)  # type: ignore[no-untyped-call]
                header_list = header_df.iloc[0].dropna().tolist()
            elif header_ext.endswith(('.xlsx', '.xls')):
                header_df = pd.read_excel(header_file, header=None)  # type: ignore[no-untyped-call]
                header_list = header_df.iloc[0].dropna().tolist()
            else:
                st.error("Unsupported file format for external header.")
                return pd.DataFrame()

            if not header_list:
                st.error("❌ Uploaded header file is empty or unreadable.")
                st.stop()

            if len(header_list) != claims_df.shape[1]:
                st.warning(
                    f"⚠️ Mismatch: Header file has {len(header_list)} columns, "
                    f"but claims file has {claims_df.shape[1]} columns."
                )
                st.markdown(
                    """
                    <div style="background-color:#fff3cd; border:1px solid #ffeeba; padding:16px; border-radius:8px;">
                    <strong>Why this happens:</strong><br>
                    - Merged cells across columns<br>
                    - Extra blank rows<br>
                    - Missing values causing shifts<br><br>
                    <strong>How to fix it:</strong><br>
                    - Open header file<br>
                    - Remove merged cells<br>
                    - Make sure only <u>one clean row</u> is there<br>
                    - Reupload after fixing
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.stop()

            claims_df.columns = header_list
            st.toast(f"✅ Header '{header_file.name}' applied successfully!", icon="✅")

        except Exception as e:
            st.error(f"Error reading external header file: {e}")
            return pd.DataFrame()

    return claims_df


