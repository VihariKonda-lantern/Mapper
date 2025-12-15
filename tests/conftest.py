# --- conftest.py ---
"""Pytest configuration and fixtures."""
import pytest
import pandas as pd
from typing import Any, Dict, Generator
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit for testing."""
    with patch('streamlit.session_state', new={}) as mock_st:
        # Mock common Streamlit functions
        mock_st.set_page_config = MagicMock()
        mock_st.title = MagicMock()
        mock_st.write = MagicMock()
        mock_st.dataframe = MagicMock()
        mock_st.button = MagicMock(return_value=False)
        mock_st.text_input = MagicMock(return_value="")
        mock_st.selectbox = MagicMock(return_value="")
        mock_st.file_uploader = MagicMock(return_value=None)
        mock_st.cache_data = lambda *args, **kwargs: lambda func: func
        yield mock_st


@pytest.fixture
def sample_claims_df() -> pd.DataFrame:
    """Create sample claims DataFrame for testing."""
    return pd.DataFrame({
        'Patient_ID': ['P001', 'P002', 'P003'],
        'DOB': ['1990-01-01', '1985-05-15', '1992-12-25'],
        'SSN': ['123-45-6789', '987-65-4321', '555-55-5555'],
        'Claim_Amount': [1000.50, 2500.75, 500.25],
        'Service_Date': ['2024-01-15', '2024-02-20', '2024-03-10']
    })


@pytest.fixture
def sample_layout_df() -> pd.DataFrame:
    """Create sample layout DataFrame for testing."""
    return pd.DataFrame({
        'Internal Field': ['Patient_ID', 'DOB', 'SSN', 'Claim_Amount', 'Service_Date'],
        'Usage': ['Mandatory', 'Mandatory', 'Optional', 'Mandatory', 'Mandatory'],
        'Data Type': ['String', 'Date', 'String', 'Numeric', 'Date'],
        'Description': [
            'Patient identifier',
            'Date of birth',
            'Social Security Number',
            'Claim amount',
            'Service date'
        ]
    })


@pytest.fixture
def sample_mapping() -> Dict[str, Dict[str, Any]]:
    """Create sample mapping dictionary for testing."""
    return {
        'Patient_ID': {'value': 'Patient_ID', 'mode': 'auto', 'confidence': 95.0},
        'DOB': {'value': 'DOB', 'mode': 'auto', 'confidence': 90.0},
        'SSN': {'value': 'SSN', 'mode': 'auto', 'confidence': 85.0},
        'Claim_Amount': {'value': 'Claim_Amount', 'mode': 'auto', 'confidence': 95.0},
        'Service_Date': {'value': 'Service_Date', 'mode': 'auto', 'confidence': 92.0}
    }


@pytest.fixture
def sample_validation_results() -> list[Dict[str, Any]]:
    """Create sample validation results for testing."""
    return [
        {
            'check': 'Null Check',
            'status': 'Pass',
            'field': 'Patient_ID',
            'fail_count': 0,
            'total_count': 3,
            'fail_pct': '0.00'
        },
        {
            'check': 'Range Check',
            'status': 'Warning',
            'field': 'Claim_Amount',
            'fail_count': 1,
            'total_count': 3,
            'fail_pct': '33.33'
        }
    ]


@pytest.fixture
def temp_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.csv"
    file_path.write_text("col1,col2\nval1,val2\nval3,val4")
    yield file_path
    if file_path.exists():
        file_path.unlink()


@pytest.fixture
def mock_file_upload():
    """Mock file upload object."""
    mock_file = MagicMock()
    mock_file.name = "test_file.csv"
    mock_file.size = 1024
    mock_file.read.return_value = b"col1,col2\nval1,val2"
    mock_file.seek = MagicMock()
    mock_file.tell = MagicMock(return_value=0)
    return mock_file


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """Create empty DataFrame for testing."""
    return pd.DataFrame()


@pytest.fixture
def large_dataframe() -> pd.DataFrame:
    """Create large DataFrame for performance testing."""
    return pd.DataFrame({
        f'col_{i}': range(10000) for i in range(50)
    })


# Test data generators
class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_claims_data(num_rows: int = 100) -> pd.DataFrame:
        """Generate synthetic claims data."""
        import random
        from datetime import datetime, timedelta
        
        data = {
            'Patient_ID': [f'P{i:05d}' for i in range(num_rows)],
            'DOB': [
                (datetime.now() - timedelta(days=random.randint(18*365, 80*365))).strftime('%Y-%m-%d')
                for _ in range(num_rows)
            ],
            'SSN': [
                f'{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}'
                for _ in range(num_rows)
            ],
            'Claim_Amount': [random.uniform(100, 10000) for _ in range(num_rows)],
            'Service_Date': [
                (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
                for _ in range(num_rows)
            ]
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_mapping_with_confidence(
        fields: list[str],
        confidence_range: tuple[float, float] = (70.0, 100.0)
    ) -> Dict[str, Dict[str, Any]]:
        """Generate mapping with confidence scores."""
        import random
        return {
            field: {
                'value': field,
                'mode': 'auto',
                'confidence': random.uniform(*confidence_range)
            }
            for field in fields
        }


@pytest.fixture
def test_data_generator() -> TestDataGenerator:
    """Provide test data generator."""
    return TestDataGenerator()

