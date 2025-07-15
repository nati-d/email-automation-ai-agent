"""
Application Settings

Clean architecture configuration management.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with clean architecture principles"""
    
    # Application
    app_name: str = "Email Agent API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    
    # Database
    database_url: str = "sqlite:///./email_agent.db"
    
    # Firebase
    firebase_credentials_path: str = "turing-rush-466007-b2-firebase-adminsdk-fbsvc-8a2e3a7e05.json"
    firebase_project_id: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False
    
    # Email Service
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    
    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    google_scopes: List[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send"
    ]
    frontend_url: str = "http://localhost:3000"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Business Rules
    max_recipients_per_email: int = 100
    max_email_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 