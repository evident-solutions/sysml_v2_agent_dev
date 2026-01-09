"""Tests for file manager."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.file_manager import FileManager


class TestFileManager:
    """Tests for FileManager class."""
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing."""
        return "test_api_key_123"
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @patch('src.file_manager.genai')
    def test_initialization(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test FileManager initialization."""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.cache_dir = temp_cache_dir
            mock_settings_instance.file_search_store_name = "test-store"
            mock_settings.return_value = mock_settings_instance
            
            mock_client = Mock()
            mock_file_search_stores = Mock()
            mock_file_search_stores.list.return_value = []
            mock_store = Mock()
            mock_store.name = "test-store-name"
            mock_file_search_stores.create.return_value = mock_store
            mock_client.file_search_stores = mock_file_search_stores
            mock_genai.Client.return_value = mock_client
            
            manager = FileManager(mock_api_key)
            assert manager is not None
            mock_genai.Client.assert_called_once_with(api_key=mock_api_key)
            assert manager.client == mock_client
    
    @patch('src.file_manager.genai')
    def test_load_tracking_empty(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test loading tracking when file doesn't exist."""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.cache_dir = temp_cache_dir
            mock_settings_instance.file_search_store_name = "test-store"
            mock_settings.return_value = mock_settings_instance
            
            mock_client = Mock()
            mock_file_search_stores = Mock()
            mock_file_search_stores.list.return_value = []
            mock_store = Mock()
            mock_store.name = "test-store-name"
            mock_file_search_stores.create.return_value = mock_store
            mock_client.file_search_stores = mock_file_search_stores
            mock_genai.Client.return_value = mock_client
            
            manager = FileManager(mock_api_key)
            assert manager._tracked_files == {}
    
    @patch('src.file_manager.genai')
    def test_load_tracking_existing(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test loading tracking from existing file."""
        tracking_file = temp_cache_dir / "file_tracking.json"
        tracking_data = {
            "file1": {
                "name": "test_name",
                "uri": "test_uri",
                "hash": "test_hash",
                "upload_date": "2024-01-01",
                "original_path": "/path/to/file"
            }
        }
        tracking_file.write_text(json.dumps(tracking_data))
        
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.cache_dir = temp_cache_dir
            mock_settings_instance.file_search_store_name = "test-store"
            mock_settings.return_value = mock_settings_instance
            
            mock_client = Mock()
            mock_file_search_stores = Mock()
            mock_file_search_stores.list.return_value = []
            mock_store = Mock()
            mock_store.name = "test-store-name"
            mock_file_search_stores.create.return_value = mock_store
            mock_client.file_search_stores = mock_file_search_stores
            mock_genai.Client.return_value = mock_client
            
            manager = FileManager(mock_api_key)
            assert manager._tracked_files == tracking_data
    
    @patch('src.file_manager.genai')
    def test_save_tracking(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test saving tracking data."""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.cache_dir = temp_cache_dir
            mock_settings_instance.file_search_store_name = "test-store"
            mock_settings.return_value = mock_settings_instance
            
            mock_client = Mock()
            mock_file_search_stores = Mock()
            mock_file_search_stores.list.return_value = []
            mock_store = Mock()
            mock_store.name = "test-store-name"
            mock_file_search_stores.create.return_value = mock_store
            mock_client.file_search_stores = mock_file_search_stores
            mock_genai.Client.return_value = mock_client
            
            manager = FileManager(mock_api_key)
            manager._tracked_files = {"test": {"data": "value"}}
            manager._save_tracking()
            
            tracking_file = temp_cache_dir / "file_tracking.json"
            assert tracking_file.exists()
            loaded_data = json.loads(tracking_file.read_text())
            assert loaded_data == {"test": {"data": "value"}}
    
    @patch('src.file_manager.genai')
    def test_compute_file_hash(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test file hash computation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            with patch('config.settings.get_settings') as mock_settings:
                mock_settings_instance = Mock()
                mock_settings_instance.cache_dir = temp_cache_dir
                mock_settings_instance.file_search_store_name = "test-store"
                mock_settings.return_value = mock_settings_instance
                
                mock_client = Mock()
                mock_file_search_stores = Mock()
                mock_file_search_stores.list.return_value = []
                mock_store = Mock()
                mock_store.name = "test-store-name"
                mock_file_search_stores.create.return_value = mock_store
                mock_client.file_search_stores = mock_file_search_stores
                mock_genai.Client.return_value = mock_client
                
                manager = FileManager(mock_api_key)
                hash1 = manager._compute_file_hash(Path(temp_path))
                hash2 = manager._compute_file_hash(Path(temp_path))
                
                assert hash1 == hash2
                assert len(hash1) == 64  # SHA256 produces 64 char hex string
        finally:
            os.unlink(temp_path)
    
    @patch('src.file_manager.genai')
    def test_list_files_empty(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test listing files when none are tracked."""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.cache_dir = temp_cache_dir
            mock_settings_instance.file_search_store_name = "test-store"
            mock_settings.return_value = mock_settings_instance
            
            mock_client = Mock()
            mock_file_search_stores = Mock()
            mock_file_search_stores.list.return_value = []
            mock_store = Mock()
            mock_store.name = "test-store-name"
            mock_file_search_stores.create.return_value = mock_store
            mock_client.file_search_stores = mock_file_search_stores
            mock_genai.Client.return_value = mock_client
            
            manager = FileManager(mock_api_key)
            files = manager.list_files()
            assert files == []
    
    @patch('src.file_manager.genai')
    def test_clear_cache(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test clearing cache."""
        tracking_file = temp_cache_dir / "file_tracking.json"
        tracking_file.write_text('{"test": "data"}')
        
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.cache_dir = temp_cache_dir
            mock_settings_instance.file_search_store_name = "test-store"
            mock_settings.return_value = mock_settings_instance
            
            mock_client = Mock()
            mock_file_search_stores = Mock()
            mock_file_search_stores.list.return_value = []
            mock_store = Mock()
            mock_store.name = "test-store-name"
            mock_file_search_stores.create.return_value = mock_store
            mock_client.file_search_stores = mock_file_search_stores
            mock_genai.Client.return_value = mock_client
            
            manager = FileManager(mock_api_key)
            result = manager.clear_cache()
            
            assert result is True
            assert not tracking_file.exists()
            assert manager._tracked_files == {}
    
    @patch('src.file_manager.genai')
    def test_get_file_search_store_name(self, mock_genai, mock_api_key, temp_cache_dir):
        """Test getting file search store name."""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.cache_dir = temp_cache_dir
            mock_settings_instance.file_search_store_name = "test-store"
            mock_settings.return_value = mock_settings_instance
            
            mock_client = Mock()
            mock_file_search_stores = Mock()
            mock_file_search_stores.list.return_value = []
            mock_store = Mock()
            mock_store.name = "test-store-name"
            mock_file_search_stores.create.return_value = mock_store
            mock_client.file_search_stores = mock_file_search_stores
            mock_genai.Client.return_value = mock_client
            
            manager = FileManager(mock_api_key)
            store_name = manager.get_file_search_store_name()
            
            assert store_name == "test-store-name"

