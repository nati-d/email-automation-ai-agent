"""
Use Cases

Business use cases that orchestrate domain logic.
"""

from .email_use_cases import (
    CreateEmailUseCase,
    GetEmailUseCase,
    UpdateEmailUseCase,
    DeleteEmailUseCase,
    SendEmailUseCase,
    ScheduleEmailUseCase,
    ListEmailsUseCase
)

from .user_use_cases import (
    CreateUserUseCase,
    GetUserUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase,
    AuthenticateUserUseCase
)

from .oauth_use_cases import (
    InitiateOAuthLoginUseCase,
    ProcessOAuthCallbackUseCase,
    RefreshOAuthTokenUseCase,
    LogoutOAuthUseCase,
    GetOAuthUserInfoUseCase
)

__all__ = [
    "CreateEmailUseCase", "GetEmailUseCase", "UpdateEmailUseCase", 
    "DeleteEmailUseCase", "SendEmailUseCase", "ScheduleEmailUseCase",
    "ListEmailsUseCase", "CreateUserUseCase", "GetUserUseCase", 
    "UpdateUserUseCase", "DeleteUserUseCase", "AuthenticateUserUseCase",
    "InitiateOAuthLoginUseCase", "ProcessOAuthCallbackUseCase", 
    "RefreshOAuthTokenUseCase", "LogoutOAuthUseCase", "GetOAuthUserInfoUseCase"
] 