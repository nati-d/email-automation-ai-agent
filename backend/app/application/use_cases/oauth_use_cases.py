"""
OAuth Use Cases

Business use cases for OAuth authentication operations.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from ...domain.entities.oauth_session import OAuthSession
from ...domain.entities.user import User
from ...domain.value_objects.email_address import EmailAddress
from ...domain.repositories.oauth_repository import OAuthRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError

from ...infrastructure.external_services.google_oauth_service import GoogleOAuthService
from ...domain.value_objects.oauth_token import OAuthToken
from ...domain.value_objects.oauth_user_info import OAuthUserInfo

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
    
    async def execute(self, flow_type: str = "login", session_id: Optional[str] = None) -> Dict[str, Any]:
        """Initiate OAuth login flow"""
        try:
            # Generate secure state parameter
            state = self.oauth_service.generate_state()
            
            # Add flow type and session ID to state for callback detection
            if flow_type == "add_account":
                if session_id:
                    state = f"{state}_add_account_{session_id}"
                else:
                    state = f"{state}_add_account"
            
            # Get authorization URL
            auth_url = self.oauth_service.get_authorization_url(state)
            
            return {
                "authorization_url": auth_url,
                "state": state,
                "flow_type": flow_type
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
        fetch_emails_use_case=None,
        fetch_sent_emails_use_case=None,
        user_account_repository=None
    ):
        super().__init__(oauth_repository, user_repository, oauth_service)
        self.fetch_emails_use_case = fetch_emails_use_case
        self.fetch_sent_emails_use_case = fetch_sent_emails_use_case
        self.user_account_repository = user_account_repository
        
        # Debug logging to verify dependencies
        print(f"🔧 ProcessOAuthCallbackUseCase initialized:")
        print(f"   - oauth_repository: {type(oauth_repository).__name__}")
        print(f"   - user_repository: {type(user_repository).__name__}")
        print(f"   - oauth_service: {type(oauth_service).__name__}")
        print(f"   - fetch_emails_use_case: {type(fetch_emails_use_case).__name__ if fetch_emails_use_case else 'None'}")
        print(f"   - fetch_sent_emails_use_case: {type(fetch_sent_emails_use_case).__name__ if fetch_sent_emails_use_case else 'None'}")
    
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
        
        # Initialize result dictionary
        result = {
            "success": True,
            "user": None,
            "session_id": None,
            "email_import": None,
            "sent_email_import": None,
            "is_new_user": False
        }
        
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
                print(f"✅ User info retrieved - Email: {str(user_info.email)}, Name: {user_info.name}")
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
                print(f"🔄 Checking if user exists for email: {str(user_info.email)}")
                existing_user = await self.user_repository.find_by_email(user_info.email)
                
                if existing_user:
                    print(f"✅ Found existing user: {existing_user.id}")
                    # Existing user - authenticate
                    user = await self._authenticate_existing_user(existing_user, oauth_session)
                    print("✅ Existing user authenticated successfully")
                    
                    # For existing users, skip email fetching
                    print("ℹ️ Skipping email fetch - existing user")
                    is_new_user = False
                else:
                    print("🔄 No existing user found, creating new user...")
                    # New user - create account
                    user = await self._create_new_user(oauth_session)
                    print(f"✅ New user created: {user.id}")
                    is_new_user = True
                
                # Create primary account entry for new user
                if self.user_account_repository:
                    try:
                        from ...domain.entities.user_account import UserAccount
                        primary_account = UserAccount.create_primary_account(
                            user_id=user.id,
                            email=user.email,
                            provider="google"
                        )
                        await self.user_account_repository.save(primary_account)
                        print(f"✅ Created primary account entry for user: {user.email.value}")
                    except Exception as e:
                        print(f"⚠️ Failed to create primary account entry: {str(e)}")
                        # Don't fail the whole flow for this
                
                # Fetch emails for new users
                try:
                    # Fetch sent emails for new users
                    if self.fetch_sent_emails_use_case:
                        try:
                            print("🔄 Fetching sent emails for new user...")
                            print(f"🔧 DEBUG: fetch_sent_emails_use_case type: {type(self.fetch_sent_emails_use_case).__name__}")
                            
                            sent_email_result = await self.fetch_sent_emails_use_case.execute(
                                oauth_token=token,
                                user_email=user.email.value,
                                limit=10
                            )
                            result["sent_email_import"] = sent_email_result
                            print(f"✅ Sent email import result: {sent_email_result}")
                            print(f"📊 Sent emails imported: {sent_email_result.get('emails_imported', 0)}")
                            print(f"📊 Sent emails summarized: {sent_email_result.get('emails_summarized', 0)}")
                        except Exception as e:
                            print(f"⚠️ Failed to fetch sent emails, but continuing: {str(e)}")
                            print(f"⚠️ Sent email fetch error type: {type(e).__name__}")
                            import traceback
                            print(f"⚠️ Sent email fetch traceback: {traceback.format_exc()}")
                            result["sent_email_import"] = {
                                "success": False,
                                "error": str(e),
                                "message": "Failed to import sent emails but registration succeeded"
                            }
                    else:
                        print("⚠️ Skipping sent email fetch - fetch_sent_emails_use_case is None")
                    
                    # --- NEW: Aggregate all emails and update user profile using LLM ---
                    try:
                        from app.infrastructure.di.container import get_container
                        container = get_container()
                        user_repo = container.user_repository()
                        email_repo = container.email_repository()
                        llm_service = container.llm_service()
                        # Fetch all emails (inbox + sent) for the user
                        all_emails = await email_repo.find_by_sender(user.email.value)
                        all_emails += await email_repo.find_by_recipient(user.email.value)
                        email_samples = []
                        for email in all_emails:
                            email_samples.append({
                                "subject": email.subject,
                                "body": email.body,
                                "summary": email.summary,
                                "sentiment": email.sentiment,
                                "main_concept": email.main_concept,
                                "key_topics": email.key_topics
                            })
                        prompt = (
                            "Analyze the following list of emails (inbox and sent) and generate a JSON user profile that describes "
                            "the user's typical tone, writing style, common structures, and favorite phrases. "
                            "Be concise and helpful. Respond ONLY with valid JSON in this format: "
                            '{"dominant_tone": "string", "tone_distribution": {"tone": count, ...}, "common_structures": ["structure1", ...], "favorite_phrases": ["phrase1", ...], "summary": "A helpful summary of the user\'s email style."}'
                            "\n\nEmails: " + str(email_samples)
                        )
                        try:
                            llm_response = llm_service.generate_content(
                                system_instruction="You are an expert at analyzing email writing style and generating user profiles.",
                                query=prompt,
                                response_type="text/plain"
                            )
                            import json
                            import re
                            llm_response_clean = llm_response.strip()
                            if llm_response_clean.startswith('```'):
                                llm_response_clean = re.sub(r'^```[a-zA-Z]*\n', '', llm_response_clean)
                                llm_response_clean = re.sub(r'```$', '', llm_response_clean)
                            profile_data = json.loads(llm_response_clean)
                            print(f"[DEBUG] LLM profile_data to be saved (onboarding): {profile_data}")
                            user.user_profile = profile_data
                            print(f"[DEBUG] About to update user {user.email} with profile: {user.user_profile}")
                            await user_repo.update(user)
                            print(f"[DEBUG] User profile (LLM, all emails) updated for user: {user.email}")
                        except Exception as e:
                            print(f"⚠️ Failed to generate user profile with LLM (onboarding): {e}")
                            user.user_profile = {"test": "value", "error": str(e)}
                            print(f"[DEBUG] About to update user {user.email} with fallback profile: {user.user_profile}")
                            await user_repo.update(user)
                            print(f"[DEBUG] Fallback user_profile set for user: {user.email}")
                    except Exception as e:
                        print(f"⚠️ [DEBUG] Failed to aggregate and store user profile after onboarding: {e}")
                    # --- END NEW ---
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
                
                # For new users, ensure primary account is added to user accounts list
                # (even if email fetching failed or was skipped)
                if is_new_user and self.user_account_repository:
                    try:
                        from ...domain.entities.user_account import UserAccount
                        # Check if primary account already exists
                        existing_account = await self.user_account_repository.find_by_user_and_email(
                            user.id, user.email
                        )
                        
                        if not existing_account:
                            primary_account = UserAccount.create_primary_account(
                                user_id=user.id,
                                email=user.email,
                                provider="google"
                            )
                            await self.user_account_repository.save(primary_account)
                            print(f"✅ Added primary account {user.email.value} to user accounts list")
                        else:
                            print(f"ℹ️ Primary account {user.email.value} already exists in user accounts list")
                    except Exception as e:
                        print(f"⚠️ Failed to add primary account to user accounts list: {str(e)}")
                        # Don't fail the whole flow for this
                
                # Save OAuth session and add to result
                oauth_session.user_id = user.id
                saved_session = await self.oauth_repository.save_session(oauth_session)
                
                # Populate result with user and session info
                result["user"] = self._user_entity_to_dto(user)
                result["session_id"] = saved_session.id
                result["is_new_user"] = is_new_user
                
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
        
        print(f"🔍 GetOAuthUserInfoUseCase: Looking for session_id: {session_id}")
        
        # Find session
        try:
            session = await self.oauth_repository.find_session_by_id(session_id)
            print(f"📋 Session found: {session is not None}")
            if not session:
                print(f"❌ Session not found for ID: {session_id}")
                raise EntityNotFoundError("OAuth session", session_id)
            
            print(f"✅ Session details - user_id: {session.user_id}, is_active: {session.is_active}")
        except Exception as e:
            print(f"❌ Error finding session: {str(e)}")
            raise e
        
        try:
            if not session.is_valid():
                print(f"❌ Session is not valid")
                raise DomainValidationError("OAuth session is not valid")
            print(f"✅ Session is valid")
        except Exception as e:
            print(f"❌ Error validating session: {str(e)}")
            raise e
        
        # Get user
        if session.user_id:
            try:
                print(f"🔍 Looking for user with ID: {session.user_id}")
                user = await self.user_repository.find_by_id(session.user_id)
                print(f"👤 User found: {user is not None}")
                if user:
                    print(f"👤 User details - email: {user.email}, name: {user.name}")
                    try:
                        user_dto = self._user_entity_to_dto(user)
                        print(f"✅ User DTO created successfully")
                        
                        session_info = {
                            "provider": session.user_info.provider,
                            "session_active": session.is_active,
                            "token_expires_in": session.token.expires_in_seconds()
                        }
                        print(f"✅ Session info created successfully")
                        
                        return {
                            "user": user_dto,
                            "session_info": session_info
                        }
                    except Exception as e:
                        print(f"❌ Error creating user DTO or session info: {str(e)}")
                        import traceback
                        print(f"❌ DTO creation traceback: {traceback.format_exc()}")
                        raise e
            except Exception as e:
                print(f"❌ Error finding user: {str(e)}")
                raise e
        
        print(f"❌ No user_id in session or user not found")
        raise EntityNotFoundError("User", session.user_id or "unknown") 


class AddAnotherAccountUseCase(OAuthUseCaseBase):
    """Use case for adding another email account to an existing user"""
    
    def __init__(
        self,
        oauth_repository: OAuthRepository,
        user_repository: UserRepository,
        oauth_service,
        fetch_emails_use_case=None,
        fetch_sent_emails_use_case=None,
        user_account_repository=None
    ):
        super().__init__(oauth_repository, user_repository, oauth_service)
        self.fetch_emails_use_case = fetch_emails_use_case
        self.fetch_sent_emails_use_case = fetch_sent_emails_use_case
        self.user_account_repository = user_account_repository
    
    async def execute(
        self, 
        code: str, 
        state: str, 
        current_user_email: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add another email account to an existing user"""
        try:
            print(f"🔄 [DEBUG] AddAnotherAccountUseCase.execute called:")
            print(f"   - current_user_email: {current_user_email}")
            print(f"   - code: {code[:20] if code else 'None'}...")
            print(f"   - state: {state[:20] if state else 'None'}...")
            print(f"   - error: {error}")
            print(f"   - fetch_emails_use_case: {self.fetch_emails_use_case}")
            print(f"   - user_account_repository: {self.user_account_repository}")
            
            if error:
                print(f"❌ [DEBUG] OAuth error received: {error}")
                return {
                    "success": False,
                    "error": "oauth_error",
                    "message": f"OAuth error: {error}"
                }
            
            # Exchange code for tokens
            print("🔄 [DEBUG] Exchanging OAuth code for tokens...")
            token_data = self.oauth_service.exchange_code_for_tokens(code, state)
            print(f"✅ [DEBUG] Token exchange successful: {token_data}")
            
            # Get user info from Google
            print("🔄 [DEBUG] Getting user info from Google...")
            user_info = self.oauth_service.get_user_info(token_data.access_token)
            print(f"✅ [DEBUG] User info retrieved: {str(user_info.email)}")
            
            # Use the user_info directly since it's already an OAuthUserInfo object
            oauth_user_info = user_info
            
            # Create OAuth session
            print("🔄 [DEBUG] Creating OAuth session...")
            oauth_session = OAuthSession(
                user_id=None,  # Will be set after user association
                token=token_data,
                user_info=oauth_user_info,
                state=state
            )
            
            # Save OAuth session
            print("🔄 [DEBUG] Saving OAuth session...")
            saved_session = await self.oauth_repository.save_session(oauth_session)
            print(f"✅ [DEBUG] OAuth session saved with ID: {saved_session.id}")
            
            # Find existing user by current_user_email
            print(f"🔄 [DEBUG] Looking up existing user by email: {current_user_email}")
            existing_user = await self.user_repository.find_by_email(EmailAddress.create(current_user_email))
            if not existing_user:
                print(f"❌ [DEBUG] User not found for email: {current_user_email}")
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": f"User with email {current_user_email} not found"
                }
            
            print(f"✅ [DEBUG] Found existing user: {existing_user.email.value}")
            
            # Check if the new account already exists for this user
            new_account_email = str(user_info.email)
            account_exists = False
            if self.user_account_repository:
                print(f"🔄 [DEBUG] Checking if account exists for user: {existing_user.id}, email: {user_info.email}")
                existing_account = await self.user_account_repository.find_by_user_and_email(
                    existing_user.id, user_info.email
                )
                account_exists = existing_account is not None
                print(f"🔍 [DEBUG] Account {new_account_email} exists for user: {account_exists}")
            else:
                print(f"⚠️ [DEBUG] user_account_repository is None!")
            
            # Associate OAuth session with existing user
            print(f"🔄 [DEBUG] Associating OAuth session with user: {existing_user.id}")
            saved_session.associate_user(existing_user.id)
            await self.oauth_repository.update_session(saved_session)
            print(f"✅ [DEBUG] OAuth session associated with user: {existing_user.id}")
            
            # Add the new account to user's account list if it doesn't exist
            account_added_to_list = False
            if self.user_account_repository and not account_exists:
                try:
                    print(f"🔄 [DEBUG] Adding new account to user's account list...")
                    from ...domain.entities.user_account import UserAccount
                    new_user_account = UserAccount.create_secondary_account(
                        user_id=existing_user.id,
                        email=user_info.email,
                        account_name=f"Account {new_account_email}",
                        provider="google"
                    )
                    await self.user_account_repository.save(new_user_account)
                    account_added_to_list = True
                    print(f"✅ [DEBUG] Added account {new_account_email} to user's account list")
                except Exception as e:
                    print(f"⚠️ [DEBUG] Failed to add account to user's account list: {str(e)}")
                    # Don't fail the whole flow for this
            elif account_exists:
                print(f"ℹ️ [DEBUG] Account {new_account_email} already exists in user's account list")
                account_added_to_list = True
            else:
                print(f"⚠️ [DEBUG] user_account_repository is None, cannot add account to list")
            
            # Fetch emails from the new account (only if it's a new account)
            email_result = None
            sent_email_result = None
            print(f"🔄 [DEBUG] fetch_emails_use_case: {self.fetch_emails_use_case}, account_exists: {account_exists}")
            if self.fetch_emails_use_case and not account_exists:
                try:
                    new_account_email = str(user_info.email)  # Convert EmailAddress to string
                    print(f"🔄 [DEBUG] Fetching emails from new account: {new_account_email}")
                    print(f"   - account_owner: {current_user_email}")
                    print(f"   - email_holder: {new_account_email}")
                    print(f"   - limit: 10")
                    print(f"   - fetch_emails_use_case type: {type(self.fetch_emails_use_case).__name__}")
                    email_result = await self.fetch_emails_use_case.execute(
                        oauth_token=token_data,
                        user_email=new_account_email,  # Use the new account's email as string
                        limit=10,
                        account_owner=current_user_email  # Set the logged-in user as account owner
                    )
                    print(f"✅ [DEBUG] Email fetch result: {email_result}")
                    print(f"📊 [DEBUG] Emails imported: {email_result.get('emails_imported', 0)}")
                    print(f"📊 [DEBUG] Emails summarized: {email_result.get('emails_summarized', 0)}")
                    
                    # Fetch sent emails from the new account
                    if self.fetch_sent_emails_use_case:
                        try:
                            print(f"🔄 [DEBUG] Fetching sent emails from new account: {new_account_email}")
                            sent_email_result = await self.fetch_sent_emails_use_case.execute(
                                oauth_token=token_data,
                                user_email=new_account_email,
                                limit=10,
                                account_owner=current_user_email
                            )
                            print(f"✅ [DEBUG] Sent email fetch result: {sent_email_result}")
                            print(f"📊 [DEBUG] Sent emails imported: {sent_email_result.get('emails_imported', 0)}")
                            print(f"📊 [DEBUG] Sent emails summarized: {sent_email_result.get('emails_summarized', 0)}")
                        except Exception as e:
                            print(f"⚠️ [DEBUG] Failed to fetch sent emails from new account: {str(e)}")
                            print(f"⚠️ [DEBUG] Sent email fetch error type: {type(e).__name__}")
                            import traceback
                            print(f"⚠️ [DEBUG] Sent email fetch traceback: {traceback.format_exc()}")
                            sent_email_result = {
                                "success": False,
                                "error": str(e),
                                "message": "Failed to fetch sent emails but account was added successfully"
                            }
                    else:
                        print(f"⚠️ [DEBUG] No fetch_sent_emails_use_case available, skipping sent email import")
                except Exception as e:
                    print(f"⚠️ [DEBUG] Failed to fetch emails from new account: {str(e)}")
                    print(f"⚠️ [DEBUG] Exception type: {type(e).__name__}")
                    import traceback
                    print(f"⚠️ [DEBUG] Email fetch traceback: {traceback.format_exc()}")
                    email_result = {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to fetch emails but account was added successfully"
                    }
            elif account_exists:
                print(f"ℹ️ [DEBUG] Skipping email fetch - account {new_account_email} already exists for user {existing_user.email.value}")
                email_result = {
                    "success": True,
                    "emails_imported": 0,
                    "emails_summarized": 0,
                    "message": f"Account {new_account_email} already exists for user {existing_user.email.value}, no emails fetched"
                }
                sent_email_result = {
                    "success": True,
                    "emails_imported": 0,
                    "emails_summarized": 0,
                    "message": f"Account {new_account_email} already exists for user {existing_user.email.value}, no sent emails fetched"
                }
            else:
                print(f"⚠️ [DEBUG] No fetch_emails_use_case available, skipping email import")
                email_result = {
                    "success": False,
                    "error": "No email fetch service available",
                    "message": "Email import service not configured"
                }
            
            # After fetching emails and sent emails, aggregate all emails for the user and update user_profile
            try:
                from app.infrastructure.di.container import get_container
                container = get_container()
                user_repo = container.user_repository()
                email_repo = container.email_repository()
                llm_service = container.llm_service()
                # Fetch all emails (inbox + sent) for the user
                all_emails = await email_repo.find_by_sender(existing_user.email.value)
                all_emails += await email_repo.find_by_recipient(existing_user.email.value)
                email_samples = []
                for email in all_emails:
                    email_samples.append({
                        "subject": email.subject,
                        "body": email.body,
                        "summary": email.summary,
                        "sentiment": email.sentiment,
                        "main_concept": email.main_concept,
                        "key_topics": email.key_topics
                    })
                prompt = (
                    "Analyze the following list of emails (inbox and sent) and generate a JSON user profile that describes "
                    "the user's typical tone, writing style, common structures, and favorite phrases. "
                    "Be concise and helpful. Respond ONLY with valid JSON in this format: "
                    '{"dominant_tone": "string", "tone_distribution": {"tone": count, ...}, "common_structures": ["structure1", ...], "favorite_phrases": ["phrase1", ...], "summary": "A helpful summary of the user\'s email style."}'
                    "\n\nEmails: " + str(email_samples)
                )
                try:
                    llm_response = llm_service.generate_content(
                        system_instruction="You are an expert at analyzing email writing style and generating user profiles.",
                        query=prompt,
                        response_type="text/plain"
                    )
                    import json
                    import re
                    llm_response_clean = llm_response.strip()
                    if llm_response_clean.startswith('```'):
                        llm_response_clean = re.sub(r'^```[a-zA-Z]*\n', '', llm_response_clean)
                        llm_response_clean = re.sub(r'```$', '', llm_response_clean)
                    profile_data = json.loads(llm_response_clean)
                    print(f"[DEBUG] LLM profile_data to be saved (add account): {profile_data}")
                    existing_user.user_profile = profile_data
                    print(f"[DEBUG] About to update user {existing_user.email} with profile: {existing_user.user_profile}")
                    await user_repo.update(existing_user)
                    print(f"[DEBUG] User profile (LLM, all emails) updated for user: {existing_user.email}")
                except Exception as e:
                    print(f"⚠️ Failed to generate user profile with LLM (add account): {e}")
                    existing_user.user_profile = {"test": "value", "error": str(e)}
                    print(f"[DEBUG] About to update user {existing_user.email} with fallback profile: {existing_user.user_profile}")
                    await user_repo.update(existing_user)
                    print(f"[DEBUG] Fallback user_profile set for user: {existing_user.email}")
            except Exception as e:
                print(f"⚠️ [DEBUG] Failed to aggregate and store user profile after adding account: {e}")
            
            result = {
                "success": True,
                "message": f"Successfully added account {new_account_email} to user {current_user_email}",
                "account_added": {
                    "email": new_account_email,
                    "name": user_info.name,
                    "picture": user_info.picture,
                    "provider": "google",
                    "was_new_account": not account_exists,
                    "added_to_account_list": account_added_to_list
                },
                "existing_user": {
                    "id": existing_user.id,
                    "email": existing_user.email.value,
                    "name": existing_user.name
                },
                "oauth_session_id": saved_session.id
            }
            
            if email_result:
                print(f"🔄 [DEBUG] Attaching email_result to response: {email_result}")
                result["email_import"] = email_result
            
            if sent_email_result:
                print(f"🔄 [DEBUG] Attaching sent_email_result to response: {sent_email_result}")
                result["sent_email_import"] = sent_email_result
            
            print(f"✅ [DEBUG] AddAnotherAccountUseCase completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ [DEBUG] AddAnotherAccountUseCase failed: {str(e)}")
            import traceback
            print(f"❌ [DEBUG] Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": "internal_error",
                "message": f"Failed to add account: {str(e)}"
            } 