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
    """Generate test data that replicates the claims file structure with dummy data.
    
    Args:
        claims_df: Original claims DataFrame
        count: Number of records to generate
        
    Returns:
        Generated DataFrame with same structure as claims_df
    """
    import random
    import string
    from datetime import datetime, timedelta
    
    data = {}
    
    for col in claims_df.columns:
        col_dtype = str(claims_df[col].dtype).lower()
        
        # Generate dummy data based on column type and name
        if 'date' in col.lower() or 'dob' in col.lower() or col_dtype.startswith('datetime'):
            start_date = datetime(2020, 1, 1)
            data[col] = [(start_date + timedelta(days=random.randint(0, 1825))).strftime("%Y-%m-%d")
                        for _ in range(count)]
        elif 'id' in col.lower() or 'code' in col.lower():
            # Generate alphanumeric IDs
            data[col] = [''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                         for _ in range(count)]
        elif col_dtype.startswith('int'):
            # Generate random integers
            data[col] = [random.randint(1, 10000) for _ in range(count)]
        elif col_dtype.startswith('float'):
            # Generate random floats
            data[col] = [round(random.uniform(0.01, 10000.0), 2) for _ in range(count)]
        elif 'name' in col.lower():
            # Generate fake names
            first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
            if 'first' in col.lower():
                data[col] = [random.choice(first_names) for _ in range(count)]
            elif 'last' in col.lower():
                data[col] = [random.choice(last_names) for _ in range(count)]
            else:
                data[col] = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(count)]
        else:
            # Default: generate random strings
            data[col] = [''.join(random.choices(string.ascii_letters + string.digits, k=15))
                        for _ in range(count)]
    
    return pd.DataFrame(data)


def generate_test_data_from_layout(layout_df: Any, count: int = 100) -> pd.DataFrame:
    """Generate test data based on layout schema with dummy data.
    
    Args:
        layout_df: Layout DataFrame
        count: Number of records to generate
        
    Returns:
        Generated DataFrame with columns matching Internal Field names
    """
    import random
    import string
    from datetime import datetime, timedelta
    
    data = {}
    
    for _, row in layout_df.iterrows():
        field_name = row.get("Internal Field", "")
        if not field_name:
            continue
        
        # Generate dummy data based on field name
        if 'date' in field_name.lower() or 'dob' in field_name.lower():
            start_date = datetime(2020, 1, 1)
            data[field_name] = [(start_date + timedelta(days=random.randint(0, 1825))).strftime("%Y-%m-%d")
                               for _ in range(count)]
        elif 'id' in field_name.lower() or 'code' in field_name.lower():
            data[field_name] = [''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                               for _ in range(count)]
        elif 'name' in field_name.lower():
            first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
            if 'first' in field_name.lower():
                data[field_name] = [random.choice(first_names) for _ in range(count)]
            elif 'last' in field_name.lower():
                data[field_name] = [random.choice(last_names) for _ in range(count)]
            else:
                data[field_name] = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(count)]
        else:
            # Default: generate random strings
            data[field_name] = [''.join(random.choices(string.ascii_letters + string.digits, k=15))
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

