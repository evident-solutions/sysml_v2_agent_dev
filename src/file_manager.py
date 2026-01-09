"""File manager for uploading and tracking PDFs in Gemini File Search."""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from google import genai
from tqdm import tqdm

from config.settings import get_settings
from utils.logger import setup_logger
from utils.validators import validate_pdf_file

logger = setup_logger(__name__)


class FileManager:
    """Manages file uploads and tracking for Gemini File Search."""
    
    def __init__(self, api_key: str):
        """
        Initialize the file manager.
        
        Args:
            api_key: Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.settings = get_settings()
        self.tracking_file = self.settings.cache_dir / "file_tracking.json"
        self._tracked_files: Dict[str, dict] = self._load_tracking()
        self.file_search_store = None
        self._initialize_file_search_store()
    
    def _load_tracking(self) -> Dict[str, dict]:
        """Load file tracking data from cache."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load tracking file: {e}. Starting fresh.")
                return {}
        return {}
    
    def _save_tracking(self):
        """Save file tracking data to cache."""
        try:
            self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracking_file, 'w') as f:
                json.dump(self._tracked_files, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save tracking file: {e}")
    
    def _initialize_file_search_store(self):
        """Initialize or get the File Search Store."""
        try:
            store_name = self.settings.file_search_store_name
            
            # Try to get existing store by name
            # Note: The API may support listing stores, but if not, we'll create a new one
            try:
                # Try to list stores - this may not be available in all SDK versions
                if hasattr(self.client.file_search_stores, 'list'):
                    stores = self.client.file_search_stores.list()
                    for store in stores:
                        if hasattr(store, 'display_name') and store.display_name == store_name:
                            self.file_search_store = store
                            logger.info(f"Using existing File Search Store: {store_name} (name: {store.name})")
                            return
                        elif hasattr(store, 'name') and store_name in str(store.name):
                            self.file_search_store = store
                            logger.info(f"Using existing File Search Store: {store_name} (name: {store.name})")
                            return
            except (AttributeError, TypeError, Exception) as e:
                logger.debug(f"Could not list existing stores: {e}. Will create new store if needed.")
            
            # Create new store if not found
            # Always try to create - if it already exists, the API should handle it
            try:
                logger.info(f"Creating File Search Store: {store_name}")
                self.file_search_store = self.client.file_search_stores.create(
                    config={'display_name': store_name}
                )
                logger.info(f"File Search Store created/accessed: {self.file_search_store.name}")
            except Exception as create_error:
                # If create fails (e.g., store already exists), try to get it differently
                logger.warning(f"Could not create store (may already exist): {create_error}")
                # Try alternative: use store name directly if API supports it
                try:
                    # Some SDK versions might allow getting store by name
                    if hasattr(self.client.file_search_stores, 'get'):
                        self.file_search_store = self.client.file_search_stores.get(name=store_name)
                        logger.info(f"Retrieved existing File Search Store: {store_name}")
                    else:
                        raise create_error
                except Exception:
                    logger.error(f"Failed to create or retrieve File Search Store: {create_error}")
                    raise
                
        except Exception as e:
            logger.error(f"Failed to initialize File Search Store: {e}")
            logger.warning("File Search Store initialization failed. Continuing without store.")
            # Continue without store - user can still upload files, but file search may not work optimally
            self.file_search_store = None
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _is_file_tracked(self, file_path: Path) -> bool:
        """Check if a file is already tracked."""
        file_hash = self._compute_file_hash(file_path)
        file_key = str(file_path.resolve())
        
        if file_key in self._tracked_files:
            tracked_hash = self._tracked_files[file_key].get('hash')
            if tracked_hash == file_hash:
                return True
        
        return False
    
    def upload_file(self, file_path: str, show_progress: bool = True) -> Optional[dict]:
        """
        Upload a PDF file to Gemini File Search.
        
        Args:
            file_path: Path to the PDF file
            show_progress: Whether to show upload progress
            
        Returns:
            File metadata dict with 'name' and 'uri' keys, or None if upload failed
        """
        path = Path(file_path)
        
        # Validate file
        is_valid, error_msg = validate_pdf_file(str(path))
        if not is_valid:
            logger.error(error_msg)
            return None
        
        # Check if already uploaded
        if self._is_file_tracked(path):
            logger.info(f"File already uploaded: {path.name}")
            file_key = str(path.resolve())
            return {
                'name': self._tracked_files[file_key]['name'],
                'uri': self._tracked_files[file_key]['uri']
            }
        
        try:
            logger.info(f"Uploading file: {path.name}")
            
            # Upload file using new SDK
            # Note: Progress tracking may need to be handled differently in new SDK
            if show_progress:
                file_size = path.stat().st_size
                # Create progress bar
                pbar = tqdm(total=file_size, unit='B', unit_scale=True, desc=path.name)
                try:
                    uploaded_file = self.client.files.upload(file=str(path))
                    # Update progress bar to completion (if the SDK doesn't provide callback)
                    pbar.update(file_size)
                finally:
                    pbar.close()
            else:
                uploaded_file = self.client.files.upload(file=str(path))
            
            # Wait for file to be processed
            logger.info("Waiting for file to be processed...")
            # Check file state - new SDK may use different state attributes
            file_state = getattr(uploaded_file, 'state', None)
            if file_state is None:
                # Try alternative attribute names
                file_state = getattr(uploaded_file, 'processing_state', None)
            
            while file_state in ['PROCESSING', 'processing']:
                time.sleep(2)
                uploaded_file = self.client.files.get(name=uploaded_file.name)
                file_state = getattr(uploaded_file, 'state', None) or getattr(uploaded_file, 'processing_state', None)
            
            # Check for failure
            if file_state in ['FAILED', 'failed']:
                error_msg = getattr(uploaded_file, 'error', None) or getattr(uploaded_file, 'error_message', 'Unknown error')
                logger.error(f"File processing failed: {error_msg}")
                return None
            
            # Import file into File Search Store if store is available
            if self.file_search_store:
                try:
                    logger.info(f"Importing file into File Search Store...")
                    operation = self.client.file_search_stores.import_file(
                        file_search_store_name=self.file_search_store.name,
                        file_name=uploaded_file.name
                    )
                    
                    # Wait for import operation to complete
                    logger.info("Waiting for file import to complete...")
                    max_wait_time = 300  # Maximum wait time in seconds (5 minutes)
                    wait_time = 0
                    operation_name = getattr(operation, 'name', None) or str(operation)
                    
                    while wait_time < max_wait_time:
                        # Check if operation is done
                        if hasattr(operation, 'done'):
                            if operation.done:
                                break
                        elif hasattr(operation, 'status'):
                            # Check if operation is complete based on status
                            status = getattr(operation, 'status', '')
                            if status in ['DONE', 'done', 'SUCCESS', 'success']:
                                break
                            elif status in ['FAILED', 'failed', 'ERROR', 'error']:
                                error_msg = getattr(operation, 'error_message', getattr(operation, 'error', 'Unknown error'))
                                logger.error(f"File import failed with status {status}: {error_msg}")
                                return None
                        
                        time.sleep(2)
                        wait_time += 2
                        
                        # Refresh operation status
                        try:
                            if hasattr(self.client, 'operations') and operation_name:
                                operation = self.client.operations.get(name=operation_name)
                            else:
                                # If operations API is not available, assume done after initial wait
                                logger.warning("Operations API not available, assuming import is in progress")
                                break
                        except Exception as e:
                            logger.debug(f"Could not refresh operation status: {e}")
                            # Continue waiting or break based on error type
                            break
                    
                    # Final check for errors
                    if hasattr(operation, 'error') and operation.error:
                        logger.error(f"File import failed: {operation.error}")
                        return None
                    elif hasattr(operation, 'status'):
                        status = getattr(operation, 'status', '')
                        if status in ['FAILED', 'failed', 'ERROR', 'error']:
                            error_msg = getattr(operation, 'error_message', getattr(operation, 'error', 'Unknown error'))
                            logger.error(f"File import failed with status {status}: {error_msg}")
                            return None
                    
                    logger.info("File import operation completed successfully")
                    
                    logger.info("File successfully imported into File Search Store")
                except Exception as e:
                    logger.warning(f"Failed to import file into store: {e}. File uploaded but may not be searchable.")
            
            # Track the file
            file_hash = self._compute_file_hash(path)
            file_key = str(path.resolve())
            # Extract name and uri - new SDK structure may differ
            file_name = getattr(uploaded_file, 'name', None) or str(uploaded_file)
            file_uri = getattr(uploaded_file, 'uri', None) or getattr(uploaded_file, 'file_uri', None) or file_name
            
            self._tracked_files[file_key] = {
                'name': file_name,
                'uri': file_uri,
                'hash': file_hash,
                'upload_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'original_path': str(path),
                'store_name': self.file_search_store.name if self.file_search_store else None
            }
            self._save_tracking()
            
            logger.info(f"Successfully uploaded: {path.name} (URI: {file_uri})")
            return {
                'name': file_name,
                'uri': file_uri
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file {path.name}: {e}")
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
        from utils.validators import validate_directory
        
        path = Path(directory_path)
        is_valid, error_msg = validate_directory(str(path))
        if not is_valid:
            logger.error(error_msg)
            return []
        
        pdf_files = list(path.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {directory_path}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF file(s) in {directory_path}")
        uploaded_files = []
        
        for pdf_file in pdf_files:
            result = self.upload_file(str(pdf_file), show_progress=show_progress)
            if result:
                uploaded_files.append(result)
        
        logger.info(f"Successfully uploaded {len(uploaded_files)}/{len(pdf_files)} file(s)")
        return uploaded_files
    
    def list_files(self) -> List[dict]:
        """
        List all tracked files.
        
        Returns:
            List of file metadata dictionaries
        """
        files = []
        for file_key, file_info in self._tracked_files.items():
            files.append({
                'original_path': file_info.get('original_path', file_key),
                'name': file_info.get('name', 'Unknown'),
                'uri': file_info.get('uri', 'Unknown'),
                'upload_date': file_info.get('upload_date', 'Unknown')
            })
        return files
    
    def clear_cache(self) -> bool:
        """
        Clear the file tracking cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.tracking_file.exists():
                self.tracking_file.unlink()
            self._tracked_files = {}
            logger.info("File tracking cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_file_search_store_name(self) -> Optional[str]:
        """
        Get the File Search Store name for use in RAG queries.
        
        Returns:
            File Search Store name, or None if not initialized
        """
        if self.file_search_store:
            return self.file_search_store.name
        return None
    
    def get_file_uris(self) -> List[str]:
        """
        Get list of all tracked file URIs (legacy method for backward compatibility).
        
        Returns:
            List of file URIs
        """
        return [
            file_info.get('uri')
            for file_info in self._tracked_files.values()
            if file_info.get('uri')
        ]

