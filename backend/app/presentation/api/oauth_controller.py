"""
OAuth Controller

Clean architecture implementation of OAuth API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from typing import Optional

# Application layer
from ...application.dto.user_dto import UserDTO
from ...application.use_cases.oauth_use_cases import (
    InitiateOAuthLoginUseCase, ProcessOAuthCallbackUseCase,
    RefreshOAuthTokenUseCase, LogoutOAuthUseCase, GetOAuthUserInfoUseCase,
    AddAnotherAccountUseCase
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
    OAuthUserResponse,
    OAuthSessionInfo,
    AddAnotherAccountRequest,
    AddAnotherAccountResponse
)

# Middleware
from ..middleware.auth_middleware import get_current_user, get_current_user_with_session_id

# Security scheme
security = HTTPBearer()


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


def get_add_another_account_use_case(container: Container = Depends(get_container)) -> AddAnotherAccountUseCase:
    return container.add_another_account_use_case()


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
        print(f"🔧 OAuth Controller - Use case type: {type(use_case).__name__}")
        
        # Handle OAuth errors
        if error:
            error_msg = error_description or error
            print(f"❌ OAuth error from Google: {error} - {error_msg}")
            redirect_url = f"{settings.frontend_url}/login?error={error}&message={error_msg}"
            print(f"🔄 Redirecting to error page: {redirect_url}")
            return RedirectResponse(url=redirect_url)
        
        # Check if this is an add account flow
        is_add_account_flow = state is not None and "_add_account" in state
        
        if is_add_account_flow:
            # Extract session ID from state parameter
            session_id = None
            if state is not None and "_add_account_" in state:
                # Format: {random_state}_add_account_{session_id}
                parts = state.split("_add_account_")
                if len(parts) == 2:
                    session_id = parts[1]
                    print(f"🔄 Extracted session ID from state: {session_id}")
            
            print("🔄 Detected add account flow, redirecting to frontend with code/state")
            redirect_params = [
                f"flow=add_account",
                f"code={code}",
                f"state={state}",
                f"status=success"
            ]
            
            # Add session ID to redirect params if available
            if session_id:
                redirect_params.append(f"session_id={session_id}")
            
            redirect_url = f"{settings.frontend_url}/?{'&'.join(redirect_params)}"
            print(f"✅ Add account OAuth successful! Redirecting to: {redirect_url}")
            return RedirectResponse(url=redirect_url)
        
        # Process OAuth callback for normal login flow
        print("🔄 Processing OAuth callback with use case...")
        if code is None or state is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "MISSING_CODE_OR_STATE", "message": "Missing code or state in OAuth callback."}
            )
        try:
            result = await use_case.execute(code=code, state=state, error=error)
            print(f"✅ Use case executed successfully for user: {result['user'].email}")
        except Exception as use_case_error:
            print(f"❌ Use case execution failed: {str(use_case_error)}")
            print(f"❌ Use case error type: {type(use_case_error).__name__}")
            import traceback
            print(f"❌ Use case traceback: {traceback.format_exc()}")
            raise use_case_error
        
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
        
        # Add email import results if available
        if "email_import" in result:
            email_import = result["email_import"]
            redirect_params.append(f"emails_imported={email_import.get('emails_imported', 0)}")
            redirect_params.append(f"email_import_success={str(email_import.get('success', False)).lower()}")
            if email_import.get('error'):
                redirect_params.append(f"email_import_error={email_import['error'][:100]}")  # Truncate error
        
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
            description="Refresh an expired OAuth access token using the refresh token.",
            dependencies=[Depends(security)])
async def refresh_oauth_token(
    user_and_session: tuple[UserDTO, str] = Depends(get_current_user_with_session_id),
    use_case: RefreshOAuthTokenUseCase = Depends(get_refresh_oauth_token_use_case)
) -> OAuthTokenRefreshResponse:
    """
    ## Refresh OAuth Token
    
    Refresh an expired OAuth access token using the stored refresh token.
    
    ### Usage
    
    Use this endpoint when your access token expires to get a new one without
    requiring the user to re-authenticate.
    
    ### Authentication
    
    - **Authorization**: Bearer token (session ID) required in Authorization header
    - **Example**: `Authorization: Bearer your_session_id_here`
    
    ### Response
    
    Returns a new access token with updated expiration time.
    """
    try:
        current_user, session_id = user_and_session
        
        result = await use_case.execute(session_id)
        
        return OAuthTokenRefreshResponse(
            access_token=result["access_token"],
            expires_in=result["expires_in"],
            message="Token refreshed successfully",
            session_id=session_id
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
           description="Get current authenticated user information from OAuth session.",
           dependencies=[Depends(security)])
async def get_current_user_info(
    user_and_session: tuple[UserDTO, str] = Depends(get_current_user_with_session_id),
    use_case: GetOAuthUserInfoUseCase = Depends(get_oauth_user_info_use_case)
) -> OAuthUserInfoResponse:
    """
    ## Get Current User Info
    
    Get information about the currently authenticated user from their OAuth session.
    
    ### Usage
    
    Use this endpoint to get user details and session information for the
    authenticated user. Requires a valid Bearer token in the Authorization header.
    
    ### Authentication
    
    - **Authorization**: Bearer token (session ID) required in Authorization header
    - **Example**: `Authorization: Bearer your_session_id_here`
    
    ### Response
    
    Returns user information and session details for the authenticated user.
    """
    try:
        current_user, session_id = user_and_session
        
        # Get complete user and session info from use case
        result = await use_case.execute(session_id)
        print(f"✅ Use case executed successfully, result keys: {result.keys()}")
        
        user_data = result["user"]
        session_info = result["session_info"]
        
        # Convert user data to OAuthUserResponse format
        user_response = OAuthUserResponse(
            id=user_data.id,
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            is_active=user_data.is_active,
            last_login=user_data.last_login,
            created_at=user_data.created_at,
            updated_at=user_data.updated_at
        )
        
        # Create OAuthSessionInfo from session_info
        oauth_session_info = OAuthSessionInfo(
            provider=session_info["provider"],
            session_active=session_info["session_active"],
            token_expires_in=session_info["token_expires_in"]
        )
        
        return OAuthUserInfoResponse(
            user=user_response,
            session_info=oauth_session_info
        )
        
    except DomainException as e:
        print(f"❌ Domain exception in get_current_user_info: {str(e)}")
        raise _handle_domain_exception(e)
    except Exception as e:
        print(f"❌ Unexpected exception in get_current_user_info: {str(e)}")
        print(f"❌ Exception type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/auth/logout",
            response_model=OAuthLogoutResponse,
            summary="OAuth Logout",
            description="Logout user and revoke OAuth tokens.",
            dependencies=[Depends(security)])
async def oauth_logout(
    user_and_session: tuple[UserDTO, str] = Depends(get_current_user_with_session_id),
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
    
    ### Authentication
    
    - **Authorization**: Bearer token (session ID) required in Authorization header
    - **Example**: `Authorization: Bearer your_session_id_here`
    
    ### Usage
    
    This endpoint will logout the authenticated user and revoke their OAuth tokens.
    The session ID is automatically extracted from the Bearer token.
    """
    try:
        current_user, session_id = user_and_session
        
        # Execute logout use case with session ID
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



@router.get("/oauth/add-another-account/initiate",
           response_model=OAuthLoginResponse,
           summary="Initiate Add Another Account OAuth",
           description="Get OAuth URL for adding another email account to the current user.",
           dependencies=[Depends(security)])
async def initiate_add_another_account(
    user_and_session: tuple[UserDTO, str] = Depends(get_current_user_with_session_id),
    use_case: InitiateOAuthLoginUseCase = Depends(get_initiate_oauth_login_use_case)
) -> OAuthLoginResponse:
    """
    Initiate OAuth flow for adding another email account.
    
    This endpoint generates an OAuth authorization URL that the user can use
    to authorize another Gmail account to be added to their existing account.
    
    Requires a valid session ID as Bearer token in Authorization header.
    """
    try:
        current_user, session_id = user_and_session
        print(f"🔄 initiate_add_another_account called for user: {current_user.email} with session: {session_id}")
        
        result = await use_case.execute(flow_type="add_account", session_id=session_id)
        
        return OAuthLoginResponse(
            authorization_url=result["authorization_url"],
            state=result["state"],
            message="Redirect to the authorization URL to add another account"
        )
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/oauth/add-another-account",
           response_model=AddAnotherAccountResponse,
           summary="Add Another Email Account",
           description="Add another email account to the current user using OAuth.",
           dependencies=[Depends(security)])
async def add_another_account(
    request: AddAnotherAccountRequest,
    current_user: UserDTO = Depends(get_current_user),
    use_case: AddAnotherAccountUseCase = Depends(get_add_another_account_use_case)
) -> AddAnotherAccountResponse:
    """
    Add another email account to the current user using OAuth.
    
    This endpoint allows a logged-in user to add another email account (e.g., work email)
    to their existing account. The new account's emails will be fetched and stored with:
    - account_owner: current_user.email (the logged-in user)
    - email_holder: new_account.email (the new account being added)
    
    Requires a valid session ID as Bearer token in Authorization header.
    """
    try:
        print(f"🔄 add_another_account endpoint called:")
        print(f"   - current_user.email: {current_user.email}")
        print(f"   - code: {request.code[:20] if request.code else 'None'}...")
        print(f"   - state: {request.state[:20] if request.state else 'None'}...")
        
        result = await use_case.execute(
            code=request.code,
            state=request.state,
            current_user_email=current_user.email
        )
        
        print(f"✅ add_another_account completed: {result.get('success', False)}")
        
        # Convert result to AddAnotherAccountResponse
        return AddAnotherAccountResponse(
            success=result.get('success', False),
            message=result.get('message', ''),
            account_added=result.get('account_added'),
            email_import=result.get('email_import'),
            error=result.get('error')
        )
        
    except DomainException as e:
        raise _handle_domain_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": str(e)}
        ) 