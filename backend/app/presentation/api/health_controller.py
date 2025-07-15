"""
Health Controller

Clean architecture implementation of health check endpoints.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any

# Infrastructure
from ...infrastructure.di.container import Container, get_container

# Presentation models
from ..models.base_models import SuccessResponse


router = APIRouter()


@router.get("/health",
           response_model=SuccessResponse,
           summary="Basic Health Check",
           description="Simple health check endpoint to verify the API is running.")
async def health_check() -> SuccessResponse:
    """Basic health check endpoint"""
    return SuccessResponse(
        message="Email Agent API is healthy",
        data={
            "status": "healthy",
            "service": "Email Agent API",
            "version": "1.0.0"
        }
    )


@router.get("/health/detailed",
           summary="Detailed Health Check",
           description="Comprehensive health check with system information.")
async def detailed_health_check(
    container: Container = Depends(get_container)
) -> Dict[str, Any]:
    """Detailed health check with system information"""
    
    # Check Firebase service
    firebase_status = "unknown"
    try:
        firebase_service = container.firebase_service()
        firebase_status = "connected" if firebase_service.is_initialized() else "disconnected"
    except Exception:
        firebase_status = "error"
    
    # Check email service
    email_service = container.email_service()
    email_status = "configured" if email_service.is_configured() else "not_configured"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Email Agent API",
        "version": "1.0.0",
        "uptime": "System operational",
        "dependencies": {
            "firestore": firebase_status,
            "email_service": email_status,
            "redis": "not_configured"
        },
        "features": {
            "clean_architecture": True,
            "dependency_injection": True,
            "domain_driven_design": True,
            "swagger_documentation": True
        }
    } 