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
from datetime import datetime, timedelta
import mimetypes
from io import BytesIO

# Azure Storage imports
try:
    from azure.storage.blob import BlobServiceClient, generate_blob_sas, generate_container_sas, BlobSasPermissions, ContainerSasPermissions
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

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
            # Build base URL without SAS parameters
            base_url = f"{self.base_url}/{self.container_name}"
            
            # Parse SAS token into parameters
            from urllib.parse import parse_qs, urlparse, unquote
            if sas_token.startswith('?'):
                sas_token = sas_token[1:]
            
            # Decode URL encoding first to avoid double encoding
            sas_token_decoded = unquote(sas_token)
            
            # Combine SAS parameters with listing parameters
            params = {}
            for param_pair in sas_token_decoded.split('&'):
                if '=' in param_pair:
                    key, value = param_pair.split('=', 1)
                    params[key] = value
            
            # Add query parameters for listing
            params.update({
                "restype": "container",
                "comp": "list"
            })
            
            if prefix:
                params["prefix"] = prefix
            
            logger.info(f"Attempting to list blobs from container '{self.container_name}'")
            logger.info(f"Base URL: {base_url}")
            logger.info(f"Combined params: {params}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(base_url, params=params)
                
                logger.info(f"Blob storage response status: {response.status_code}")
                logger.info(f"Final request URL: {response.request.url}")
                
                if response.status_code == 200:
                    # Parse XML response (Azure returns XML for blob listing)
                    logger.debug(f"XML response preview: {response.text[:500]}...")
                    try:
                        blobs = self._parse_blob_list_xml(response.text)
                        logger.info(f"Successfully listed {len(blobs)} blobs from container '{self.container_name}'")
                        return blobs
                    except Exception as parse_error:
                        logger.error(f"Error parsing blob list XML: {parse_error}")
                        logger.debug(f"Full XML content: {response.text}")
                        # Return empty list if parsing fails but request was successful
                        return []
                    
                elif response.status_code == 403:
                    logger.error(f"Access denied to blob storage - Response: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied to blob storage. Invalid or expired SAS token."
                    )
                elif response.status_code == 404:
                    logger.error(f"Container '{self.container_name}' not found - Response: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Container '{self.container_name}' not found"
                    )
                else:
                    logger.error(f"Failed to list blobs: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to access blob storage: {response.status_code}: {response.text[:200]}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout while accessing blob storage")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Timeout while accessing blob storage"
            )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
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
            # Build base URL without SAS parameters
            base_url = f"{self.base_url}/{self.container_name}/{blob_name}"
            
            # Parse SAS token into parameters
            from urllib.parse import parse_qs, urlparse, unquote
            if sas_token.startswith('?'):
                sas_token = sas_token[1:]
            
            # Decode URL encoding first to avoid double encoding
            sas_token_decoded = unquote(sas_token)
            
            # Convert SAS token to parameters dict
            params = {}
            for param_pair in sas_token_decoded.split('&'):
                if '=' in param_pair:
                    key, value = param_pair.split('=', 1)
                    params[key] = value
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(base_url, params=params)
                
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
            # Build base URL without SAS parameters
            base_url = f"{self.base_url}/{self.container_name}/{blob_name}"
            
            # Parse SAS token into parameters
            from urllib.parse import parse_qs, urlparse, unquote
            if sas_token.startswith('?'):
                sas_token = sas_token[1:]
            
            # Decode URL encoding first to avoid double encoding
            sas_token_decoded = unquote(sas_token)
            
            # Convert SAS token to parameters dict
            params = {}
            for param_pair in sas_token_decoded.split('&'):
                if '=' in param_pair:
                    key, value = param_pair.split('=', 1)
                    params[key] = value
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use HEAD request to get only metadata
                response = await client.head(base_url, params=params)
                
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
            if not xml_content or not xml_content.strip():
                logger.warning("Empty XML content received from blob storage")
                return []
            
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_content)
            
            # Try both with and without namespace
            # Azure blob list XML may or may not have namespace
            namespace = {'ns': 'http://schemas.microsoft.com/windowsazure'}
            
            # First try with namespace
            blobs_container = root.find('.//ns:Blobs', namespace)
            blob_elements = root.findall('.//ns:Blob', namespace)
            
            # If no results with namespace, try without namespace
            if blobs_container is None or not blob_elements:
                blobs_container = root.find('.//Blobs')
                blob_elements = root.findall('.//Blob')
                namespace = None  # Don't use namespace for element searches
            
            if blobs_container is None and not blob_elements:
                logger.warning("No Blobs element found in XML response - container might be empty")
                return []
            
            logger.info(f"Found {len(blob_elements)} blob elements in XML")
            
            for blob_elem in blob_elements:
                blob_info = {}
                
                # Extract blob name (with or without namespace)
                if namespace:
                    name_elem = blob_elem.find('ns:Name', namespace)
                else:
                    name_elem = blob_elem.find('Name')
                    
                if name_elem is not None and name_elem.text:
                    blob_info['name'] = name_elem.text
                else:
                    logger.warning("Blob element found without name, skipping")
                    continue
                
                # Extract properties
                if namespace:
                    props_elem = blob_elem.find('ns:Properties', namespace)
                else:
                    props_elem = blob_elem.find('Properties')
                    
                if props_elem is not None:
                    # Content type
                    if namespace:
                        content_type_elem = props_elem.find('ns:Content-Type', namespace)
                    else:
                        content_type_elem = props_elem.find('Content-Type')
                        
                    if content_type_elem is not None:
                        blob_info['content_type'] = content_type_elem.text
                    
                    # Content length
                    if namespace:
                        content_length_elem = props_elem.find('ns:Content-Length', namespace)
                    else:
                        content_length_elem = props_elem.find('Content-Length')
                        
                    if content_length_elem is not None:
                        try:
                            blob_info['size'] = int(content_length_elem.text)
                        except (ValueError, TypeError):
                            blob_info['size'] = 0
                    
                    # Last modified
                    if namespace:
                        last_modified_elem = props_elem.find('ns:Last-Modified', namespace)
                    else:
                        last_modified_elem = props_elem.find('Last-Modified')
                        
                    if last_modified_elem is not None:
                        blob_info['last_modified'] = last_modified_elem.text
                    
                    # ETag
                    if namespace:
                        etag_elem = props_elem.find('ns:Etag', namespace)
                    else:
                        etag_elem = props_elem.find('Etag')
                        
                    if etag_elem is not None:
                        blob_info['etag'] = etag_elem.text.strip('"')
                
                # Add file extension if available
                if 'name' in blob_info and '.' in blob_info['name']:
                    blob_info['file_extension'] = blob_info['name'].split('.')[-1].lower()
                
                blobs.append(blob_info)
                
            logger.info(f"Successfully parsed {len(blobs)} blobs from XML")
        
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            logger.debug(f"Problematic XML content: {xml_content[:1000]}...")
            raise Exception(f"Invalid XML response from blob storage: {e}")
        
        except Exception as e:
            logger.error(f"Error parsing blob list XML: {e}")
            logger.debug(f"XML content preview: {xml_content[:500]}...")
            raise Exception(f"Failed to parse blob list: {e}")
        
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

    def generate_sas_token(self) -> Optional[str]:
        """
        Generate a SAS token for blob storage access using Azure Storage SDK.
        
        Returns:
            SAS token string or None if not available
        """
        try:
            if not AZURE_AVAILABLE:
                logger.error("Azure Storage SDK not available. Install azure-storage-blob package.")
                return None
            
            if not settings.AZURE_STORAGE_CONNECTION_STRING:
                logger.error("Azure Storage connection string not configured")
                return None
            
            # Create blob service client
            blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            
            # Generate SAS token for container with read and list permissions for 1 hour
            sas_token = generate_container_sas(
                account_name=blob_service_client.account_name,
                container_name=self.container_name,
                account_key=blob_service_client.credential.account_key,
                permission=ContainerSasPermissions(read=True, list=True),
                expiry=datetime.utcnow() + timedelta(hours=1)
            )
            
            logger.info("Generated SAS token for auto-vectorization")
            return sas_token
            
        except Exception as e:
            logger.error(f"Error generating SAS token: {e}")
            return None
    
    async def list_blobs_async(self) -> List[Dict[str, Any]]:
        """
        List all blobs in the container using Azure Storage SDK.
        
        Returns:
            List of blob metadata dictionaries
        """
        try:
            if not AZURE_AVAILABLE:
                logger.error("Azure Storage SDK not available. Install azure-storage-blob package.")
                return []
            
            if not settings.AZURE_STORAGE_CONNECTION_STRING:
                logger.error("Azure Storage connection string not configured")
                return []
            
            # Create blob service client
            blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            
            # Get container client
            container_client = blob_service_client.get_container_client(self.container_name)
            
            # List all blobs (using sync iterator, run in thread pool)
            import asyncio
            def _list_blobs():
                blobs = []
                for blob in container_client.list_blobs():
                    blob_info = {
                        'name': blob.name,
                        'size': blob.size,
                        'last_modified': blob.last_modified.isoformat() if blob.last_modified else None,
                        'content_type': blob.content_settings.content_type if blob.content_settings else None,
                        'etag': blob.etag
                    }
                    blobs.append(blob_info)
                return blobs
            
            # Run the sync operation in a thread pool
            blobs = await asyncio.get_event_loop().run_in_executor(None, _list_blobs)
            
            logger.info(f"Listed {len(blobs)} blobs from container '{self.container_name}'")
            return blobs
            
        except Exception as e:
            logger.error(f"Error listing blobs: {e}")
            return []
