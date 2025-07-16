"""
Presentation Middleware

Middleware components for the presentation layer following clean architecture principles.
"""

from .auth_middleware import get_current_user, get_optional_current_user

__all__ = [
    "get_current_user",
    "get_optional_current_user"
] 