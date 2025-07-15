from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from firebase_admin import firestore
from app.firebase_service import get_firestore_db


class EmailMessage(BaseModel):
    """Model for email message data"""
    id: Optional[str] = None
    sender: EmailStr
    recipients: List[EmailStr]
    subject: str
    body: str
    html_body: Optional[str] = None
    timestamp: Optional[datetime] = None
    status: str = "draft"  # draft, sent, failed
    metadata: Optional[Dict[str, Any]] = None


class EmailService:
    """Service class for email-related Firestore operations"""
    
    def __init__(self):
        self.collection_name = "emails"
    
    async def save_email(self, email: EmailMessage) -> str:
        """Save an email to Firestore"""
        db = get_firestore_db()
        
        # Prepare email data
        email_data = {
            "sender": email.sender,
            "recipients": email.recipients,
            "subject": email.subject,
            "body": email.body,
            "html_body": email.html_body,
            "timestamp": email.timestamp or firestore.SERVER_TIMESTAMP,
            "status": email.status,
            "metadata": email.metadata or {},
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        # Save to Firestore
        if email.id:
            doc_ref = db.collection(self.collection_name).document(email.id)
            doc_ref.set(email_data)
            return email.id
        else:
            doc_ref = db.collection(self.collection_name).add(email_data)
            return doc_ref[1].id
    
    async def get_email(self, email_id: str) -> Optional[EmailMessage]:
        """Get an email by ID from Firestore"""
        db = get_firestore_db()
        
        doc_ref = db.collection(self.collection_name).document(email_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        return EmailMessage(
            id=doc.id,
            sender=data["sender"],
            recipients=data["recipients"],
            subject=data["subject"],
            body=data["body"],
            html_body=data.get("html_body"),
            timestamp=data.get("timestamp"),
            status=data["status"],
            metadata=data.get("metadata", {})
        )
    
    async def get_emails_by_sender(self, sender: str, limit: int = 50) -> List[EmailMessage]:
        """Get emails by sender from Firestore"""
        db = get_firestore_db()
        
        docs = db.collection(self.collection_name)\
                .where("sender", "==", sender)\
                .limit(limit)\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .stream()
        
        emails = []
        for doc in docs:
            data = doc.to_dict()
            emails.append(EmailMessage(
                id=doc.id,
                sender=data["sender"],
                recipients=data["recipients"],
                subject=data["subject"],
                body=data["body"],
                html_body=data.get("html_body"),
                timestamp=data.get("timestamp"),
                status=data["status"],
                metadata=data.get("metadata", {})
            ))
        
        return emails
    
    async def update_email_status(self, email_id: str, status: str) -> bool:
        """Update email status in Firestore"""
        db = get_firestore_db()
        
        doc_ref = db.collection(self.collection_name).document(email_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.update({
            "status": status,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        return True
    
    async def delete_email(self, email_id: str) -> bool:
        """Delete an email from Firestore"""
        db = get_firestore_db()
        
        doc_ref = db.collection(self.collection_name).document(email_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.delete()
        return True


# Create global instance
email_service = EmailService() 