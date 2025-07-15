"""
Domain Entities

Core business objects with identity and lifecycle.
"""

from .email import Email
from .user import User
from .oauth_session import OAuthSession

__all__ = ["Email", "User", "OAuthSession"] 