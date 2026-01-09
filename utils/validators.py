"""Input validation utilities."""

import os
from pathlib import Path
from typing import Optional, Tuple


def validate_pdf_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a file exists and is a PDF.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File does not exist: {file_path}"
    
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    
    if path.suffix.lower() != '.pdf':
        return False, f"File is not a PDF: {file_path}"
    
    if path.stat().st_size == 0:
        return False, f"File is empty: {file_path}"
    
    return True, None


def validate_directory(dir_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a directory exists and is readable.
    
    Args:
        dir_path: Path to the directory to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(dir_path)
    
    if not path.exists():
        return False, f"Directory does not exist: {dir_path}"
    
    if not path.is_dir():
        return False, f"Path is not a directory: {dir_path}"
    
    if not os.access(path, os.R_OK):
        return False, f"Directory is not readable: {dir_path}"
    
    return True, None

