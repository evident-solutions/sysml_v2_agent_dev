"""Main agent class orchestrating file management and RAG operations."""

from typing import List, Optional

from config.settings import get_settings
from src.file_manager import FileManager
from src.rag_handler import RAGHandler
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SysMLAgent:
    """Main SysML v2 expert agent."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SysML agent.
        
        Args:
            api_key: Optional Gemini API key (uses settings if not provided)
        """
        self.settings = get_settings()
        self.api_key = api_key or self.settings.gemini_api_key
        
        # Validate configuration
        is_valid, error_msg = self.settings.validate()
        if not is_valid:
            raise ValueError(f"Configuration error: {error_msg}")
        
        # Initialize components
        try:
            self.file_manager = FileManager(self.api_key)
            self.rag_handler = RAGHandler(self.api_key)
            logger.info("SysML Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    def upload_file(self, file_path: str, show_progress: bool = True) -> Optional[dict]:
        """
        Upload a PDF file to Gemini File Search.
        
        Args:
            file_path: Path to the PDF file
            show_progress: Whether to show upload progress
            
        Returns:
            File metadata dict or None if upload failed
        """
        try:
            return self.file_manager.upload_file(file_path, show_progress=show_progress)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None
    
    def upload_directory(self, directory_path: str, show_progress: bool = True) -> List[dict]:
        """
        Upload all PDF files from a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            show_progress: Whether to show upload progress
            
        Returns:
            List of successfully uploaded file metadata
        """
        try:
            return self.file_manager.upload_directory(directory_path, show_progress=show_progress)
        except Exception as e:
            logger.error(f"Error uploading directory: {e}")
            return []
    
    def list_files(self) -> List[dict]:
        """
        List all tracked files.
        
        Returns:
            List of file metadata dictionaries
        """
        try:
            return self.file_manager.list_files()
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def ask_question(
        self,
        question: str,
        use_retry: bool = True,
        max_retries: int = 3
    ) -> str:
        """
        Ask a SysML question using RAG.
        
        Args:
            question: The question to ask
            use_retry: Whether to use retry logic
            max_retries: Maximum number of retry attempts (if use_retry is True)
            
        Returns:
            The agent's response
        """
        try:
            # Get File Search Store name for context
            store_name = self.file_manager.get_file_search_store_name()
            
            if not store_name:
                logger.warning(
                    "No File Search Store available. Answering question without file context. "
                    "Consider uploading PDF documents first."
                )
            
            # Ask question with or without retry
            if use_retry:
                return self.rag_handler.ask_with_retry(
                    question,
                    file_search_store_name=store_name,
                    max_retries=max_retries
                )
            else:
                return self.rag_handler.ask_question(question, file_search_store_name=store_name)
                
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"Error: Failed to generate response. {str(e)}"
    
    def clear_cache(self) -> bool:
        """
        Clear the file tracking cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.file_manager.clear_cache()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_file_count(self) -> int:
        """
        Get the number of tracked files.
        
        Returns:
            Number of tracked files
        """
        return len(self.file_manager.list_files())

