"""
Domain Repository Interfaces

Abstract definitions for data access.
"""

from .email_repository import EmailRepository
from .user_repository import UserRepository
from .oauth_repository import OAuthRepository

__all__ = ["EmailRepository", "UserRepository", "OAuthRepository"] 