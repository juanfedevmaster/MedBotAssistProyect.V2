"""
Vectorization API Routes

FastAPI endpoints for document vectorization management.
All endpoints require JWT authentication with UseAgent permission.
"""

from fastapi import APIRouter, HTTPException, status, Query, Header
from typing import Optional, Dict, Any
import logging

from app.services.vectorization_manager import VectorizationManager
from app.services.jwt_service import JWTService
from app.agents.tools.instructive_search_tools import InstructiveSearchTools

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
vectorization_manager = VectorizationManager()
jwt_service = JWTService()
instructive_search = InstructiveSearchTools()

def validate_jwt_and_permissions(authorization: str) -> Dict[str, Any]:
    """
    Validates JWT token and checks for UseAgent permission.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Dict with user information
        
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )
        
    token = authorization.split(" ")[1]
    
    try:
        user_permissions = jwt_service.get_user_permissions(token)
        username = jwt_service.extract_username(token)
        user_id = jwt_service.extract_user_id(token)
        
        # Check for UseAgent permission
        if "UseAgent" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="UseAgent permission required to access vectorization endpoints"
            )
        
        logger.info(f"User '{username}' authenticated for vectorization endpoint")
        
        return {
            "username": username,
            "user_id": user_id,
            "permissions": user_permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid JWT token: {str(e)}"
        )

@router.get("/revectorize-all",
           summary="Revectorize all files in the blob container", 
           description="Clears existing vectors and revectorizes all files from scratch. Requires UseAgent permission and JWT with sasToken claim.")
async def revectorize_all(
    authorization: str = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Delete all existing vectors and revectorize all files in the blob container.
    
    This endpoint:
    1. Validates JWT authentication and UseAgent permission
    2. Extracts SAS token from JWT claims for blob storage access
    3. Clears all existing vectors and logs from ChromaDB
    4. Lists all files in the Azure Blob Storage container
    5. Processes each file individually, vectorizing from scratch
    6. Provides detailed summary of the operation
    7. Stores the names of vectorized files for tracking
    
    Warning: This operation is destructive and cannot be undone.
    All existing vectors will be permanently deleted.
    
    Args:
        authorization: JWT token with UseAgent permission and sasToken claim
        
    Returns:
        Operation summary with processed files, failures, and statistics
        
    Raises:
        HTTPException:
            - 401 for authentication errors
            - 403 for insufficient permissions or missing sasToken claim
            - 500 for internal errors
    """
    try:
        # Validate JWT and permissions
        user_info = validate_jwt_and_permissions(authorization)
        logger.info(f"API request to revectorize all files by user '{user_info['username']}'")
        
        # Extract SAS token from JWT
        token = authorization.split(" ")[1]
        sas_token = jwt_service.extract_sas_token(token)
        
        if not sas_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SAS token not found in JWT. Cannot access blob storage for revectorization."
            )
        
        # Perform complete revectorization
        result = await vectorization_manager.revectorize_all(sas_token)
        result["requested_by"] = user_info["username"]
        
        logger.info(f"Revectorization completed by '{user_info['username']}': {result.get('files_processed', 0)} files processed")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in revectorize_all endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )



@router.delete("/clear-vectors",
              summary="Clear all vectors and logs",
              description="Removes all vectors and vectorization logs (destructive operation). Requires UseAgent permission.")
async def clear_all_vectors(
    authorization: str = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Clear all vectors and vectorization logs from ChromaDB.
    
    Warning: This is a destructive operation that cannot be undone.
    All vectorized content will be permanently deleted.
    
    Args:
        authorization: JWT token with UseAgent permission
    
    Returns:
        Confirmation message with deletion counts
        
    Raises:
        HTTPException:
            - 401 for authentication errors
            - 403 for insufficient permissions
            - 500 for internal errors
    """
    try:
        # Validate JWT and permissions
        user_info = validate_jwt_and_permissions(authorization)
        logger.info(f"API request to clear all vectors by user '{user_info['username']}'")
        
        # Get current counts before deletion
        initial_vectors = vectorization_manager.collection.count()
        initial_logs = vectorization_manager.log_collection.count()
        
        # Clear vectors
        vector_results = vectorization_manager.collection.get()
        if vector_results['ids']:
            vectorization_manager.collection.delete(ids=vector_results['ids'])
        
        # Clear logs
        log_results = vectorization_manager.log_collection.get()
        if log_results['ids']:
            vectorization_manager.log_collection.delete(ids=log_results['ids'])
        
        result = {
            "status": "success",
            "message": "All vectors and logs cleared successfully",
            "vectors_deleted": initial_vectors,
            "logs_deleted": initial_logs,
            "requested_by": user_info["username"],
            "timestamp": vectorization_manager._get_current_timestamp()
        }
        
        logger.info(f"Cleared {initial_vectors} vectors and {initial_logs} logs by '{user_info['username']}'")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in clear_vectors endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        logger.error(f"Error clearing vectors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing vectors: {str(e)}"
        )

# Add a helper method to VectorizationManager for timestamp
def _get_current_timestamp():
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()

# Monkey patch the method (not ideal but works for this case)
vectorization_manager._get_current_timestamp = _get_current_timestamp


# ================================
# INSTRUCTIVE SEARCH ENDPOINTS
# ================================

@router.get("/search-instructives", 
           summary="Search in vectorized instructives",
           description="Search for information in vectorized medical instructives. Requires UseAgent permission.")
async def search_instructives(
    query: str = Query(..., description="Search query for instructives"),
    max_results: int = Query(5, description="Maximum number of results", ge=1, le=20),
    min_similarity: float = Query(0.7, description="Minimum similarity threshold", ge=0.0, le=1.0),
    authorization: str = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Search for information in vectorized medical instructives.
    
    This endpoint allows healthcare professionals to search through
    vectorized medical documents for specific procedures, protocols,
    or medication information.
    
    Args:
        query: Search query (e.g., "insulin administration procedure")
        max_results: Maximum number of results to return (1-20)
        min_similarity: Minimum similarity score (0.0-1.0)
        authorization: JWT token with UseAgent permission
    
    Returns:
        Dictionary with search results and contextual response
        
    Raises:
        HTTPException:
            - 401 for authentication errors
            - 403 for insufficient permissions
            - 500 for internal errors
    
    Example:
        GET /api/v1/vectorization/search-instructives?query=wound care protocol&max_results=3
    """
    try:
        # Validate JWT and permissions
        user_info = validate_jwt_and_permissions(authorization)
        
        # Use the instructive search tools
        result = instructive_search.search_instructive_information(
            query=query,
            max_results=max_results,
            min_similarity=min_similarity
        )
        
        # Add user info to result
        result["requested_by"] = user_info["username"]
        
        logger.info(f"Instructive search for '{query}' by '{user_info['username']}' returned {result.get('total_found', 0)} results")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching instructives: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching instructives: {str(e)}"
        )


@router.get("/available-instructives", 
           summary="Get list of available instructives",
           description="Get a list of all available instructives in the vector database. Requires UseAgent permission.")
async def get_available_instructives(
    authorization: str = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Get a list of all available instructives in the vector database.
    
    Returns information about what medical documents have been
    vectorized and are available for searching.
    
    Args:
        authorization: JWT token with UseAgent permission
    
    Returns:
        Dictionary with list of available instructive documents
        
    Raises:
        HTTPException:
            - 401 for authentication errors
            - 403 for insufficient permissions
            - 500 for internal errors
    
    Example:
        GET /api/v1/vectorization/available-instructives
    """
    try:
        # Validate JWT and permissions
        user_info = validate_jwt_and_permissions(authorization)
        
        result = instructive_search.get_available_instructives()
        result["requested_by"] = user_info["username"]
        
        logger.info(f"Retrieved {result.get('total_files', 0)} available instructives for '{user_info['username']}'")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available instructives: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting available instructives: {str(e)}"
        )


@router.get("/search-by-filename", 
           summary="Search within a specific instructive file",
           description="Search for information within a specific instructive file. Requires UseAgent permission.")
async def search_by_filename(
    filename: str = Query(..., description="Name of the file to search in"),
    query: str = Query("", description="Search query within the file (optional)"),
    authorization: str = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Search for information within a specific instructive file.
    
    This endpoint allows searching within a particular document
    that has been vectorized.
    
    Args:
        filename: Name of the file to search in
        query: Optional search query within the file
        authorization: JWT token with UseAgent permission
    
    Returns:
        Dictionary with search results from the specific file
        
    Raises:
        HTTPException:
            - 401 for authentication errors
            - 403 for insufficient permissions
            - 500 for internal errors
    
    Example:
        GET /api/v1/vectorization/search-by-filename?filename=insulin_protocol.pdf&query=dosage
    """
    try:
        # Validate JWT and permissions
        user_info = validate_jwt_and_permissions(authorization)
        
        result = instructive_search.search_by_filename(filename=filename, query=query)
        result["requested_by"] = user_info["username"]
        
        logger.info(f"Search in file '{filename}' with query '{query}' by '{user_info['username']}' returned {result.get('total_chunks', 0)} chunks")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching in file {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching in file: {str(e)}"
        )
