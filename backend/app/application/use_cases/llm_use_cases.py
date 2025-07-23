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
    """Use case for generating email responses"""
    
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
        prompt = f"Generate a {response_type} response to the following email:\n\n{original_email}"
        
        if additional_context:
            prompt += f"\n\nAdditional context: {additional_context}"
        
        return self.llm_service.generate_email_content(prompt)


class ComposeEmailUseCase:
    """Use case for composing emails with user profile integration"""
    
    def __init__(self, llm_service: LLMService, user_repository=None):
        self.llm_service = llm_service
        self.user_repository = user_repository
    
    def _detect_email_type(self, text: str) -> str:
        """
        Automatically detect if the text is a reply to an email or a started email.
        
        Args:
            text (str): The input text
            
        Returns:
            str: 'reply' if it appears to be a reply, 'started' if it appears to be a started email
        """
        # Convert to lowercase for easier analysis
        text_lower = text.lower().strip()
        
        # Common reply indicators
        reply_indicators = [
            "re:", "reply:", "responding to", "in response to", "regarding your email",
            "thank you for your email", "i received your email", "i got your message",
            "as per your email", "following up on", "in reply to", "answering your",
            "you mentioned", "you wrote", "you said", "your email", "your message"
        ]
        
        # Check if text contains reply indicators
        for indicator in reply_indicators:
            if indicator in text_lower:
                return "reply"
        
        # Check if text starts with common email patterns that suggest it's a reply
        if text_lower.startswith(("hi", "hello", "dear")) and any(indicator in text_lower for indicator in ["your email", "your message", "re:", "reply:"]):
            return "reply"
        
        # If text is very short or incomplete, it's likely a started email
        if len(text.strip()) < 50:
            return "started"
        
        # Default to started email if no clear reply indicators
        return "started"
    
    async def execute(self, 
                     user_id: str,
                     text: str,
                     recipients: List[str],
                     purpose: Optional[str] = None,
                     tone: str = "auto",
                     additional_context: str = "") -> Dict[str, Any]:
        """
        Compose an email using the user's profile and preferences.
        
        Args:
            user_id (str): ID of the user composing the email
            text (str): Email text - either original email to reply to or partial email text
            recipients (List[str]): List of recipient email addresses
            purpose (Optional[str]): Optional purpose or context of the email
            tone (str): Desired tone (auto, professional, casual, formal, friendly, etc.)
            additional_context (str): Additional context or requirements
            
        Returns:
            Dict: Dictionary containing content, subject, tone_used, and user_profile_used
        """
        # Get user profile if available
        user_profile = None
        user_profile_used = False
        
        if self.user_repository:
            try:
                user = await self.user_repository.find_by_id(user_id)
                if user and user.user_profile:
                    user_profile = user.user_profile
                    user_profile_used = True
                    print(f"✅ Using user profile for {user.email.value}")
                else:
                    print(f"ℹ️ No user profile available for user {user_id}")
            except Exception as e:
                print(f"⚠️ Error fetching user profile: {e}")
        
        # Determine the tone to use
        tone_used = tone
        if tone == "auto" and user_profile and user_profile.get("dominant_tone"):
            tone_used = user_profile["dominant_tone"]
            print(f"🎯 Using auto-detected tone: {tone_used}")
        
        # Automatically detect email type
        email_type = self._detect_email_type(text)
        print(f"🔍 Detected email type: {email_type}")
        
        # Build the system instruction
        system_instruction = f"You are an expert email composer. Compose a {tone_used} email."
        
        # Add user profile context if available
        if user_profile:
            profile_context = f"""
User's email style profile:
- Dominant tone: {user_profile.get('dominant_tone', 'professional')}
- Common structures: {', '.join(user_profile.get('common_structures', []))}
- Favorite phrases: {', '.join(user_profile.get('favorite_phrases', []))}
- Style summary: {user_profile.get('summary', 'Professional and clear communication style')}

Please incorporate the user's typical writing style, tone, and favorite phrases into the email composition.
"""
            system_instruction += profile_context
        
        # Build the query based on detected email type
        if email_type == "reply":
            query = f"""
Compose a {tone_used} reply to the following email:

Original Email:
{text}

Recipients: {', '.join(recipients)}
{f"Purpose: {purpose}" if purpose else ""}
{f"Additional context: {additional_context}" if additional_context else ""}

Please write a complete reply that matches the user's typical style and tone.
"""
        else:  # started email
            query = f"""
Complete the following email that the user started writing:

Partial Email Text:
{text}

Recipients: {', '.join(recipients)}
{f"Purpose: {purpose}" if purpose else ""}
{f"Additional context: {additional_context}" if additional_context else ""}

Please complete the email in a natural way that matches the user's typical style and tone.
"""
        
        # Generate the email content
        content = self.llm_service.generate_content(
            system_instruction=system_instruction,
            query=query,
            response_type="text/plain"
        )
        
        result = {
            "content": content,
            "tone_used": tone_used,
            "user_profile_used": user_profile_used,
            "email_type_detected": email_type
        }
        
        # Generate subject line for started emails if the original text doesn't have one
        if email_type == "started" and not any(line.strip().lower().startswith("subject:") for line in text.split('\n')):
            try:
                # Extract a potential subject from the first line or generate one
                first_line = text.strip().split('\n')[0]
                if len(first_line) < 100:  # If first line is short, it might be a subject
                    subject = first_line
                else:
                    subject = self.llm_service.suggest_email_subject(content, purpose or "Email composition")
                result["subject"] = subject
            except Exception as e:
                print(f"⚠️ Failed to generate subject line: {e}")
                result["subject"] = None
        
        return result


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