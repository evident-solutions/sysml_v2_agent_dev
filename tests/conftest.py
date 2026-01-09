"""Pytest configuration and fixtures."""

import os
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_for_testing")
    monkeypatch.setenv("DATA_DIR", "./test_data")
    monkeypatch.setenv("CACHE_DIR", "./test_cache")

