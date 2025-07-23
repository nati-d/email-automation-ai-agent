"""
Domain Entities

Core business objects with identity and lifecycle.
"""

from .email import Email
from .user import User
from .oauth_session import OAuthSession
from .user_profile import UserProfile

__all__ = ["Email", "User", "OAuthSession", "UserProfile"] 