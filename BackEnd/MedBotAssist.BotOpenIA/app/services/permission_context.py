"""
Permission context service for sharing user permissions across the agent and tools.
"""

from typing import List, Optional
import threading
from dataclasses import dataclass

@dataclass
class UserContext:
    """User context with permissions and metadata."""
    username: str
    permissions: List[str]
    jwt_token: Optional[str] = None
    has_view_patients: bool = False
    
    def __post_init__(self):
        """Initialize computed fields."""
        self.has_view_patients = "ViewPatients" in self.permissions

class PermissionContextService:
    """
    Thread-local service to store and access user permissions during tool execution.
    
    This allows tools to check user permissions without having to pass them 
    through the entire execution chain.
    """
    
    def __init__(self):
        self._local = threading.local()
    
    def set_user_context(self, username: str, permissions: List[str], jwt_token: Optional[str] = None) -> None:
        """Set the current user context for this thread."""
        self._local.context = UserContext(
            username=username,
            permissions=permissions,
            jwt_token=jwt_token
        )
    
    def get_user_context(self) -> Optional[UserContext]:
        """Get the current user context for this thread."""
        return getattr(self._local, 'context', None)
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if the current user has a specific permission."""
        context = self.get_user_context()
        if not context:
            return False
        return permission_name in context.permissions
    
    def get_username(self) -> Optional[str]:
        """Get the current username."""
        context = self.get_user_context()
        return context.username if context else None
    
    def get_permissions(self) -> List[str]:
        """Get the current user permissions."""
        context = self.get_user_context()
        return context.permissions if context else []
    
    def get_jwt_token(self) -> Optional[str]:
        """Get the current JWT token."""
        context = self.get_user_context()
        return context.jwt_token if context else None
    
    def clear_context(self) -> None:
        """Clear the current user context."""
        if hasattr(self._local, 'context'):
            del self._local.context

# Global instance
permission_context = PermissionContextService()
