from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

# Import routers
from app.routers import health, firestore, email
from app.firebase_service import firebase_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI application starting up...")
    
    # Initialize Firebase/Firestore
    try:
        firebase_service.initialize_firebase()
        print("🔥 Firebase services initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        raise e
    
    yield
    
    # Shutdown
    print("🛑 FastAPI application shutting down...")
    
    # Clean up Firebase resources
    try:
        firebase_service.close()
        print("🔥 Firebase services cleaned up")
    except Exception as e:
        print(f"⚠️ Error during Firebase cleanup: {e}")


# OpenAPI tags metadata
tags_metadata = [
    {
        "name": "root",
        "description": "Root endpoints providing basic API information and welcome messages.",
    },
    {
        "name": "health",
        "description": "Health check endpoints for monitoring application status and connectivity.",
    },
    {
        "name": "firestore",
        "description": "Firestore database operations including CRUD operations for documents and collections. "
                      "These endpoints allow you to interact with Firebase Firestore database.",
    },
    {
        "name": "emails",
        "description": "Email management operations including sending, storing, and retrieving email messages.",
    },
]

# Create FastAPI instance with enhanced OpenAPI configuration
app = FastAPI(
    title="Email Agent API",
    description="""
    ## Email Agent Backend API
    
    A comprehensive FastAPI backend for the Email Agent application that provides:
    
    * **Email Management**: Send, store, and manage email messages
    * **Firestore Integration**: Direct database operations with Firebase Firestore
    * **Health Monitoring**: Application health and status endpoints
    * **Authentication**: Secure API access (coming soon)
    
    ### Features
    
    - 🔥 **Firebase/Firestore Integration**: Seamless cloud database operations
    - 📧 **Email Operations**: Full email lifecycle management
    - 🚀 **High Performance**: Built with FastAPI for optimal speed
    - 📖 **Auto Documentation**: Interactive API documentation
    - 🔒 **Security**: JWT authentication and authorization (planned)
    
    ### Getting Started
    
    1. Check application health with `/api/health`
    2. Test Firestore connection with `/api/firestore/test`
    3. Explore the interactive documentation below
    
    ---
    
    **Note**: This API is designed for integration with email agent applications and requires proper authentication for production use.
    """,
    version="1.0.0",
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
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(firestore.router, prefix="/api", tags=["firestore"])
app.include_router(email.router, prefix="/api", tags=["emails"])


def custom_openapi():
    """Custom OpenAPI schema generation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Add servers
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://your-api-domain.com", "description": "Production server"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", 
         tags=["root"],
         summary="Root endpoint",
         description="Welcome endpoint that provides basic API information and status.")
async def root():
    """
    ## Welcome to Email Agent API
    
    This is the root endpoint of the Email Agent API. It provides basic information
    about the API and confirms that the service is running correctly.
    
    ### Response
    Returns a welcome message with API information.
    """
    return {
        "message": "Welcome to Email Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "status": "online"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 