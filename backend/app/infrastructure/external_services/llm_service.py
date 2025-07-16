"""
LLM Service

Integration with Google Gemini for AI-powered features.
"""

import os
import json
from typing import Dict, List, Optional, Any
import google.generativeai as genai

from ..config.settings import Settings


class LLMService:
    """Gemini LLM service wrapper for AI-powered features."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_name = getattr(settings, 'llm_model_name', 'gemini-2.5-flash')
        self.vision_model_name = getattr(settings, 'llm_vision_model_name', 'gemini-2.5-flash')
        self.pro_model_name = getattr(settings, 'llm_pro_model_name', 'gemini-2.5-pro')

        # Load API key from settings
        self.api_key = getattr(settings, 'gemini_api_key', None)

        # Validate required API key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in the .env file or environment variables.")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize chat sessions
        self._chat_sessions = {}

    # ------------------------------------------------------------------
    # Core Gemini Methods
    # ------------------------------------------------------------------
    
    def generate_content(
        self,
        system_instruction: str = "",
        query: str = "",
        response_type: str = "text/plain",
        response_schema: Optional[dict] = None,
        model_name: Optional[str] = None
    ) -> str:
        """
        Generate content using Gemini.
        
        Args:
            system_instruction: System instruction for the model
            query: The query/prompt to send to the model
            response_type: Expected response type (text/plain, application/json)
            response_schema: JSON schema for structured responses
            model_name: Specific model to use (optional)
            
        Returns:
            Generated content as string
        """
        print(f"🔧 DEBUG: [LLMService] generate_content called")
        print(f"🔧 DEBUG: [LLMService] model_name: {model_name or self.model_name}")
        print(f"🔧 DEBUG: [LLMService] response_type: {response_type}")
        print(f"🔧 DEBUG: [LLMService] query length: {len(query)}")
        
        try:
            # Create model
            print(f"🔧 DEBUG: [LLMService] Creating GenerativeModel...")
            model = genai.GenerativeModel(
                model_name=model_name or self.model_name
            )
            print(f"🔧 DEBUG: [LLMService] Model created successfully")

            # Handle different response types
            if response_type == "application/json" and response_schema:
                # For JSON responses, use the response_schema parameter
                print(f"🔧 DEBUG: [LLMService] Using JSON response schema")
                response = model.generate_content(
                    query,
                    response_schema=response_schema
                )
            else:
                # For plain text responses
                print(f"🔧 DEBUG: [LLMService] Using plain text response")
                response = model.generate_content(query)

            print(f"🔧 DEBUG: [LLMService] Response received, text length: {len(response.text)}")
            print(f"🔧 DEBUG: [LLMService] Response preview: {response.text[:200]}...")
            return response.text

        except Exception as e:
            print(f"🔧 DEBUG: [LLMService] generate_content failed: {e}")
            print(f"🔧 DEBUG: [LLMService] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [LLMService] Full traceback: {traceback.format_exc()}")
            raise



    def start_chat(
        self,
        system_instruction: str = "",
        tools: Optional[List[Dict]] = None,
        history: Optional[List] = None,
        session_id: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Start a chat session with Gemini.
        
        Args:
            system_instruction: System instruction for the chat
            tools: List of tool definitions (optional)
            history: Chat history (optional)
            session_id: Unique session identifier (optional)
            model_name: Specific model to use (optional)
            
        Returns:
            Chat session object
        """
        try:
            model = genai.GenerativeModel(
                model_name=model_name or self.model_name
            )
            
            chat = model.start_chat(history=history or [])
            
            # Store chat session if session_id provided
            if session_id:
                self._chat_sessions[session_id] = chat
                
            return chat
            
        except Exception as e:
            print(f"[LLMService] start_chat failed: {e}")
            raise

    def send_message(
        self,
        message: str,
        session_id: str,
        model_name: Optional[str] = None
    ) -> str:
        """
        Send a message to an existing chat session.
        
        Args:
            message: Message to send
            session_id: Session identifier
            model_name: Specific model to use (optional)
            
        Returns:
            Response from the chat session
        """
        try:
            if session_id not in self._chat_sessions:
                raise ValueError(f"Chat session '{session_id}' not found")
                
            chat = self._chat_sessions[session_id]
            response = chat.send_message(message)
            return response.text
            
        except Exception as e:
            print(f"[LLMService] send_message failed: {e}")
            raise

    def end_chat(self, session_id: str) -> bool:
        """
        End a chat session.
        
        Args:
            session_id: Session identifier to end
            
        Returns:
            True if session was ended successfully
        """
        try:
            if session_id in self._chat_sessions:
                del self._chat_sessions[session_id]
                return True
            return False
        except Exception as e:
            print(f"[LLMService] end_chat failed: {e}")
            return False

    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Model name (uses default if not provided)
            
        Returns:
            Model information dictionary
        """
        try:
            model_name = model_name or self.model_name
            return {
                "name": model_name,
                "display_name": f"Gemini {model_name}",
                "description": f"Google's {model_name} model for text generation",
                "generation_methods": ["text"],
                "input_content_types": ["text"],
                "output_content_types": ["text"]
            }
        except Exception as e:
            print(f"[LLMService] get_model_info failed: {e}")
            return {}

    # ------------------------------------------------------------------
    # Email-specific Gemini Methods
    # ------------------------------------------------------------------

    def generate_email_content(self, prompt: str, context: str = "") -> str:
        """
        Generate email content using Gemini.
        
        Args:
            prompt: Description of what kind of email to generate
            context: Optional context about recipient, situation, etc.
            
        Returns:
            Generated email content
        """
        system_instruction = (
            "You are an expert email writer. Generate professional, clear, and engaging email content "
            "based on the provided prompt. The email should be well-structured, appropriate in tone, "
            "and ready to send. Include a proper greeting and closing."
        )
        
        query = f"Generate an email based on this request: {prompt}"
        if context:
            query += f"\n\nContext: {context}"
            
        return self.generate_content(
            system_instruction=system_instruction,
            query=query,
            response_type="text/plain"
        )

    def analyze_email_sentiment(self, email_content: str) -> Dict[str, Any]:
        """
        Analyze email sentiment using Gemini.
        
        Args:
            email_content: The email content to analyze
            
        Returns:
            Analysis results including sentiment, tone, and suggestions
        """
        system_instruction = (
            "You are an expert in email analysis. Analyze the provided email content for sentiment, "
            "tone, professionalism, and provide suggestions for improvement if needed. "
            "Respond in JSON format with the following structure: "
            '{"sentiment": "positive/negative/neutral", "tone": "description", '
            '"professionalism_score": number_0_to_10, "suggestions": ["suggestion1", "suggestion2"], '
            '"summary": "brief summary"}'
        )
        
        try:
            response = self.generate_content(
                system_instruction=system_instruction,
                query=f"Analyze this email:\n\n{email_content}",
                response_type="text/plain"
            )
            return json.loads(response)
        except Exception as e:
            print(f"[LLMService] analyze_email_sentiment failed: {e}")
            return {
                "sentiment": "neutral",
                "tone": "unknown",
                "professionalism_score": 5.0,
                "suggestions": ["Unable to analyze email"],
                "summary": "Analysis failed"
            }

    def suggest_email_subject(self, email_content: str, context: str = "") -> str:
        """
        Suggest an email subject line using Gemini.
        
        Args:
            email_content: The email content
            context: Optional context about the recipient or situation
            
        Returns:
            Suggested subject line
        """
        system_instruction = (
            "You are an expert at writing email subject lines. Generate a clear, concise, "
            "and compelling subject line that accurately represents the email content. "
            "Keep it under 60 characters and avoid spam trigger words."
        )
        
        query = f"Suggest a subject line for this email:\n\n{email_content}"
        if context:
            query += f"\n\nContext: {context}"
            
        return self.generate_content(
            system_instruction=system_instruction,
            query=query,
            response_type="text/plain"
        ).strip()

    def generate_email_response(
        self,
        original_email: str,
        response_type: str = "acknowledge",
        additional_context: str = ""
    ) -> str:
        """
        Generate an appropriate response to an email using Gemini.
        
        Args:
            original_email: The email to respond to
            response_type: Type of response (acknowledge, follow_up, decline, etc.)
            additional_context: Additional context for the response
            
        Returns:
            Generated response
        """
        system_instruction = (
            f"You are an expert at writing email responses. Generate a {response_type} response "
            "to the provided email. The response should be professional, appropriate, and "
            "address the key points from the original email."
        )
        
        query = f"Generate a {response_type} response to this email:\n\n{original_email}"
        if additional_context:
            query += f"\n\nAdditional context: {additional_context}"
        
        return self.generate_content(
            system_instruction=system_instruction,
            query=query,
            response_type="text/plain"
        )

    def summarize_email(
        self,
        email_content: str,
        email_subject: str = "",
        sender: str = "",
        recipient: str = ""
    ) -> Dict[str, Any]:
        """
        Summarize email content and extract key information using Gemini.
        
        Args:
            email_content: The email body content
            email_subject: The email subject line
            sender: The sender's email address
            recipient: The recipient's email address
            
        Returns:
            Dictionary containing summary, main concept, sentiment, and key topics
        """
        print(f"🔧 DEBUG: [LLMService] summarize_email called")
        print(f"🔧 DEBUG: [LLMService] email_content length: {len(email_content)}")
        print(f"🔧 DEBUG: [LLMService] email_subject: {email_subject}")
        print(f"🔧 DEBUG: [LLMService] sender: {sender}")
        print(f"🔧 DEBUG: [LLMService] recipient: {recipient}")
        
        system_instruction = (
            "You are an expert email analyst. Analyze the provided email and extract key information. "
            "You MUST respond with ONLY valid JSON in the exact format specified. "
            "Do not include any markdown formatting, explanations, or additional text. "
            "The response must be parseable JSON with this exact structure: "
            '{"summary": "concise summary of the email content", '
            '"main_concept": "the primary topic or purpose of the email", '
            '"sentiment": "positive/negative/neutral/mixed", '
            '"key_topics": ["topic1", "topic2", "topic3"]}'
        )
        
        print(f"🔧 DEBUG: [LLMService] system_instruction: {system_instruction}")
        
        # Build context for better analysis
        context_parts = []
        if email_subject:
            context_parts.append(f"Subject: {email_subject}")
        if sender:
            context_parts.append(f"From: {sender}")
        if recipient:
            context_parts.append(f"To: {recipient}")
        
        context = "\n".join(context_parts)
        print(f"🔧 DEBUG: [LLMService] context: {context}")
        
        query = f"Analyze and summarize this email. Return ONLY valid JSON with no additional text or formatting:\n\n"
        if context:
            query += f"Context:\n{context}\n\n"
        query += f"Content:\n{email_content}\n\n"
        query += f"Return ONLY this JSON structure:\n"
        query += f'{{"summary": "brief summary", "main_concept": "main topic", "sentiment": "positive/negative/neutral/mixed", "key_topics": ["topic1", "topic2"]}}'
        
        print(f"🔧 DEBUG: [LLMService] query length: {len(query)}")
        print(f"🔧 DEBUG: [LLMService] query preview: {query[:500]}...")
        
        try:
            print(f"🔧 DEBUG: [LLMService] Calling generate_content...")
            response = self.generate_content(
                system_instruction=system_instruction,
                query=query,
                response_type="text/plain"
            )
            print(f"🔧 DEBUG: [LLMService] generate_content returned: {response[:200]}...")
            
            # Parse JSON response
            print(f"🔧 DEBUG: [LLMService] Parsing JSON response...")
            result = json.loads(response)
            print(f"🔧 DEBUG: [LLMService] Parsed JSON: {result}")
            
            # Validate required fields
            required_fields = ["summary", "main_concept", "sentiment", "key_topics"]
            for field in required_fields:
                if field not in result:
                    print(f"🔧 DEBUG: [LLMService] Missing field '{field}', setting default")
                    result[field] = "Unknown" if field != "key_topics" else []
            
            print(f"🔧 DEBUG: [LLMService] Final result: {result}")
            return result
            
        except json.JSONDecodeError as e:
            print(f"🔧 DEBUG: [LLMService] JSON decode error: {e}")
            print(f"🔧 DEBUG: [LLMService] Raw response: {response}")
            
            # Try to extract JSON from the response if it contains JSON
            try:
                import re
                # Look for JSON pattern in the response
                json_pattern = r'\{[^{}]*"summary"[^{}]*"main_concept"[^{}]*"sentiment"[^{}]*"key_topics"[^{}]*\}'
                json_match = re.search(json_pattern, response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    print(f"🔧 DEBUG: [LLMService] Found JSON pattern: {json_str}")
                    extracted_result = json.loads(json_str)
                    print(f"🔧 DEBUG: [LLMService] Successfully extracted JSON: {extracted_result}")
                    return extracted_result
            except Exception as extract_error:
                print(f"🔧 DEBUG: [LLMService] Failed to extract JSON: {extract_error}")
            
            # Return fallback data
            return {
                "summary": "Unable to generate summary - JSON parsing failed",
                "main_concept": "Unknown",
                "sentiment": "neutral",
                "key_topics": []
            }
        except Exception as e:
            print(f"🔧 DEBUG: [LLMService] summarize_email failed: {e}")
            print(f"🔧 DEBUG: [LLMService] Error type: {type(e).__name__}")
            import traceback
            print(f"🔧 DEBUG: [LLMService] Full traceback: {traceback.format_exc()}")
            # Return fallback data
            return {
                "summary": "Unable to generate summary",
                "main_concept": "Unknown",
                "sentiment": "neutral",
                "key_topics": []
            }

    def extract_email_concepts(self, email_content: str) -> List[str]:
        """
        Extract key concepts and topics from email content.
        
        Args:
            email_content: The email content to analyze
            
        Returns:
            List of key concepts/topics
        """
        system_instruction = (
            "You are an expert at extracting key concepts from text. "
            "Identify the main topics, concepts, and themes mentioned in the email. "
            "Return a JSON array of strings, each representing a key concept or topic. "
            "Keep concepts concise (1-3 words each) and avoid duplicates."
        )
        
        query = f"Extract key concepts from this email:\n\n{email_content}"
        
        try:
            response = self.generate_content(
                system_instruction=system_instruction,
                query=query,
                response_type="text/plain"
            )
            
            concepts = json.loads(response)
            if isinstance(concepts, list):
                return [str(concept).strip() for concept in concepts if concept.strip()]
            else:
                return []
                
        except Exception as e:
            print(f"[LLMService] extract_email_concepts failed: {e}")
            return []

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Gemini service.
        
        Returns:
            Health check results
        """
        try:
            # Test basic functionality
            test_response = self.generate_content(
                system_instruction="You are a helpful assistant.",
                query="Say 'Hello'",
                response_type="text/plain"
            )
            
            return {
                "status": "healthy",
                "service": "Gemini LLM Service",
                "model": self.model_name,
                "test_response": test_response,
                "available_models": []
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Gemini LLM Service",
                "error": str(e)
            }

    def cleanup(self):
        """Clean up resources."""
        try:
            self._chat_sessions.clear()
        except Exception as e:
            print(f"[LLMService] cleanup failed: {e}") 