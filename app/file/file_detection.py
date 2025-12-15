"""Enhanced file detection: encoding, delimiter, header detection."""
from typing import Any, Dict, List, Optional, Tuple
import chardet
import csv
import io
import pandas as pd
from pathlib import Path


class FileDetector:
    """Enhanced file detection utilities."""
    
    @staticmethod
    def detect_encoding(file_obj: Any, sample_size: int = 10000) -> Tuple[str, float]:
        """
        Detect file encoding.
        
        Args:
            file_obj: File-like object
            sample_size: Size of sample to analyze
        
        Returns:
            Tuple of (encoding, confidence)
        """
        # Read sample
        position = file_obj.tell()
        sample = file_obj.read(sample_size)
        file_obj.seek(position)
        
        # Use chardet
        result = chardet.detect(sample)
        
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0.0)
        
        # Fallback to utf-8 if confidence is low
        if confidence < 0.7:
            encoding = 'utf-8'
        
        return encoding, confidence
    
    @staticmethod
    def detect_delimiter(
        file_obj: Any,
        sample_lines: int = 10,
        encoding: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Detect CSV delimiter.
        
        Args:
            file_obj: File-like object
            sample_lines: Number of lines to sample
            encoding: File encoding (auto-detect if None)
        
        Returns:
            Tuple of (delimiter, confidence)
        """
        position = file_obj.tell()
        
        # Read sample
        if encoding:
            text_io = io.TextIOWrapper(file_obj, encoding=encoding, errors='ignore')
        else:
            detected_encoding, _ = FileDetector.detect_encoding(file_obj)
            file_obj.seek(position)
            text_io = io.TextIOWrapper(file_obj, encoding=detected_encoding, errors='ignore')
        
        sample = []
        for i, line in enumerate(text_io):
            if i >= sample_lines:
                break
            sample.append(line)
        
        file_obj.seek(position)
        
        # Test common delimiters
        delimiters = [',', '\t', ';', '|', ' ']
        delimiter_scores: Dict[str, float] = {}
        
        for delimiter in delimiters:
            scores = []
            for line in sample:
                if not line.strip():
                    continue
                
                # Count occurrences
                count = line.count(delimiter)
                if count > 0:
                    # Check consistency (all lines should have similar count)
                    scores.append(count)
            
            if scores:
                # Calculate consistency score
                avg_count = sum(scores) / len(scores)
                variance = sum((s - avg_count) ** 2 for s in scores) / len(scores)
                consistency = 1.0 / (1.0 + variance)  # Higher consistency = lower variance
                
                # Weight by average count (more delimiters = more likely)
                score = avg_count * consistency
                delimiter_scores[delimiter] = score
        
        if delimiter_scores:
            best_delimiter = max(delimiter_scores, key=delimiter_scores.get)  # type: ignore
            best_score = delimiter_scores[best_delimiter]
            
            # Normalize confidence
            max_score = max(delimiter_scores.values())
            confidence = best_score / max_score if max_score > 0 else 0.0
            
            return best_delimiter, confidence
        
        return ',', 0.5  # Default to comma
    
    @staticmethod
    def detect_header(
        file_obj: Any,
        delimiter: str = ',',
        encoding: Optional[str] = None,
        sample_lines: int = 5
    ) -> Tuple[bool, Optional[List[str]]]:
        """
        Detect if file has header row.
        
        Args:
            file_obj: File-like object
            delimiter: CSV delimiter
            encoding: File encoding
            sample_lines: Number of lines to sample
        
        Returns:
            Tuple of (has_header, header_columns)
        """
        position = file_obj.tell()
        
        # Read sample
        if encoding:
            text_io = io.TextIOWrapper(file_obj, encoding=encoding, errors='ignore')
        else:
            detected_encoding, _ = FileDetector.detect_encoding(file_obj)
            file_obj.seek(position)
            text_io = io.TextIOWrapper(file_obj, encoding=detected_encoding, errors='ignore')
        
        reader = csv.reader(text_io, delimiter=delimiter)
        
        try:
            first_row = next(reader)
            second_row = next(reader) if sample_lines > 1 else None
        except StopIteration:
            file_obj.seek(position)
            return False, None
        
        file_obj.seek(position)
        
        # Check if first row looks like header
        # Headers typically:
        # 1. Are strings (not numbers)
        # 2. Have unique values
        # 3. Don't match data patterns
        
        is_header = True
        
        # Check if all values are strings
        if not all(isinstance(cell, str) for cell in first_row):
            is_header = False
        
        # Check if values are unique
        if len(first_row) != len(set(first_row)):
            is_header = False
        
        # Check if second row looks like data (numbers, dates, etc.)
        if second_row:
            # If second row has numeric values, first row is likely header
            numeric_count = sum(
                1 for cell in second_row
                if isinstance(cell, (int, float)) or (isinstance(cell, str) and cell.replace('.', '').replace('-', '').isdigit())
            )
            if numeric_count > len(second_row) * 0.5:
                is_header = True
        
        # Check for common header patterns
        header_keywords = ['id', 'name', 'date', 'code', 'amount', 'field', 'column']
        first_row_lower = [str(cell).lower() for cell in first_row]
        keyword_matches = sum(1 for kw in header_keywords if any(kw in cell for cell in first_row_lower))
        
        if keyword_matches > len(first_row) * 0.3:
            is_header = True
        
        return is_header, first_row if is_header else None
    
    @staticmethod
    def detect_file_properties(
        file_obj: Any,
        sample_size: int = 10000
    ) -> Dict[str, Any]:
        """
        Detect all file properties at once.
        
        Args:
            file_obj: File-like object
            sample_size: Sample size for detection
        
        Returns:
            Dictionary with detected properties
        """
        position = file_obj.tell()
        
        # Detect encoding
        encoding, encoding_confidence = FileDetector.detect_encoding(file_obj, sample_size)
        file_obj.seek(position)
        
        # Detect delimiter
        delimiter, delimiter_confidence = FileDetector.detect_delimiter(file_obj, encoding=encoding)
        file_obj.seek(position)
        
        # Detect header
        has_header, header_columns = FileDetector.detect_header(
            file_obj,
            delimiter=delimiter,
            encoding=encoding
        )
        file_obj.seek(position)
        
        return {
            "encoding": encoding,
            "encoding_confidence": encoding_confidence,
            "delimiter": delimiter,
            "delimiter_confidence": delimiter_confidence,
            "has_header": has_header,
            "header_columns": header_columns,
            "column_count": len(header_columns) if header_columns else None
        }

