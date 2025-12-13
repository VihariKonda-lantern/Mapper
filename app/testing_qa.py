# --- testing_qa.py ---
"""Testing and Quality Assurance features."""
import streamlit as st
import pandas as pd
import json
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

st: Any = st
pd: Any = pd


def create_unit_test(test_name: str, test_func: Callable,
                    expected_result: Any, test_data: Any) -> Dict[str, Any]:
    """Create a unit test.
    
    Args:
        test_name: Name of test
        test_func: Test function
        expected_result: Expected result
        test_data: Test data
        
    Returns:
        Test dictionary
    """
    return {
        "name": test_name,
        "func": test_func,
        "expected_result": expected_result,
        "test_data": test_data,
        "created_at": datetime.now().isoformat()
    }


def run_unit_tests(tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run a suite of unit tests.
    
    Args:
        tests: List of test dictionaries
        
    Returns:
        Test results dictionary
    """
    results = {
        "total": len(tests),
        "passed": 0,
        "failed": 0,
        "test_results": []
    }
    
    for test in tests:
        test_name = test.get("name", "Unknown")
        test_func = test.get("func")
        expected = test.get("expected_result")
        test_data = test.get("test_data")
        
        try:
            actual = test_func(test_data)
            passed = actual == expected
            
            # Check for duplicate info stored in function attribute
            duplicate_info = getattr(test_func, 'duplicate_info', None)
            error_msg = None
            if not passed and duplicate_info:
                error_msg = f"Duplicate mappings found: {duplicate_info}"
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["test_results"].append({
                "name": test_name,
                "passed": passed,
                "expected": expected,
                "actual": actual,
                "error": error_msg
            })
        except Exception as e:
            results["failed"] += 1
            results["test_results"].append({
                "name": test_name,
                "passed": False,
                "error": str(e),
                "expected": expected,
                "actual": None
            })
    
    return results


def generate_test_data(data_type: str, count: int = 100,
                      schema: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Generate synthetic test data.
    
    Args:
        data_type: Type of data (claims, layout, lookup)
        count: Number of records to generate
        schema: Optional schema dictionary
        
    Returns:
        Generated DataFrame
    """
    import random
    import string
    
    if schema is None:
        if data_type == "claims":
            schema = {
                "member_id": "string",
                "claim_id": "string",
                "service_date": "date",
                "diagnosis_code": "string",
                "amount": "float"
            }
        else:
            schema = {"id": "string", "value": "string"}
    
    data = {}
    for col, col_type in schema.items():
        if col_type == "string":
            data[col] = [''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) 
                        for _ in range(count)]
        elif col_type == "int":
            data[col] = [random.randint(1, 1000) for _ in range(count)]
        elif col_type == "float":
            data[col] = [round(random.uniform(1.0, 1000.0), 2) for _ in range(count)]
        elif col_type == "date":
            start_date = datetime(2020, 1, 1)
            data[col] = [(start_date + pd.Timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
                        for _ in range(count)]
        else:
            data[col] = [None for _ in range(count)]
    
    return pd.DataFrame(data)


def run_regression_test(mapping: Dict[str, Dict[str, Any]],
                       known_good_data: pd.DataFrame,
                       expected_output: pd.DataFrame) -> Dict[str, Any]:
    """Run regression test against known good data.
    
    Args:
        mapping: Mapping dictionary
        known_good_data: Known good input data
        expected_output: Expected output data
        
    Returns:
        Test result dictionary
    """
    try:
        # Apply mapping (simplified - would use actual transformation)
        from transformer import transform_claims_data
        actual_output = transform_claims_data(known_good_data, mapping)
        
        # Compare
        matches = actual_output.equals(expected_output)
        
        if not matches:
            # Find differences
            differences = []
            if len(actual_output) != len(expected_output):
                differences.append(f"Row count mismatch: {len(actual_output)} vs {len(expected_output)}")
            else:
                for col in expected_output.columns:
                    if col not in actual_output.columns:
                        differences.append(f"Missing column: {col}")
                    else:
                        if not actual_output[col].equals(expected_output[col]):
                            diff_count = (actual_output[col] != expected_output[col]).sum()
                            differences.append(f"Column '{col}': {diff_count} differences")
        
        return {
            "passed": matches,
            "differences": differences if not matches else [],
            "actual_shape": actual_output.shape,
            "expected_shape": expected_output.shape
        }
    except Exception as e:
        return {
            "passed": False,
            "error": str(e),
            "differences": []
        }


def validate_mapping_correctness(mapping: Dict[str, Dict[str, Any]],
                                test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Test suite for mapping correctness.
    
    Args:
        mapping: Mapping dictionary
        test_cases: List of test case dictionaries
        
    Returns:
        Test results dictionary
    """
    results = {
        "total_tests": len(test_cases),
        "passed": 0,
        "failed": 0,
        "test_results": []
    }
    
    for test_case in test_cases:
        field = test_case.get("field")
        input_value = test_case.get("input_value")
        expected_output = test_case.get("expected_output")
        
        if field not in mapping:
            results["failed"] += 1
            results["test_results"].append({
                "field": field,
                "passed": False,
                "error": "Field not in mapping"
            })
            continue
        
        # Apply mapping transformation (simplified)
        source_col = mapping[field].get("value")
        if source_col:
            # In real implementation, would apply actual transformation
            actual_output = input_value  # Placeholder
        
        passed = actual_output == expected_output
        
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        results["test_results"].append({
            "field": field,
            "passed": passed,
            "expected": expected_output,
            "actual": actual_output
        })
    
    return results


def generate_test_data_from_claims(claims_df: Any, count: int = 100) -> pd.DataFrame:
    """Generate test data that replicates the claims file structure with realistic dummy data.
    
    Analyzes actual data patterns (formats, lengths, ranges, value distributions) and generates
    test data that matches those patterns.
    
    Args:
        claims_df: Original claims DataFrame
        count: Number of records to generate
        
    Returns:
        Generated DataFrame with same structure as claims_df, with realistic data patterns
    """
    import random
    import string
    import re
    from datetime import datetime, timedelta
    from collections import Counter
    
    data = {}
    
    # Sample a subset of actual data for pattern analysis (max 1000 rows for performance)
    sample_size = min(1000, len(claims_df))
    sample_df = claims_df.head(sample_size) if sample_size > 0 else claims_df
    
    for col in claims_df.columns:
        col_dtype = str(claims_df[col].dtype).lower()
        col_lower = col.lower()
        
        # Get non-null sample values for pattern analysis
        sample_values = sample_df[col].dropna().astype(str).tolist()
        non_empty_samples = [v for v in sample_values if v.strip()]
        
        if not non_empty_samples:
            # If no samples, use default generation
            data[col] = [None for _ in range(count)]
            continue
        
        # Analyze patterns from actual data
        sample_lengths = [len(str(v)) for v in non_empty_samples[:100]]
        avg_length = int(sum(sample_lengths) / len(sample_lengths)) if sample_lengths else 10
        min_length = min(sample_lengths) if sample_lengths else 1
        max_length = max(sample_lengths) if sample_lengths else 20
        
        # Check if values follow a pattern (numeric, alphanumeric, date format, etc.)
        first_few = non_empty_samples[:10]
        
        # Detect date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',   # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',   # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',   # YYYY/MM/DD
        ]
        is_date = False
        date_format = None
        if 'date' in col_lower or 'dob' in col_lower or col_dtype.startswith('datetime'):
            is_date = True
            # Detect date format from samples
            for pattern in date_patterns:
                if any(re.match(pattern, str(v)) for v in first_few):
                    date_format = pattern
                    break
            if not date_format:
                date_format = '%Y-%m-%d'  # Default
        
        # Detect numeric patterns
        is_numeric = False
        is_integer = False
        numeric_range = None
        if col_dtype.startswith('int') or all(str(v).replace('-', '').replace('.', '').isdigit() for v in first_few if v):
            is_numeric = True
            is_integer = col_dtype.startswith('int') or all('.' not in str(v) for v in first_few if v)
            try:
                numeric_values = [float(str(v).replace(',', '')) for v in non_empty_samples[:100] if str(v).replace('-', '').replace('.', '').replace(',', '').isdigit()]
                if numeric_values:
                    numeric_range = (min(numeric_values), max(numeric_values))
            except:
                pass
        
        # Detect ID/code patterns (alphanumeric, specific length, prefixes, etc.)
        is_id_like = 'id' in col_lower or 'code' in col_lower
        id_pattern = None
        if is_id_like and non_empty_samples:
            # Check if IDs have consistent format
            sample_id = str(non_empty_samples[0])
            if sample_id.isdigit():
                id_pattern = 'numeric'
            elif sample_id.isalnum():
                id_pattern = 'alphanumeric'
            elif any(c.isalpha() for c in sample_id) and any(c.isdigit() for c in sample_id):
                id_pattern = 'mixed'
            else:
                id_pattern = 'string'
        
        # Generate data based on analyzed patterns
        if is_date:
            # Generate dates in the detected format
            start_date = datetime(2020, 1, 1)
            dates = [(start_date + timedelta(days=random.randint(0, 1825))) for _ in range(count)]
            
            if date_format == r'\d{2}/\d{2}/\d{4}':
                data[col] = [d.strftime("%m/%d/%Y") for d in dates]
            elif date_format == r'\d{2}-\d{2}-\d{4}':
                data[col] = [d.strftime("%m-%d-%Y") for d in dates]
            elif date_format == r'\d{4}/\d{2}/\d{2}':
                data[col] = [d.strftime("%Y/%m/%d") for d in dates]
            else:
                data[col] = [d.strftime("%Y-%m-%d") for d in dates]
                
        elif is_numeric and numeric_range:
            # Generate numbers within actual range
            min_val, max_val = numeric_range
            if is_integer:
                data[col] = [random.randint(int(min_val), int(max_val)) for _ in range(count)]
            else:
                # Preserve decimal places from samples
                decimals = 2
                sample_decimals = [len(str(v).split('.')[-1]) if '.' in str(v) else 0 for v in first_few]
                if sample_decimals:
                    decimals = max(sample_decimals)
                data[col] = [round(random.uniform(min_val, max_val), decimals) for _ in range(count)]
        elif is_id_like and id_pattern:
            # Generate IDs matching the pattern
            if id_pattern == 'numeric':
                # Generate numeric IDs with similar length
                data[col] = [str(random.randint(10**(min_length-1), 10**max_length - 1))[:max_length] 
                            for _ in range(count)]
            elif id_pattern == 'alphanumeric':
                # Generate alphanumeric IDs with similar length
                chars = string.ascii_uppercase + string.digits
                data[col] = [''.join(random.choices(chars, k=random.randint(min_length, max_length)))
                            for _ in range(count)]
            else:
                # Mixed pattern - analyze character distribution
                chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
                data[col] = [''.join(random.choices(chars, k=random.randint(min_length, max_length)))
                            for _ in range(count)]
        elif 'name' in col_lower:
            # Extract actual names from samples if available
            name_samples = [v for v in non_empty_samples if any(c.isalpha() for c in str(v))]
            if name_samples and len(name_samples) > 5:
                # Use actual name patterns
                data[col] = [random.choice(name_samples) for _ in range(count)]
            else:
                # Generate fake names
                first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank", 
                             "Michael", "Sarah", "David", "Emily", "James", "Lisa", "Robert", "Maria"]
                last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                            "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]
                if 'first' in col_lower:
                    data[col] = [random.choice(first_names) for _ in range(count)]
                elif 'last' in col_lower:
                    data[col] = [random.choice(last_names) for _ in range(count)]
                else:
                    data[col] = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(count)]
        else:
            # For other strings, use actual value patterns if available
            if len(non_empty_samples) > 10:
                # Use actual samples with some variation
                data[col] = [random.choice(non_empty_samples) for _ in range(count)]
            else:
                # Generate strings matching length patterns
                chars = string.ascii_letters + string.digits + " -_"
                data[col] = [''.join(random.choices(chars, k=random.randint(min_length, max_length)))
                            for _ in range(count)]
    
    return pd.DataFrame(data)


def generate_test_data_from_layout(layout_df: Any, count: int = 100) -> pd.DataFrame:
    """Generate test data based on layout schema with realistic dummy data.
    
    Uses the actual claims data if available to match patterns, otherwise generates
    data based on field name patterns.
    
    Args:
        layout_df: Layout DataFrame
        count: Number of records to generate
        
    Returns:
        Generated DataFrame with columns matching Internal Field names
    """
    import random
    import string
    import re
    from datetime import datetime, timedelta
    
    data = {}
    
    # Try to get actual claims data to match patterns
    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})
    
    for _, row in layout_df.iterrows():
        field_name = row.get("Internal Field", "")
        if not field_name:
            continue
        
        field_lower = field_name.lower()
        
        # Try to find mapped column in claims data to match patterns
        mapped_col = None
        if field_name in final_mapping:
            mapped_col = final_mapping[field_name].get("value")
        
        # If we have claims data and a mapping, use actual patterns
        if claims_df is not None and mapped_col and mapped_col in claims_df.columns:
            sample_values = claims_df[mapped_col].dropna().astype(str).tolist()
            non_empty_samples = [v for v in sample_values if v.strip()]
            
            if non_empty_samples:
                # Use actual value patterns
                if len(non_empty_samples) > 10:
                    data[field_name] = [random.choice(non_empty_samples) for _ in range(count)]
                else:
                    # Analyze pattern and generate similar
                    sample_lengths = [len(str(v)) for v in non_empty_samples]
                    avg_length = int(sum(sample_lengths) / len(sample_lengths)) if sample_lengths else 10
                    
                    first_few = non_empty_samples[:5]
                    if all(str(v).replace('-', '').replace('.', '').isdigit() for v in first_few if v):
                        # Numeric pattern
                        try:
                            numeric_values = [float(str(v).replace(',', '')) for v in non_empty_samples if str(v).replace('-', '').replace('.', '').replace(',', '').isdigit()]
                            if numeric_values:
                                min_val, max_val = min(numeric_values), max(numeric_values)
                                data[field_name] = [round(random.uniform(min_val, max_val), 2) for _ in range(count)]
                            else:
                                data[field_name] = [random.choice(non_empty_samples) for _ in range(count)]
                        except:
                            data[field_name] = [random.choice(non_empty_samples) for _ in range(count)]
                    else:
                        # String pattern - use actual samples
                        data[field_name] = [random.choice(non_empty_samples) for _ in range(count)]
                continue
        
        # Fallback: Generate based on field name patterns
        if 'date' in field_lower or 'dob' in field_lower:
            start_date = datetime(2020, 1, 1)
            data[field_name] = [(start_date + timedelta(days=random.randint(0, 1825))).strftime("%Y-%m-%d")
                               for _ in range(count)]
        elif 'id' in field_lower or 'code' in field_lower:
            # Generate IDs with reasonable length
            chars = string.ascii_uppercase + string.digits
            data[field_name] = [''.join(random.choices(chars, k=random.randint(8, 12)))
                               for _ in range(count)]
        elif 'amount' in field_lower or 'cost' in field_lower or 'price' in field_lower or 'fee' in field_lower:
            # Generate monetary values
            data[field_name] = [round(random.uniform(10.0, 5000.0), 2) for _ in range(count)]
        elif 'name' in field_lower:
            first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank",
                         "Michael", "Sarah", "David", "Emily", "James", "Lisa", "Robert", "Maria"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                        "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]
            if 'first' in field_lower:
                data[field_name] = [random.choice(first_names) for _ in range(count)]
            elif 'last' in field_lower:
                data[field_name] = [random.choice(last_names) for _ in range(count)]
            else:
                data[field_name] = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(count)]
        elif 'phone' in field_lower or 'tel' in field_lower:
            # Generate phone numbers
            data[field_name] = [f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                               for _ in range(count)]
        elif 'email' in field_lower:
            # Generate emails
            domains = ["example.com", "test.com", "sample.org", "demo.net"]
            names = ["user", "test", "sample", "demo", "john", "jane"]
            data[field_name] = [f"{random.choice(names)}{random.randint(1, 999)}@{random.choice(domains)}"
                               for _ in range(count)]
        elif 'zip' in field_lower or 'postal' in field_lower:
            # Generate zip codes
            data[field_name] = [f"{random.randint(10000, 99999)}" for _ in range(count)]
        else:
            # Default: generate reasonable strings
            chars = string.ascii_letters + string.digits + " -_"
            data[field_name] = [''.join(random.choices(chars, k=random.randint(5, 20)))
                               for _ in range(count)]
    
    return pd.DataFrame(data)


def create_mapping_unit_tests(final_mapping: Dict[str, Dict[str, Any]], 
                             claims_df: Any, 
                             layout_df: Any) -> List[Dict[str, Any]]:
    """Create unit tests for mapping automatically.
    
    Args:
        final_mapping: Final mapping dictionary
        claims_df: Claims DataFrame
        layout_df: Layout DataFrame
        
    Returns:
        List of test dictionaries
    """
    tests = []
    
    # Test 1: All required fields are mapped
    if layout_df is not None:
        usage_normalized = layout_df["Usage"].astype(str).str.strip().str.lower()
        required_fields = layout_df[usage_normalized == "required"]["Internal Field"].tolist()
        
        def test_required_fields_mapped(_: Any) -> bool:
            for field in required_fields:
                if field not in final_mapping or not final_mapping[field].get("value"):
                    return False
            return True
        
        tests.append({
            "name": "All Required Fields Mapped",
            "func": test_required_fields_mapped,
            "expected_result": True,
            "test_data": None
        })
    
    # Test 2: Mapped columns exist in claims file
    if claims_df is not None:
        def test_mapped_columns_exist(_: Any) -> bool:
            for field, mapping_info in final_mapping.items():
                source_col = mapping_info.get("value", "")
                if source_col and source_col not in claims_df.columns:
                    return False
            return True
        
        tests.append({
            "name": "All Mapped Columns Exist in Claims File",
            "func": test_mapped_columns_exist,
            "expected_result": True,
            "test_data": None
        })
    
    # Test 3: No duplicate column mappings
    def test_no_duplicate_mappings(_: Any) -> bool:
        mapped_cols = [info.get("value") for info in final_mapping.values() if info.get("value")]
        unique_cols = set(mapped_cols)
        has_duplicates = len(mapped_cols) != len(unique_cols)
        
        # Store duplicate info for error message
        if has_duplicates:
            from collections import Counter
            col_counts = Counter(mapped_cols)
            field_to_col = {}
            for field, info in final_mapping.items():
                source_col = info.get("value", "")
                if source_col:
                    if source_col not in field_to_col:
                        field_to_col[source_col] = []
                    field_to_col[source_col].append(field)
            
            duplicates = {col: field_to_col[col] for col, count in col_counts.items() if count > 1}
            dup_messages = [f"'{col}' mapped to {len(fields)} fields: {', '.join(fields)}" 
                          for col, fields in duplicates.items()]
            # Store in a way that can be accessed for error message
            test_no_duplicate_mappings.duplicate_info = "; ".join(dup_messages)
        else:
            test_no_duplicate_mappings.duplicate_info = None
        
        return not has_duplicates
    
    tests.append({
        "name": "No Duplicate Column Mappings",
        "func": test_no_duplicate_mappings,
        "expected_result": True,
        "test_data": None
    })
    
    # Test 4: Mapping can be transformed
    if claims_df is not None and final_mapping:
        def test_mapping_transformable(_: Any) -> bool:
            try:
                from transformer import transform_claims_data
                transformed = transform_claims_data(claims_df.head(10), final_mapping)
                return transformed is not None and not transformed.empty
            except Exception:
                return False
        
        tests.append({
            "name": "Mapping Can Be Transformed",
            "func": test_mapping_transformable,
            "expected_result": True,
            "test_data": None
        })
    
    return tests

