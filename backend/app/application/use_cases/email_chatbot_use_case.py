"""
Email Chatbot Use Case

Specialized chatbot for email intelligence and analysis.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ...domain.repositories.email_repository import EmailRepository
from ...domain.repositories.user_repository import UserRepository
from ...infrastructure.external_services.llm_service import LLMService
from ...domain.value_objects.email_address import EmailAddress


class EmailChatbotUseCase:
    """Use case for email intelligence chatbot with tools"""
    
    def __init__(self, llm_service: LLMService, email_repository: EmailRepository, user_repository: UserRepository):
        self.llm_service = llm_service
        self.email_repository = email_repository
        self.user_repository = user_repository
    
    def _get_email_tools(self, user_email: str) -> List[Dict[str, Any]]:
        """No tools needed - we'll feed emails directly to Gemini"""
        return []
    
    def _get_system_instruction(self, user_email: str) -> str:
        """Get system instruction for email chatbot"""
        return f"""You are a direct, human-friendly email assistant for {user_email}.

RESPONSE STYLE:
- Give direct, clear answers in natural sentences
- No fillers, fluff, or unnecessary phrases
- Focus on the main message and key information
- Be conversational but concise
- Use simple, everyday language

WHEN ANSWERING:
- If asked about specific topics: "You have X emails about [topic]. Here are the key ones: [list main emails]"
- If asked about senders: "You have X emails from [sender]. The most recent is about [subject]"
- If asked for statistics: "You have X total emails. Y are work-related, Z are personal"
- If no relevant emails found: "You don't have any emails about [topic]"

FORMAT:
- Use bullet points only for listing multiple items
- Include dates and subjects for context
- Mention email IDs if user needs to reference them
- Keep responses under 3-4 sentences unless listing multiple emails

EXAMPLE:
User: "do i have any email related to amazon"
You: "You have 3 emails from Amazon. The most recent is an order confirmation from January 15th for electronics. The other two are shipping updates from last week."

Analyze the email data and give direct, human-friendly answers."""
    
    async def send_email_chat_message(self, message: str, user_email: str) -> str:
        """Send a message to the email chatbot (sessionless)"""
        try:
            # Get user's emails
            print(f"🔧 DEBUG: Fetching emails for user: {user_email}")
            emails = await self.email_repository.find_by_account_owner(user_email, limit=50)
            print(f"🔧 DEBUG: Found {len(emails)} emails")
            
            # Format emails for Gemini
            email_data = self._format_emails_for_analysis(emails)
            
            # Get system instruction
            system_instruction = self._get_system_instruction(user_email)
            
            # Create a new chat session (no tools needed)
            chat = self.llm_service.start_chat(
                system_instruction=system_instruction
            )
            
            # Create the full prompt with email data
            full_prompt = f"""Your emails:

{email_data}

Question: {message}

Answer directly and naturally."""
            
            # Send the complete prompt
            response = chat.send_message(full_prompt)
            
            print(f"🔧 DEBUG: Response received successfully")
            return response.text
            
        except Exception as e:
            print(f"❌ ERROR in send_email_chat_message: {str(e)}")
            import traceback
            print(f"❌ TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Failed to send email chat message: {str(e)}")
    

    
    def _format_emails_for_analysis(self, emails: List) -> str:
        """Format emails for Gemini analysis"""
        if not emails:
            return "No emails found."
        
        formatted_emails = []
        for i, email in enumerate(emails[:20], 1):  # Limit to 20 emails for context
            email_info = f"""Email {i}:
- ID: {email.id}
- From: {email.sender}
- To: {', '.join(str(r) for r in email.recipients)}
- Subject: {email.subject}
- Date: {email.created_at.strftime('%Y-%m-%d %H:%M') if email.created_at else 'Unknown'}
- Category: {email.category or 'Uncategorized'}
- Type: {email.email_type.value if hasattr(email, 'email_type') else 'inbox'}"""
            
            if email.summary:
                email_info += f"\n- Summary: {email.summary}"
            
            if email.sentiment:
                email_info += f"\n- Sentiment: {email.sentiment}"
            
            if email.key_topics:
                email_info += f"\n- Key Topics: {', '.join(email.key_topics)}"
            
            email_info += f"\n- Content: {email.body[:300]}..." if len(email.body) > 300 else f"\n- Content: {email.body}"
            
            formatted_emails.append(email_info)
        
        return "\n\n".join(formatted_emails)
    
    async def get_email_chatbot_info(self, user_email: str) -> Dict[str, Any]:
        """Get information about the email chatbot capabilities"""
        return {
            "message": f"Email chatbot ready for {user_email}. I can help you analyze your emails, find specific messages, get statistics, and provide insights. What would you like to know about your emails?",
            "capabilities": [
                "Search emails by sender, recipient, subject, content, category, and date",
                "Get detailed email analysis with summaries and sentiment",
                "Generate email statistics and trends",
                "Find related emails and conversation threads",
                "Track recent email activity and important items"
            ]
        } 