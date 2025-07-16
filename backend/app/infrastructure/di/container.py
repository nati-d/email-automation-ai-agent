"""
Dependency Injection Container

Container for managing all application dependencies.
"""

from typing import Optional
from functools import lru_cache

# Infrastructure
from ..config.settings import Settings, get_settings
from ..external_services.firebase_service import FirebaseService
from ..external_services.email_service import EmailService
from ..external_services.google_oauth_service import GoogleOAuthService
from ..external_services.gmail_service import GmailService
from ..repositories.firestore_email_repository import FirestoreEmailRepository
from ..repositories.firestore_user_repository import FirestoreUserRepository
from ..repositories.firestore_oauth_repository import FirestoreOAuthRepository

# Domain
from ...domain.repositories.email_repository import EmailRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.oauth_repository import OAuthRepository

# Application
from ...application.use_cases.email_use_cases import (
    CreateEmailUseCase, GetEmailUseCase, UpdateEmailUseCase,
    DeleteEmailUseCase, SendEmailUseCase, SendNewEmailUseCase, ScheduleEmailUseCase,
    ListEmailsUseCase, FetchInitialEmailsUseCase
)
from ...application.use_cases.user_use_cases import (
    CreateUserUseCase, GetUserUseCase, UpdateUserUseCase,
    DeleteUserUseCase, AuthenticateUserUseCase
)
from ...application.use_cases.oauth_use_cases import (
    InitiateOAuthLoginUseCase, ProcessOAuthCallbackUseCase,
    RefreshOAuthTokenUseCase, LogoutOAuthUseCase, GetOAuthUserInfoUseCase
)


class Container:
    """Dependency injection container"""
    
    def __init__(self):
        self._settings: Optional[Settings] = None
        self._firebase_service: Optional[FirebaseService] = None
        self._email_service: Optional[EmailService] = None
        self._google_oauth_service: Optional[GoogleOAuthService] = None
        self._gmail_service: Optional[GmailService] = None
        self._email_repository: Optional[EmailRepository] = None
        self._user_repository: Optional[UserRepository] = None
        self._oauth_repository: Optional[OAuthRepository] = None
        
        # Email use cases
        self._create_email_use_case: Optional[CreateEmailUseCase] = None
        self._get_email_use_case: Optional[GetEmailUseCase] = None
        self._update_email_use_case: Optional[UpdateEmailUseCase] = None
        self._delete_email_use_case: Optional[DeleteEmailUseCase] = None
        self._send_email_use_case: Optional[SendEmailUseCase] = None
        self._send_new_email_use_case: Optional[SendNewEmailUseCase] = None
        self._schedule_email_use_case: Optional[ScheduleEmailUseCase] = None
        self._list_emails_use_case: Optional[ListEmailsUseCase] = None
        self._fetch_initial_emails_use_case: Optional[FetchInitialEmailsUseCase] = None
        
        # User use cases
        self._create_user_use_case: Optional[CreateUserUseCase] = None
        self._get_user_use_case: Optional[GetUserUseCase] = None
        self._update_user_use_case: Optional[UpdateUserUseCase] = None
        self._delete_user_use_case: Optional[DeleteUserUseCase] = None
        self._authenticate_user_use_case: Optional[AuthenticateUserUseCase] = None
        
        # OAuth use cases
        self._initiate_oauth_login_use_case: Optional[InitiateOAuthLoginUseCase] = None
        self._process_oauth_callback_use_case: Optional[ProcessOAuthCallbackUseCase] = None
        self._refresh_oauth_token_use_case: Optional[RefreshOAuthTokenUseCase] = None
        self._logout_oauth_use_case: Optional[LogoutOAuthUseCase] = None
        self._get_oauth_user_info_use_case: Optional[GetOAuthUserInfoUseCase] = None
    
    # Configuration
    def settings(self) -> Settings:
        """Get application settings"""
        if self._settings is None:
            self._settings = get_settings()
        return self._settings
    
    # External Services
    def firebase_service(self) -> FirebaseService:
        """Get Firebase service"""
        if self._firebase_service is None:
            self._firebase_service = FirebaseService(self.settings())
        return self._firebase_service
    
    def email_service(self) -> EmailService:
        """Get email service"""
        if self._email_service is None:
            self._email_service = EmailService(self.settings())
        return self._email_service
    
    def google_oauth_service(self) -> GoogleOAuthService:
        """Get Google OAuth service"""
        if self._google_oauth_service is None:
            self._google_oauth_service = GoogleOAuthService(self.settings())
        return self._google_oauth_service
    
    def gmail_service(self) -> GmailService:
        """Get Gmail service"""
        if self._gmail_service is None:
            self._gmail_service = GmailService()
        return self._gmail_service
    
    # Repositories
    def email_repository(self) -> EmailRepository:
        """Get email repository"""
        if self._email_repository is None:
            firebase = self.firebase_service()
            db = firebase.get_firestore_client()
            self._email_repository = FirestoreEmailRepository(db)
        return self._email_repository
    
    def user_repository(self) -> UserRepository:
        """Get user repository"""
        if self._user_repository is None:
            firebase = self.firebase_service()
            db = firebase.get_firestore_client()
            self._user_repository = FirestoreUserRepository(db)
        return self._user_repository
    
    def oauth_repository(self) -> OAuthRepository:
        """Get OAuth repository"""
        if self._oauth_repository is None:
            firebase = self.firebase_service()
            db = firebase.get_firestore_client()
            self._oauth_repository = FirestoreOAuthRepository(db)
        return self._oauth_repository
    
    # Email Use Cases
    def create_email_use_case(self) -> CreateEmailUseCase:
        """Get create email use case"""
        if self._create_email_use_case is None:
            self._create_email_use_case = CreateEmailUseCase(self.email_repository())
        return self._create_email_use_case
    
    def get_email_use_case(self) -> GetEmailUseCase:
        """Get email use case"""
        if self._get_email_use_case is None:
            self._get_email_use_case = GetEmailUseCase(self.email_repository())
        return self._get_email_use_case
    
    def update_email_use_case(self) -> UpdateEmailUseCase:
        """Get update email use case"""
        if self._update_email_use_case is None:
            self._update_email_use_case = UpdateEmailUseCase(self.email_repository())
        return self._update_email_use_case
    
    def delete_email_use_case(self) -> DeleteEmailUseCase:
        """Get delete email use case"""
        if self._delete_email_use_case is None:
            self._delete_email_use_case = DeleteEmailUseCase(self.email_repository())
        return self._delete_email_use_case
    
    def send_email_use_case(self) -> SendEmailUseCase:
        """Get send email use case"""
        if self._send_email_use_case is None:
            self._send_email_use_case = SendEmailUseCase(self.email_repository())
        return self._send_email_use_case
    
    def send_new_email_use_case(self) -> SendNewEmailUseCase:
        """Get send new email use case"""
        if self._send_new_email_use_case is None:
            print(f"🔍 DEBUG: Creating SendNewEmailUseCase")
            email_repo = self.email_repository()
            email_svc = self.email_service()
            print(f"   📧 Email repository type: {type(email_repo).__name__}")
            print(f"   📧 Email service type: {type(email_svc).__name__}")
            print(f"   📧 Email service configured: {email_svc.is_configured()}")
            
            self._send_new_email_use_case = SendNewEmailUseCase(
                email_repository=email_repo,
                email_service=email_svc
            )
            print(f"   ✅ SendNewEmailUseCase created successfully")
        return self._send_new_email_use_case
    
    def schedule_email_use_case(self) -> ScheduleEmailUseCase:
        """Get schedule email use case"""
        if self._schedule_email_use_case is None:
            self._schedule_email_use_case = ScheduleEmailUseCase(self.email_repository())
        return self._schedule_email_use_case
    
    def list_emails_use_case(self) -> ListEmailsUseCase:
        """Get list emails use case"""
        if self._list_emails_use_case is None:
            self._list_emails_use_case = ListEmailsUseCase(self.email_repository())
        return self._list_emails_use_case
    
    def fetch_initial_emails_use_case(self) -> FetchInitialEmailsUseCase:
        """Get fetch initial emails use case"""
        if self._fetch_initial_emails_use_case is None:
            email_repo = self.email_repository()
            gmail_svc = self.gmail_service()
            
            print(f"🔧 Creating FetchInitialEmailsUseCase with:")
            print(f"   - email_repository: {type(email_repo).__name__}")
            print(f"   - gmail_service: {type(gmail_svc).__name__}")
            
            self._fetch_initial_emails_use_case = FetchInitialEmailsUseCase(
                email_repo,
                gmail_svc
            )
        return self._fetch_initial_emails_use_case
    
    # User Use Cases
    def create_user_use_case(self) -> CreateUserUseCase:
        """Get create user use case"""
        if self._create_user_use_case is None:
            self._create_user_use_case = CreateUserUseCase(self.user_repository())
        return self._create_user_use_case
    
    def get_user_use_case(self) -> GetUserUseCase:
        """Get user use case"""
        if self._get_user_use_case is None:
            self._get_user_use_case = GetUserUseCase(self.user_repository())
        return self._get_user_use_case
    
    def update_user_use_case(self) -> UpdateUserUseCase:
        """Get update user use case"""
        if self._update_user_use_case is None:
            self._update_user_use_case = UpdateUserUseCase(self.user_repository())
        return self._update_user_use_case
    
    def delete_user_use_case(self) -> DeleteUserUseCase:
        """Get delete user use case"""
        if self._delete_user_use_case is None:
            self._delete_user_use_case = DeleteUserUseCase(self.user_repository())
        return self._delete_user_use_case
    
    def authenticate_user_use_case(self) -> AuthenticateUserUseCase:
        """Get authenticate user use case"""
        if self._authenticate_user_use_case is None:
            self._authenticate_user_use_case = AuthenticateUserUseCase(self.user_repository())
        return self._authenticate_user_use_case
    
    # OAuth Use Cases
    def initiate_oauth_login_use_case(self) -> InitiateOAuthLoginUseCase:
        """Get initiate OAuth login use case"""
        if self._initiate_oauth_login_use_case is None:
            self._initiate_oauth_login_use_case = InitiateOAuthLoginUseCase(
                oauth_repository=self.oauth_repository(),
                user_repository=self.user_repository(),
                oauth_service=self.google_oauth_service()
            )
        return self._initiate_oauth_login_use_case
    
    def process_oauth_callback_use_case(self) -> ProcessOAuthCallbackUseCase:
        """Get process OAuth callback use case"""
        if self._process_oauth_callback_use_case is None:
            # Debug logging
            oauth_service = self.google_oauth_service()
            oauth_repository = self.oauth_repository()
            user_repository = self.user_repository()
            fetch_emails_use_case = self.fetch_initial_emails_use_case()
            
            print(f"🔧 Creating ProcessOAuthCallbackUseCase with:")
            print(f"   - oauth_service: {type(oauth_service).__name__}")
            print(f"   - oauth_repository: {type(oauth_repository).__name__}")
            print(f"   - user_repository: {type(user_repository).__name__}")
            print(f"   - fetch_emails_use_case: {type(fetch_emails_use_case).__name__}")
            
            self._process_oauth_callback_use_case = ProcessOAuthCallbackUseCase(
                oauth_repository=oauth_repository,
                user_repository=user_repository,
                oauth_service=oauth_service,
                fetch_emails_use_case=fetch_emails_use_case
            )
        return self._process_oauth_callback_use_case
    
    def refresh_oauth_token_use_case(self) -> RefreshOAuthTokenUseCase:
        """Get refresh OAuth token use case"""
        if self._refresh_oauth_token_use_case is None:
            self._refresh_oauth_token_use_case = RefreshOAuthTokenUseCase(
                oauth_repository=self.oauth_repository(),
                user_repository=self.user_repository(),
                oauth_service=self.google_oauth_service()
            )
        return self._refresh_oauth_token_use_case
    
    def logout_oauth_use_case(self) -> LogoutOAuthUseCase:
        """Get logout OAuth use case"""
        if self._logout_oauth_use_case is None:
            self._logout_oauth_use_case = LogoutOAuthUseCase(
                oauth_repository=self.oauth_repository(),
                user_repository=self.user_repository(),
                oauth_service=self.google_oauth_service()
            )
        return self._logout_oauth_use_case
    
    def get_oauth_user_info_use_case(self) -> GetOAuthUserInfoUseCase:
        """Get OAuth user info use case"""
        if self._get_oauth_user_info_use_case is None:
            self._get_oauth_user_info_use_case = GetOAuthUserInfoUseCase(
                oauth_repository=self.oauth_repository(),
                user_repository=self.user_repository(),
                oauth_service=self.google_oauth_service()
            )
        return self._get_oauth_user_info_use_case
    
    def initialize(self) -> None:
        """Initialize all services"""
        # Initialize Firebase
        firebase = self.firebase_service()
        firebase.initialize()
    
    def cleanup(self) -> None:
        """Cleanup all services"""
        if self._firebase_service:
            self._firebase_service.close()


# Global container instance
_container: Optional[Container] = None


@lru_cache()
def get_container() -> Container:
    """Get the global container instance"""
    global _container
    if _container is None:
        _container = Container()
    return _container 