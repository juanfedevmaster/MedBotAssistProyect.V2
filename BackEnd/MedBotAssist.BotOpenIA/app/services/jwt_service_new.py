from typing import Optional, Dict, Any, List
import jwt
from fastapi import HTTPException, status
from app.core.config import settings
from app.services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)

class JWTService:
    """Service to handle JWT and obtain user permissions."""
    
    def __init__(self):
        self.db_service = DatabaseService()
        
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodes a JWT token and validates its authenticity.
        
        Args:
            token: JWT token (without the 'Bearer ' prefix)
            
        Returns:
            Decoded payload of the token
            Raises:
                HTTPException: If the token is invalid or has expired
        """
        try:
            # Decodificar el token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                issuer=settings.JWT_ISSUER,
                audience=settings.JWT_AUDIENCE
            )
            
            logger.info(f"Token decoded successfully for user: {payload.get('name', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def extract_username(self, token: str) -> str:
        """
        Extracts the username from the "name" claim of the JWT.
        
        Arguments:
            token: JWT token
            
        Returns:
            Username of the token
        """
        payload = self.decode_token(token)
        username = payload.get("name")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username not found in token"
            )
        
        return username
    
    def extract_user_id(self, token: str) -> str:
        """
        Extracts the user ID from the "userid" claim of the JWT.
        
        Arguments:
            token: JWT token
            
        Returns:
            User ID from the token
        """
        payload = self.decode_token(token)
        user_id = payload.get("userid")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        return str(user_id)
    
    def get_user_permissions(self, token: str) -> List[str]:
        """
        Obtains a user's permissions from the JWT's 'permissions' claim,
        or from the database if they are not in the token.

        Args:
            token: JWT token

        Returns:
            List of permission names for the user
        """
        try:
            payload = self.decode_token(token)

            # First check if permissions are in the token's claim
            permissions_claim = payload.get("permissions", [])
            if permissions_claim and isinstance(permissions_claim, list):
                logger.info(f"Using permissions from JWT claim: {permissions_claim}")
                return permissions_claim

            # If not in the token, query the database
            username = payload.get("name")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Username not found in token"
                )

            # Obtain permissions from the database
            db_permissions = self.db_service.get_user_permissions(username)
            permission_names = [perm["permission_name"] for perm in db_permissions]
            
            logger.info(f"Retrieved {len(permission_names)} permissions from database for user '{username}'")
            return permission_names
            
        except HTTPException:
            # Re-raise HTTPExceptions (JWT errors, etc.) to be handled by FastAPI
            logger.error("HTTPException occurred while getting user permissions")
            raise
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user permissions"
            )
    
    def get_user_permissions_detailed(self, token: str) -> List[Dict[str, Any]]:
        """
        Obtains detailed user permissions from the database using the JWT.
        This function always queries the database to obtain complete information.
        
        Args:
            token: JWT token
            
        Returns:
            List of detailed user permissions
        """
        try:
            # Extract username from the token
            username = self.extract_username(token)

            # Obtain permissions from the database
            permissions = self.db_service.get_user_permissions(username)
            
            logger.info(f"Retrieved {len(permissions)} detailed permissions for user '{username}'")
            return permissions
            
        except HTTPException:
            # Re-raise HTTPExceptions (JWT errors, etc.) to be handled by FastAPI
            raise
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user permissions"
            )
    
    def get_user_permission_names(self, token: str) -> List[str]:
        """
        Obtains only the names of the user's permissions (for easy verification).
        This function uses the get_user_permissions method to retrieve detailed permissions
        and then extracts just the names.
        Args:
            token: JWT token

        Returns:
            List of permission names
        """
        permissions = self.get_user_permissions(token)
        return [perm["permission_name"] for perm in permissions]
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Obtains complete information about the token and user permissions.
        This function decodes the token, extracts the username, and retrieves
        the user's permissions from the database.
        Args:
            token: JWT token

        Returns:
            Dictionary with token and permission information
        """
        try:
            # Decode token
            payload = self.decode_token(token)
            username = payload.get("name")

            # Obtain permissions
            permissions = self.get_user_permissions(token)
            permission_names = [perm["permission_name"] for perm in permissions]
            
            return {
                "username": username,
                "token_payload": payload,
                "permissions": permissions,
                "permission_names": permission_names,
                "total_permissions": len(permissions)
            }
            
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            raise
