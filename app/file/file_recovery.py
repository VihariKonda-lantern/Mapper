"""Error recovery utilities for corrupted files."""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import csv
import io
from pathlib import Path
from core.exceptions import FileError


class FileRecovery:
    """Recovery utilities for corrupted files."""
    
    @staticmethod
    def recover_csv(
        file_obj: Any,
        encoding: str = 'utf-8',
        max_errors: int = 100,
        error_bad_lines: bool = False
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Attempt to recover corrupted CSV file.
        
        Args:
            file_obj: File-like object
            encoding: File encoding
            max_errors: Maximum errors to tolerate
            error_bad_lines: Whether to skip bad lines
        
        Returns:
            Tuple of (recovered DataFrame, error log)
        """
        errors = []
        recovered_rows = []
        header = None
        
        try:
            # Try reading with pandas first
            file_obj.seek(0)
            df = pd.read_csv(
                file_obj,
                encoding=encoding,
                error_bad_lines=error_bad_lines,
                on_bad_lines='skip' if not error_bad_lines else 'error'
            )
            return df, []
        except Exception as e:
            errors.append({"type": "pandas_read", "error": str(e)})
        
        # Manual recovery
        try:
            file_obj.seek(0)
            text_io = io.TextIOWrapper(file_obj, encoding=encoding, errors='replace')
            reader = csv.reader(text_io)
            
            error_count = 0
            row_num = 0
            
            for row in reader:
                row_num += 1
                
                try:
                    # Try to parse row
                    if header is None:
                        header = row
                        continue
                    
                    # Validate row length
                    if len(row) != len(header):
                        if error_count < max_errors:
                            # Pad or truncate row
                            if len(row) < len(header):
                                row.extend([None] * (len(header) - len(row)))
                            else:
                                row = row[:len(header)]
                            error_count += 1
                            errors.append({
                                "row": row_num,
                                "type": "length_mismatch",
                                "expected": len(header),
                                "actual": len(row)
                            })
                        else:
                            continue
                    
                    recovered_rows.append(row)
                    
                except Exception as e:
                    if error_count < max_errors:
                        error_count += 1
                        errors.append({
                            "row": row_num,
                            "type": "parse_error",
                            "error": str(e)
                        })
                    continue
            
            if header and recovered_rows:
                df = pd.DataFrame(recovered_rows, columns=header)
                return df, errors
            
        except Exception as e:
            errors.append({"type": "manual_recovery", "error": str(e)})
        
        raise FileError(
            f"Unable to recover file: {len(errors)} errors encountered",
            error_code="FILE_RECOVERY_FAILED"
        )
    
    @staticmethod
    def recover_excel(
        file_obj: Any,
        sheet_name: Optional[str] = None,
        skip_rows: int = 0
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Attempt to recover corrupted Excel file.
        
        Args:
            file_obj: File-like object
            sheet_name: Sheet name to read
            skip_rows: Number of rows to skip
        
        Returns:
            Tuple of (recovered DataFrame, error log)
        """
        errors = []
        
        try:
            # Try reading with pandas
            file_obj.seek(0)
            df = pd.read_excel(
                file_obj,
                sheet_name=sheet_name,
                skiprows=skip_rows,
                engine='openpyxl'
            )
            return df, []
        except Exception as e:
            errors.append({"type": "pandas_read", "error": str(e)})
        
        # Try with different engines
        engines = ['openpyxl', 'xlrd']
        for engine in engines:
            try:
                file_obj.seek(0)
                df = pd.read_excel(file_obj, sheet_name=sheet_name, engine=engine)
                return df, errors
            except Exception:
                continue
        
        raise FileError(
            "Unable to recover Excel file",
            error_code="EXCEL_RECOVERY_FAILED"
        )
    
    @staticmethod
    def validate_file_integrity(
        file_obj: Any,
        file_type: str
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate file integrity.
        
        Args:
            file_obj: File-like object
            file_type: File type ('csv', 'excel', etc.)
        
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        
        try:
            file_obj.seek(0)
            file_size = len(file_obj.read())
            file_obj.seek(0)
            
            if file_size == 0:
                issues.append({"type": "empty_file", "severity": "error"})
                return False, issues
            
            if file_type == 'csv':
                # Try to read first few lines
                try:
                    text_io = io.TextIOWrapper(file_obj, encoding='utf-8', errors='strict')
                    reader = csv.reader(text_io)
                    first_row = next(reader)
                    if not first_row:
                        issues.append({"type": "no_header", "severity": "warning"})
                except Exception as e:
                    issues.append({"type": "read_error", "error": str(e), "severity": "error"})
                    return False, issues
            
            return len([i for i in issues if i.get("severity") == "error"]) == 0, issues
            
        except Exception as e:
            issues.append({"type": "validation_error", "error": str(e), "severity": "error"})
            return False, issues

