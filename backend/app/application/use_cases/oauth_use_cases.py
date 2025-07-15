"""
OAuth Use Cases

Business use cases for OAuth authentication operations.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from ...domain.entities.oauth_session import OAuthSession
from ...domain.entities.user import User
from ...domain.value_objects.email_address import EmailAddress
from ...domain.repositories.oauth_repository import OAuthRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError

from ...infrastructure.external_services.google_oauth_service import GoogleOAuthService

from ..dto.user_dto import UserDTO


class OAuthUseCaseBase:
    """Base class for OAuth use cases"""
    
    def __init__(
        self, 
        oauth_repository: OAuthRepository,
        user_repository: UserRepository,
        oauth_service: GoogleOAuthService
    ):
        self.oauth_repository = oauth_repository
        self.user_repository = user_repository
        self.oauth_service = oauth_service
    
    def _user_entity_to_dto(self, user: User) -> UserDTO:
        """Convert user entity to DTO"""
        return UserDTO(
            id=user.id,
            email=str(user.email),
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


class InitiateOAuthLoginUseCase(OAuthUseCaseBase):
    """Use case for initiating OAuth login"""
    
    async def execute(self) -> Dict[str, Any]:
        """Initiate OAuth login flow"""
        try:
            # Generate secure state parameter
            state = self.oauth_service.generate_state()
            
            # Get authorization URL
            auth_url = self.oauth_service.get_authorization_url(state)
            
            return {
                "authorization_url": auth_url,
                "state": state
            }
            
        except Exception as e:
            raise DomainValidationError(f"Failed to initiate OAuth login: {str(e)}")


class ProcessOAuthCallbackUseCase(OAuthUseCaseBase):
    """Use case for processing OAuth callback"""
    
    async def execute(
        self, 
        code: str, 
        state: str, 
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process OAuth callback and create/authenticate user"""
        
        if error:
            raise DomainValidationError(f"OAuth error: {error}")
        
        if not code:
            raise DomainValidationError("Authorization code is required")
        
        if not state:
            raise DomainValidationError("State parameter is required")
        
        try:
            # Exchange code for tokens
            token = self.oauth_service.exchange_code_for_tokens(code, state)
            
            # Get user information
            user_info = self.oauth_service.get_user_info(token.access_token)
            
            # Create OAuth session
            oauth_session = OAuthSession(
                user_id=None,  # Will be set after user creation/authentication
                token=token,
                user_info=user_info,
                state=state
            )
            
            # Check if user exists
            existing_user = await self.user_repository.find_by_email(user_info.email)
            
            if existing_user:
                # Existing user - authenticate
                user = await self._authenticate_existing_user(existing_user, oauth_session)
            else:
                # New user - create account
                user = await self._create_new_user(oauth_session)
            
            # Associate session with user
            oauth_session.associate_user(user.id)
            
            # Save OAuth session
            await self.oauth_repository.save_session(oauth_session)
            
            # Update user's last login
            user.update_last_login()
            await self.user_repository.update(user)
            
            return {
                "user": self._user_entity_to_dto(user),
                "session_id": oauth_session.id,
                "access_token": token.access_token,
                "is_new_user": existing_user is None
            }
            
        except Exception as e:
            raise DomainValidationError(f"Failed to process OAuth callback: {str(e)}")
    
    async def _authenticate_existing_user(
        self, 
        user: User, 
        oauth_session: OAuthSession
    ) -> User:
        """Authenticate existing user and update OAuth info"""
        
        # Update user's OAuth information if needed
        if not user.google_id:
            user.set_oauth_info(
                google_id=oauth_session.user_info.provider_id,
                profile_picture=oauth_session.user_info.picture
            )
            await self.user_repository.update(user)
        
        # Deactivate any existing OAuth sessions for this user
        await self.oauth_repository.deactivate_user_sessions(user.id)
        
        return user
    
    async def _create_new_user(self, oauth_session: OAuthSession) -> User:
        """Create new user from OAuth session"""
        
        # Create user from OAuth info
        user = User.create_from_oauth(
            email=oauth_session.user_info.email,
            name=oauth_session.user_info.name,
            google_id=oauth_session.user_info.provider_id,
            profile_picture=oauth_session.user_info.picture
        )
        
        # Save user
        saved_user = await self.user_repository.save(user)
        
        return saved_user


class RefreshOAuthTokenUseCase(OAuthUseCaseBase):
    """Use case for refreshing OAuth tokens"""
    
    async def execute(self, session_id: str) -> Dict[str, Any]:
        """Refresh OAuth token for a session"""
        
        # Find session
        session = await self.oauth_repository.find_session_by_id(session_id)
        if not session:
            raise EntityNotFoundError("OAuth session", session_id)
        
        if not session.is_active:
            raise DomainValidationError("OAuth session is not active")
        
        if not session.token.refresh_token:
            raise DomainValidationError("No refresh token available")
        
        try:
            # Refresh token
            new_token = self.oauth_service.refresh_access_token(session.token.refresh_token)
            
            # Update session with new token
            session.refresh_token(new_token)
            
            # Save updated session
            await self.oauth_repository.update_session(session)
            
            return {
                "access_token": new_token.access_token,
                "expires_in": new_token.expires_in_seconds()
            }
            
        except Exception as e:
            raise DomainValidationError(f"Failed to refresh token: {str(e)}")


class LogoutOAuthUseCase(OAuthUseCaseBase):
    """Use case for OAuth logout"""
    
    async def execute(self, session_id: str) -> Dict[str, Any]:
        """Logout user and revoke OAuth tokens"""
        
        # Find session
        session = await self.oauth_repository.find_session_by_id(session_id)
        if not session:
            raise EntityNotFoundError("OAuth session", session_id)
        
        try:
            # Revoke access token
            token_revoked = self.oauth_service.revoke_token(session.token.access_token)
            
            # Revoke refresh token if available
            if session.token.refresh_token:
                self.oauth_service.revoke_token(session.token.refresh_token)
            
            # Deactivate session
            session.deactivate()
            await self.oauth_repository.update_session(session)
            
            return {
                "success": True,
                "token_revoked": token_revoked
            }
            
        except Exception as e:
            # Even if token revocation fails, deactivate the session locally
            session.deactivate()
            await self.oauth_repository.update_session(session)
            
            return {
                "success": True,
                "token_revoked": False,
                "warning": f"Token revocation failed: {str(e)}"
            }


class GetOAuthUserInfoUseCase(OAuthUseCaseBase):
    """Use case for getting current OAuth user info"""
    
    async def execute(self, session_id: str) -> Dict[str, Any]:
        """Get current user info from OAuth session"""
        
        # Find session
        session = await self.oauth_repository.find_session_by_id(session_id)
        if not session:
            raise EntityNotFoundError("OAuth session", session_id)
        
        if not session.is_valid():
            raise DomainValidationError("OAuth session is not valid")
        
        # Get user
        if session.user_id:
            user = await self.user_repository.find_by_id(session.user_id)
            if user:
                return {
                    "user": self._user_entity_to_dto(user),
                    "session_info": {
                        "provider": session.user_info.provider,
                        "session_active": session.is_active,
                        "token_expires_in": session.token.expires_in_seconds()
                    }
                }
        
        raise EntityNotFoundError("User", session.user_id or "unknown") 