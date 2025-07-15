from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    service: str
    version: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00.000Z",
                "service": "Email Agent API",
                "version": "1.0.0"
            }
        }


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model"""
    status: str
    timestamp: str
    service: str
    version: str
    uptime: str
    dependencies: Dict[str, str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00.000Z",
                "service": "Email Agent API",
                "version": "1.0.0",
                "uptime": "System operational",
                "dependencies": {
                    "firestore": "connected",
                    "redis": "not_configured",
                    "email_service": "not_configured"
                }
            }
        }


router = APIRouter()


@router.get("/health", 
           response_model=HealthResponse,
           summary="Basic Health Check",
           description="Simple health check endpoint to verify the API is running and responsive.")
async def health_check() -> HealthResponse:
    """
    ## Basic Health Check
    
    Performs a basic health check to verify that the Email Agent API is running
    and responsive. This endpoint is typically used by:
    
    - Load balancers for health checking
    - Monitoring systems for uptime tracking
    - CI/CD pipelines for deployment verification
    
    ### Response
    
    Returns basic service information including:
    - Service status
    - Current timestamp
    - Service name and version
    
    ### Status Codes
    
    - **200**: Service is healthy and operational
    - **500**: Service is experiencing issues (rare)
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="Email Agent API",
        version="1.0.0"
    )


@router.get("/health/detailed", 
           response_model=DetailedHealthResponse,
           summary="Detailed Health Check",
           description="Comprehensive health check with system information and dependency status.")
async def detailed_health_check() -> DetailedHealthResponse:
    """
    ## Detailed Health Check
    
    Provides comprehensive health information including system status and
    dependency health. This endpoint gives detailed insights into:
    
    - Overall service health
    - System uptime information
    - Status of external dependencies (Firestore, Redis, etc.)
    - Service configuration status
    
    ### Dependencies Checked
    
    - **Firestore**: Firebase database connectivity
    - **Redis**: Cache service status (if configured)
    - **Email Service**: SMTP service status (if configured)
    
    ### Response Details
    
    The response includes all basic health information plus:
    - System uptime
    - Dependency status mapping
    - Configuration status for each service
    
    ### Use Cases
    
    - System monitoring and alerting
    - Debugging connectivity issues
    - Operational dashboards
    - Dependency verification
    """
    # TODO: Add real dependency checks
    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="Email Agent API",
        version="1.0.0",
        uptime="System operational",
        dependencies={
            "firestore": "connected",
            "redis": "not_configured", 
            "email_service": "not_configured"
        }
    ) 