"""
Email Agent API - Clean Architecture Implementation

FastAPI application following clean architecture principles with:
- Domain-driven design
- Dependency injection
- SOLID principles
- Separation of concerns
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Infrastructure
from app.infrastructure.config.settings import get_settings
from app.infrastructure.di.container import get_container

# Presentation layer - Clean controllers
from app.presentation.api.email_controller import router as email_router
from app.presentation.api.user_controller import router as user_router
from app.presentation.api.health_controller import router as health_router

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
        "name": "firestore-legacy",
        "description": "Legacy Firestore endpoints (for backward compatibility).",
    },
]

# Create FastAPI instance with clean architecture configuration
app = FastAPI(
    title=settings.app_name,
    description=f"""
    ## {settings.app_name} - Clean Architecture Implementation
    
    A comprehensive FastAPI backend following **clean architecture principles**:
    
    ### 🏗️ Architecture Layers
    
    - **🎯 Domain Layer**: Core business logic, entities, and repository interfaces
    - **🔄 Application Layer**: Use cases, DTOs, and application services  
    - **🏭 Infrastructure Layer**: Repository implementations and external services
    - **🌐 Presentation Layer**: API controllers and request/response models
    
    ### 🎯 Key Features
    
    - **🔥 Firebase/Firestore Integration**: Seamless cloud database operations
    - **📧 Email Management**: Complete email lifecycle with business rules
    - **👥 User Management**: User authentication and role-based access
    - **🏥 Health Monitoring**: Application health and dependency status
    - **📖 Auto Documentation**: Interactive API documentation with examples
    - **🔧 Dependency Injection**: Clean separation of concerns
    - **⚡ High Performance**: Built with FastAPI for optimal speed
    
    ### 🚀 Clean Architecture Benefits
    
    - **Testability**: Easy unit and integration testing
    - **Maintainability**: Clear separation of concerns
    - **Scalability**: Modular and extensible design
    - **Independence**: Framework and database agnostic
    - **Flexibility**: Easy to swap implementations
    
    ### 📚 Getting Started
    
    1. **Health Check**: `GET /api/health` - Verify service status
    2. **Create Email**: `POST /api/emails` - Send your first email
    3. **List Emails**: `GET /api/emails` - View your email history
    4. **Explore Documentation**: Use the interactive interface below
    
    ---
    
    **Built with Clean Architecture** • **Domain-Driven Design** • **SOLID Principles**
    """,
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