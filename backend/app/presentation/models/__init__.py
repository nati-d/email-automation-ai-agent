"""
Presentation Models

Pydantic models for API request/response contracts.
"""

from .email_models import (
    CreateEmailRequest, UpdateEmailRequest, EmailResponse,
    EmailListResponse, ScheduleEmailRequest
)
from .user_models import (
    CreateUserRequest, UpdateUserRequest, UserResponse
)
from .oauth_models import (
    OAuthLoginResponse, OAuthCallbackRequest, OAuthCallbackResponse,
    OAuthUserResponse, OAuthTokenRefreshResponse, OAuthUserInfoResponse,
    OAuthLogoutResponse, OAuthErrorResponse
)
from .base_models import ErrorResponse

__all__ = [
    "CreateEmailRequest", "UpdateEmailRequest", "EmailResponse",
    "EmailListResponse", "ScheduleEmailRequest", "CreateUserRequest",
    "UpdateUserRequest", "UserResponse", "OAuthLoginResponse",
    "OAuthCallbackRequest", "OAuthCallbackResponse", "OAuthUserResponse",
    "OAuthTokenRefreshResponse", "OAuthUserInfoResponse", "OAuthLogoutResponse",
    "OAuthErrorResponse", "ErrorResponse"
] 