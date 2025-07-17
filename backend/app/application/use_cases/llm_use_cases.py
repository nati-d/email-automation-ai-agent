"""
LLM Use Cases

Application use cases for Gemini-powered features.
"""

from typing import Dict, List, Optional, Union, Any
from PIL import Image
from ...domain.entities.email import Email
from ...infrastructure.external_services.llm_service import LLMService


class GenerateEmailContentUseCase:
    """Use case for generating email content using Gemini"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def execute(self, prompt: str, context: str = "") -> str:
        """
        Generate email content based on a prompt and optional context.
        
        Args:
            prompt (str): Description of what kind of email to generate
            context (str): Optional context about recipient, situation, etc.
            
        Returns:
            str: Generated email content
        """
        return self.llm_service.generate_email_content(prompt, context)


class AnalyzeEmailSentimentUseCase:
    """Use case for analyzing email sentiment and tone using Gemini"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def execute(self, email_content: str) -> Dict[str, Any]:
        """
        Analyze the sentiment and tone of an email.
        
        Args:
            email_content (str): The email content to analyze
            
        Returns:
            Dict: Analysis results including sentiment, tone, and suggestions
        """
        return self.llm_service.analyze_email_sentiment(email_content)


class SuggestEmailSubjectUseCase:
    """Use case for suggesting email subject lines using Gemini"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def execute(self, email_content: str, context: str = "") -> str:
        """
        Suggest an appropriate subject line for an email.
        
        Args:
            email_content (str): The email content
            context (str): Optional context about the recipient or situation
            
        Returns:
            str: Suggested subject line
        """
        return self.llm_service.suggest_email_subject(email_content, context)


class GenerateEmailResponseUseCase:
    """Use case for generating email responses using Gemini"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def execute(self, 
                original_email: str, 
                response_type: str = "acknowledge",
                additional_context: str = "") -> str:
        """
        Generate an appropriate response to an email.
        
        Args:
            original_email (str): The email to respond to
            response_type (str): Type of response (acknowledge, follow_up, decline, etc.)
            additional_context (str): Additional context for the response
            
        Returns:
            str: Generated response
        """
        return self.llm_service.generate_email_response(
            original_email, response_type, additional_context
        )


class SmartEmailComposerUseCase:
    """Use case for smart email composition with multiple Gemini features"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def execute(self, 
                purpose: str, 
                recipient_context: str = "", 
                tone: str = "professional",
                include_subject: bool = True) -> Dict[str, str]:
        """
        Compose a complete email using multiple Gemini features.
        
        Args:
            purpose (str): The purpose of the email
            recipient_context (str): Context about the recipient
            tone (str): Desired tone (professional, casual, formal, etc.)
            include_subject (bool): Whether to generate a subject line
            
        Returns:
            Dict: Dictionary containing subject and content
        """
        # Build the prompt with tone and context
        prompt = f"Write a {tone} email for the following purpose: {purpose}"
        if recipient_context:
            prompt += f"\n\nRecipient context: {recipient_context}"
        
        # Generate email content
        content = self.llm_service.generate_email_content(prompt)
        
        result = {"content": content}
        
        # Generate subject line if requested
        if include_subject:
            subject = self.llm_service.suggest_email_subject(content, recipient_context)
            result["subject"] = subject
        
        return result


class GeminiChatUseCase:
    """Use case for managing Gemini chat sessions"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def start_chat(self, 
                   system_instruction: str = "",
                   tools: Optional[List[Dict]] = None,
                   history: Optional[List] = None,
                   session_id: Optional[str] = None,
                   model_name: Optional[str] = None):
        """
        Start a new chat session.
        
        Args:
            system_instruction (str): System instruction for the chat
            tools (List[Dict]): List of tool definitions
            history (List): Chat history
            session_id (str): Unique session identifier
            model_name (str): Specific model to use
            
        Returns:
            Chat session object
        """
        return self.llm_service.start_chat(
            system_instruction, tools, history, session_id, model_name
        )
    
    def send_message(self, message: str, session_id: str, model_name: Optional[str] = None) -> str:
        """
        Send a message to an existing chat session.
        
        Args:
            message (str): Message to send
            session_id (str): Session identifier
            model_name (str): Specific model to use
            
        Returns:
            str: Response from the chat session
        """
        return self.llm_service.send_message(message, session_id, model_name)
    
    def end_chat(self, session_id: str) -> bool:
        """
        End a chat session.
        
        Args:
            session_id (str): Session identifier to end
            
        Returns:
            bool: True if session was ended successfully
        """
        return self.llm_service.end_chat(session_id)


class GeminiVisionUseCase:
    """Use case for Gemini vision capabilities"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def analyze_image(self, 
                     system_instruction: str,
                     query: str,
                     image_data: Union[str, bytes, Image.Image],
                     model_name: Optional[str] = None) -> str:
        """
        Analyze an image using Gemini Vision.
        
        Args:
            system_instruction (str): System instruction for the analysis
            query (str): Query about the image
            image_data: Image data (file path, bytes, or PIL Image)
            model_name (str): Specific vision model to use
            
        Returns:
            str: Analysis result
        """
        return self.llm_service.generate_content_with_vision(
            system_instruction, query, image_data, model_name
        )


class GeminiToolsUseCase:
    """Use case for Gemini tools functionality"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def execute_with_tools(self, 
                          query: str, 
                          tools: List[Dict],
                          model_name: Optional[str] = None) -> str:
        """
        Execute a query using Gemini with specified tools.
        
        Args:
            query (str): The query to execute
            tools (List[Dict]): List of tool definitions
            model_name (str): Specific model to use
            
        Returns:
            str: Generated response
        """
        return self.llm_service.generate_content_with_tools(query, tools, model_name)


class GeminiHealthCheckUseCase:
    """Use case for checking Gemini service health"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def execute(self) -> Dict[str, Any]:
        """
        Perform a health check on the Gemini service.
        
        Returns:
            Dict: Health check results
        """
        return self.llm_service.health_check() 