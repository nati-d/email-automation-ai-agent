"""
Authentication Middleware

Middleware for extracting and validating authenticated users from OAuth sessions.
"""

from fastapi import Depends, HTTPException, status, Header, Query
from typing import Optional

# Application layer
from ...application.dto.user_dto import UserDTO
from ...application.use_cases.oauth_use_cases import GetOAuthUserInfoUseCase

# Domain exceptions
from ...domain.exceptions.domain_exceptions import DomainException, EntityNotFoundError

# Infrastructure
from ...infrastructure.di.container import Container, get_container


def get_oauth_user_info_use_case(
    container: Container = Depends(get_container)
) -> GetOAuthUserInfoUseCase:
    """Dependency injection for OAuth user info use case"""
    return container.get_oauth_user_info_use_case()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    session_id_query: Optional[str] = Query(None, alias="session_id"),  # Keep for backward compatibility
    use_case: GetOAuthUserInfoUseCase = Depends(get_oauth_user_info_use_case)
) -> UserDTO:
    print(f"[DEBUG] Incoming Authorization header: {authorization}")
    # Extract session ID from Authorization header (Bearer token) or query parameter
    actual_session_id = None
    
    if authorization:
        # Check if it's a Bearer token
        if authorization.startswith("Bearer "):
            actual_session_id = authorization[7:].strip()  # Remove "Bearer " prefix and trim whitespace
            print(f"🔐 Auth Middleware - Session ID from Bearer token: {actual_session_id[:10]}...")
        else:
            # Treat as plain session ID for backward compatibility
            actual_session_id = authorization.strip()  # Trim whitespace
            print(f"🔐 Auth Middleware - Session ID from Authorization header: {actual_session_id[:10]}...")
    
    if not actual_session_id and session_id_query:
        actual_session_id = session_id_query.strip()  # Trim whitespace
        print(f"🔐 Auth Middleware - Session ID from query parameter: {actual_session_id[:10]}...")
    
    print(f"🔐 Auth Middleware - Final session ID: {actual_session_id[:10] if actual_session_id else 'None'}...")
    
    if not actual_session_id:
        print("❌ Auth Middleware - No session ID provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "MISSING_SESSION_ID",
                "message": "Session ID is required. Provide it as Bearer token in Authorization header or session_id query parameter."
            }
        )
    
    try:
        print(f"🔐 Auth Middleware - Executing use case with session ID: {actual_session_id}")
        # Get user info from session
        result = await use_case.execute(actual_session_id)
        print(f"✅ Auth Middleware - Use case executed successfully")
        print(f"🔐 Auth Middleware - Result keys: {list(result.keys())}")
        
        user_data = result["user"]
        print(f"🔐 Auth Middleware - User data type: {type(user_data)}")
        
        # Check if user_data is already a UserDTO or a dictionary
        if isinstance(user_data, UserDTO):
            user_dto = user_data
            print(f"✅ Auth Middleware - User data is already UserDTO: {user_dto.email}")
        else:
            user_dto = UserDTO(**user_data)
            print(f"✅ Auth Middleware - User DTO created from dict: {user_dto.email}")
        
        print(f"🔐 Auth Middleware - User DTO fields: id={user_dto.id}, email={user_dto.email}, name={user_dto.name}")
        
        return user_dto
        
    except EntityNotFoundError as e:
        print(f"❌ Auth Middleware - EntityNotFoundError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_SESSION",
                "message": "Invalid or expired session. Please login again."
            }
        )
    except DomainException as e:
        print(f"❌ Auth Middleware - DomainException: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "SESSION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        print(f"❌ Auth Middleware - Unexpected exception: {str(e)}")
        print(f"❌ Auth Middleware - Exception type: {type(e).__name__}")
        import traceback
        print(f"❌ Auth Middleware - Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to authenticate user"
            }
        )


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    session_id_query: Optional[str] = Query(None, alias="session_id"),  # Keep for backward compatibility
    use_case: GetOAuthUserInfoUseCase = Depends(get_oauth_user_info_use_case)
) -> Optional[UserDTO]:
    """
    Optional middleware to get the currently authenticated user.
    
    This middleware works like get_current_user but returns None instead of
    raising an error if no valid session is found. Useful for endpoints that
    can work with or without authentication.
    
    Args:
        session_id: Session ID from X-Session-ID header
        session_id_query: Session ID from query parameter
        use_case: OAuth user info use case
        
    Returns:
        Optional[UserDTO]: The authenticated user's data or None if not authenticated
    """
    # Extract session ID from Authorization header (Bearer token) or query parameter
    actual_session_id = None
    
    if authorization:
        # Check if it's a Bearer token
        if authorization.startswith("Bearer "):
            actual_session_id = authorization[7:].strip()  # Remove "Bearer " prefix and trim whitespace
        else:
            # Treat as plain session ID for backward compatibility
            actual_session_id = authorization.strip()  # Trim whitespace
    
    if not actual_session_id and session_id_query:
        actual_session_id = session_id_query.strip()  # Trim whitespace
    
    if not actual_session_id:
        return None
    
    try:
        # Get user info from session
        result = await use_case.execute(actual_session_id)
        user_data = result["user"]
        
        return UserDTO(**user_data)
        
    except (EntityNotFoundError, DomainException):
        # Return None for any session-related errors
        return None
    except Exception:
        # Return None for any other errors
        return None


async def get_current_user_with_session_id(
    authorization: Optional[str] = Header(None),
    session_id_query: Optional[str] = Query(None, alias="session_id"),  # Keep for backward compatibility
    use_case: GetOAuthUserInfoUseCase = Depends(get_oauth_user_info_use_case)
) -> tuple[UserDTO, str]:
    """
    Middleware to get the currently authenticated user and session ID.
    
    This middleware extracts the session ID and returns both the user and session ID.
    Useful for endpoints that need both the user information and session ID.
    
    Args:
        authorization: Authorization header (Bearer token)
        session_id_query: Session ID from query parameter
        use_case: OAuth user info use case
        
    Returns:
        tuple[UserDTO, str]: The authenticated user's data and session ID
        
    Raises:
        HTTPException: 401 if no valid session found, 500 for other errors
    """
    # Extract session ID from Authorization header (Bearer token) or query parameter
    actual_session_id = None
    
    if authorization:
        # Check if it's a Bearer token
        if authorization.startswith("Bearer "):
            actual_session_id = authorization[7:].strip()  # Remove "Bearer " prefix and trim whitespace
        else:
            # Treat as plain session ID for backward compatibility
            actual_session_id = authorization.strip()  # Trim whitespace
    
    if not actual_session_id and session_id_query:
        actual_session_id = session_id_query.strip()  # Trim whitespace
    
    if not actual_session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "MISSING_SESSION_ID",
                "message": "Session ID is required. Provide it as Bearer token in Authorization header or session_id query parameter."
            }
        )
    
    try:
        # Get user info from session
        result = await use_case.execute(actual_session_id)
        user_data = result["user"]
        
        # Check if user_data is already a UserDTO or a dictionary
        if isinstance(user_data, UserDTO):
            user_dto = user_data
        else:
            user_dto = UserDTO(**user_data)
        
        return user_dto, actual_session_id
        
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_SESSION",
                "message": "Invalid or expired session. Please login again."
            }
        )
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "SESSION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to authenticate user"
            }
        ) 