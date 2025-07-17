"""
Firestore Email Repository Implementation

Concrete implementation of email repository using Firestore.
"""

from typing import List, Optional
from datetime import datetime
from firebase_admin import firestore

from ...domain.entities.email import Email, EmailStatus, EmailType
from ...domain.value_objects.email_address import EmailAddress
from ...domain.repositories.email_repository import EmailRepository
from ...domain.exceptions.domain_exceptions import EntityNotFoundError


class FirestoreEmailRepository(EmailRepository):
    """Firestore implementation of email repository"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "emails"
    
    def _entity_to_doc(self, email: Email) -> dict:
        """Convert email entity to Firestore document"""
        return {
            "sender": str(email.sender),
            "recipients": [str(recipient) for recipient in email.recipients],
            "subject": email.subject,
            "body": email.body,
            "html_body": email.html_body,
            "status": email.status.value,
            "scheduled_at": email.scheduled_at,
            "sent_at": email.sent_at,
            "created_at": email.created_at,
            "updated_at": email.updated_at,
            "metadata": email.metadata,
            # AI Summarization fields
            "summary": email.summary,
            "main_concept": email.main_concept,
            "sentiment": email.sentiment,
            "key_topics": email.key_topics,
            "summarized_at": email.summarized_at,
            # Email categorization
            "email_type": email.email_type.value,
            "category": email.category,
            "categorized_at": email.categorized_at
        }
    
    def _doc_to_entity(self, doc_id: str, doc_data: dict) -> Email:
        """Convert Firestore document to email entity"""
        sender = EmailAddress.create(doc_data["sender"])
        recipients = [EmailAddress.create(recipient) for recipient in doc_data["recipients"]]
        
        email = Email(
            sender=sender,
            recipients=recipients,
            subject=doc_data["subject"],
            body=doc_data["body"],
            html_body=doc_data.get("html_body"),
            status=EmailStatus(doc_data["status"]),
            scheduled_at=doc_data.get("scheduled_at"),
            sent_at=doc_data.get("sent_at"),
            metadata=doc_data.get("metadata", {}),
            # AI Summarization fields
            summary=doc_data.get("summary"),
            main_concept=doc_data.get("main_concept"),
            sentiment=doc_data.get("sentiment"),
            key_topics=doc_data.get("key_topics", []),
            summarized_at=doc_data.get("summarized_at"),
            # Email categorization
            email_type=EmailType(doc_data.get("email_type", "inbox")),
            category=doc_data.get("category"),
            categorized_at=doc_data.get("categorized_at")
        )
        
        # Set entity ID and timestamps
        email.id = doc_id
        email.created_at = doc_data.get("created_at")
        email.updated_at = doc_data.get("updated_at")
        
        return email
    
    async def save(self, email: Email) -> Email:
        """Save an email to Firestore"""
        doc_data = self._entity_to_doc(email)
        doc_data["created_at"] = firestore.SERVER_TIMESTAMP
        doc_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        if email.id:
            # Update existing email
            doc_ref = self.db.collection(self.collection_name).document(email.id)
            doc_ref.set(doc_data)
        else:
            # Create new email
            doc_ref = self.db.collection(self.collection_name).add(doc_data)
            email.id = doc_ref[1].id
        
        return email
    
    async def find_by_id(self, email_id: str) -> Optional[Email]:
        """Find email by ID"""
        doc_ref = self.db.collection(self.collection_name).document(email_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        return self._doc_to_entity(doc.id, doc.to_dict())
    
    async def find_by_sender(self, sender: EmailAddress, limit: int = 50) -> List[Email]:
        """Find emails by sender"""
        query = self.db.collection(self.collection_name)\
            .where("sender", "==", str(sender))\
            .order_by("created_at", direction=firestore.Query.DESCENDING)\
            .limit(limit)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs]
    
    async def find_by_recipient(self, recipient: EmailAddress, limit: int = 50) -> List[Email]:
        """Find emails by recipient"""
        query = self.db.collection(self.collection_name).where("recipients", "array_contains", str(recipient)).limit(limit)
        docs = query.get()
        
        emails = []
        for doc in docs:
            emails.append(self._doc_to_entity(doc.id, doc.to_dict()))
        
        return emails
    

    
    async def find_by_status(self, status: EmailStatus, limit: int = 50) -> List[Email]:
        """Find emails by status"""
        query = self.db.collection(self.collection_name)\
            .where("status", "==", status.value)\
            .order_by("created_at", direction=firestore.Query.DESCENDING)\
            .limit(limit)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs]
    
    async def find_scheduled_emails(self, before: datetime = None) -> List[Email]:
        """Find scheduled emails to be sent"""
        query = self.db.collection(self.collection_name)\
            .where("status", "==", EmailStatus.SCHEDULED.value)
        
        if before:
            query = query.where("scheduled_at", "<=", before)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs]
    
    async def update(self, email: Email) -> Email:
        """Update an email"""
        print(f"🔧 DEBUG: [FirestoreEmailRepository] update called for email: {email.id}")
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Email has summarization: {email.has_summarization()}")
        
        if not email.id:
            raise ValueError("Email ID is required for update")
        
        doc_data = self._entity_to_doc(email)
        doc_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Document data keys: {list(doc_data.keys())}")
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Summary in doc_data: {doc_data.get('summary', 'NOT_FOUND')}")
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Main concept in doc_data: {doc_data.get('main_concept', 'NOT_FOUND')}")
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Sentiment in doc_data: {doc_data.get('sentiment', 'NOT_FOUND')}")
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Key topics in doc_data: {doc_data.get('key_topics', 'NOT_FOUND')}")
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Email type in doc_data: {doc_data.get('email_type', 'NOT_FOUND')}")
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Categorized at in doc_data: {doc_data.get('categorized_at', 'NOT_FOUND')}")
        
        doc_ref = self.db.collection(self.collection_name).document(email.id)
        doc_ref.update(doc_data)
        
        print(f"🔧 DEBUG: [FirestoreEmailRepository] Email updated successfully in Firestore")
        return email
    
    async def delete(self, email_id: str) -> bool:
        """Delete an email"""
        doc_ref = self.db.collection(self.collection_name).document(email_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.delete()
        return True
    
    async def count_by_sender(self, sender: EmailAddress) -> int:
        """Count emails by sender"""
        query = self.db.collection(self.collection_name)\
            .where("sender", "==", str(sender))
        
        docs = query.stream()
        return len(list(docs))
    
    async def find_recent_emails(self, limit: int = 10) -> List[Email]:
        """Find recent emails"""
        query = self.db.collection(self.collection_name)\
            .order_by("created_at", direction=firestore.Query.DESCENDING)\
            .limit(limit)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs] 