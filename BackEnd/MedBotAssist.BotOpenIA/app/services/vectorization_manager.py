"""
Vectorization Manager for MedBot Assistant

This service handles vectorization of files from Azure Blob Storage using OpenAI embeddings
and in-memory vector storage for fast retrieval.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
from io import BytesIO
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Document processing
import PyPDF2
import docx
from bs4 import BeautifulSoup

# OpenAI embeddings
from openai import AsyncOpenAI

# Project imports
from app.services.blob_service import BlobService
from app.core.config import settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class VectorInMemoryDocument:
    """Represents a vectorized document chunk in memory."""
    
    def __init__(self, id: str, content: str, embedding: List[float], metadata: Dict[str, Any]):
        self.id = id
        self.content = content
        self.embedding = np.array(embedding)
        self.metadata = metadata

class VectorizationManager:
    """
    Manages vectorization of files from Azure Blob Storage using OpenAI embeddings 
    and in-memory vector storage for fast retrieval.
    """
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the VectorizationManager with in-memory storage.
        
        Args:
            chunk_size: Size of text chunks for vectorization
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        # In-memory storage for vectorized documents
        self.documents: Dict[str, VectorInMemoryDocument] = {}
        self.vectorization_log: Dict[str, Dict[str, Any]] = {}
        
        # Initialize services
        self.blob_service = BlobService()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        logger.info("VectorizationManager initialized with in-memory vector storage")
    
    def get_document_count(self) -> int:
        """Get the number of vectorized documents."""
        return len(self.documents)
    
    def clear_all_documents(self):
        """Clear all vectorized documents from memory."""
        self.documents.clear()
        self.vectorization_log.clear()
        logger.info("All documents cleared from memory")
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query_embedding: Query vector (1536 dimensions)
            top_k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        if not self.documents:
            return []
        
        query_vec = np.array(query_embedding).reshape(1, -1)
        similarities = []
        
        for doc_id, doc in self.documents.items():
            doc_vec = doc.embedding.reshape(1, -1)
            similarity = cosine_similarity(query_vec, doc_vec)[0][0]
            
            similarities.append({
                'id': doc_id,
                'content': doc.content,
                'metadata': doc.metadata,
                'similarity_score': float(similarity)
            })
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similarities[:top_k]
    async def vectorize_file(self, blob_name: str, sas_token: str) -> Dict[str, Any]:
        """
        Vectorize a single file from blob storage and store in memory.
        
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
            
            # 5. Store in memory
            chunks_stored = 0
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
                
                # Store document in memory
                self.documents[chunk_id] = VectorInMemoryDocument(
                    id=chunk_id,
                    content=chunk,
                    embedding=embedding,
                    metadata=chunk_metadata
                )
                chunks_stored += 1
            
            # 6. Update vectorization log
            self.vectorization_log[blob_name] = {
                'etag': metadata.get('etag', ''),
                'last_modified': metadata.get('last_modified', ''),
                'chunks_processed': chunks_stored,
                'vectorization_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully vectorized {blob_name}: {chunks_stored} chunks stored. Total documents: {len(self.documents)}")
            
            return {
                'success': True,
                'file_name': blob_name,
                'chunks_processed': chunks_stored,
                'file_size': len(file_content),
                'text_length': len(text_content),
                'total_documents': len(self.documents),
                'vectorization_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error vectorizing file {blob_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error vectorizing file {blob_name}: {str(e)}"
            )

    def _extract_text_from_file(self, file_content: bytes, file_name: str, content_type: str) -> str:
        """Extract text from various file types."""
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
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"File type '.{file_extension}' is not supported. Supported: PDF, DOCX, DOC, TXT, MD, CSV, HTML, HTM"
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
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error extracting DOCX content: {str(e)}"
            )
    
    def _extract_from_html(self, file_content: bytes) -> str:
        """Extract text from HTML file."""
        try:
            soup = BeautifulSoup(file_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator='\n').strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error extracting HTML content: {str(e)}"
            )
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
        
        if not chunks and text.strip():
            chunks.append(text.strip())
        
        return chunks
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI (1536 dimensions)."""
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts
            )
            
            embeddings = [embedding.embedding for embedding in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings with {len(embeddings[0])} dimensions")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating embeddings: {str(e)}"
            )

    async def revectorize_all(self, sas_token: str) -> Dict[str, Any]:
        """
        Clear all vectors and revectorize all files in the blob container.
        
        Args:
            sas_token: SAS token for blob access
            
        Returns:
            Dictionary with operation summary
        """
        try:
            logger.info("Starting complete revectorization process")
            
            # 1. Clear existing data
            self.clear_all_documents()
            
            # 2. List all blobs in the container
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
                "total_documents": len(self.documents),
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

    async def auto_vectorize_on_startup(self) -> Dict[str, Any]:
        """
        Auto-vectorize all files from Azure Blob Storage on server startup
        if the VectorInMemory database is empty.
        
        This method is called automatically when the server starts and the
        vector database is empty. It processes all files in the configured
        blob container.
        
        Returns:
            Dictionary with auto-vectorization results
        """
        try:
            # Check if auto-vectorization is enabled
            if not settings.AUTO_VECTORIZE_ON_STARTUP:
                logger.info("Auto-vectorization on startup is disabled")
                return {
                    "status": "disabled",
                    "message": "Auto-vectorization on startup is disabled in configuration"
                }
            
            # Check if vector database is empty
            if self.get_document_count() > 0:
                logger.info(f"Vector database already contains {self.get_document_count()} documents. Skipping auto-vectorization.")
                return {
                    "status": "skipped",
                    "message": f"Vector database already contains {self.get_document_count()} documents",
                    "document_count": self.get_document_count()
                }
            
            logger.info("Vector database is empty. Starting auto-vectorization from Azure Blob Storage...")
            
            # Check if Azure Storage connection string is configured
            if not settings.AZURE_STORAGE_CONNECTION_STRING:
                logger.warning("Azure Storage connection string not configured. Cannot perform auto-vectorization.")
                return {
                    "status": "error",
                    "message": "Azure Storage connection string not configured"
                }
            
            # Get SAS token for blob access
            sas_token = self.blob_service.generate_sas_token()
            if not sas_token:
                raise Exception("Failed to generate SAS token for blob access")
            
            # Get list of all blobs in the container
            blobs = await self.blob_service.list_blobs_async()
            if not blobs:
                logger.info("No files found in Azure Blob Storage container")
                return {
                    "status": "completed",
                    "message": "No files found in Azure Blob Storage container",
                    "files_processed": 0,
                    "files_failed": 0,
                    "total_chunks": 0,
                    "total_documents": 0,
                    "processed_files": [],
                    "failed_files": [],
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info(f"Found {len(blobs)} files in Azure Blob Storage. Starting auto-vectorization...")
            
            processed_files = []
            failed_files = []
            total_chunks = 0
            
            for blob in blobs:
                blob_name = blob.get('name', '')
                if not blob_name:
                    continue
                
                try:
                    logger.info(f"Auto-vectorizing file {len(processed_files) + len(failed_files) + 1}/{len(blobs)}: '{blob_name}'")
                    
                    result = await self.vectorize_file(blob_name, sas_token)
                    
                    processed_files.append({
                        "name": blob_name,
                        "chunks": result.get('chunks_processed', 0),
                        "size": result.get('file_size', '0')
                    })
                    
                    total_chunks += result.get('chunks_processed', 0)
                    
                except Exception as e:
                    logger.error(f"Failed to auto-vectorize '{blob_name}': {e}")
                    failed_files.append({
                        "name": blob_name,
                        "error": str(e)
                    })
            
            logger.info(f"Auto-vectorization completed: {len(processed_files)} successful, {len(failed_files)} failed, {total_chunks} total chunks")
            
            return {
                "status": "completed",
                "message": f"Auto-vectorization completed on startup. Processed {len(processed_files)} files with {total_chunks} chunks.",
                "files_processed": len(processed_files),
                "files_failed": len(failed_files),
                "total_chunks": total_chunks,
                "total_documents": len(self.documents),
                "processed_files": processed_files,
                "failed_files": failed_files,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during auto-vectorization on startup: {e}")
            return {
                "status": "error",
                "message": f"Error during auto-vectorization: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


# Global instance for the application - using singleton pattern
_vectorization_manager_instance = None

def get_vectorization_manager():
    """Get the singleton instance of VectorizationManager."""
    global _vectorization_manager_instance
    if _vectorization_manager_instance is None:
        _vectorization_manager_instance = VectorizationManager()
        logger.info(f"Created new VectorizationManager instance with {_vectorization_manager_instance.get_document_count()} documents")
    return _vectorization_manager_instance

# Backwards compatibility
vectorization_manager = get_vectorization_manager()
logger.info(f"VectorizationManager singleton initialized with {vectorization_manager.get_document_count()} documents")

