"""RAG handler for processing questions using Gemini File Search."""

import time
from typing import List, Optional

from google import genai
from google.genai import types

from config.settings import get_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RAGHandler:
    """Handles RAG queries using Gemini File Search."""
    
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """
        Initialize the RAG handler.
        
        Args:
            api_key: Gemini API key
            model_name: Optional name of the Gemini model to use (defaults to settings)
        """
        self.client = genai.Client(api_key=api_key)
        self.settings = get_settings()
        self.model_name = model_name or self.settings.gemini_model
        logger.info(f"Initialized RAG handler with model: {self.model_name}")
    
    def ask_question(
        self,
        question: str,
        file_search_store_name: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Ask a question using RAG with File Search Store.
        
        Args:
            question: The question to ask
            file_search_store_name: Optional File Search Store name to search in
            system_prompt: Optional system prompt to guide the model
            
        Returns:
            The model's response as a string
        """
        if not file_search_store_name:
            logger.warning("No File Search Store name provided. Answering without file context.")
        
        try:
            # Build the prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nQuestion: {question}"
            else:
                full_prompt = self._build_default_prompt(question)
            
            logger.info(f"Processing question: {question[:100]}...")
            
            # Build contents - just the prompt text, no file URIs needed
            contents = [types.Part.from_text(text=full_prompt)]
            
            # Generate response using new SDK with File Search Store
            # Configure generation parameters
            config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
            )
            
            # Enable file search tool with File Search Store if store name provided
            if file_search_store_name:
                try:
                    # Configure file search tool with store name
                    config.tools = [
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[file_search_store_name]
                            )
                        )
                    ]
                    logger.info(f"Using File Search Store: {file_search_store_name}")
                except (AttributeError, TypeError) as e:
                    logger.error(f"Failed to configure File Search tool: {e}")
                    logger.warning("Continuing without file search tool - answer may not use file context")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # Extract text from response
            # Response structure may differ in new SDK
            if hasattr(response, 'text'):
                answer = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Try to extract from candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content'):
                    if hasattr(candidate.content, 'parts'):
                        # Extract text from parts
                        text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                        answer = ' '.join(text_parts)
                    else:
                        answer = str(candidate.content)
                else:
                    answer = str(candidate)
            else:
                answer = str(response)
            
            logger.info("Successfully generated response")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _build_default_prompt(self, question: str) -> str:
        """Build a default prompt for SysML questions."""
        return f"""You are a SysML v2 expert assistant. Answer the following question about SysML v2 concepts, definitions, and best practices based on the provided documentation.

Question: {question}

Please provide a clear, accurate, and comprehensive answer. If the information is not available in the provided documents, please state that clearly."""
    
    def ask_with_retry(
        self,
        question: str,
        file_search_store_name: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> str:
        """
        Ask a question with retry logic for handling transient errors.
        
        Args:
            question: The question to ask
            file_search_store_name: Optional File Search Store name to search in
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            The model's response as a string
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.ask_question(question, file_search_store_name=file_search_store_name)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(f"All {max_retries} attempts failed")
        
        raise RuntimeError(
            f"Failed to get response after {max_retries} attempts"
        ) from last_exception

