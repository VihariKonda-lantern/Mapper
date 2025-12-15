# --- streaming_parser.py ---
"""Streaming parsers for very large CSV/JSON files (>1GB)."""
from typing import Any, Iterator, Optional, Dict, List, Callable
import csv
import json
import io
from pathlib import Path
import pandas as pd
from core.exceptions import FileError


class StreamingCSVParser:
    """Streaming CSV parser for very large files."""
    
    def __init__(
        self,
        file_obj: Any,
        chunk_size: int = 10000,
        delimiter: Optional[str] = None,
        has_header: bool = True,
        encoding: str = 'utf-8'
    ):
        """
        Initialize streaming CSV parser.
        
        Args:
            file_obj: File-like object to read
            chunk_size: Number of rows per chunk
            delimiter: CSV delimiter (auto-detect if None)
            has_header: Whether file has header row
            encoding: File encoding
        """
        self.file_obj = file_obj
        self.chunk_size = chunk_size
        self.delimiter = delimiter
        self.has_header = has_header
        self.encoding = encoding
        self._header: Optional[List[str]] = None
        self._delimiter: Optional[str] = None
    
    def _detect_delimiter(self, sample: str) -> str:
        """Detect CSV delimiter from sample."""
        if self.delimiter:
            return self.delimiter
        
        # Common delimiters
        delimiters = [',', '\t', ';', '|']
        delimiter_counts = {d: sample.count(d) for d in delimiters}
        
        if delimiter_counts:
            return max(delimiter_counts, key=delimiter_counts.get)  # type: ignore
        return ','
    
    def _read_header(self) -> List[str]:
        """Read and return header row."""
        if self._header is not None:
            return self._header
        
        if not self.has_header:
            return []
        
        # Read first line
        self.file_obj.seek(0)
        first_line = self.file_obj.readline()
        
        if isinstance(first_line, bytes):
            first_line = first_line.decode(self.encoding, errors='ignore')
        
        self._delimiter = self._detect_delimiter(first_line)
        
        reader = csv.reader([first_line], delimiter=self._delimiter)
        self._header = next(reader)
        
        return self._header
    
    def read_chunks(self) -> Iterator[pd.DataFrame]:
        """
        Read CSV file in chunks.
        
        Yields:
            DataFrame chunks
        """
        self.file_obj.seek(0)
        
        # Read header
        header = self._read_header()
        
        # Create CSV reader
        if isinstance(self.file_obj, io.TextIOWrapper):
            file_handle = self.file_obj
        else:
            # Handle bytes
            file_handle = io.TextIOWrapper(self.file_obj, encoding=self.encoding, errors='ignore')
        
        reader = csv.reader(file_handle, delimiter=self._delimiter)
        
        # Skip header if present
        if self.has_header and header:
            next(reader, None)
        
        # Read in chunks
        chunk_rows = []
        row_count = 0
        
        for row in reader:
            chunk_rows.append(row)
            row_count += 1
            
            if len(chunk_rows) >= self.chunk_size:
                # Create DataFrame from chunk
                df_chunk = pd.DataFrame(chunk_rows, columns=header if header else None)
                yield df_chunk
                chunk_rows = []
        
        # Yield remaining rows
        if chunk_rows:
            df_chunk = pd.DataFrame(chunk_rows, columns=header if header else None)
            yield df_chunk
    
    def process_streaming(
        self,
        process_func: Callable[[pd.DataFrame], Any],
        accumulate: bool = False
    ) -> Iterator[Any]:
        """
        Process CSV file in streaming fashion.
        
        Args:
            process_func: Function to process each chunk
            accumulate: Whether to accumulate results
        
        Yields:
            Processed results
        """
        accumulated = None
        
        for chunk in self.read_chunks():
            result = process_func(chunk)
            
            if accumulate:
                if accumulated is None:
                    accumulated = result
                else:
                    # Try to concatenate if DataFrames
                    if isinstance(accumulated, pd.DataFrame) and isinstance(result, pd.DataFrame):
                        accumulated = pd.concat([accumulated, result], ignore_index=True)
                    elif isinstance(accumulated, list) and isinstance(result, list):
                        accumulated.extend(result)
                    else:
                        # Fallback: return as list
                        if not isinstance(accumulated, list):
                            accumulated = [accumulated]
                        accumulated.append(result)
            else:
                yield result
        
        if accumulate and accumulated is not None:
            yield accumulated


class StreamingJSONParser:
    """Streaming JSON parser for very large files."""
    
    def __init__(
        self,
        file_obj: Any,
        chunk_size: int = 1000,
        encoding: str = 'utf-8',
        json_lines: bool = False  # JSONL format (one JSON object per line)
    ):
        """
        Initialize streaming JSON parser.
        
        Args:
            file_obj: File-like object to read
            chunk_size: Number of objects per chunk
            encoding: File encoding
            json_lines: Whether file is in JSONL format (one object per line)
        """
        self.file_obj = file_obj
        self.chunk_size = chunk_size
        self.encoding = encoding
        self.json_lines = json_lines
    
    def read_chunks(self) -> Iterator[List[Dict[str, Any]]]:
        """
        Read JSON file in chunks.
        
        Yields:
            Lists of JSON objects
        """
        self.file_obj.seek(0)
        
        if self.json_lines:
            # JSONL format - one object per line
            chunk_objects = []
            
            if isinstance(self.file_obj, io.TextIOWrapper):
                file_handle = self.file_obj
            else:
                file_handle = io.TextIOWrapper(self.file_obj, encoding=self.encoding, errors='ignore')
            
            for line in file_handle:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    obj = json.loads(line)
                    chunk_objects.append(obj)
                    
                    if len(chunk_objects) >= self.chunk_size:
                        yield chunk_objects
                        chunk_objects = []
                except json.JSONDecodeError:
                    continue
            
            # Yield remaining objects
            if chunk_objects:
                yield chunk_objects
        
        else:
            # Regular JSON array format
            try:
                # Try to read as streaming array
                decoder = json.JSONDecoder()
                buffer = ""
                
                if isinstance(self.file_obj, io.TextIOWrapper):
                    content = self.file_obj.read()
                else:
                    content = self.file_obj.read().decode(self.encoding, errors='ignore')
                
                # Check if it's an array
                content = content.strip()
                if not content.startswith('['):
                    raise FileError("JSON file must be an array or JSONL format", error_code="INVALID_JSON_FORMAT")
                
                # Remove brackets
                content = content[1:-1].strip()
                
                # Parse objects one by one
                chunk_objects = []
                idx = 0
                
                while idx < len(content):
                    # Find next JSON object
                    try:
                        obj, idx = decoder.raw_decode(content, idx)
                        chunk_objects.append(obj)
                        
                        if len(chunk_objects) >= self.chunk_size:
                            yield chunk_objects
                            chunk_objects = []
                        
                        # Skip whitespace and commas
                        while idx < len(content) and content[idx] in [' ', '\n', '\t', ',']:
                            idx += 1
                    except json.JSONDecodeError:
                        break
                
                # Yield remaining objects
                if chunk_objects:
                    yield chunk_objects
            
            except Exception as e:
                raise FileError(
                    f"Error parsing JSON: {str(e)}",
                    error_code="JSON_PARSE_ERROR"
                ) from e
    
    def read_chunks_as_dataframe(self) -> Iterator[pd.DataFrame]:
        """
        Read JSON file in chunks as DataFrames.
        
        Yields:
            DataFrame chunks
        """
        for chunk_objects in self.read_chunks():
            if chunk_objects:
                df_chunk = pd.DataFrame(chunk_objects)
                yield df_chunk
    
    def process_streaming(
        self,
        process_func: Callable[[List[Dict[str, Any]]], Any],
        accumulate: bool = False
    ) -> Iterator[Any]:
        """
        Process JSON file in streaming fashion.
        
        Args:
            process_func: Function to process each chunk
            accumulate: Whether to accumulate results
        
        Yields:
            Processed results
        """
        accumulated = None
        
        for chunk in self.read_chunks():
            result = process_func(chunk)
            
            if accumulate:
                if accumulated is None:
                    accumulated = result
                else:
                    # Try to concatenate if DataFrames
                    if isinstance(accumulated, pd.DataFrame) and isinstance(result, pd.DataFrame):
                        accumulated = pd.concat([accumulated, result], ignore_index=True)
                    elif isinstance(accumulated, list) and isinstance(result, list):
                        accumulated.extend(result)
                    else:
                        # Fallback: return as list
                        if not isinstance(accumulated, list):
                            accumulated = [accumulated]
                        accumulated.append(result)
            else:
                yield result
        
        if accumulate and accumulated is not None:
            yield accumulated


def stream_large_file(
    file_obj: Any,
    file_type: str,
    chunk_size: int = 10000,
    **kwargs: Any
) -> Iterator[Any]:
    """
    Stream a large file in chunks.
    
    Args:
        file_obj: File-like object
        file_type: File type ('csv', 'json', 'jsonl')
        chunk_size: Number of rows/objects per chunk
        **kwargs: Additional arguments for parser
    
    Yields:
        Chunks of data (DataFrames for CSV, lists/DataFrames for JSON)
    """
    if file_type.lower() in ['csv', 'txt', 'tsv']:
        parser = StreamingCSVParser(
            file_obj,
            chunk_size=chunk_size,
            delimiter=kwargs.get('delimiter'),
            has_header=kwargs.get('has_header', True),
            encoding=kwargs.get('encoding', 'utf-8')
        )
        yield from parser.read_chunks()
    
    elif file_type.lower() in ['json', 'jsonl']:
        parser = StreamingJSONParser(
            file_obj,
            chunk_size=chunk_size,
            encoding=kwargs.get('encoding', 'utf-8'),
            json_lines=(file_type.lower() == 'jsonl')
        )
        if kwargs.get('as_dataframe', False):
            yield from parser.read_chunks_as_dataframe()
        else:
            yield from parser.read_chunks()
    
    else:
        raise FileError(
            f"Unsupported file type for streaming: {file_type}",
            error_code="UNSUPPORTED_STREAMING_TYPE"
        )


def process_large_file_streaming(
    file_obj: Any,
    file_type: str,
    process_func: Callable[[Any], Any],
    chunk_size: int = 10000,
    accumulate: bool = False,
    **kwargs: Any
) -> Iterator[Any]:
    """
    Process a large file in streaming fashion.
    
    Args:
        file_obj: File-like object
        file_type: File type ('csv', 'json', 'jsonl')
        process_func: Function to process each chunk
        chunk_size: Number of rows/objects per chunk
        accumulate: Whether to accumulate results
        **kwargs: Additional arguments for parser
    
    Yields:
        Processed results
    """
    if file_type.lower() in ['csv', 'txt', 'tsv']:
        parser = StreamingCSVParser(
            file_obj,
            chunk_size=chunk_size,
            delimiter=kwargs.get('delimiter'),
            has_header=kwargs.get('has_header', True),
            encoding=kwargs.get('encoding', 'utf-8')
        )
        yield from parser.process_streaming(process_func, accumulate=accumulate)
    
    elif file_type.lower() in ['json', 'jsonl']:
        parser = StreamingJSONParser(
            file_obj,
            chunk_size=chunk_size,
            encoding=kwargs.get('encoding', 'utf-8'),
            json_lines=(file_type.lower() == 'jsonl')
        )
        yield from parser.process_streaming(process_func, accumulate=accumulate)
    
    else:
        raise FileError(
            f"Unsupported file type for streaming: {file_type}",
            error_code="UNSUPPORTED_STREAMING_TYPE"
        )

