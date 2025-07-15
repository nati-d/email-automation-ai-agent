"""
OAuth Presentation Models

Pydantic models for OAuth API contracts.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class OAuthLoginResponse(BaseModel):
    """Response model for OAuth login initiation"""
    authorization_url: HttpUrl = Field(..., description="Google OAuth authorization URL")
    state: str = Field(..., description="OAuth state parameter for security")
    message: str = Field(default="Redirect to the authorization URL to continue", description="Instructions for the user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
                "state": "secure-random-state-parameter",
                "message": "Redirect to the authorization URL to continue"
            }
        }


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback (query parameters)"""
    code: Optional[str] = Field(None, description="Authorization code from OAuth provider")
    state: Optional[str] = Field(None, description="OAuth state parameter")
    error: Optional[str] = Field(None, description="Error code if authorization failed")
    error_description: Optional[str] = Field(None, description="Human-readable error description")


class OAuthUserResponse(BaseModel):
    """Response model for OAuth user information"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user account is active")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
                "role": "user",
                "is_active": True,
                "last_login": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-15T09:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class OAuthSessionInfo(BaseModel):
    """Session information model"""
    provider: str = Field(..., description="OAuth provider name")
    session_active: bool = Field(..., description="Whether session is active")
    token_expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "google",
                "session_active": True,
                "token_expires_in": 3600
            }
        }


class OAuthCallbackResponse(BaseModel):
    """Response model for OAuth callback processing"""
    user: OAuthUserResponse = Field(..., description="User information")
    session_id: str = Field(..., description="OAuth session ID")
    access_token: str = Field(..., description="OAuth access token")
    is_new_user: bool = Field(..., description="Whether this is a new user registration")
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "user-123",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "role": "user",
                    "is_active": True
                },
                "session_id": "session-456",
                "access_token": "ya29.access-token",
                "is_new_user": False,
                "message": "OAuth authentication successful"
            }
        }


class OAuthTokenRefreshResponse(BaseModel):
    """Response model for token refresh"""
    access_token: str = Field(..., description="New access token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    message: str = Field(default="Token refreshed successfully", description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "ya29.new-access-token",
                "expires_in": 3600,
                "message": "Token refreshed successfully"
            }
        }


class OAuthUserInfoResponse(BaseModel):
    """Response model for getting OAuth user info"""
    user: OAuthUserResponse = Field(..., description="User information")
    session_info: OAuthSessionInfo = Field(..., description="Session information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "user-123",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "role": "user",
                    "is_active": True
                },
                "session_info": {
                    "provider": "google",
                    "session_active": True,
                    "token_expires_in": 3600
                }
            }
        }


class OAuthLogoutResponse(BaseModel):
    """Response model for OAuth logout"""
    success: bool = Field(..., description="Whether logout was successful")
    token_revoked: bool = Field(..., description="Whether OAuth token was revoked")
    message: str = Field(..., description="Logout status message")
    warning: Optional[str] = Field(None, description="Warning message if any")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "token_revoked": True,
                "message": "Successfully logged out",
                "warning": None
            }
        }


class OAuthErrorResponse(BaseModel):
    """Response model for OAuth errors"""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "OAUTH_ERROR",
                "message": "OAuth authentication failed",
                "details": {
                    "provider": "google",
                    "error_code": "access_denied"
                }
            }
        } 