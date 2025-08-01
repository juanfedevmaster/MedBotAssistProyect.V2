"""
Vectorization Manager for MedBot Assistant

This service handles vectorization of files from Azure Blob Storage using OpenAI embeddings
and ChromaDB for storage and metadata management.
"""

# SQLite fix for Azure App Service BEFORE any other imports
try:
    import sqlite_fix
except ImportError:
    pass

from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime
import hashlib
import mimetypes
from io import BytesIO
import uuid

# Document processing
import PyPDF2
import docx
from bs4 import BeautifulSoup

# Vector database and embeddings
import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import AsyncOpenAI

# Project imports
from app.services.blob_service import BlobService
from app.core.config import settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class VectorizationManager:
    """
    Manages vectorization of files from Azure Blob Storage using OpenAI embeddings and ChromaDB.
    
    Features:
    - File download from Azure Blob Storage
    - Text extraction from various file types
    - Document chunking and vectorization
    - Metadata management and deduplication
    - URL generation for file access
    """
    
    def __init__(self, collection_name: str = None, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the VectorizationManager.
        
        Args:
            collection_name: Name of the ChromaDB collection for document vectors
            chunk_size: Size of text chunks for vectorization
            chunk_overlap: Overlap between chunks
        """
        self.collection_name = collection_name or settings.DEFAULT_COLLECTION_NAME
        self.log_collection_name = "vectorization_log"
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        # Initialize services
        self.blob_service = BlobService()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize ChromaDB client with environment detection
        try:
            import os
            
            # Detect if running in Azure App Service
            is_azure = os.environ.get('WEBSITE_SITE_NAME') is not None
            
            if is_azure:
                # Azure App Service configuration
                azure_db_path = "/home/site/wwwroot/chroma_db"
                logger.info(f"Azure environment detected. Using path: {azure_db_path}")
                
                # Ensure the directory exists
                os.makedirs(azure_db_path, exist_ok=True)
                
                # Use chromadb.Client with Settings for Azure
                from chromadb.config import Settings
                self.chroma_client = chromadb.Client(Settings(
                    persist_directory=azure_db_path,
                    anonymized_telemetry=False
                ))
                logger.info(f"ChromaDB initialized for Azure App Service at: {azure_db_path}")
                
            else:
                # Local development configuration
                logger.info(f"Local environment detected. Using path: {settings.VECTOR_DB_PATH}")
                
                # Ensure the directory exists
                os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
                
                # Use PersistentClient for local development
                self.chroma_client = chromadb.PersistentClient(
                    path=settings.VECTOR_DB_PATH,
                    settings=ChromaSettings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info(f"ChromaDB initialized for local development at: {settings.VECTOR_DB_PATH}")
            
        except Exception as e:
            logger.error(f"ChromaDB client initialization failed: {e}")
            logger.error("This will cause vectorization to fail. Check directory permissions and disk space.")
            # Don't fall back to in-memory - this breaks the system
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Vector database initialization failed: {str(e)}"
            )
        
        # Get or create collections
        self.collection = self._get_or_create_collection(self.collection_name)
        
        # Log collection status for debugging
        try:
            count = self.collection.count()
            logger.info(f"Collection '{self.collection_name}' initialized with {count} documents")
        except Exception as e:
            logger.error(f"Error getting collection count: {e}")
            logger.error("This may indicate ChromaDB initialization issues")
        self.log_collection = self._get_or_create_collection(self.log_collection_name)
        
        logger.info(f"VectorizationManager initialized with collection '{self.collection_name}'")
        
        # Comprehensive debug logging for collection state
        try:
            all_collections = self.chroma_client.list_collections()
            logger.info(f"DEBUG: All available collections: {[c.name for c in all_collections]}")
            
            main_count = self.collection.count()
            logger.info(f"DEBUG: Main collection '{self.collection_name}' document count: {main_count}")
            
            # Test adding and retrieving a sample document to verify persistence
            test_id = f"test_document_{datetime.now().timestamp()}"
            try:
                self.collection.add(
                    ids=[test_id],
                    documents=["Test document for persistence verification"],
                    metadatas=[{"test": True, "timestamp": datetime.now().isoformat()}]
                )
                logger.info(f"DEBUG: Successfully added test document {test_id}")
                
                # Immediately verify the document exists
                verification_count = self.collection.count()
                logger.info(f"DEBUG: Collection count after test add: {verification_count}")
                
                # Try to retrieve the test document
                test_results = self.collection.get(ids=[test_id])
                if test_results and test_results.get('documents'):
                    logger.info(f"DEBUG: Successfully retrieved test document: {test_results['documents'][0][:50]}...")
                    # Clean up test document
                    self.collection.delete(ids=[test_id])
                    logger.info(f"DEBUG: Test document cleaned up. Final count: {self.collection.count()}")
                else:
                    logger.error(f"DEBUG: Failed to retrieve test document {test_id}")
                    
            except Exception as test_e:
                logger.error(f"DEBUG: Test document operation failed: {test_e}")
                
        except Exception as debug_e:
            logger.error(f"DEBUG: Collection debugging failed: {debug_e}")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        try:
            collection = self.chroma_client.get_collection(name=name)
            logger.info(f"Retrieved existing collection: {name}")
        except Exception:
            collection = self.chroma_client.create_collection(name=name)
            logger.info(f"Created new collection: {name}")
        return collection
    
    def _generate_download_url(self, blob_name: str, sas_token: str) -> str:
        """
        Generate download URL for a blob using the BlobService logic.
        
        Args:
            blob_name: Name of the blob
            sas_token: SAS token for authentication
            
        Returns:
            Complete download URL with SAS token
        """
        return self.blob_service._build_blob_url(blob_name, sas_token)
    
    def _extract_text_from_file(self, file_content: bytes, file_name: str, content_type: str) -> str:
        """
        Extract text from various file types.
        
        Args:
            file_content: Binary content of the file
            file_name: Name of the file (for extension detection)
            content_type: MIME type of the file
            
        Returns:
            Extracted text content
            
        Raises:
            HTTPException: If file type is not supported or extraction fails
        """
        try:
            file_extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
            
            # PDF files
            if file_extension == 'pdf' or 'pdf' in content_type.lower():
                return self._extract_from_pdf(file_content)
            
            # Word documents
            elif file_extension in ['docx', 'doc'] or 'word' in content_type.lower():
                return self._extract_from_docx(file_content)
            
            # Text files
            elif file_extension in ['txt', 'md', 'csv'] or 'text' in content_type.lower():
                return file_content.decode('utf-8', errors='ignore')
            
            # HTML files
            elif file_extension in ['html', 'htm'] or 'html' in content_type.lower():
                return self._extract_from_html(file_content)
            
            # Unsupported format
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"File type '.{file_extension}' is not supported. Supported formats: PDF, DOCX, DOC, TXT, MD, CSV, HTML, HTM"
                )
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not extract text from file '{file_name}': {str(e)}"
            )
    
    def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error extracting PDF content: {str(e)}"
            )
    
    def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error extracting DOCX content: {str(e)}"
            )
    
    def _extract_from_html(self, file_content: bytes) -> str:
        """Extract text from HTML file."""
        try:
            soup = BeautifulSoup(file_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator='\n').strip()
        except Exception as e:
            logger.error(f"Error extracting from HTML: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error extracting HTML content: {str(e)}"
            )
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():  # Only add non-empty chunks
                chunks.append(chunk_text.strip())
        
        # If text is smaller than chunk size, return as single chunk
        if not chunks and text.strip():
            chunks.append(text.strip())
        
        return chunks
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.
        
        Args:
            texts: List of text chunks to vectorize
            
        Returns:
            List of embedding vectors
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts
            )
            
            embeddings = [embedding.embedding for embedding in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating embeddings: {str(e)}"
            )
    
    async def vectorize_file(self, blob_name: str, sas_token: str) -> Dict[str, Any]:
        """
        Vectorize a single file from blob storage.
        
        Args:
            blob_name: Name of the blob file to vectorize
            sas_token: SAS token for blob access
            
        Returns:
            Dictionary with vectorization results
        """
        try:
            logger.info(f"Starting vectorization of file: {blob_name}")
            
            # 1. Download file from blob storage
            file_content, metadata = await self.blob_service.download_blob(blob_name, sas_token)
            
            if not file_content:
                raise ValueError(f"No content retrieved for file {blob_name}")
            
            logger.info(f"Downloaded file {blob_name}: {len(file_content)} bytes")
            
            # 2. Extract text from file
            content_type = metadata.get('content_type', 'application/octet-stream')
            text_content = self._extract_text_from_file(file_content, blob_name, content_type)
            
            if not text_content or text_content.strip() == "":
                raise ValueError(f"No readable text content extracted from {blob_name}")
            
            logger.info(f"Extracted {len(text_content)} characters from {blob_name}")
            
            # 3. Chunk the text
            chunks = self._chunk_text(text_content)
            
            if not chunks:
                raise ValueError(f"No chunks generated from {blob_name}")
            
            logger.info(f"Generated {len(chunks)} chunks from {blob_name}")
            
            # 4. Generate embeddings
            embeddings = await self._generate_embeddings(chunks)
            
            if not embeddings or len(embeddings) != len(chunks):
                raise ValueError(f"Embedding generation failed for {blob_name}")
            
            # 5. Prepare data for ChromaDB
            chunk_ids = []
            chunk_metadatas = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{blob_name}_{i}_{hash(chunk[:50])}"
                chunk_metadata = {
                    'filename': blob_name,
                    'file_type': content_type,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_size': len(file_content),
                    'etag': metadata.get('etag', ''),
                    'last_modified': metadata.get('last_modified', ''),
                    'vectorization_timestamp': datetime.now().isoformat()
                }
                
                chunk_ids.append(chunk_id)
                chunk_metadatas.append(chunk_metadata)
            
            # 6. Add to ChromaDB collection
            logger.info(f"Adding {len(chunks)} chunks to ChromaDB collection for {blob_name}")
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadatas
            )
            
            # Verify the data was added
            collection_count = self.collection.count()
            logger.info(f"Successfully vectorized {blob_name}: {len(chunks)} chunks stored. Total collection count: {collection_count}")
            
            # Test query to verify data is accessible
            try:
                test_results = self.collection.query(
                    query_embeddings=[embeddings[0]],
                    n_results=1,
                    include=['documents']
                )
                if test_results and test_results.get('documents') and test_results['documents'][0]:
                    logger.info(f"Verification successful: Can query data for {blob_name}")
                else:
                    logger.warning(f"Verification failed: Cannot query data for {blob_name}")
            except Exception as e:
                logger.error(f"Verification query failed for {blob_name}: {e}")
            
            # 7. Log vectorization
            self._log_vectorization(
                blob_name=blob_name,
                etag=metadata.get('etag', ''),
                last_modified=metadata.get('last_modified', ''),
                chunks_processed=len(chunks)
            )
            
            return {
                'success': True,
                'file_name': blob_name,
                'chunks_processed': len(chunks),
                'file_size': len(file_content),
                'text_length': len(text_content),
                'vectorization_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error vectorizing file {blob_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error vectorizing file {blob_name}: {str(e)}"
            )

    def _log_vectorization(self, blob_name: str, etag: str, last_modified: str, chunks_processed: int):
        """
        Log vectorization operation to the log collection.
        
        Args:
            blob_name: Name of the vectorized blob
            etag: ETag of the blob
            last_modified: Last modified timestamp
            chunks_processed: Number of chunks processed
        """
        try:
            log_id = f"log_{blob_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Remove old log entries for this blob
            try:
                old_results = self.log_collection.get(where={"blob_name": blob_name})
                if old_results['ids']:
                    self.log_collection.delete(ids=old_results['ids'])
                    logger.info(f"Removed {len(old_results['ids'])} old log entries for '{blob_name}'")
            except:
                pass  # Ignore errors when removing old entries
            
            # Add new log entry
            self.log_collection.add(
                ids=[log_id],
                documents=[f"Vectorization log for {blob_name}"],
                metadatas=[{
                    "blob_name": blob_name,
                    "etag": etag,
                    "last_modified": last_modified,
                    "vectorization_timestamp": datetime.now().isoformat(),
                    "chunks_processed": chunks_processed
                }]
            )
            
            logger.info(f"Logged vectorization of '{blob_name}' ({chunks_processed} chunks)")
            
        except Exception as e:
            logger.error(f"Error logging vectorization: {e}")
            # Don't raise exception as this is not critical
    
    async def revectorize_all(self, sas_token: str) -> Dict[str, Any]:
        """
        Delete all vectors and revectorize all files in the blob container.
        
        Args:
            sas_token: SAS token for blob access
            
        Returns:
            Dictionary with operation summary
        """
        try:
            logger.info("Starting complete revectorization process")
            
            # 1. Clear existing vectors and logs
            logger.info("Clearing existing vectors and logs...")
            
            # Get all documents to delete them
            try:
                all_vectors = self.collection.get()
                if all_vectors['ids']:
                    self.collection.delete(ids=all_vectors['ids'])
                    logger.info(f"Deleted {len(all_vectors['ids'])} existing vectors")
            except Exception as e:
                logger.warning(f"Error clearing vectors: {e}")
            
            # Clear vectorization logs
            try:
                all_logs = self.log_collection.get()
                if all_logs['ids']:
                    self.log_collection.delete(ids=all_logs['ids'])
                    logger.info(f"Deleted {len(all_logs['ids'])} existing logs")
            except Exception as e:
                logger.warning(f"Error clearing logs: {e}")
            
            # 2. List all blobs in the container
            logger.info("Listing all files in blob container...")
            blobs = await self.blob_service.list_blobs(sas_token)
            
            if not blobs:
                return {
                    "status": "success",
                    "message": "No files found in blob container",
                    "files_processed": 0,
                    "files_failed": 0,
                    "total_chunks": 0
                }
            
            # 3. Process each blob
            processed_files = []
            failed_files = []
            total_chunks = 0
            
            logger.info(f"Processing {len(blobs)} files...")
            
            for blob in blobs:
                blob_name = blob.get('name', '')
                if not blob_name:
                    continue
                
                try:
                    logger.info(f"Processing file {len(processed_files) + len(failed_files) + 1}/{len(blobs)}: '{blob_name}'")
                    
                    result = await self.vectorize_file(blob_name, sas_token)
                    
                    processed_files.append({
                        "name": blob_name,
                        "chunks": result.get('chunks_processed', 0),
                        "size": result.get('file_size', '0')
                    })
                    
                    total_chunks += result.get('chunks_processed', 0)
                    
                except Exception as e:
                    logger.error(f"Failed to process '{blob_name}': {e}")
                    failed_files.append({
                        "name": blob_name,
                        "error": str(e)
                    })
            
            logger.info(f"Revectorization completed: {len(processed_files)} successful, {len(failed_files)} failed")
            
            return {
                "status": "completed",
                "message": f"Revectorization completed. Processed {len(processed_files)} files, {len(failed_files)} failed.",
                "files_processed": len(processed_files),
                "files_failed": len(failed_files),
                "total_chunks": total_chunks,
                "processed_files": processed_files,
                "failed_files": failed_files,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during revectorization: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during revectorization: {str(e)}"
            )

