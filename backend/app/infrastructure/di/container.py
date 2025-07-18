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
from ..external_services.llm_service import LLMService
from ..repositories.firestore_email_repository import FirestoreEmailRepository
from ..repositories.firestore_user_repository import FirestoreUserRepository
from ..repositories.firestore_oauth_repository import FirestoreOAuthRepository
from ..repositories.firestore_category_repository import FirestoreCategoryRepository
from ..repositories.firestore_user_account_repository import FirestoreUserAccountRepository

# Domain
from ...domain.repositories.email_repository import EmailRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.oauth_repository import OAuthRepository
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.repositories.user_account_repository import UserAccountRepository

# Application
from ...application.use_cases.email_use_cases import (
    CreateEmailUseCase, GetEmailUseCase, UpdateEmailUseCase,
    DeleteEmailUseCase, SendEmailUseCase, SendNewEmailUseCase, ScheduleEmailUseCase,
    ListEmailsUseCase, FetchInitialEmailsUseCase, SummarizeEmailUseCase, SummarizeMultipleEmailsUseCase
)
from ...application.use_cases.user_use_cases import (
    CreateUserUseCase, GetUserUseCase, UpdateUserUseCase,
    DeleteUserUseCase, AuthenticateUserUseCase
)
from ...application.use_cases.oauth_use_cases import (
    InitiateOAuthLoginUseCase, ProcessOAuthCallbackUseCase,
    RefreshOAuthTokenUseCase, LogoutOAuthUseCase, GetOAuthUserInfoUseCase,
    AddAnotherAccountUseCase
)
from ...application.use_cases.llm_use_cases import (
    GenerateEmailContentUseCase, AnalyzeEmailSentimentUseCase,
    SuggestEmailSubjectUseCase, GenerateEmailResponseUseCase,
    SmartEmailComposerUseCase, GeminiChatUseCase,
    GeminiVisionUseCase, GeminiToolsUseCase, GeminiHealthCheckUseCase
)
from ...application.use_cases.category_use_cases import (
    CreateCategoryUseCase, GetCategoryUseCase, UpdateCategoryUseCase,
    DeleteCategoryUseCase, ListCategoriesUseCase, RecategorizeEmailsUseCase
)
from ...application.use_cases.user_account_use_cases import (
    CreateUserAccountUseCase, GetUserAccountsUseCase, GetActiveUserAccountsUseCase,
    UpdateUserAccountUseCase, DeleteUserAccountUseCase, CheckAccountExistsUseCase,
    AddAccountIfNotExistsUseCase
)


class Container:
    """Dependency injection container"""
    
    def __init__(self):
        self._settings: Optional[Settings] = None
        self._firebase_service: Optional[FirebaseService] = None
        self._email_service: Optional[EmailService] = None
        self._google_oauth_service: Optional[GoogleOAuthService] = None
        self._gmail_service: Optional[GmailService] = None
        self._llm_service: Optional[LLMService] = None
        self._email_repository: Optional[EmailRepository] = None
        self._user_repository: Optional[UserRepository] = None
        self._oauth_repository: Optional[OAuthRepository] = None
        self._category_repository: Optional[CategoryRepository] = None
        self._user_account_repository: Optional[UserAccountRepository] = None
        
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
        self._summarize_email_use_case: Optional[SummarizeEmailUseCase] = None
        self._summarize_multiple_emails_use_case: Optional[SummarizeMultipleEmailsUseCase] = None
        
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
        self._add_another_account_use_case: Optional[AddAnotherAccountUseCase] = None
        
        # LLM use cases
        self._generate_email_content_use_case: Optional[GenerateEmailContentUseCase] = None
        self._analyze_email_sentiment_use_case: Optional[AnalyzeEmailSentimentUseCase] = None
        self._suggest_email_subject_use_case: Optional[SuggestEmailSubjectUseCase] = None
        self._generate_email_response_use_case: Optional[GenerateEmailResponseUseCase] = None
        self._smart_email_composer_use_case: Optional[SmartEmailComposerUseCase] = None
        self._gemini_chat_use_case: Optional[GeminiChatUseCase] = None
        self._gemini_vision_use_case: Optional[GeminiVisionUseCase] = None
        self._gemini_tools_use_case: Optional[GeminiToolsUseCase] = None
        self._gemini_health_check_use_case: Optional[GeminiHealthCheckUseCase] = None
        
        # Category use cases
        self._create_category_use_case: Optional[CreateCategoryUseCase] = None
        self._get_category_use_case: Optional[GetCategoryUseCase] = None
        self._update_category_use_case: Optional[UpdateCategoryUseCase] = None
        self._delete_category_use_case: Optional[DeleteCategoryUseCase] = None
        self._list_categories_use_case: Optional[ListCategoriesUseCase] = None
        self._recategorize_emails_use_case: Optional[RecategorizeEmailsUseCase] = None
        
        # User account use cases
        self._create_user_account_use_case: Optional[CreateUserAccountUseCase] = None
        self._get_user_accounts_use_case: Optional[GetUserAccountsUseCase] = None
        self._get_active_user_accounts_use_case: Optional[GetActiveUserAccountsUseCase] = None
        self._update_user_account_use_case: Optional[UpdateUserAccountUseCase] = None
        self._delete_user_account_use_case: Optional[DeleteUserAccountUseCase] = None
        self._check_account_exists_use_case: Optional[CheckAccountExistsUseCase] = None
        self._add_account_if_not_exists_use_case: Optional[AddAccountIfNotExistsUseCase] = None
    
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
    
    def llm_service(self) -> LLMService:
        """Get LLM service"""
        if self._llm_service is None:
            print(f"🔧 DEBUG: [Container] Creating new LLMService instance")
            try:
                settings = self.settings()
                print(f"🔧 DEBUG: [Container] Settings loaded, GEMINI_API_KEY present: {bool(getattr(settings, 'gemini_api_key', None))}")
                self._llm_service = LLMService(settings)
                print(f"🔧 DEBUG: [Container] LLMService created successfully")
            except Exception as e:
                print(f"🔧 DEBUG: [Container] Failed to create LLMService: {e}")
                print(f"🔧 DEBUG: [Container] Error type: {type(e).__name__}")
                import traceback
                print(f"🔧 DEBUG: [Container] Full traceback: {traceback.format_exc()}")
                self._llm_service = None
        else:
            print(f"🔧 DEBUG: [Container] Returning existing LLMService instance")
        return self._llm_service
    
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
    
    def category_repository(self) -> CategoryRepository:
        """Get category repository"""
        print(f"🔧 DEBUG: [Container] category_repository called")
        if self._category_repository is None:
            print(f"🔧 DEBUG: [Container] Creating new FirestoreCategoryRepository")
            firebase = self.firebase_service()
            db = firebase.get_firestore_client()
            print(f"🔧 DEBUG: [Container] Firestore client type: {type(db).__name__}")
            self._category_repository = FirestoreCategoryRepository(db)
            print(f"🔧 DEBUG: [Container] FirestoreCategoryRepository created successfully")
        else:
            print(f"🔧 DEBUG: [Container] Returning existing category repository")
        return self._category_repository
    
    def user_account_repository(self) -> UserAccountRepository:
        """Get user account repository"""
        if self._user_account_repository is None:
            firebase = self.firebase_service()
            db = firebase.get_firestore_client()
            self._user_account_repository = FirestoreUserAccountRepository(db)
        return self._user_account_repository
    
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
            print(f"🔧 DEBUG: [Container] Creating FetchInitialEmailsUseCase")
            email_repo = self.email_repository()
            gmail_svc = self.gmail_service()
            llm_svc = self.llm_service()
            
            print(f"🔧 DEBUG: [Container] Creating FetchInitialEmailsUseCase with:")
            print(f"   - email_repository: {type(email_repo).__name__}")
            print(f"   - gmail_service: {type(gmail_svc).__name__}")
            print(f"   - llm_service: {type(llm_svc).__name__}")
            print(f"   - llm_service is None: {llm_svc is None}")
            
            self._fetch_initial_emails_use_case = FetchInitialEmailsUseCase(
                email_repo,
                gmail_svc,
                llm_svc,
                self.category_repository()
            )
            print(f"🔧 DEBUG: [Container] FetchInitialEmailsUseCase created successfully")
        else:
            print(f"🔧 DEBUG: [Container] Returning existing FetchInitialEmailsUseCase")
        return self._fetch_initial_emails_use_case
    
    def summarize_email_use_case(self) -> SummarizeEmailUseCase:
        """Get summarize email use case"""
        if self._summarize_email_use_case is None:
            email_repo = self.email_repository()
            llm_svc = self.llm_service()
            
            self._summarize_email_use_case = SummarizeEmailUseCase(
                email_repo,
                llm_svc
            )
        return self._summarize_email_use_case
    
    def summarize_multiple_emails_use_case(self) -> SummarizeMultipleEmailsUseCase:
        """Get summarize multiple emails use case"""
        if self._summarize_multiple_emails_use_case is None:
            email_repo = self.email_repository()
            llm_svc = self.llm_service()
            
            self._summarize_multiple_emails_use_case = SummarizeMultipleEmailsUseCase(
                email_repo,
                llm_svc
            )
        return self._summarize_multiple_emails_use_case
    
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
                fetch_emails_use_case=fetch_emails_use_case,
                user_account_repository=self.user_account_repository()
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
    
    def add_another_account_use_case(self) -> AddAnotherAccountUseCase:
        """Get add another account use case"""
        if self._add_another_account_use_case is None:
            self._add_another_account_use_case = AddAnotherAccountUseCase(
                oauth_repository=self.oauth_repository(),
                user_repository=self.user_repository(),
                oauth_service=self.google_oauth_service(),
                fetch_emails_use_case=self.fetch_initial_emails_use_case(),
                user_account_repository=self.user_account_repository()
            )
        return self._add_another_account_use_case
    
    # LLM Use Cases
    def generate_email_content_use_case(self) -> GenerateEmailContentUseCase:
        """Get generate email content use case"""
        if self._generate_email_content_use_case is None:
            self._generate_email_content_use_case = GenerateEmailContentUseCase(self.llm_service())
        return self._generate_email_content_use_case
    
    def analyze_email_sentiment_use_case(self) -> AnalyzeEmailSentimentUseCase:
        """Get analyze email sentiment use case"""
        if self._analyze_email_sentiment_use_case is None:
            self._analyze_email_sentiment_use_case = AnalyzeEmailSentimentUseCase(self.llm_service())
        return self._analyze_email_sentiment_use_case
    
    def suggest_email_subject_use_case(self) -> SuggestEmailSubjectUseCase:
        """Get suggest email subject use case"""
        if self._suggest_email_subject_use_case is None:
            self._suggest_email_subject_use_case = SuggestEmailSubjectUseCase(self.llm_service())
        return self._suggest_email_subject_use_case
    
    def generate_email_response_use_case(self) -> GenerateEmailResponseUseCase:
        """Get generate email response use case"""
        if self._generate_email_response_use_case is None:
            self._generate_email_response_use_case = GenerateEmailResponseUseCase(self.llm_service())
        return self._generate_email_response_use_case
    
    def smart_email_composer_use_case(self) -> SmartEmailComposerUseCase:
        """Get smart email composer use case"""
        if self._smart_email_composer_use_case is None:
            self._smart_email_composer_use_case = SmartEmailComposerUseCase(self.llm_service())
        return self._smart_email_composer_use_case
    
    def gemini_chat_use_case(self) -> GeminiChatUseCase:
        """Get Gemini chat use case"""
        if self._gemini_chat_use_case is None:
            self._gemini_chat_use_case = GeminiChatUseCase(self.llm_service())
        return self._gemini_chat_use_case
    
    def gemini_vision_use_case(self) -> GeminiVisionUseCase:
        """Get Gemini vision use case"""
        if self._gemini_vision_use_case is None:
            self._gemini_vision_use_case = GeminiVisionUseCase(self.llm_service())
        return self._gemini_vision_use_case
    
    def gemini_tools_use_case(self) -> GeminiToolsUseCase:
        """Get Gemini tools use case"""
        if self._gemini_tools_use_case is None:
            self._gemini_tools_use_case = GeminiToolsUseCase(self.llm_service())
        return self._gemini_tools_use_case
    
    def gemini_health_check_use_case(self) -> GeminiHealthCheckUseCase:
        """Get Gemini health check use case"""
        if self._gemini_health_check_use_case is None:
            self._gemini_health_check_use_case = GeminiHealthCheckUseCase(self.llm_service())
        return self._gemini_health_check_use_case
    
    # Category Use Cases
    def create_category_use_case(self) -> CreateCategoryUseCase:
        """Get create category use case"""
        print(f"🔧 DEBUG: [Container] create_category_use_case called")
        if self._create_category_use_case is None:
            print(f"🔧 DEBUG: [Container] Creating new CreateCategoryUseCase")
            category_repo = self.category_repository()
            email_repo = self.email_repository()
            user_repo = self.user_repository()
            print(f"🔧 DEBUG: [Container] Category repository type: {type(category_repo).__name__}")
            print(f"🔧 DEBUG: [Container] Email repository type: {type(email_repo).__name__}")
            print(f"🔧 DEBUG: [Container] User repository type: {type(user_repo).__name__}")
            self._create_category_use_case = CreateCategoryUseCase(category_repo, email_repo, user_repo)
            print(f"🔧 DEBUG: [Container] CreateCategoryUseCase created successfully")
        else:
            print(f"🔧 DEBUG: [Container] Returning existing CreateCategoryUseCase")
        return self._create_category_use_case
    
    def get_category_use_case(self) -> GetCategoryUseCase:
        """Get get category use case"""
        if self._get_category_use_case is None:
            self._get_category_use_case = GetCategoryUseCase(self.category_repository())
        return self._get_category_use_case
    
    def update_category_use_case(self) -> UpdateCategoryUseCase:
        """Get update category use case"""
        if self._update_category_use_case is None:
            self._update_category_use_case = UpdateCategoryUseCase(self.category_repository())
        return self._update_category_use_case
    
    def delete_category_use_case(self) -> DeleteCategoryUseCase:
        """Get delete category use case"""
        if self._delete_category_use_case is None:
            self._delete_category_use_case = DeleteCategoryUseCase(
                self.category_repository(),
                self.email_repository()
            )
        return self._delete_category_use_case
    
    def list_categories_use_case(self) -> ListCategoriesUseCase:
        """Get list categories use case"""
        print(f"🔧 DEBUG: [Container] list_categories_use_case called")
        if self._list_categories_use_case is None:
            print(f"🔧 DEBUG: [Container] Creating new ListCategoriesUseCase")
            category_repo = self.category_repository()
            print(f"🔧 DEBUG: [Container] Category repository type: {type(category_repo).__name__}")
            self._list_categories_use_case = ListCategoriesUseCase(category_repo)
            print(f"🔧 DEBUG: [Container] ListCategoriesUseCase created successfully")
        else:
            print(f"🔧 DEBUG: [Container] Returning existing ListCategoriesUseCase")
        return self._list_categories_use_case
    
    def recategorize_emails_use_case(self) -> RecategorizeEmailsUseCase:
        """Get recategorize emails use case"""
        if self._recategorize_emails_use_case is None:
            self._recategorize_emails_use_case = RecategorizeEmailsUseCase(
                self.email_repository(),
                self.category_repository(),
                self.user_repository()
            )
        return self._recategorize_emails_use_case
    
    # User Account Use Cases
    def create_user_account_use_case(self) -> CreateUserAccountUseCase:
        """Get create user account use case"""
        if self._create_user_account_use_case is None:
            self._create_user_account_use_case = CreateUserAccountUseCase(self.user_account_repository())
        return self._create_user_account_use_case
    
    def get_user_accounts_use_case(self) -> GetUserAccountsUseCase:
        """Get user accounts use case"""
        if self._get_user_accounts_use_case is None:
            self._get_user_accounts_use_case = GetUserAccountsUseCase(self.user_account_repository())
        return self._get_user_accounts_use_case
    
    def get_active_user_accounts_use_case(self) -> GetActiveUserAccountsUseCase:
        """Get active user accounts use case"""
        if self._get_active_user_accounts_use_case is None:
            self._get_active_user_accounts_use_case = GetActiveUserAccountsUseCase(self.user_account_repository())
        return self._get_active_user_accounts_use_case
    
    def update_user_account_use_case(self) -> UpdateUserAccountUseCase:
        """Get update user account use case"""
        if self._update_user_account_use_case is None:
            self._update_user_account_use_case = UpdateUserAccountUseCase(self.user_account_repository())
        return self._update_user_account_use_case
    
    def delete_user_account_use_case(self) -> DeleteUserAccountUseCase:
        """Get delete user account use case"""
        if self._delete_user_account_use_case is None:
            self._delete_user_account_use_case = DeleteUserAccountUseCase(self.user_account_repository())
        return self._delete_user_account_use_case
    
    def check_account_exists_use_case(self) -> CheckAccountExistsUseCase:
        """Get check account exists use case"""
        if self._check_account_exists_use_case is None:
            self._check_account_exists_use_case = CheckAccountExistsUseCase(self.user_account_repository())
        return self._check_account_exists_use_case
    
    def add_account_if_not_exists_use_case(self) -> AddAccountIfNotExistsUseCase:
        """Get add account if not exists use case"""
        if self._add_account_if_not_exists_use_case is None:
            self._add_account_if_not_exists_use_case = AddAccountIfNotExistsUseCase(self.user_account_repository())
        return self._add_account_if_not_exists_use_case
    
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