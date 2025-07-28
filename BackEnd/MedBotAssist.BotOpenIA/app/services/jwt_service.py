from typing import Optional, Dict, Any, List
import jwt
from fastapi import HTTPException, status
from app.core.config import settings
from app.services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)

class JWTService:
    """Servicio para manejar JWT y obtener permisos de usuario."""
    
    def __init__(self):
        self.db_service = DatabaseService()
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodifica un JWT token y valida su autenticidad.
        
        Args:
            token: Token JWT (sin el prefijo 'Bearer ')
            
        Returns:
            Payload decodificado del token
            
        Raises:
            HTTPException: Si el token es inválido o ha expirado
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
        Extrae el username del claim 'name' del JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Username del token
        """
        payload = self.decode_token(token)
        username = payload.get("name")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username not found in token"
            )
        
        return username
    
    def get_user_permissions(self, token: str) -> List[str]:
        """
        Obtiene los permisos del usuario desde el claim 'permissions' del JWT, 
        o desde la base de datos si no están en el token.
        
        Args:
            token: Token JWT
            
        Returns:
            Lista de nombres de permisos del usuario
        """
        try:
            payload = self.decode_token(token)
            
            # Primero verificar si los permisos están en el claim del token
            permissions_claim = payload.get("permissions", [])
            if permissions_claim and isinstance(permissions_claim, list):
                logger.info(f"Using permissions from JWT claim: {permissions_claim}")
                return permissions_claim
            
            # Si no están en el token, consultar la base de datos
            username = payload.get("name")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Username not found in token"
                )
            
            # Obtener permisos desde la base de datos
            db_permissions = self.db_service.get_user_permissions(username)
            permission_names = [perm["permission_name"] for perm in db_permissions]
            
            logger.info(f"Retrieved {len(permission_names)} permissions from database for user '{username}'")
            return permission_names
            
        except HTTPException:
            # Re-lanzar HTTPExceptions (errores de JWT)
            raise
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user permissions"
            )
    
    def get_user_permissions_detailed(self, token: str) -> List[Dict[str, Any]]:
        """
        Obtiene los permisos detallados del usuario desde la base de datos usando el JWT.
        Esta función siempre consulta la base de datos para obtener información completa.
        
        Args:
            token: Token JWT
            
        Returns:
            Lista de permisos detallados del usuario
        """
        try:
            # Extraer username del token
            username = self.extract_username(token)
            
            # Obtener permisos desde la base de datos
            permissions = self.db_service.get_user_permissions(username)
            
            logger.info(f"Retrieved {len(permissions)} detailed permissions for user '{username}'")
            return permissions
            
        except HTTPException:
            # Re-lanzar HTTPExceptions (errores de JWT)
            raise
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user permissions"
            )
    
    def get_user_permission_names(self, token: str) -> List[str]:
        """
        Obtiene solo los nombres de los permisos del usuario (para fácil verificación).
        
        Args:
            token: Token JWT
            
        Returns:
            Lista de nombres de permisos
        """
        permissions = self.get_user_permissions(token)
        return [perm["permission_name"] for perm in permissions]
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Obtiene información completa del token y permisos del usuario.
        
        Args:
            token: Token JWT
            
        Returns:
            Diccionario con información del token y permisos
        """
        try:
            # Decodificar token
            payload = self.decode_token(token)
            username = payload.get("name")
            
            # Obtener permisos
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
