# --- path_utils.py ---
"""Path utilities using pathlib for better path handling."""
from pathlib import Path
from typing import Optional, Union, List, Tuple
import os


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    
    Returns:
        Path object for the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_file_extension(path: Union[str, Path]) -> str:
    """
    Get file extension from path.
    
    Args:
        path: File path
    
    Returns:
        File extension (with dot, e.g., '.csv')
    """
    return Path(path).suffix.lower()


def get_file_name(path: Union[str, Path], with_extension: bool = True) -> str:
    """
    Get file name from path.
    
    Args:
        path: File path
        with_extension: Whether to include extension
    
    Returns:
        File name
    """
    path_obj = Path(path)
    if with_extension:
        return path_obj.name
    return path_obj.stem


def get_file_size(path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: File path
    
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    path_obj = Path(path)
    if path_obj.exists() and path_obj.is_file():
        return path_obj.stat().st_size
    return 0


def is_valid_path(path: Union[str, Path]) -> bool:
    """
    Check if path is valid.
    
    Args:
        path: Path to check
    
    Returns:
        True if path is valid
    """
    try:
        path_obj = Path(path)
        return True
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.replace("..", "").replace("/", "_").replace("\\", "_")
    
    # Remove dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure it's not empty
    if not filename:
        filename = "file"
    
    return filename


def join_paths(*parts: Union[str, Path]) -> Path:
    """
    Join path parts using pathlib.
    
    Args:
        *parts: Path parts to join
    
    Returns:
        Joined Path object
    """
    if not parts:
        return Path()
    
    result = Path(parts[0])
    for part in parts[1:]:
        result = result / part
    
    return result


def find_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = True
) -> List[Path]:
    """
    Find files matching a pattern.
    
    Args:
        directory: Directory to search
        pattern: File pattern (e.g., "*.csv")
        recursive: Whether to search recursively
    
    Returns:
        List of matching file paths
    """
    directory_path = Path(directory)
    if not directory_path.exists() or not directory_path.is_dir():
        return []
    
    if recursive:
        return list(directory_path.rglob(pattern))
    else:
        return list(directory_path.glob(pattern))


def get_relative_path(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
    Get relative path from base directory.
    
    Args:
        path: Target path
        base: Base directory
    
    Returns:
        Relative path
    """
    return Path(path).relative_to(Path(base))


def ensure_file_path(path: Union[str, Path]) -> Path:
    """
    Ensure file path exists, creating parent directories if needed.
    
    Args:
        path: File path
    
    Returns:
        Path object for the file
    """
    path_obj = Path(path)
    if path_obj.parent:
        path_obj.parent.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_file_info(path: Union[str, Path]) -> dict:
    """
    Get comprehensive file information.
    
    Args:
        path: File path
    
    Returns:
        Dictionary with file information
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        return {
            "exists": False,
            "path": str(path_obj),
            "name": path_obj.name,
            "extension": path_obj.suffix,
            "size": 0
        }
    
    stat = path_obj.stat()
    
    return {
        "exists": True,
        "path": str(path_obj.absolute()),
        "name": path_obj.name,
        "stem": path_obj.stem,
        "extension": path_obj.suffix,
        "size": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "is_file": path_obj.is_file(),
        "is_dir": path_obj.is_dir(),
        "modified": stat.st_mtime
    }


# Compatibility functions for migration from os.path
def path_exists(path: Union[str, Path]) -> bool:
    """Check if path exists (pathlib version of os.path.exists)."""
    return Path(path).exists()


def path_isfile(path: Union[str, Path]) -> bool:
    """Check if path is a file (pathlib version of os.path.isfile)."""
    return Path(path).is_file()


def path_isdir(path: Union[str, Path]) -> bool:
    """Check if path is a directory (pathlib version of os.path.isdir)."""
    return Path(path).is_dir()


def path_join(*parts: Union[str, Path]) -> Path:
    """Join path parts (pathlib version of os.path.join)."""
    return join_paths(*parts)


def path_basename(path: Union[str, Path]) -> str:
    """Get basename (pathlib version of os.path.basename)."""
    return Path(path).name


def path_dirname(path: Union[str, Path]) -> Path:
    """Get directory name (pathlib version of os.path.dirname)."""
    return Path(path).parent


def path_splitext(path: Union[str, Path]) -> Tuple[str, str]:
    """Split extension (pathlib version of os.path.splitext)."""
    path_obj = Path(path)
    return (path_obj.stem, path_obj.suffix)

