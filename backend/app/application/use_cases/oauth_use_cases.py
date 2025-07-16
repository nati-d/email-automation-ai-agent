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
            updated_at=user.updated_at,
            google_id=user.google_id,
            profile_picture=user.profile_picture,
            oauth_provider=user.oauth_provider
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
    
    def __init__(
        self,
        oauth_repository,
        user_repository,
        oauth_service,
        fetch_emails_use_case=None
    ):
        super().__init__(oauth_repository, user_repository, oauth_service)
        self.fetch_emails_use_case = fetch_emails_use_case
        
        # Debug logging to verify dependencies
        print(f"🔧 ProcessOAuthCallbackUseCase initialized:")
        print(f"   - oauth_repository: {type(oauth_repository).__name__}")
        print(f"   - user_repository: {type(user_repository).__name__}")
        print(f"   - oauth_service: {type(oauth_service).__name__}")
        print(f"   - fetch_emails_use_case: {type(fetch_emails_use_case).__name__ if fetch_emails_use_case else 'None'}")
    
    async def execute(
        self, 
        code: str, 
        state: str, 
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process OAuth callback and create/authenticate user"""
        
        print(f"🔄 ProcessOAuthCallbackUseCase.execute called with:")
        print(f"   - code: {code[:10] if code else 'None'}...")
        print(f"   - state: {state[:10] if state else 'None'}...")
        print(f"   - error: {error}")
        
        if error:
            print(f"❌ OAuth error received: {error}")
            raise DomainValidationError(f"OAuth error: {error}")
        
        if not code:
            print("❌ No authorization code provided")
            raise DomainValidationError("Authorization code is required")
        
        if not state:
            print("❌ No state parameter provided")
            raise DomainValidationError("State parameter is required")
        
        try:
            print(f"🔄 Processing OAuth callback - Code: {code[:10]}..., State: {state[:10]}...")
            print(f"🔧 DEBUG: Available instance attributes: {[attr for attr in dir(self) if not attr.startswith('_')]}")
            
            # Exchange code for tokens
            try:
                print("🔄 Exchanging authorization code for tokens...")
                print(f"🔧 DEBUG: self.oauth_service type: {type(self.oauth_service).__name__}")
                print(f"🔧 DEBUG: self.oauth_service has exchange_code_for_tokens: {hasattr(self.oauth_service, 'exchange_code_for_tokens')}")
                
                if not hasattr(self.oauth_service, 'exchange_code_for_tokens'):
                    print(f"❌ CRITICAL: oauth_service is wrong type: {type(self.oauth_service)}")
                    print(f"❌ Available methods: {[method for method in dir(self.oauth_service) if not method.startswith('_')]}")
                    raise DomainValidationError(f"OAuth service is incorrect type: {type(self.oauth_service).__name__}")
                
                token = self.oauth_service.exchange_code_for_tokens(code, state)
                print(f"✅ Token exchange successful - Access token: {token.access_token[:20]}...")
            except Exception as e:
                print(f"❌ Token exchange failed: {str(e)}")
                print(f"❌ Exception type: {type(e).__name__}")
                import traceback
                print(f"❌ Full traceback: {traceback.format_exc()}")
                raise DomainValidationError(f"Token exchange failed: {str(e)}")
            
            # Get user information
            try:
                print("🔄 Getting user information from Google...")
                user_info = self.oauth_service.get_user_info(token.access_token)
                print(f"✅ User info retrieved - Email: {user_info.email}, Name: {user_info.name}")
            except Exception as e:
                print(f"❌ Failed to get user info: {str(e)}")
                raise DomainValidationError(f"Failed to get user info: {str(e)}")
            
            # Create OAuth session
            try:
                print("🔄 Creating OAuth session...")
                oauth_session = OAuthSession(
                    user_id=None,  # Will be set after user creation/authentication
                    token=token,
                    user_info=user_info,
                    state=state
                )
                print("✅ OAuth session created successfully")
            except Exception as e:
                print(f"❌ Failed to create OAuth session: {str(e)}")
                raise DomainValidationError(f"Failed to create OAuth session: {str(e)}")
            
            # Check if user exists
            try:
                print(f"🔄 Checking if user exists for email: {user_info.email}")
                existing_user = await self.user_repository.find_by_email(user_info.email)
                
                if existing_user:
                    print(f"✅ Found existing user: {existing_user.id}")
                    # Existing user - authenticate
                    user = await self._authenticate_existing_user(existing_user, oauth_session)
                    print("✅ Existing user authenticated successfully")
                else:
                    print("🔄 No existing user found, creating new user...")
                    # New user - create account
                    user = await self._create_new_user(oauth_session)
                    print(f"✅ New user created: {user.id}")
            except Exception as e:
                print(f"❌ Failed during user creation/authentication: {str(e)}")
                raise DomainValidationError(f"Failed during user creation/authentication: {str(e)}")
            
            # Associate session with user
            try:
                print("🔄 Associating session with user...")
                oauth_session.associate_user(user.id)
                print("✅ Session associated with user")
            except Exception as e:
                print(f"❌ Failed to associate session with user: {str(e)}")
                raise DomainValidationError(f"Failed to associate session with user: {str(e)}")
            
            # Save OAuth session
            try:
                print("🔄 Saving OAuth session...")
                await self.oauth_repository.save_session(oauth_session)
                print("✅ OAuth session saved successfully")
            except Exception as e:
                print(f"❌ Failed to save OAuth session: {str(e)}")
                raise DomainValidationError(f"Failed to save OAuth session: {str(e)}")
            
            # Update user's last login
            try:
                print("🔄 Updating user's last login...")
                user.update_last_login()
                await self.user_repository.update(user)
                print("✅ User's last login updated")
            except Exception as e:
                print(f"❌ Failed to update user's last login: {str(e)}")
                # Don't fail the whole flow for this
                print("⚠️ Continuing despite last login update failure...")
            
            try:
                print("🔄 Preparing return data...")
                is_new_user = existing_user is None
                
                result = {
                    "user": self._user_entity_to_dto(user),
                    "session_id": oauth_session.id,
                    "access_token": token.access_token,
                    "is_new_user": is_new_user
                }
                
                # Fetch initial emails for new users
                if is_new_user and self.fetch_emails_use_case:
                    try:
                        print("🔄 Fetching initial emails for new user...")
                        print(f"🔧 DEBUG: fetch_emails_use_case type: {type(self.fetch_emails_use_case).__name__}")
                        print(f"🔧 DEBUG: token type: {type(token).__name__}")
                        print(f"🔧 DEBUG: user email: {user.email.value}")
                        
                        email_result = await self.fetch_emails_use_case.execute(
                            oauth_token=token,
                            user_email=user.email.value,
                            limit=50
                        )
                        result["email_import"] = email_result
                        print(f"✅ Email import result: {email_result}")
                        print(f"📊 Emails imported: {email_result.get('emails_imported', 0)}")
                    except Exception as e:
                        print(f"⚠️ Failed to fetch initial emails, but continuing: {str(e)}")
                        print(f"⚠️ Email fetch error type: {type(e).__name__}")
                        import traceback
                        print(f"⚠️ Email fetch traceback: {traceback.format_exc()}")
                        result["email_import"] = {
                            "success": False,
                            "error": str(e),
                            "message": "Failed to import emails but registration succeeded"
                        }
                else:
                    if not is_new_user:
                        print("ℹ️ Skipping email fetch - existing user")
                    if not self.fetch_emails_use_case:
                        print("⚠️ Skipping email fetch - fetch_emails_use_case is None")
                
                print("✅ OAuth callback processed successfully!")
                return result
            except Exception as e:
                print(f"❌ Failed to prepare return data: {str(e)}")
                raise DomainValidationError(f"Failed to prepare return data: {str(e)}")
            
        except Exception as e:
            print(f"❌ OAuth callback processing failed: {str(e)}")
            print(f"❌ Exception type: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
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