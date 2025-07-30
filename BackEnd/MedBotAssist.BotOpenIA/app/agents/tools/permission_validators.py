"""
Permission validation utilities for medical agent tools.

This module contains all permission checking functions used by the medical agent tools.
Each tool must validate permissions before executing any operations.
"""

from typing import Tuple
from app.services.permission_context import permission_context
import logging

logger = logging.getLogger(__name__)


def check_use_agent_permission() -> Tuple[bool, str]:
    """
    Check if the current user has UseAgent permission - required for ALL agent interactions.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    if not permission_context.has_permission("UseAgent"):
        username = permission_context.get_username() or "Unknown"
        permissions = permission_context.get_permissions()
        
        error_msg = f"""**Access Denied to Medical Agent**

User '{username}' does not have permission to use the medical agent.

**Current Permissions:** {', '.join(permissions) if permissions else 'None'}
**Required Permission:** UseAgent (required for any interaction with the agent)

Please contact your system administrator to obtain the 'Use Agent' permission."""
        return False, error_msg
    
    return True, ""


def check_view_patients_permission() -> Tuple[bool, str]:
    """
    Check if the current user has ViewPatients permission.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    if not permission_context.has_permission("ViewPatients"):
        username = permission_context.get_username() or "Unknown"
        permissions = permission_context.get_permissions()

        error_msg = f"""**Access Denied**

User '{username}' does not have permission to access patient information.

**Current Permissions:** {', '.join(permissions) if permissions else 'None'}
**Required Permission:** View Patients

Please contact your system administrator to obtain the necessary permissions."""

        return False, error_msg
    
    return True, ""


def check_create_patients_permission() -> Tuple[bool, str]:
    """
    Check if the current user has ManagePatients permission.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    if not permission_context.has_permission("ManagePatients"):
        username = permission_context.get_username() or "Unknown"
        permissions = permission_context.get_permissions()

        error_msg = f"""**Access Denied**

User '{username}' does not have permission to create/modify patients.

**Current Permissions:** {', '.join(permissions) if permissions else 'None'}
**Required Permission:** Manage Patients

Please contact your system administrator to obtain the necessary permissions."""

        return False, error_msg
    
    return True, ""


def validate_agent_permissions() -> Tuple[bool, str]:
    """
    Validates the basic UseAgent permission that all tools require.
    This is a convenience function that can be used as the first check in any tool.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    return check_use_agent_permission()


def validate_patient_view_permissions() -> Tuple[bool, str]:
    """
    Validates both UseAgent and ViewPatients permissions.
    This is a convenience function for patient query tools.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    # 1. First check UseAgent
    has_use_agent, error_msg = check_use_agent_permission()
    if not has_use_agent:
        return False, error_msg

    # 2. Then check ViewPatients
    has_view_patients, error_msg = check_view_patients_permission()
    if not has_view_patients:
        return False, error_msg
    
    return True, ""


def validate_patient_management_permissions() -> Tuple[bool, str]:
    """
    Validates both UseAgent and ManagePatients permissions.
    This is a convenience function for patient management tools.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    # 1. First check UseAgent
    has_use_agent, error_msg = check_use_agent_permission()
    if not has_use_agent:
        return False, error_msg

    # 2. Then check ManagePatients
    has_manage_patients, error_msg = check_create_patients_permission()
    if not has_manage_patients:
        return False, error_msg
    
    return True, ""
