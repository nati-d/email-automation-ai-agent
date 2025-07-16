"""
Auth Test Controller

Test controller to demonstrate authentication middleware usage.
"""

from fastapi import APIRouter, Depends
from typing import Optional

# Application layer
from ...application.dto.user_dto import UserDTO

# Middleware
from ..middleware.auth_middleware import get_current_user, get_optional_current_user


router = APIRouter()


@router.get("/auth-test/protected",
           summary="Protected Endpoint",
           description="Test endpoint that requires authentication.")
async def protected_endpoint(
    current_user: UserDTO = Depends(get_current_user)
) -> dict:
    """
    Protected endpoint that requires authentication.
    
    This endpoint demonstrates the required authentication middleware.
    It will return 401 if no valid session ID is provided.
    """
    return {
        "message": "Access granted!",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role
        },
        "session_info": "Valid OAuth session detected"
    }


@router.get("/auth-test/optional",
           summary="Optional Auth Endpoint",
           description="Test endpoint that works with or without authentication.")
async def optional_auth_endpoint(
    current_user: Optional[UserDTO] = Depends(get_optional_current_user)
) -> dict:
    """
    Optional authentication endpoint.
    
    This endpoint demonstrates the optional authentication middleware.
    It works whether the user is authenticated or not.
    """
    if current_user:
        return {
            "message": "Hello authenticated user!",
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "role": current_user.role
            },
            "authentication_status": "authenticated"
        }
    else:
        return {
            "message": "Hello anonymous user!",
            "user": None,
            "authentication_status": "anonymous"
        }


@router.get("/auth-test/user-info",
           summary="Get User Info",
           description="Get current user information from session.")
async def get_user_info(
    current_user: UserDTO = Depends(get_current_user)
) -> dict:
    """
    Get detailed user information from the current session.
    
    This endpoint shows how to access user data from the middleware.
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
        "oauth_info": {
            "google_id": current_user.google_id,
            "profile_picture": current_user.profile_picture,
            "oauth_provider": current_user.oauth_provider
        }
    }


@router.get("/auth-test/session-status",
           summary="Session Status",
           description="Check if current session is valid.")
async def check_session_status(
    current_user: Optional[UserDTO] = Depends(get_optional_current_user)
) -> dict:
    """
    Check the status of the current session.
    
    This endpoint is useful for frontend applications to verify
    if the user's session is still valid.
    """
    if current_user:
        return {
            "status": "valid",
            "message": "Session is valid and active",
            "user_email": current_user.email,
            "session_active": True
        }
    else:
        return {
            "status": "invalid",
            "message": "No valid session found",
            "user_email": None,
            "session_active": False
        } 