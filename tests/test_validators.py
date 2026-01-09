"""Tests for validators."""

import os
import tempfile
from pathlib import Path
import pytest

from utils.validators import validate_pdf_file, validate_directory


class TestValidatePDFFile:
    """Tests for PDF file validation."""
    
    def test_nonexistent_file(self):
        """Test validation of non-existent file."""
        is_valid, error_msg = validate_pdf_file("nonexistent.pdf")
        assert not is_valid
        assert "does not exist" in error_msg
    
    def test_non_pdf_file(self):
        """Test validation of non-PDF file."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            is_valid, error_msg = validate_pdf_file(temp_path)
            assert not is_valid
            assert "not a PDF" in error_msg
        finally:
            os.unlink(temp_path)
    
    def test_empty_file(self):
        """Test validation of empty file."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            is_valid, error_msg = validate_pdf_file(temp_path)
            assert not is_valid
            assert "empty" in error_msg
        finally:
            os.unlink(temp_path)
    
    def test_valid_pdf(self):
        """Test validation of valid PDF file."""
        # Create a minimal valid PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 0\ntrailer\n<< /Size 0 /Root 1 0 R >>\nstartxref\n0\n%%EOF"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_content)
            temp_path = f.name
        
        try:
            is_valid, error_msg = validate_pdf_file(temp_path)
            assert is_valid
            assert error_msg is None
        finally:
            os.unlink(temp_path)


class TestValidateDirectory:
    """Tests for directory validation."""
    
    def test_nonexistent_directory(self):
        """Test validation of non-existent directory."""
        is_valid, error_msg = validate_directory("nonexistent_dir")
        assert not is_valid
        assert "does not exist" in error_msg
    
    def test_file_as_directory(self):
        """Test validation when path is a file, not directory."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            temp_path = f.name
        
        try:
            is_valid, error_msg = validate_directory(temp_path)
            assert not is_valid
            assert "not a directory" in error_msg
        finally:
            os.unlink(temp_path)
    
    def test_valid_directory(self):
        """Test validation of valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            is_valid, error_msg = validate_directory(temp_dir)
            assert is_valid
            assert error_msg is None

