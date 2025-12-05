import difflib
import pandas as pd
from typing import Dict, List, Any

import re
from typing import List

def guess_column_type(values: List[str]) -> str:
    """
    Very simple guess of column type based on sample values.
    """
    numeric_count = 0
    text_count = 0
    date_count = 0

    for v in values:
        v = str(v).strip()
        if re.match(r'^\d{5}(-\d{4})?$', v):  # ZIP
            numeric_count += 1
        elif re.match(r'^\d{10}$', v):  # NPI
            numeric_count += 1
        elif re.match(r'^\d{5}$', v):  # CPT
            numeric_count += 1
        elif re.match(r'^[A-TV-Z][0-9][0-9A-TV-Z].*$', v, re.IGNORECASE):  # ICD-10
            text_count += 1
        elif re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', v):  # Basic date
            date_count += 1
        else:
            text_count += 1

    counts = {"numeric": numeric_count, "text": text_count, "date": date_count}
    return max(counts, key=lambda k: counts.get(k, 0))

def match_known_patterns(values: List[str]) -> str:
    """
    Try to match known structures like ICD, CPT, NPI, ZIP.
    """
    for v in values:
        v = str(v).strip()
        if re.match(r'^[A-TV-Z][0-9][0-9A-TV-Z].*$', v, re.IGNORECASE):
            return "icd"
        elif re.match(r'^\d{5}$', v):
            return "cpt"
        elif re.match(r'^\d{10}$', v):
            return "npi"
        elif re.match(r'^\d{5}(-\d{4})?$', v):
            return "zip"
    return "unknown"

def get_enhanced_automap(layout_df: pd.DataFrame, claims_df: pd.DataFrame, threshold: float = 0.6) -> Dict[str, Dict[str, Any]]:
    """
    Suggests best source column for each internal field using enhanced heuristics:
    fuzzy match, sample value matching, regex pattern detection, and type guessing.
    """
    suggestions: Dict[str, Dict[str, Any]] = {}
    internal_fields: List[str] = [str(x) for x in layout_df["Internal Field"].dropna().tolist()]  # type: ignore[no-untyped-call]
    examples = dict(zip(layout_df["Internal Field"], layout_df.get("Example Value", "")))  # type: ignore[no-untyped-call]
    source_columns: List[str] = claims_df.columns.tolist()

    for internal in internal_fields:
        best_match = None
        best_score = 0

        expected_example = examples.get(internal, "")
        expected_type = "text"
        if any(keyword in internal.lower() for keyword in ["zip", "npi", "cpt", "icd", "date", "dob"]):
            expected_type = "numeric" if "zip" in internal.lower() or "npi" in internal.lower() or "cpt" in internal.lower() else "text"

        for source in source_columns:
            # Step 1: Fuzzy match score
            name_score = difflib.SequenceMatcher(None, internal.lower(), source.lower()).ratio()

            # Step 2: Sample value related boosts
            sample_values = claims_df[source].dropna().astype(str).head(5).tolist()  # type: ignore[no-untyped-call]

            # Example match boost
            example_boost = 0
            if expected_example:
                for sample in sample_values:
                    if expected_example.lower() in sample.lower():
                        example_boost = 0.2
                        break

            # Regex structure boost
            regex_boost = 0
            pattern = match_known_patterns(sample_values)
            if pattern in ["icd", "cpt", "npi", "zip"]:
                regex_boost = 0.15

            # Data type boost
            type_boost = 0
            column_type = guess_column_type(sample_values)
            if expected_type == column_type:
                type_boost = 0.1

            # Final Score
            total_score = name_score + example_boost + regex_boost + type_boost

            if total_score > best_score and total_score >= threshold:
                best_score = total_score
                best_match = source

        if best_match:
            suggestions[internal] = {
                "value": best_match,
                "score": round(best_score * 100, 2)
            }

    return suggestions

