"""
API Controllers

FastAPI routers implementing clean architecture.
"""

from .email_controller import router as email_router
from .user_controller import router as user_router
from .health_controller import router as health_router
from .oauth_controller import router as oauth_router

__all__ = ["email_router", "user_router", "health_router", "oauth_router"] 