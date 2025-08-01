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
    
    async def execute(self, user_id: str, query: str) -> dict:
        """
        Compose an email body using the user's profile and the provided query.
        Args:
            user_id (str): ID of the user composing the email
            query (str): The query for composing the email (email to reply to, or any text)
        Returns:
            dict: { 'body': <generated email body as plain text> }
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
        # Detect email type
        email_type = self._detect_email_type(query)
        print(f"🔍 Detected email type: {email_type}")
        # Build detailed, human-centered system instruction
        system_instruction = """You are an expert email composer with deep understanding of human communication, psychology, and professional relationships. Your role is to craft emails that feel genuinely human, authentic, and contextually appropriate.

CORE PRINCIPLES:
- Write as if you are the actual person, not an AI assistant
- Consider the emotional and professional context of the communication
- Use natural, conversational language that builds genuine connections
- Be mindful of power dynamics, cultural nuances, and relationship context
- Ensure the tone matches the urgency, importance, and nature of the situation
- Create emails that feel personal and thoughtful, not generic or robotic

EMAIL COMPOSITION GUIDELINES:
- Start with appropriate greetings based on relationship and formality level
- Acknowledge the recipient's perspective and any previous context
- Be specific, clear, and actionable in your communication
- Show empathy and understanding when appropriate
- Use natural transitions between ideas
- End with appropriate closing that matches the relationship and purpose
- Keep the overall tone consistent throughout the email

IMPORTANT CONSTRAINTS:
- Compose email body only (no subject line or signature)
- Write in plain text format
- Focus on substance over length - be concise but complete
- Avoid corporate jargon unless the context specifically requires it
- Make sure the email feels like it was written by a real person, not generated by AI"""
        
        if user_profile:
            profile_context = f"""

PERSONAL EMAIL STYLE PROFILE:
Based on analysis of the user's previous emails, here are their unique characteristics:

TONE & PERSONALITY:
- Dominant tone: {user_profile.get('dominant_tone', 'professional')}
- Communication style: {user_profile.get('communication_style', 'direct and clear')}
- Emotional expression: {user_profile.get('emotional_expression', 'balanced')}

WRITING PATTERNS:
- Common structures: {', '.join(user_profile.get('common_structures', ['clear introduction', 'logical flow', 'actionable conclusion']))}
- Favorite phrases: {', '.join(user_profile.get('favorite_phrases', ['Thank you for your time', 'I appreciate your consideration']))}
- Transition words: {', '.join(user_profile.get('transition_words', ['Additionally', 'Furthermore', 'However']))}

PERSONAL TOUCHES:
- How they show appreciation: {user_profile.get('appreciation_style', 'direct and sincere')}
- How they handle disagreements: {user_profile.get('conflict_style', 'diplomatic and solution-focused')}
- How they build rapport: {user_profile.get('rapport_style', 'professional yet warm')}

SUMMARY OF STYLE:
{user_profile.get('summary', 'Professional communicator who values clarity, respect, and actionable outcomes.')}

IMPORTANT: Mirror these characteristics authentically while maintaining the natural flow and context of the current communication."""
            system_instruction += profile_context
        
        # Compose detailed, context-aware prompt
        if email_type == "reply":
            prompt = f"""CRAFT A THOUGHTFUL REPLY

CONTEXT: You need to respond to the following email. Consider the sender's perspective, the relationship dynamics, and what would be most helpful and appropriate.

ORIGINAL EMAIL:
{query}

TASK: Write a reply that:
1. Acknowledges the sender's message appropriately
2. Addresses any questions, concerns, or requests they've raised
3. Maintains the relationship and tone appropriate for your connection
4. Provides clear, actionable next steps if needed
5. Shows genuine engagement with their communication

Remember: This should feel like a natural, human response that builds on the conversation and moves it forward constructively."""
        else:
            prompt = f"""COMPLETE A STARTED EMAIL

CONTEXT: The user has begun writing an email but needs help completing it. Your task is to continue their thought process and complete the communication naturally.

PARTIAL EMAIL:
{query}

TASK: Complete this email by:
1. Understanding the user's intent and direction
2. Continuing their natural thought process and style
3. Adding appropriate content to fulfill the email's purpose
4. Ensuring the completed email feels cohesive and complete
5. Maintaining the user's authentic voice throughout

Remember: This should feel like a natural continuation of their writing, not a separate addition. The completed email should flow seamlessly from their original words."""
        # Call LLM service
        body = self.llm_service.generate_content(
            system_instruction=system_instruction,
            query=prompt,
            response_type="text/plain"
        )
        return {"body": body}


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