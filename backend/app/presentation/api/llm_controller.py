"""
LLM Controller

API endpoints for Gemini-powered features.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, List, Optional, Any
import base64
from PIL import Image
import io

from ...infrastructure.di.container import get_container
from ...presentation.middleware.auth_middleware import get_current_user
from ...domain.entities.user import User
from ...presentation.models.llm_models import (
    GenerateEmailContentRequest,
    GenerateEmailContentResponse,
    AnalyzeEmailSentimentRequest,
    AnalyzeEmailSentimentResponse,
    SuggestEmailSubjectRequest,
    SuggestEmailSubjectResponse,
    SmartEmailComposerRequest,
    SmartEmailComposerResponse,
    GenerateEmailResponseRequest,
    GenerateEmailResponseResponse,
    GeminiChatRequest,
    GeminiChatResponse,
    GeminiVisionRequest,
    GeminiVisionResponse,
    GeminiToolsRequest,
    GeminiToolsResponse,
    GeminiHealthResponse
)

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/generate-email-content", response_model=GenerateEmailContentResponse)
async def generate_email_content(
    request: GenerateEmailContentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate email content using Gemini.
    """
    try:
        container = get_container()
        use_case = container.generate_email_content_use_case()
        
        content = use_case.execute(
            prompt=request.prompt,
            context=request.context
        )
        
        return GenerateEmailContentResponse(
            content=content,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate email content: {str(e)}")


@router.post("/analyze-email-sentiment", response_model=AnalyzeEmailSentimentResponse)
async def analyze_email_sentiment(
    request: AnalyzeEmailSentimentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze email sentiment and tone using Gemini.
    """
    try:
        container = get_container()
        use_case = container.analyze_email_sentiment_use_case()
        
        analysis = use_case.execute(request.email_content)
        
        return AnalyzeEmailSentimentResponse(
            sentiment=analysis.get("sentiment", "neutral"),
            tone=analysis.get("tone", "unknown"),
            professionalism_score=analysis.get("professionalism_score", 5.0),
            suggestions=analysis.get("suggestions", []),
            summary=analysis.get("summary", ""),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze email sentiment: {str(e)}")


@router.post("/suggest-email-subject", response_model=SuggestEmailSubjectResponse)
async def suggest_email_subject(
    request: SuggestEmailSubjectRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Suggest an email subject line using Gemini.
    """
    try:
        container = get_container()
        use_case = container.suggest_email_subject_use_case()
        
        subject = use_case.execute(
            email_content=request.email_content,
            context=request.context
        )
        
        return SuggestEmailSubjectResponse(
            subject=subject,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest email subject: {str(e)}")


@router.post("/smart-email-composer", response_model=SmartEmailComposerResponse)
async def smart_email_composer(
    request: SmartEmailComposerRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Compose a complete email using multiple Gemini features.
    """
    try:
        container = get_container()
        use_case = container.smart_email_composer_use_case()
        
        result = use_case.execute(
            purpose=request.purpose,
            recipient_context=request.recipient_context,
            tone=request.tone,
            include_subject=request.include_subject
        )
        
        return SmartEmailComposerResponse(
            content=result.get("content", ""),
            subject=result.get("subject", ""),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compose email: {str(e)}")


@router.post("/generate-email-response", response_model=GenerateEmailResponseResponse)
async def generate_email_response(
    request: GenerateEmailResponseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate an appropriate response to an email using Gemini.
    """
    try:
        container = get_container()
        use_case = container.generate_email_response_use_case()
        
        response = use_case.execute(
            original_email=request.original_email,
            response_type=request.response_type,
            additional_context=request.additional_context
        )
        
        return GenerateEmailResponseResponse(
            response=response,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate email response: {str(e)}")


@router.post("/chat/start", response_model=GeminiChatResponse)
async def start_chat(
    request: GeminiChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Start a new Gemini chat session.
    """
    try:
        container = get_container()
        use_case = container.gemini_chat_use_case()
        
        chat = use_case.start_chat(
            system_instruction=request.system_instruction,
            tools=request.tools,
            history=request.history,
            session_id=request.session_id,
            model_name=request.model_name
        )
        
        return GeminiChatResponse(
            session_id=request.session_id,
            message="Chat session started successfully",
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start chat: {str(e)}")


@router.post("/chat/send", response_model=GeminiChatResponse)
async def send_chat_message(
    message: str,
    session_id: str,
    model_name: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to an existing Gemini chat session.
    """
    try:
        container = get_container()
        use_case = container.gemini_chat_use_case()
        
        response = use_case.send_message(message, session_id, model_name)
        
        return GeminiChatResponse(
            session_id=session_id,
            message=response,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.delete("/chat/{session_id}")
async def end_chat(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    End a Gemini chat session.
    """
    try:
        container = get_container()
        use_case = container.gemini_chat_use_case()
        
        success = use_case.end_chat(session_id)
        
        if success:
            return {"message": f"Chat session '{session_id}' ended successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Chat session '{session_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end chat: {str(e)}")


@router.post("/vision/analyze", response_model=GeminiVisionResponse)
async def analyze_image(
    request: GeminiVisionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze an image using Gemini Vision.
    """
    try:
        container = get_container()
        use_case = container.gemini_vision_use_case()
        
        # Decode base64 image if provided
        if request.image_base64:
            image_data = base64.b64decode(request.image_base64)
        else:
            image_data = request.image_data
        
        result = use_case.analyze_image(
            system_instruction=request.system_instruction,
            query=request.query,
            image_data=image_data,
            model_name=request.model_name
        )
        
        return GeminiVisionResponse(
            analysis=result,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")


@router.post("/vision/analyze-file", response_model=GeminiVisionResponse)
async def analyze_image_file(
    file: UploadFile = File(...),
    system_instruction: str = "",
    query: str = "Describe this image",
    model_name: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze an uploaded image file using Gemini Vision.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        container = get_container()
        use_case = container.gemini_vision_use_case()
        
        result = use_case.analyze_image(
            system_instruction=system_instruction,
            query=query,
            image_data=image_data,
            model_name=model_name
        )
        
        return GeminiVisionResponse(
            analysis=result,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")


@router.post("/tools/execute", response_model=GeminiToolsResponse)
async def execute_with_tools(
    request: GeminiToolsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Execute a query using Gemini with specified tools.
    """
    try:
        container = get_container()
        use_case = container.gemini_tools_use_case()
        
        result = use_case.execute_with_tools(
            query=request.query,
            tools=request.tools,
            model_name=request.model_name
        )
        
        return GeminiToolsResponse(
            result=result,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute with tools: {str(e)}")


@router.get("/health", response_model=GeminiHealthResponse)
async def llm_health_check():
    """
    Health check for Gemini service.
    """
    try:
        container = get_container()
        use_case = container.gemini_health_check_use_case()
        
        health_info = use_case.execute()
        
        return GeminiHealthResponse(
            status=health_info.get("status", "unknown"),
            service=health_info.get("service", "Gemini LLM Service"),
            model=health_info.get("model", "unknown"),
            test_response=health_info.get("test_response", ""),
            available_models=health_info.get("available_models", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini service health check failed: {str(e)}") 