"""Tests for main agent class."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from src.agent import SysMLAgent


class TestSysMLAgent:
    """Tests for SysMLAgent class."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('src.agent.get_settings') as mock_get_settings:
            mock_settings_instance = Mock()
            mock_settings_instance.gemini_api_key = "test_api_key"
            mock_settings_instance.validate.return_value = (True, None)
            mock_get_settings.return_value = mock_settings_instance
            yield mock_settings_instance
    
    @patch('src.agent.FileManager')
    @patch('src.agent.RAGHandler')
    def test_initialization(self, mock_rag_handler, mock_file_manager, mock_settings):
        """Test agent initialization."""
        mock_file_manager_instance = Mock()
        mock_rag_handler_instance = Mock()
        mock_file_manager.return_value = mock_file_manager_instance
        mock_rag_handler.return_value = mock_rag_handler_instance
        
        agent = SysMLAgent()
        
        assert agent is not None
        assert agent.file_manager == mock_file_manager_instance
        assert agent.rag_handler == mock_rag_handler_instance
    
    @patch('src.agent.FileManager')
    @patch('src.agent.RAGHandler')
    def test_upload_file(self, mock_rag_handler, mock_file_manager, mock_settings):
        """Test uploading a file."""
        mock_file_manager_instance = Mock()
        mock_file_manager_instance.upload_file.return_value = {"name": "test", "uri": "test_uri"}
        mock_file_manager.return_value = mock_file_manager_instance
        mock_rag_handler.return_value = Mock()
        
        agent = SysMLAgent()
        result = agent.upload_file("test.pdf")
        
        assert result == {"name": "test", "uri": "test_uri"}
        mock_file_manager_instance.upload_file.assert_called_once_with("test.pdf", show_progress=True)
    
    @patch('src.agent.FileManager')
    @patch('src.agent.RAGHandler')
    def test_list_files(self, mock_rag_handler, mock_file_manager, mock_settings):
        """Test listing files."""
        mock_file_manager_instance = Mock()
        mock_file_manager_instance.list_files.return_value = [
            {"name": "file1", "uri": "uri1"}
        ]
        mock_file_manager.return_value = mock_file_manager_instance
        mock_rag_handler.return_value = Mock()
        
        agent = SysMLAgent()
        files = agent.list_files()
        
        assert len(files) == 1
        assert files[0]["name"] == "file1"
    
    @patch('src.agent.FileManager')
    @patch('src.agent.RAGHandler')
    def test_ask_question(self, mock_rag_handler, mock_file_manager, mock_settings):
        """Test asking a question."""
        mock_file_manager_instance = Mock()
        mock_file_manager_instance.get_file_search_store_name.return_value = "test-store-name"
        mock_file_manager_instance.list_files.return_value = [{"name": "file1"}]
        mock_file_manager.return_value = mock_file_manager_instance
        
        mock_rag_handler_instance = Mock()
        mock_rag_handler_instance.ask_with_retry.return_value = "Test answer"
        mock_rag_handler.return_value = mock_rag_handler_instance
        
        agent = SysMLAgent()
        response = agent.ask_question("Test question")
        
        assert response == "Test answer"
        mock_rag_handler_instance.ask_with_retry.assert_called_once_with(
            "Test question",
            file_search_store_name="test-store-name",
            max_retries=3
        )
        mock_file_manager_instance.get_file_search_store_name.assert_called_once()
    
    @patch('src.agent.FileManager')
    @patch('src.agent.RAGHandler')
    def test_get_file_count(self, mock_rag_handler, mock_file_manager, mock_settings):
        """Test getting file count."""
        mock_file_manager_instance = Mock()
        mock_file_manager_instance.list_files.return_value = [
            {"name": "file1"},
            {"name": "file2"}
        ]
        mock_file_manager.return_value = mock_file_manager_instance
        mock_rag_handler.return_value = Mock()
        
        agent = SysMLAgent()
        count = agent.get_file_count()
        
        assert count == 2

