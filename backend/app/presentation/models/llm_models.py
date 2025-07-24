"""
LLM Models

Pydantic models for Gemini API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union


# Generate Email Content
class GenerateEmailContentRequest(BaseModel):
    prompt: str = Field(..., description="Description of what kind of email to generate")
    context: str = Field("", description="Optional context about recipient, situation, etc.")


class GenerateEmailContentResponse(BaseModel):
    content: str = Field(..., description="Generated email content")
    success: bool = Field(..., description="Whether the operation was successful")


# Analyze Email Sentiment
class AnalyzeEmailSentimentRequest(BaseModel):
    email_content: str = Field(..., description="The email content to analyze")


class AnalyzeEmailSentimentResponse(BaseModel):
    sentiment: str = Field(..., description="Sentiment analysis result (positive, negative, neutral)")
    tone: str = Field(..., description="Tone analysis result")
    professionalism_score: float = Field(..., description="Professionalism score (0-10)")
    suggestions: List[str] = Field(..., description="List of improvement suggestions")
    summary: str = Field(..., description="Summary of the analysis")
    success: bool = Field(..., description="Whether the operation was successful")


# Suggest Email Subject
class SuggestEmailSubjectRequest(BaseModel):
    email_content: str = Field(..., description="The email content")
    context: str = Field("", description="Optional context about the recipient or situation")


class SuggestEmailSubjectResponse(BaseModel):
    subject: str = Field(..., description="Suggested subject line")
    success: bool = Field(..., description="Whether the operation was successful")


# Smart Email Composer
class SmartEmailComposerRequest(BaseModel):
    purpose: str = Field(..., description="The purpose of the email")
    recipient_context: str = Field("", description="Context about the recipient")
    tone: str = Field("professional", description="Desired tone (professional, casual, formal, etc.)")
    include_subject: bool = Field(True, description="Whether to generate a subject line")


class SmartEmailComposerResponse(BaseModel):
    content: str = Field(..., description="Generated email content")
    subject: str = Field("", description="Generated subject line")
    success: bool = Field(..., description="Whether the operation was successful")


# Generate Email Response
class GenerateEmailResponseRequest(BaseModel):
    original_email: str = Field(..., description="The email to respond to")
    response_type: str = Field("acknowledge", description="Type of response (acknowledge, follow_up, decline, etc.)")
    additional_context: str = Field("", description="Additional context for the response")


class GenerateEmailResponseResponse(BaseModel):
    response: str = Field(..., description="Generated response")
    success: bool = Field(..., description="Whether the operation was successful")


# Compose Email with User Profile (NEW: Query-based, body-only)
class ComposeEmailQueryRequest(BaseModel):
    query: str = Field(
        ..., 
        description="Query for composing an email. Can be an email to reply to, or any text to start a new email.",
        min_length=1,
        max_length=10000
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Hi John, I received your email about the project proposal. I think we should discuss this further."
            }
        }

class ComposeEmailBodyResponse(BaseModel):
    body: str = Field(
        ..., 
        description="The generated email body as plain text."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "body": "Hi John,\n\nThank you for your email about the project proposal. I'd be happy to discuss this further. Please let me know your availability.\n\nBest regards,\n[Your Name]"
            }
        }


# Gemini Chat
class GeminiChatRequest(BaseModel):
    system_instruction: str = Field("", description="System instruction for the chat")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="List of tool definitions")
    history: Optional[List] = Field(None, description="Chat history")
    session_id: Optional[str] = Field(None, description="Unique session identifier")
    model_name: Optional[str] = Field(None, description="Specific model to use")


class GeminiChatResponse(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Response message or status")
    success: bool = Field(..., description="Whether the operation was successful")


# Gemini Vision
class GeminiVisionRequest(BaseModel):
    system_instruction: str = Field("", description="System instruction for the analysis")
    query: str = Field(..., description="Query about the image")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data")
    image_data: Optional[bytes] = Field(None, description="Raw image data")
    model_name: Optional[str] = Field(None, description="Specific vision model to use")


class GeminiVisionResponse(BaseModel):
    analysis: str = Field(..., description="Analysis result")
    success: bool = Field(..., description="Whether the operation was successful")


# Gemini Tools
class GeminiToolsRequest(BaseModel):
    query: str = Field(..., description="The query to execute")
    tools: List[Dict[str, Any]] = Field(..., description="List of tool definitions")
    model_name: Optional[str] = Field(None, description="Specific model to use")


class GeminiToolsResponse(BaseModel):
    result: str = Field(..., description="Generated result")
    success: bool = Field(..., description="Whether the operation was successful")


# Gemini Health Check
class GeminiHealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    model: str = Field(..., description="Current model name")
    test_response: str = Field(..., description="Test response from Gemini")
    available_models: List[str] = Field(..., description="List of available models") 