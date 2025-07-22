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
        user_account_repository=None
    ):
        super().__init__(oauth_repository, user_repository, oauth_service)
        self.fetch_emails_use_case = fetch_emails_use_case
        self.user_account_repository = user_account_repository
        
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
                else:
                    print("🔄 No existing user found, creating new user...")
                    # New user - create account
                    user = await self._create_new_user(oauth_session)
                    print(f"✅ New user created: {user.id}")
                    
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
                        print(f"🔧 DEBUG: is_new_user: {is_new_user}")
                        print(f"🔧 DEBUG: fetch_emails_use_case is None: {self.fetch_emails_use_case is None}")
                        
                        email_result = await self.fetch_emails_use_case.execute(
                            oauth_token=token,
                            user_email=user.email.value,
                            limit=50
                        )
                        result["email_import"] = email_result
                        print(f"✅ Email import result: {email_result}")
                        print(f"📊 Emails imported: {email_result.get('emails_imported', 0)}")
                        print(f"📊 Emails summarized: {email_result.get('emails_summarized', 0)}")
                        
                        # Add primary account to user accounts list if emails were successfully imported
                        if self.user_account_repository and email_result.get('success', False):
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
        user_account_repository=None
    ):
        super().__init__(oauth_repository, user_repository, oauth_service)
        self.fetch_emails_use_case = fetch_emails_use_case
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
            print(f"🔄 AddAnotherAccountUseCase.execute called:")
            print(f"   - current_user_email: {current_user_email}")
            print(f"   - code: {code[:20] if code else 'None'}...")
            print(f"   - state: {state[:20] if state else 'None'}...")
            print(f"   - error: {error}")
            
            if error:
                return {
                    "success": False,
                    "error": "oauth_error",
                    "message": f"OAuth error: {error}"
                }
            
            # Exchange code for tokens
            print("🔄 Exchanging OAuth code for tokens...")
            token_data = self.oauth_service.exchange_code_for_tokens(code, state)
            print(f"✅ Token exchange successful")
            
            # Get user info from Google
            print("🔄 Getting user info from Google...")
            user_info = self.oauth_service.get_user_info(token_data.access_token)
            print(f"✅ User info retrieved: {str(user_info.email)}")
            
            # Use the user_info directly since it's already an OAuthUserInfo object
            oauth_user_info = user_info
            
            # Create OAuth session
            oauth_session = OAuthSession(
                user_id=None,  # Will be set after user association
                token=token_data,
                user_info=oauth_user_info,
                state=state
            )
            
            # Save OAuth session
            saved_session = await self.oauth_repository.save_session(oauth_session)
            print(f"✅ OAuth session saved with ID: {saved_session.id}")
            
            # Find existing user by current_user_email
            existing_user = await self.user_repository.find_by_email(EmailAddress.create(current_user_email))
            if not existing_user:
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": f"User with email {current_user_email} not found"
                }
            
            print(f"✅ Found existing user: {existing_user.email.value}")
            
            # Check if the new account already exists for this user
            new_account_email = str(user_info.email)
            account_exists = False
            if self.user_account_repository:
                existing_account = await self.user_account_repository.find_by_user_and_email(
                    existing_user.id, user_info.email
                )
                account_exists = existing_account is not None
                print(f"🔍 Account {new_account_email} exists for user: {account_exists}")
            
            # Associate OAuth session with existing user
            saved_session.associate_user(existing_user.id)
            await self.oauth_repository.update_session(saved_session)
            print(f"✅ OAuth session associated with user: {existing_user.id}")
            
            # Add the new account to user's account list if it doesn't exist
            account_added_to_list = False
            if self.user_account_repository and not account_exists:
                try:
                    from ...domain.entities.user_account import UserAccount
                    new_user_account = UserAccount.create_secondary_account(
                        user_id=existing_user.id,
                        email=user_info.email,
                        account_name=f"Account {new_account_email}",
                        provider="google"
                    )
                    await self.user_account_repository.save(new_user_account)
                    account_added_to_list = True
                    print(f"✅ Added account {new_account_email} to user's account list")
                except Exception as e:
                    print(f"⚠️ Failed to add account to user's account list: {str(e)}")
                    # Don't fail the whole flow for this
            elif account_exists:
                print(f"ℹ️ Account {new_account_email} already exists in user's account list")
                account_added_to_list = True
            
            # Fetch emails from the new account (only if it's a new account)
            email_result = None
            if self.fetch_emails_use_case and not account_exists:
                try:
                    new_account_email = str(user_info.email)  # Convert EmailAddress to string
                    print(f"🔄 Fetching emails from new account: {new_account_email}")
                    print(f"   - account_owner: {current_user_email}")
                    print(f"   - email_holder: {new_account_email}")
                    print(f"   - limit: 50")
                    print(f"   - fetch_emails_use_case type: {type(self.fetch_emails_use_case).__name__}")
                    
                    email_result = await self.fetch_emails_use_case.execute(
                        oauth_token=token_data,
                        user_email=new_account_email,  # Use the new account's email as string
                        limit=10,
                        account_owner=current_user_email  # Set the logged-in user as account owner
                    )
                    print(f"✅ Email fetch result: {email_result}")
                    print(f"📊 Emails imported: {email_result.get('emails_imported', 0)}")
                    print(f"📊 Emails summarized: {email_result.get('emails_summarized', 0)}")
                except Exception as e:
                    print(f"⚠️ Failed to fetch emails from new account: {str(e)}")
                    print(f"⚠️ Exception type: {type(e).__name__}")
                    import traceback
                    print(f"⚠️ Email fetch traceback: {traceback.format_exc()}")
                    email_result = {
                        "success": False,
                        "error": str(e),
                        "message": "Failed to fetch emails but account was added successfully"
                    }
            elif account_exists:
                print(f"ℹ️ Skipping email fetch - account {new_account_email} already exists for user {existing_user.email.value}")
                email_result = {
                    "success": True,
                    "emails_imported": 0,
                    "emails_summarized": 0,
                    "message": f"Account {new_account_email} already exists for user {existing_user.email.value}, no emails fetched"
                }
            else:
                print(f"⚠️ No fetch_emails_use_case available, skipping email import")
                email_result = {
                    "success": False,
                    "error": "No email fetch service available",
                    "message": "Email import service not configured"
                }
            
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
                result["email_import"] = email_result
            
            print(f"✅ AddAnotherAccountUseCase completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ AddAnotherAccountUseCase failed: {str(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": "internal_error",
                "message": f"Failed to add account: {str(e)}"
            } 