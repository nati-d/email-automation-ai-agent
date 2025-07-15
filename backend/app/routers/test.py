"""
Test Router

Router for test and debugging endpoints.
"""

from fastapi import APIRouter

from ..presentation.api.test_controller import router as test_controller

# Create test router
router = APIRouter(prefix="/test", tags=["Test & Debug"])

# Include test controller
router.include_router(test_controller) 