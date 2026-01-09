"""Configuration management with environment variable support."""

import os
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        self.gemini_api_key: str = self._get_required_env("GEMINI_API_KEY")
        self.data_dir: Path = Path(self._get_env("DATA_DIR", "./data"))
        self.pdf_dir: Path = Path(self._get_env("PDF_DIR", "./data/pdfs"))
        self.cache_dir: Path = Path(self._get_env("CACHE_DIR", "./.cache"))
        self.log_level: str = self._get_env("LOG_LEVEL", "INFO")
        self.log_file: Optional[str] = self._get_env("LOG_FILE", None)
        self.file_search_store_name: str = self._get_env("FILE_SEARCH_STORE_NAME", "sysml-v2-pdf-documents")
        self.gemini_model: str = self._get_env("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _get_required_env(key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable '{key}' is not set. "
                f"Please set it in your .env file or environment."
            )
        return value
    
    @staticmethod
    def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get an optional environment variable."""
        return os.getenv(key, default)
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate that all required settings are properly configured.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.gemini_api_key:
            return False, "GEMINI_API_KEY is not set"
        
        if len(self.gemini_api_key) < 10:
            return False, "GEMINI_API_KEY appears to be invalid (too short)"
        
        return True, None


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

