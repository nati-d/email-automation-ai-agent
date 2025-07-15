"""
Test Controller for Debugging

Test endpoints for debugging Gmail integration and email fetching.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

# Infrastructure
from ...infrastructure.di.container import Container, get_container

router = APIRouter()


@router.get("/test/gmail-service", 
           summary="Test Gmail Service",
           description="Test if Gmail service can be instantiated.")
async def test_gmail_service(
    container: Container = Depends(get_container)
) -> Dict[str, Any]:
    """Test Gmail service instantiation"""
    try:
        gmail_service = container.gmail_service()
        return {
            "success": True,
            "gmail_service_type": type(gmail_service).__name__,
            "message": "Gmail service instantiated successfully"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "message": "Failed to instantiate Gmail service"
        }


@router.get("/test/fetch-emails-use-case",
           summary="Test Fetch Emails Use Case", 
           description="Test if email fetching use case can be instantiated.")
async def test_fetch_emails_use_case(
    container: Container = Depends(get_container)
) -> Dict[str, Any]:
    """Test fetch emails use case instantiation"""
    try:
        use_case = container.fetch_initial_emails_use_case()
        return {
            "success": True,
            "use_case_type": type(use_case).__name__,
            "gmail_service_type": type(use_case.gmail_service).__name__,
            "email_repository_type": type(use_case.email_repository).__name__,
            "message": "Fetch emails use case instantiated successfully"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "message": "Failed to instantiate fetch emails use case"
        }


@router.get("/test/oauth-callback-use-case",
           summary="Test OAuth Callback Use Case",
           description="Test if OAuth callback use case is properly configured.")
async def test_oauth_callback_use_case(
    container: Container = Depends(get_container)
) -> Dict[str, Any]:
    """Test OAuth callback use case configuration"""
    try:
        use_case = container.process_oauth_callback_use_case()
        return {
            "success": True,
            "use_case_type": type(use_case).__name__,
            "has_fetch_emails_use_case": use_case.fetch_emails_use_case is not None,
            "fetch_emails_use_case_type": type(use_case.fetch_emails_use_case).__name__ if use_case.fetch_emails_use_case else "None",
            "oauth_service_type": type(use_case.oauth_service).__name__,
            "message": "OAuth callback use case configured successfully"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "message": "Failed to configure OAuth callback use case"
        }


@router.get("/test/dependencies",
           summary="Test All Dependencies",
           description="Test all dependencies for email fetching.")
async def test_dependencies() -> Dict[str, Any]:
    """Test all dependencies for email fetching"""
    results = {}
    
    try:
        # Test google-api-python-client import
        from googleapiclient.discovery import build
        results["google_api_client"] = {"success": True, "message": "google-api-python-client available"}
    except ImportError as e:
        results["google_api_client"] = {"success": False, "error": str(e), "message": "google-api-python-client not installed"}
    
    try:
        # Test google-auth import
        from google.oauth2.credentials import Credentials
        results["google_auth"] = {"success": True, "message": "google-auth available"}
    except ImportError as e:
        results["google_auth"] = {"success": False, "error": str(e), "message": "google-auth not installed"}
    
    try:
        # Test gmail service import
        from ...infrastructure.external_services.gmail_service import GmailService
        results["gmail_service_import"] = {"success": True, "message": "GmailService import successful"}
    except ImportError as e:
        results["gmail_service_import"] = {"success": False, "error": str(e), "message": "GmailService import failed"}
    
    try:
        # Test email use case import
        from ...application.use_cases.email_use_cases import FetchInitialEmailsUseCase
        results["fetch_emails_use_case_import"] = {"success": True, "message": "FetchInitialEmailsUseCase import successful"}
    except ImportError as e:
        results["fetch_emails_use_case_import"] = {"success": False, "error": str(e), "message": "FetchInitialEmailsUseCase import failed"}
    
    return {
        "overall_success": all(result.get("success", False) for result in results.values()),
        "results": results
    } 