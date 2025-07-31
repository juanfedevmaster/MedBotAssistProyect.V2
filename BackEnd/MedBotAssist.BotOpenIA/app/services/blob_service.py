"""
Azure Blob Storage Service for MedBot Assistant

This service handles file operations with Azure Blob Storage using SAS tokens from JWT claims.
It provides methods to list, download, and retrieve metadata from blob files in the instructions-files container.
"""

from typing import List, Dict, Any, Optional, Tuple
import httpx
import asyncio
from urllib.parse import urljoin, quote
from fastapi import HTTPException, status
from app.core.config import settings
import logging
from datetime import datetime
import mimetypes
from io import BytesIO

logger = logging.getLogger(__name__)

class BlobService:
    """Service for interacting with Azure Blob Storage using SAS tokens."""
    
    def __init__(self):
        self.base_url = settings.BLOB_STORAGE_BASE_URL
        self.container_name = settings.BLOB_CONTAINER_NAME
        self.timeout = 30.0
        
    def _build_blob_url(self, blob_name: str = "", sas_token: str = "") -> str:
        """
        Build the complete URL for blob operations.
        
        Args:
            blob_name: Name of the blob file (empty for container operations)
            sas_token: SAS token for authentication
            
        Returns:
            Complete URL for the blob operation
        """
        if blob_name:
            # URL for specific blob
            url = f"{self.base_url}/{self.container_name}/{quote(blob_name)}"
        else:
            # URL for container operations
            url = f"{self.base_url}/{self.container_name}"
            
        if sas_token:
            # Add SAS token (remove leading ? if present)
            sas_clean = sas_token.lstrip('?')
            url += f"?{sas_clean}"
            
        return url
    
    async def list_blobs(self, sas_token: str, prefix: str = "") -> List[Dict[str, Any]]:
        """
        List all blobs in the instructions-files container.
        
        Args:
            sas_token: SAS token from JWT claim
            prefix: Optional prefix to filter blobs
            
        Returns:
            List of blob metadata dictionaries
            
        Raises:
            HTTPException: If the request fails or authentication is invalid
        """
        try:
            # Build URL for listing blobs
            url = self._build_blob_url(sas_token=sas_token)
            
            # Add query parameters for listing
            params = {
                "restype": "container",
                "comp": "list"
            }
            
            if prefix:
                params["prefix"] = prefix
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    # Parse XML response (Azure returns XML for blob listing)
                    blobs = self._parse_blob_list_xml(response.text)
                    logger.info(f"Successfully listed {len(blobs)} blobs from container '{self.container_name}'")
                    return blobs
                    
                elif response.status_code == 403:
                    logger.error("Access denied to blob storage - invalid or expired SAS token")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied to blob storage. Invalid or expired SAS token."
                    )
                elif response.status_code == 404:
                    logger.error(f"Container '{self.container_name}' not found")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Container '{self.container_name}' not found"
                    )
                else:
                    logger.error(f"Failed to list blobs: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to access blob storage: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout while accessing blob storage")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Timeout while accessing blob storage"
            )
        except Exception as e:
            logger.error(f"Error listing blobs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error accessing blob storage: {str(e)}"
            )
    
    async def download_blob(self, blob_name: str, sas_token: str) -> Tuple[bytes, Dict[str, str]]:
        """
        Download a specific blob file.
        
        Args:
            blob_name: Name of the blob to download
            sas_token: SAS token from JWT claim
            
        Returns:
            Tuple of (file_content_bytes, metadata_dict)
            
        Raises:
            HTTPException: If the blob doesn't exist or download fails
        """
        try:
            url = self._build_blob_url(blob_name, sas_token)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    # Extract metadata from headers
                    metadata = {
                        "content_type": response.headers.get("content-type", "application/octet-stream"),
                        "content_length": response.headers.get("content-length", "0"),
                        "last_modified": response.headers.get("last-modified", ""),
                        "etag": response.headers.get("etag", ""),
                        "blob_name": blob_name
                    }
                    
                    logger.info(f"Successfully downloaded blob '{blob_name}' ({metadata['content_length']} bytes)")
                    return response.content, metadata
                    
                elif response.status_code == 404:
                    logger.error(f"Blob '{blob_name}' not found")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"File '{blob_name}' not found in blob storage"
                    )
                elif response.status_code == 403:
                    logger.error("Access denied to blob - invalid or expired SAS token")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied to blob storage. Invalid or expired SAS token."
                    )
                else:
                    logger.error(f"Failed to download blob '{blob_name}': {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to download file: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout while downloading blob '{blob_name}'")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Timeout while downloading file"
            )
        except Exception as e:
            logger.error(f"Error downloading blob '{blob_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error downloading file: {str(e)}"
            )
    
    async def get_blob_metadata(self, blob_name: str, sas_token: str) -> Dict[str, Any]:
        """
        Get metadata for a specific blob without downloading its content.
        
        Args:
            blob_name: Name of the blob
            sas_token: SAS token from JWT claim
            
        Returns:
            Dictionary with blob metadata
            
        Raises:
            HTTPException: If the blob doesn't exist or request fails
        """
        try:
            url = self._build_blob_url(blob_name, sas_token)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use HEAD request to get only metadata
                response = await client.head(url)
                
                if response.status_code == 200:
                    metadata = {
                        "blob_name": blob_name,
                        "content_type": response.headers.get("content-type", "application/octet-stream"),
                        "content_length": int(response.headers.get("content-length", "0")),
                        "last_modified": response.headers.get("last-modified", ""),
                        "etag": response.headers.get("etag", "").strip('"'),
                        "creation_time": response.headers.get("x-ms-creation-time", ""),
                        "blob_type": response.headers.get("x-ms-blob-type", "BlockBlob"),
                        "server_encrypted": response.headers.get("x-ms-server-encrypted", "false") == "true"
                    }
                    
                    # Try to determine file extension and type
                    if "." in blob_name:
                        file_extension = blob_name.split(".")[-1].lower()
                        metadata["file_extension"] = file_extension
                        
                        # Guess content type if not properly set
                        if metadata["content_type"] == "application/octet-stream":
                            guessed_type, _ = mimetypes.guess_type(blob_name)
                            if guessed_type:
                                metadata["guessed_content_type"] = guessed_type
                    
                    logger.info(f"Retrieved metadata for blob '{blob_name}'")
                    return metadata
                    
                elif response.status_code == 404:
                    logger.error(f"Blob '{blob_name}' not found")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"File '{blob_name}' not found in blob storage"
                    )
                elif response.status_code == 403:
                    logger.error("Access denied to blob metadata")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied to blob storage. Invalid or expired SAS token."
                    )
                else:
                    logger.error(f"Failed to get blob metadata: {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to get file metadata: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout while getting blob metadata for '{blob_name}'")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Timeout while accessing file metadata"
            )
        except Exception as e:
            logger.error(f"Error getting blob metadata for '{blob_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting file metadata: {str(e)}"
            )
    
    def _parse_blob_list_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Parse XML response from Azure Blob Storage list operation.
        
        Args:
            xml_content: XML response from Azure
            
        Returns:
            List of blob information dictionaries
        """
        blobs = []
        
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_content)
            
            # Azure blob list XML has namespace
            namespace = {'ns': 'http://schemas.microsoft.com/windowsazure'}
            
            # Find all blob elements
            for blob_elem in root.findall('.//ns:Blob', namespace):
                blob_info = {}
                
                # Extract blob name
                name_elem = blob_elem.find('ns:Name', namespace)
                if name_elem is not None:
                    blob_info['name'] = name_elem.text
                
                # Extract properties
                props_elem = blob_elem.find('ns:Properties', namespace)
                if props_elem is not None:
                    # Content type
                    content_type_elem = props_elem.find('ns:Content-Type', namespace)
                    if content_type_elem is not None:
                        blob_info['content_type'] = content_type_elem.text
                    
                    # Content length
                    content_length_elem = props_elem.find('ns:Content-Length', namespace)
                    if content_length_elem is not None:
                        blob_info['size'] = int(content_length_elem.text)
                    
                    # Last modified
                    last_modified_elem = props_elem.find('ns:Last-Modified', namespace)
                    if last_modified_elem is not None:
                        blob_info['last_modified'] = last_modified_elem.text
                    
                    # ETag
                    etag_elem = props_elem.find('ns:Etag', namespace)
                    if etag_elem is not None:
                        blob_info['etag'] = etag_elem.text.strip('"')
                
                # Add file extension if available
                if 'name' in blob_info and '.' in blob_info['name']:
                    blob_info['file_extension'] = blob_info['name'].split('.')[-1].lower()
                
                blobs.append(blob_info)
        
        except Exception as e:
            logger.error(f"Error parsing blob list XML: {e}")
            # Return empty list if parsing fails
            return []
        
        return blobs
    
    async def blob_exists(self, blob_name: str, sas_token: str) -> bool:
        """
        Check if a blob exists in the container.
        
        Args:
            blob_name: Name of the blob to check
            sas_token: SAS token from JWT claim
            
        Returns:
            True if the blob exists, False otherwise
        """
        try:
            await self.get_blob_metadata(blob_name, sas_token)
            return True
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                return False
            # Re-raise other errors
            raise
    
    def get_container_info(self) -> Dict[str, str]:
        """
        Get information about the blob service configuration.
        
        Returns:
            Dictionary with service configuration
        """
        return {
            "base_url": self.base_url,
            "container_name": self.container_name,
            "timeout_seconds": self.timeout,
            "service_type": "Azure Blob Storage"
        }
