"""File chunking utilities for splitting large files."""
from typing import Any, Iterator, List, Optional, Union
from pathlib import Path
import pandas as pd
import csv
import json
import io
from core.exceptions import FileError


class FileChunker:
    """Utility for splitting large files into smaller chunks."""
    
    def __init__(
        self,
        chunk_size: int = 100000,  # rows per chunk
        output_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize file chunker.
        
        Args:
            chunk_size: Number of rows per chunk
            output_dir: Directory to save chunks (None = same as input)
        """
        self.chunk_size = chunk_size
        self.output_dir = Path(output_dir) if output_dir else None
    
    def chunk_csv(
        self,
        input_file: Union[str, Path],
        output_prefix: Optional[str] = None,
        has_header: bool = True
    ) -> List[Path]:
        """
        Split CSV file into chunks.
        
        Args:
            input_file: Path to input CSV file
            output_prefix: Prefix for output files (default: input filename)
            has_header: Whether file has header row
        
        Returns:
            List of output file paths
        """
        input_path = Path(input_file)
        output_dir = self.output_dir or input_path.parent
        
        if output_prefix is None:
            output_prefix = input_path.stem
        
        output_files = []
        header = None
        
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
            reader = csv.reader(infile)
            
            if has_header:
                header = next(reader)
            
            chunk_num = 0
            current_chunk = []
            
            for row in reader:
                current_chunk.append(row)
                
                if len(current_chunk) >= self.chunk_size:
                    # Write chunk
                    output_file = output_dir / f"{output_prefix}_chunk_{chunk_num:04d}.csv"
                    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                        writer = csv.writer(outfile)
                        if header:
                            writer.writerow(header)
                        writer.writerows(current_chunk)
                    
                    output_files.append(output_file)
                    chunk_num += 1
                    current_chunk = []
            
            # Write remaining rows
            if current_chunk:
                output_file = output_dir / f"{output_prefix}_chunk_{chunk_num:04d}.csv"
                with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                    writer = csv.writer(outfile)
                    if header:
                        writer.writerow(header)
                    writer.writerows(current_chunk)
                output_files.append(output_file)
        
        return output_files
    
    def chunk_dataframe(
        self,
        df: pd.DataFrame,
        output_prefix: str,
        output_dir: Optional[Union[str, Path]] = None,
        format: str = 'csv'
    ) -> List[Path]:
        """
        Split DataFrame into chunks and save to files.
        
        Args:
            df: DataFrame to chunk
            output_prefix: Prefix for output files
            output_dir: Directory to save chunks
            format: Output format ('csv', 'parquet', 'json')
        
        Returns:
            List of output file paths
        """
        output_dir_path = Path(output_dir) if output_dir else (self.output_dir or Path.cwd())
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        output_files = []
        num_chunks = (len(df) + self.chunk_size - 1) // self.chunk_size
        
        for i in range(0, len(df), self.chunk_size):
            chunk = df.iloc[i:i + self.chunk_size]
            chunk_num = i // self.chunk_size
            
            if format == 'csv':
                output_file = output_dir_path / f"{output_prefix}_chunk_{chunk_num:04d}.csv"
                chunk.to_csv(output_file, index=False)
            elif format == 'parquet':
                output_file = output_dir_path / f"{output_prefix}_chunk_{chunk_num:04d}.parquet"
                chunk.to_parquet(output_file, index=False)
            elif format == 'json':
                output_file = output_dir_path / f"{output_prefix}_chunk_{chunk_num:04d}.json"
                chunk.to_json(output_file, orient='records', lines=True)
            else:
                raise FileError(f"Unsupported format: {format}", error_code="UNSUPPORTED_FORMAT")
            
            output_files.append(output_file)
        
        return output_files
    
    def chunk_json(
        self,
        input_file: Union[str, Path],
        output_prefix: Optional[str] = None,
        json_lines: bool = False
    ) -> List[Path]:
        """
        Split JSON file into chunks.
        
        Args:
            input_file: Path to input JSON file
            output_prefix: Prefix for output files
            json_lines: Whether file is in JSONL format
        
        Returns:
            List of output file paths
        """
        input_path = Path(input_file)
        output_dir = self.output_dir or input_path.parent
        
        if output_prefix is None:
            output_prefix = input_path.stem
        
        output_files = []
        chunk_num = 0
        current_chunk = []
        
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
            if json_lines:
                # JSONL format - one object per line
                for line in infile:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        obj = json.loads(line)
                        current_chunk.append(obj)
                        
                        if len(current_chunk) >= self.chunk_size:
                            output_file = output_dir / f"{output_prefix}_chunk_{chunk_num:04d}.jsonl"
                            with open(output_file, 'w', encoding='utf-8') as outfile:
                                for item in current_chunk:
                                    outfile.write(json.dumps(item) + '\n')
                            
                            output_files.append(output_file)
                            chunk_num += 1
                            current_chunk = []
                    except json.JSONDecodeError:
                        continue
            else:
                # Regular JSON array
                try:
                    data = json.load(infile)
                    if not isinstance(data, list):
                        raise FileError("JSON file must be an array", error_code="INVALID_JSON_FORMAT")
                    
                    for item in data:
                        current_chunk.append(item)
                        
                        if len(current_chunk) >= self.chunk_size:
                            output_file = output_dir / f"{output_prefix}_chunk_{chunk_num:04d}.json"
                            with open(output_file, 'w', encoding='utf-8') as outfile:
                                json.dump(current_chunk, outfile, indent=2)
                            
                            output_files.append(output_file)
                            chunk_num += 1
                            current_chunk = []
                except json.JSONDecodeError as e:
                    raise FileError(f"Error parsing JSON: {str(e)}", error_code="JSON_PARSE_ERROR") from e
            
            # Write remaining items
            if current_chunk:
                if json_lines:
                    output_file = output_dir / f"{output_prefix}_chunk_{chunk_num:04d}.jsonl"
                    with open(output_file, 'w', encoding='utf-8') as outfile:
                        for item in current_chunk:
                            outfile.write(json.dumps(item) + '\n')
                else:
                    output_file = output_dir / f"{output_prefix}_chunk_{chunk_num:04d}.json"
                    with open(output_file, 'w', encoding='utf-8') as outfile:
                        json.dump(current_chunk, outfile, indent=2)
                output_files.append(output_file)
        
        return output_files


def auto_chunk_file(
    file_path: Union[str, Path],
    chunk_size: int = 100000,
    output_dir: Optional[Union[str, Path]] = None
) -> List[Path]:
    """
    Automatically chunk a file based on its type.
    
    Args:
        file_path: Path to file
        chunk_size: Rows per chunk
        output_dir: Output directory
    
    Returns:
        List of chunk file paths
    """
    file_path_obj = Path(file_path)
    chunker = FileChunker(chunk_size=chunk_size, output_dir=output_dir)
    
    suffix = file_path_obj.suffix.lower()
    
    if suffix == '.csv':
        return chunker.chunk_csv(file_path)
    elif suffix in ['.json', '.jsonl']:
        return chunker.chunk_json(file_path, json_lines=(suffix == '.jsonl'))
    else:
        # Try to load as DataFrame and chunk
        try:
            if suffix == '.xlsx':
                df = pd.read_excel(file_path)
            elif suffix == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                df = pd.read_csv(file_path)
            
            return chunker.chunk_dataframe(df, file_path_obj.stem, output_dir)
        except Exception as e:
            raise FileError(
                f"Unable to auto-chunk file: {str(e)}",
                error_code="AUTO_CHUNK_ERROR"
            ) from e

