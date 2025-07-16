"""
Email Agent API - Clean Architecture Implementation

FastAPI application following clean architecture principles with:
- Domain-driven design
- Dependency injection
- SOLID principles
- Separation of concerns
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager

# Infrastructure
from app.infrastructure.config.settings import get_settings
from app.infrastructure.di.container import get_container

# Presentation layer - Clean controllers
from app.presentation.api.email_controller import router as email_router
from app.presentation.api.user_controller import router as user_router
from app.presentation.api.health_controller import router as health_router
from app.presentation.api.oauth_controller import router as oauth_router
from app.presentation.api.test_controller import router as test_router
from app.presentation.api.auth_test_controller import router as auth_test_router
from app.presentation.api.llm_controller import router as llm_router
from app.presentation.api.category_controller import router as category_router

# Keep the old routers for compatibility (temporary)
from app.routers import firestore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI application starting up with Clean Architecture...")
    
    # Initialize dependency injection container
    try:
        container = get_container()
        container.initialize()
        print("✅ Clean Architecture services initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Clean Architecture services: {e}")
        raise e
    
    yield
    
    # Shutdown
    print("🛑 FastAPI application shutting down...")
    
    # Clean up services
    try:
        container = get_container()
        container.cleanup()
        print("✅ Clean Architecture services cleaned up")
    except Exception as e:
        print(f"⚠️ Error during Clean Architecture cleanup: {e}")


# Get application settings
settings = get_settings()

# Security scheme for Bearer token authentication
security_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Enter your session ID as a Bearer token. This is the session ID you receive after OAuth authentication."
)

# OpenAPI tags metadata for better organization
tags_metadata = [
    {
        "name": "root",
        "description": "Root endpoints providing basic API information.",
    },
    {
        "name": "health",
        "description": "Health check endpoints for monitoring application status.",
    },
    {
        "name": "emails",
        "description": "Email management operations with clean architecture implementation.",
    },
    {
        "name": "users", 
        "description": "User management operations with clean architecture implementation.",
    },
    {
        "name": "auth",
        "description": "Google OAuth authentication operations including login, callback, and token management.",
    },
    {
        "name": "firestore-legacy",
        "description": "Legacy Firestore endpoints (for backward compatibility).",
    },
    {
        "name": "test",
        "description": "Test and debugging endpoints for development.",
    },
    {
        "name": "auth-test",
        "description": "Authentication middleware test endpoints for development.",
    },
    {
        "name": "llm",
        "description": "LLM-powered email features including content generation, sentiment analysis, and smart composition.",
    },
    {
        "name": "categories",
        "description": "Email category management for organizing inbox emails with user-defined categories.",
    },
]

# Create FastAPI instance with clean architecture configuration
app = FastAPI(
    title=settings.app_name,
    description="Email Agent API for managing emails and users with Firebase integration.",
    version=settings.app_version,
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Email Agent API Support",
        "url": "https://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include clean architecture routers
app.include_router(health_router, prefix=settings.api_prefix, tags=["health"])
app.include_router(email_router, prefix=settings.api_prefix, tags=["emails"])
app.include_router(user_router, prefix=settings.api_prefix, tags=["users"])
app.include_router(oauth_router, prefix=settings.api_prefix, tags=["auth"])
app.include_router(test_router, prefix=settings.api_prefix, tags=["test"])
app.include_router(auth_test_router, prefix=settings.api_prefix, tags=["auth-test"])
app.include_router(llm_router, prefix=settings.api_prefix, tags=["llm"])
app.include_router(category_router, prefix=settings.api_prefix, tags=["categories"])

# Include legacy routers for backward compatibility
app.include_router(firestore.router, prefix=settings.api_prefix, tags=["firestore-legacy"])


@app.get("/", 
         tags=["root"],
         summary="API Root",
         description="Welcome endpoint with clean architecture information.")
async def root():
    """
    ## Welcome to Email Agent API - Clean Architecture Edition
    
    This API implementation follows **clean architecture principles** with:
    
    ### 🏗️ Architecture Overview
    - **Domain Layer**: Pure business logic and rules
    - **Application Layer**: Use cases and application services
    - **Infrastructure Layer**: External integrations and data persistence
    - **Presentation Layer**: API controllers and models
    
    ### 🎯 Benefits
    - **Testable**: Clear separation enables easy testing
    - **Maintainable**: Organized code structure
    - **Scalable**: Modular design for growth
    - **Flexible**: Easy to change implementations
    
    ### 📖 Documentation
    - **Swagger UI**: `/docs` - Interactive API testing
    - **ReDoc**: `/redoc` - Beautiful API documentation
    - **OpenAPI Schema**: `/openapi.json` - Machine-readable spec
    """
    return {
        "message": f"Welcome to {settings.app_name} - Clean Architecture Edition",
        "version": settings.app_version,
        "architecture": "Clean Architecture",
        "features": {
            "domain_driven_design": True,
            "dependency_injection": True,
            "solid_principles": True,
            "testable_design": True
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc", 
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": f"{settings.api_prefix}/health",
            "emails": f"{settings.api_prefix}/emails",
            "users": f"{settings.api_prefix}/users"
        },
        "status": "online"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.api_host, 
        port=settings.api_port,
        log_level=settings.log_level.lower()
    ) 