"""
Firestore OAuth Repository Implementation

Concrete implementation of OAuth repository using Firestore.
"""

from typing import Optional
from firebase_admin import firestore
from datetime import datetime

from ...domain.entities.oauth_session import OAuthSession
from ...domain.repositories.oauth_repository import OAuthRepository
from ...domain.value_objects.oauth_token import OAuthToken
from ...domain.value_objects.oauth_user_info import OAuthUserInfo
from ...domain.value_objects.email_address import EmailAddress


class FirestoreOAuthRepository(OAuthRepository):
    """Firestore implementation of OAuth repository"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "oauth_sessions"
    
    def _entity_to_doc(self, session: OAuthSession) -> dict:
        """Convert OAuth session entity to Firestore document"""
        return {
            "user_id": session.user_id,
            "token": {
                "access_token": session.token.access_token,
                "refresh_token": session.token.refresh_token,
                "expires_at": session.token.expires_at.isoformat(),
                "scope": session.token.scope,
                "token_type": session.token.token_type
            },
            "user_info": {
                "provider_id": session.user_info.provider_id,
                "email": str(session.user_info.email),
                "name": session.user_info.name,
                "picture": session.user_info.picture,
                "locale": session.user_info.locale,
                "provider": session.user_info.provider
            },
            "state": session.state,
            "is_active": session.is_active,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None
        }
    
    def _doc_to_entity(self, doc_id: str, doc_data: dict) -> OAuthSession:
        """Convert Firestore document to OAuth session entity"""
        # Reconstruct token
        token_data = doc_data["token"]
        expires_at = token_data["expires_at"]
        if isinstance(expires_at, str):
            expires_at_dt = datetime.fromisoformat(expires_at)
        else:
            # Handle Firestore timestamp
            expires_at_dt = expires_at
            
        token = OAuthToken(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at_dt,
            scope=token_data["scope"],
            token_type=token_data.get("token_type", "Bearer")
        )
        
        # Reconstruct user info
        user_info_data = doc_data["user_info"]
        email = EmailAddress.create(user_info_data["email"])
        user_info = OAuthUserInfo(
            provider_id=user_info_data["provider_id"],
            email=email,
            name=user_info_data["name"],
            picture=user_info_data.get("picture"),
            locale=user_info_data.get("locale"),
            provider=user_info_data.get("provider", "google")
        )
        
        # Create session
        session = OAuthSession(
            user_id=doc_data.get("user_id"),
            token=token,
            user_info=user_info,
            state=doc_data["state"],
            is_active=doc_data.get("is_active", True)
        )
        
        # Set entity ID and timestamps
        session.id = doc_id
        if doc_data.get("created_at"):
            created_at = doc_data["created_at"]
            if isinstance(created_at, str):
                session.created_at = datetime.fromisoformat(created_at)
            else:
                # Handle Firestore timestamp
                session.created_at = created_at
        if doc_data.get("updated_at"):
            updated_at = doc_data["updated_at"]
            if isinstance(updated_at, str):
                session.updated_at = datetime.fromisoformat(updated_at)
            else:
                # Handle Firestore timestamp
                session.updated_at = updated_at
        
        return session
    
    async def save_session(self, session: OAuthSession) -> OAuthSession:
        """Save an OAuth session to Firestore"""
        doc_data = self._entity_to_doc(session)
        doc_data["created_at"] = firestore.SERVER_TIMESTAMP
        doc_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        if session.id:
            # Update existing session
            doc_ref = self.db.collection(self.collection_name).document(session.id)
            doc_ref.set(doc_data)
        else:
            # Create new session
            doc_ref = self.db.collection(self.collection_name).add(doc_data)
            session.id = doc_ref[1].id
        
        return session
    
    async def find_session_by_id(self, session_id: str) -> Optional[OAuthSession]:
        """Find OAuth session by ID"""
        doc_ref = self.db.collection(self.collection_name).document(session_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        return self._doc_to_entity(doc.id, doc.to_dict())
    
    async def find_session_by_state(self, state: str) -> Optional[OAuthSession]:
        """Find OAuth session by state parameter"""
        query = self.db.collection(self.collection_name)\
            .where(filter=firestore.FieldFilter("state", "==", state))\
            .where(filter=firestore.FieldFilter("is_active", "==", True))\
            .limit(1)
        
        docs = list(query.stream())
        if not docs:
            return None
        
        doc = docs[0]
        return self._doc_to_entity(doc.id, doc.to_dict())
    
    async def find_active_session_by_user_id(self, user_id: str) -> Optional[OAuthSession]:
        """Find active OAuth session for a user"""
        query = self.db.collection(self.collection_name)\
            .where(filter=firestore.FieldFilter("user_id", "==", user_id))\
            .where(filter=firestore.FieldFilter("is_active", "==", True))\
            .limit(1)
        
        docs = list(query.stream())
        if not docs:
            return None
        
        doc = docs[0]
        return self._doc_to_entity(doc.id, doc.to_dict())
    
    async def update_session(self, session: OAuthSession) -> OAuthSession:
        """Update an OAuth session"""
        if not session.id:
            raise ValueError("Session ID is required for update")
        
        doc_data = self._entity_to_doc(session)
        doc_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        doc_ref = self.db.collection(self.collection_name).document(session.id)
        doc_ref.update(doc_data)
        
        return session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete an OAuth session"""
        doc_ref = self.db.collection(self.collection_name).document(session_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.delete()
        return True
    
    async def find_by_user_email(self, user_email: str) -> Optional[OAuthSession]:
        """Find active OAuth session by user email"""
        query = self.db.collection(self.collection_name)\
            .where(filter=firestore.FieldFilter("user_info.email", "==", user_email))\
            .where(filter=firestore.FieldFilter("is_active", "==", True))\
            .limit(1)
        
        docs = list(query.stream())
        if not docs:
            return None
        
        doc = docs[0]
        return self._doc_to_entity(doc.id, doc.to_dict())
    
    async def deactivate_user_sessions(self, user_id: str) -> bool:
        """Deactivate all sessions for a user"""
        query = self.db.collection(self.collection_name)\
            .where(filter=firestore.FieldFilter("user_id", "==", user_id))\
            .where(filter=firestore.FieldFilter("is_active", "==", True))
        
        docs = list(query.stream())
        
        for doc in docs:
            doc.reference.update({
                "is_active": False,
                "updated_at": firestore.SERVER_TIMESTAMP
            })
        
        return len(docs) > 0 