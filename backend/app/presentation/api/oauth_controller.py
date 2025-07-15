"""
OAuth Controller

Clean architecture implementation of OAuth API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from typing import Optional

# Application layer
from ...application.use_cases.oauth_use_cases import (
    InitiateOAuthLoginUseCase,
    ProcessOAuthCallbackUseCase,
    RefreshOAuthTokenUseCase,
    LogoutOAuthUseCase,
    GetOAuthUserInfoUseCase
)

# Domain exceptions
from ...domain.exceptions.domain_exceptions import DomainException, EntityNotFoundError

# Infrastructure
from ...infrastructure.di.container import Container, get_container
from ...infrastructure.config.settings import Settings, get_settings

# Presentation models
from ..models.oauth_models import (
    OAuthLoginResponse,
    OAuthCallbackRequest,
    OAuthCallbackResponse,
    OAuthTokenRefreshResponse,
    OAuthUserInfoResponse,
    OAuthLogoutResponse,
    OAuthErrorResponse,
    OAuthUserResponse
)


router = APIRouter()


# Dependency injection
def get_initiate_oauth_login_use_case(
    container: Container = Depends(get_container)
) -> InitiateOAuthLoginUseCase:
    return container.initiate_oauth_login_use_case()


def get_process_oauth_callback_use_case(
    container: Container = Depends(get_container)
) -> ProcessOAuthCallbackUseCase:
    return container.process_oauth_callback_use_case()


def get_refresh_oauth_token_use_case(
    container: Container = Depends(get_container)
) -> RefreshOAuthTokenUseCase:
    return container.refresh_oauth_token_use_case()


def get_logout_oauth_use_case(
    container: Container = Depends(get_container)
) -> LogoutOAuthUseCase:
    return container.logout_oauth_use_case()


def get_oauth_user_info_use_case(
    container: Container = Depends(get_container)
) -> GetOAuthUserInfoUseCase:
    return container.get_oauth_user_info_use_case()


def _handle_domain_exception(e: DomainException) -> HTTPException:
    """Convert domain exception to HTTP exception"""
    if isinstance(e, EntityNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": str(e)}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "DOMAIN_ERROR", "message": str(e)}
        )


@router.get("/auth/google/login",
           response_model=OAuthLoginResponse,
           summary="Initiate Google OAuth Login",
           description="Start the Google OAuth authentication flow by getting the authorization URL.")
async def google_oauth_login(
    use_case: InitiateOAuthLoginUseCase = Depends(get_initiate_oauth_login_use_case)
) -> OAuthLoginResponse:
    """
    ## Initiate Google OAuth Login
    
    Starts the Google OAuth authentication flow by generating a secure authorization URL.
    
    ### Flow
    
    1. Generate secure state parameter
    2. Create Google OAuth authorization URL
    3. Return URL for frontend to redirect user
    
    ### Usage
    
    1. Call this endpoint to get the authorization URL
    2. Redirect user to the authorization URL
    3. User will complete OAuth flow on Google
    4. Google will redirect back to your callback URL
    
    ### Security
    
    - Uses secure state parameter to prevent CSRF attacks
    - PKCE (Proof Key for Code Exchange) for additional security
    """
    try:
        result = await use_case.execute()
        
        return OAuthLoginResponse(
            authorization_url=result["authorization_url"],
            state=result["state"],
            message="Redirect to the authorization URL to continue"
        )
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/auth/google/callback",
           summary="Google OAuth Callback",
           description="Handle the callback from Google OAuth after user authorization.")
async def google_oauth_callback(
    code: Optional[str] = Query(None, description="Authorization code from Google"),
    state: Optional[str] = Query(None, description="State parameter for security"),
    error: Optional[str] = Query(None, description="Error code if authorization failed"),
    error_description: Optional[str] = Query(None, description="Error description"),
    settings: Settings = Depends(get_settings),
    use_case: ProcessOAuthCallbackUseCase = Depends(get_process_oauth_callback_use_case)
):
    """
    ## Google OAuth Callback
    
    Handles the callback from Google OAuth service after user authorization.
    This endpoint processes the authorization code and creates/authenticates the user.
    
    ### Process
    
    1. Validate callback parameters
    2. Exchange authorization code for tokens
    3. Get user information from Google
    4. Create new user or authenticate existing user
    5. Store OAuth session
    6. Redirect to frontend with success/error status
    
    ### Error Handling
    
    - If user denies access, redirects with error
    - If OAuth flow fails, redirects with error message
    - All errors are handled gracefully with frontend redirects
    """
    try:
        print(f"🔄 OAuth callback received - Code: {code[:10] if code else 'None'}..., State: {state[:10] if state else 'None'}..., Error: {error}")
        
        # Handle OAuth errors
        if error:
            error_msg = error_description or error
            print(f"❌ OAuth error from Google: {error} - {error_msg}")
            redirect_url = f"{settings.frontend_url}/login?error={error}&message={error_msg}"
            print(f"🔄 Redirecting to error page: {redirect_url}")
            return RedirectResponse(url=redirect_url)
        
        # Process OAuth callback
        print("🔄 Processing OAuth callback with use case...")
        result = await use_case.execute(code=code, state=state, error=error)
        print(f"✅ Use case executed successfully for user: {result['user'].email}")
        
        user = result["user"]
        
        # Build success redirect URL with user info
        redirect_params = [
            f"status=success",
            f"email={user.email}",
            f"name={user.name}",
            f"user_id={user.id}",
            f"session_id={result['session_id']}",
            f"is_new_user={str(result['is_new_user']).lower()}"
        ]
        
        redirect_url = f"{settings.frontend_url}/auth-success?{'&'.join(redirect_params)}"
        print(f"✅ OAuth authentication successful! Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
        
    except DomainException as e:
        # Redirect to frontend with error
        print(f"❌ Domain exception in OAuth callback: {str(e)}")
        redirect_url = f"{settings.frontend_url}/login?error=oauth_error&message={str(e)}"
        print(f"🔄 Redirecting to error page: {redirect_url}")
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        # Redirect to frontend with general error
        print(f"❌ Unexpected exception in OAuth callback: {str(e)}")
        import traceback
        print(f"❌ Callback traceback: {traceback.format_exc()}")
        redirect_url = f"{settings.frontend_url}/login?error=server_error&message=Authentication failed"
        print(f"🔄 Redirecting to error page: {redirect_url}")
        return RedirectResponse(url=redirect_url)


@router.post("/auth/refresh",
            response_model=OAuthTokenRefreshResponse,
            summary="Refresh OAuth Token",
            description="Refresh an expired OAuth access token using the refresh token.")
async def refresh_oauth_token(
    session_id: str,
    use_case: RefreshOAuthTokenUseCase = Depends(get_refresh_oauth_token_use_case)
) -> OAuthTokenRefreshResponse:
    """
    ## Refresh OAuth Token
    
    Refresh an expired OAuth access token using the stored refresh token.
    
    ### Usage
    
    Use this endpoint when your access token expires to get a new one without
    requiring the user to re-authenticate.
    
    ### Parameters
    
    - **session_id**: The OAuth session ID returned during login
    """
    try:
        result = await use_case.execute(session_id)
        
        return OAuthTokenRefreshResponse(
            access_token=result["access_token"],
            expires_in=result["expires_in"],
            message="Token refreshed successfully"
        )
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get("/auth/me",
           response_model=OAuthUserInfoResponse,
           summary="Get Current User Info",
           description="Get current authenticated user information from OAuth session.")
async def get_current_user_info(
    session_id: str,
    use_case: GetOAuthUserInfoUseCase = Depends(get_oauth_user_info_use_case)
) -> OAuthUserInfoResponse:
    """
    ## Get Current User Info
    
    Get information about the currently authenticated user from their OAuth session.
    
    ### Usage
    
    Use this endpoint to get user details and session information for the
    authenticated user.
    
    ### Parameters
    
    - **session_id**: The OAuth session ID returned during login
    """
    try:
        result = await use_case.execute(session_id)
        
        user_data = result["user"]
        session_info = result["session_info"]
        
        return OAuthUserInfoResponse(
            user=OAuthUserResponse(**user_data),
            session_info=session_info
        )
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/auth/logout",
            response_model=OAuthLogoutResponse,
            summary="OAuth Logout",
            description="Logout user and revoke OAuth tokens.")
async def oauth_logout(
    session_id: str,
    use_case: LogoutOAuthUseCase = Depends(get_logout_oauth_use_case)
) -> OAuthLogoutResponse:
    """
    ## OAuth Logout
    
    Logout the user and revoke their OAuth tokens for security.
    
    ### Process
    
    1. Revoke access token with Google
    2. Revoke refresh token with Google  
    3. Deactivate local OAuth session
    4. Return logout status
    
    ### Parameters
    
    - **session_id**: The OAuth session ID to logout
    """
    try:
        result = await use_case.execute(session_id)
        
        return OAuthLogoutResponse(
            success=result["success"],
            token_revoked=result["token_revoked"],
            message="Successfully logged out",
            warning=result.get("warning")
        )
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        ) 