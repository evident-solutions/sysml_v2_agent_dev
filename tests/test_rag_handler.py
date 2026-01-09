"""Tests for RAG handler."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from src.rag_handler import RAGHandler


class TestRAGHandler:
    """Tests for RAGHandler class."""
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing."""
        return "test_api_key_123"
    
    @patch('src.rag_handler.genai')
    @patch('src.rag_handler.types')
    def test_initialization(self, mock_types, mock_genai, mock_api_key):
        """Test RAGHandler initialization."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        
        handler = RAGHandler(mock_api_key)
        
        assert handler.client is not None
        mock_genai.Client.assert_called_once_with(api_key=mock_api_key)
        assert handler.model_name == "gemini-1.5-pro"
    
    @patch('src.rag_handler.genai')
    @patch('src.rag_handler.types')
    def test_ask_question(self, mock_types, mock_genai, mock_api_key):
        """Test asking a question."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test answer"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        
        # Mock Part.from_text
        mock_part = MagicMock()
        mock_types.Part.from_text.return_value = mock_part
        
        handler = RAGHandler(mock_api_key)
        response = handler.ask_question("Test question")
        
        assert response == "Test answer"
        mock_client.models.generate_content.assert_called_once()
    
    @patch('src.rag_handler.genai')
    @patch('src.rag_handler.types')
    def test_ask_question_with_file_search_store(self, mock_types, mock_genai, mock_api_key):
        """Test asking a question with file search store name."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test answer with store"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        
        # Mock Part.from_text
        mock_text_part = MagicMock()
        mock_types.Part.from_text.return_value = mock_text_part
        
        # Mock FileSearch and Tool types
        mock_file_search = MagicMock()
        mock_tool = MagicMock()
        mock_types.FileSearch.return_value = mock_file_search
        mock_types.Tool.return_value = mock_tool
        
        # Mock GenerateContentConfig
        mock_config = MagicMock()
        mock_types.GenerateContentConfig.return_value = mock_config
        
        handler = RAGHandler(mock_api_key)
        response = handler.ask_question("Test question", file_search_store_name="test-store-name")
        
        assert response == "Test answer with store"
        mock_client.models.generate_content.assert_called_once()
        # Verify FileSearch was configured with store name
        mock_types.FileSearch.assert_called_once_with(file_search_store_names=["test-store-name"])
    
    @patch('src.rag_handler.genai')
    @patch('src.rag_handler.types')
    def test_build_default_prompt(self, mock_types, mock_genai, mock_api_key):
        """Test default prompt building."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        
        handler = RAGHandler(mock_api_key)
        prompt = handler._build_default_prompt("What is SysML?")
        
        assert "SysML" in prompt
        assert "What is SysML?" in prompt
        assert "expert assistant" in prompt.lower()

