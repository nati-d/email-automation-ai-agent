"""
Firestore User Repository Implementation

Concrete implementation of user repository using Firestore.
"""

from typing import List, Optional
from firebase_admin import firestore

from ...domain.entities.user import User, UserRole
from ...domain.value_objects.email_address import EmailAddress
from ...domain.repositories.user_repository import UserRepository


class FirestoreUserRepository(UserRepository):
    """Firestore implementation of user repository"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "users"
    
    def _entity_to_doc(self, user: User) -> dict:
        """Convert user entity to Firestore document"""
        doc = {
            "email": str(user.email),
            "name": user.name,
            "role": user.role.value,
            "is_active": user.is_active,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "google_id": user.google_id,
            "profile_picture": user.profile_picture,
            "oauth_provider": user.oauth_provider
        }
        if user.user_profile is not None:
            doc["user_profile"] = user.user_profile
        return doc
    
    def _doc_to_entity(self, doc_id: str, doc_data: dict) -> User:
        """Convert Firestore document to user entity"""
        email = EmailAddress.create(doc_data["email"])
        role = UserRole(doc_data["role"])
        user = User(
            email=email,
            name=doc_data["name"],
            role=role,
            is_active=doc_data.get("is_active", True),
            last_login=doc_data.get("last_login"),
            google_id=doc_data.get("google_id"),
            profile_picture=doc_data.get("profile_picture"),
            oauth_provider=doc_data.get("oauth_provider"),
            user_profile=doc_data.get("user_profile")
        )
        # Set entity ID and timestamps
        user.id = doc_id
        user.created_at = doc_data.get("created_at")
        user.updated_at = doc_data.get("updated_at")
        return user
    
    async def save(self, user: User) -> User:
        """Save a user to Firestore"""
        doc_data = self._entity_to_doc(user)
        doc_data["created_at"] = firestore.SERVER_TIMESTAMP
        doc_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        if user.id:
            # Update existing user
            doc_ref = self.db.collection(self.collection_name).document(user.id)
            doc_ref.set(doc_data)
        else:
            # Create new user
            doc_ref = self.db.collection(self.collection_name).add(doc_data)
            user.id = doc_ref[1].id
        
        return user
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        doc_ref = self.db.collection(self.collection_name).document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        return self._doc_to_entity(doc.id, doc.to_dict())
    
    async def find_by_email(self, email: EmailAddress) -> Optional[User]:
        """Find user by email"""
        query = self.db.collection(self.collection_name)\
            .where("email", "==", str(email))\
            .limit(1)
        
        docs = list(query.stream())
        if not docs:
            return None
        
        doc = docs[0]
        return self._doc_to_entity(doc.id, doc.to_dict())
    
    async def find_by_role(self, role: UserRole) -> List[User]:
        """Find users by role"""
        query = self.db.collection(self.collection_name)\
            .where("role", "==", role.value)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs]
    
    async def find_active_users(self, limit: int = 50) -> List[User]:
        """Find active users"""
        query = self.db.collection(self.collection_name)\
            .where("is_active", "==", True)\
            .limit(limit)
        
        docs = query.stream()
        return [self._doc_to_entity(doc.id, doc.to_dict()) for doc in docs]
    
    async def update(self, user: User) -> User:
        """Update a user"""
        if not user.id:
            raise ValueError("User ID is required for update")
        
        doc_data = self._entity_to_doc(user)
        doc_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        doc_ref = self.db.collection(self.collection_name).document(user.id)
        doc_ref.update(doc_data)
        
        return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        doc_ref = self.db.collection(self.collection_name).document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.delete()
        return True
    
    async def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if user exists by email"""
        user = await self.find_by_email(email)
        return user is not None 