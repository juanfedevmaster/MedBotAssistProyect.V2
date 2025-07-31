"""
Blob Storage API Routes

This module provides endpoints for accessing Azure Blob Storage files
using SAS tokens from JWT claims.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.responses import StreamingResponse
from app.services.blob_service import BlobService
from app.services.jwt_service import JWTService
from typing import List, Dict, Any
import logging
from io import BytesIO

logger = logging.getLogger(__name__)
router = APIRouter()

# Global instances
blob_service = BlobService()
jwt_service = JWTService()

def get_blob_service() -> BlobService:
    """Dependency to get blob service instance."""
    return blob_service

def get_jwt_service() -> JWTService:
    """Dependency to get JWT service instance."""
    return jwt_service

@router.get(
    "/files",
    summary="List all instruction files",
    description="Get a list of all files in the instructions-files container",
    response_model=List[Dict[str, Any]]
)
async def list_instruction_files(
    blob_svc: BlobService = Depends(get_blob_service),
    jwt_svc: JWTService = Depends(get_jwt_service),
    authorization: str = Header(None, alias="Authorization")
) -> List[Dict[str, Any]]:
    """
    List all files in the instructions-files blob container.
    
    Requires a valid JWT token with sasToken claim for blob storage access.
    """
    try:
        # Validate JWT token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required with Bearer token"
            )
            
        token = authorization.split(" ")[1]
        
        # Extract SAS token from JWT
        sas_token = jwt_svc.extract_sas_token(token)
        if not sas_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SAS token not found in JWT. Cannot access blob storage."
            )
        
        # List blobs
        blobs = await blob_svc.list_blobs(sas_token)
        
        return {
            "files": blobs,
            "total_files": len(blobs),
            "container": blob_svc.container_name,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing instruction files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )

@router.get(
    "/files/{file_name:path}",
    summary="Download instruction file",
    description="Download a specific file from the instructions-files container"
)
async def download_instruction_file(
    file_name: str,
    blob_svc: BlobService = Depends(get_blob_service),
    jwt_svc: JWTService = Depends(get_jwt_service),
    authorization: str = Header(None, alias="Authorization")
):
    """
    Download a specific file from the instructions-files blob container.
    
    Args:
        file_name: Name of the file to download (can include folder paths)
    """
    try:
        # Validate JWT token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required with Bearer token"
            )
            
        token = authorization.split(" ")[1]
        
        # Extract SAS token from JWT
        sas_token = jwt_svc.extract_sas_token(token)
        if not sas_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SAS token not found in JWT. Cannot access blob storage."
            )
        
        # Download blob
        file_content, metadata = await blob_svc.download_blob(file_name, sas_token)
        
        # Create streaming response
        file_stream = BytesIO(file_content)
        
        return StreamingResponse(
            file_stream,
            media_type=metadata.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename={file_name.split('/')[-1]}",
                "Content-Length": metadata.get("content_length", "0"),
                "X-File-Name": file_name,
                "X-File-Size": metadata.get("content_length", "0")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file '{file_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )

@router.head(
    "/files/{file_name:path}",
    summary="Get file metadata",
    description="Get metadata for a specific file without downloading it"
)
async def get_file_metadata(
    file_name: str,
    blob_svc: BlobService = Depends(get_blob_service),
    jwt_svc: JWTService = Depends(get_jwt_service),
    authorization: str = Header(None, alias="Authorization")
):
    """
    Get metadata for a specific file in the instructions-files container.
    
    Args:
        file_name: Name of the file to get metadata for
    """
    try:
        # Validate JWT token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required with Bearer token"
            )
            
        token = authorization.split(" ")[1]
        
        # Extract SAS token from JWT
        sas_token = jwt_svc.extract_sas_token(token)
        if not sas_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SAS token not found in JWT. Cannot access blob storage."
            )
        
        # Get metadata
        metadata = await blob_svc.get_blob_metadata(file_name, sas_token)
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metadata for file '{file_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting file metadata: {str(e)}"
        )

@router.get(
    "/files/{file_name:path}/exists",
    summary="Check if file exists",
    description="Check if a specific file exists in the container"
)
async def check_file_exists(
    file_name: str,
    blob_svc: BlobService = Depends(get_blob_service),
    jwt_svc: JWTService = Depends(get_jwt_service),
    authorization: str = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Check if a specific file exists in the instructions-files container.
    
    Args:
        file_name: Name of the file to check
    """
    try:
        # Validate JWT token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required with Bearer token"
            )
            
        token = authorization.split(" ")[1]
        
        # Extract SAS token from JWT
        sas_token = jwt_svc.extract_sas_token(token)
        if not sas_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SAS token not found in JWT. Cannot access blob storage."
            )
        
        # Check if blob exists
        exists = await blob_svc.blob_exists(file_name, sas_token)
        
        return {
            "file_name": file_name,
            "exists": exists,
            "container": blob_svc.container_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking if file '{file_name}' exists: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking file existence: {str(e)}"
        )

@router.get(
    "/info",
    summary="Get blob service information",
    description="Get configuration information about the blob storage service"
)
async def get_blob_service_info(
    blob_svc: BlobService = Depends(get_blob_service)
) -> Dict[str, Any]:
    """
    Get information about the blob storage service configuration.
    """
    return blob_svc.get_container_info()
