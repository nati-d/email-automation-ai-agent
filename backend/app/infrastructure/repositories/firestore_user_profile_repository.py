"""
Firestore implementation of UserProfileRepository
"""

from typing import Optional
from google.cloud import firestore
from app.domain.entities.user_profile import UserProfile
from app.domain.repositories.user_profile_repository import UserProfileRepository

class FirestoreUserProfileRepository(UserProfileRepository):
    def __init__(self, client: Optional[firestore.Client] = None):
        self.client = client or firestore.Client()
        self.collection = self.client.collection("user_profiles")

    async def save(self, profile: UserProfile) -> UserProfile:
        doc_ref = self.collection.document(profile.user_id)
        doc_ref.set(self._to_dict(profile))
        return profile

    async def update(self, profile: UserProfile) -> UserProfile:
        doc_ref = self.collection.document(profile.user_id)
        doc_ref.update(self._to_dict(profile))
        return profile

    async def find_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        doc = self.collection.document(user_id).get()
        if doc.exists:
            return self._from_dict(doc.to_dict())
        return None

    def _to_dict(self, profile: UserProfile) -> dict:
        return {
            "user_id": profile.user_id,
            "dominant_tone": profile.dominant_tone,
            "tone_distribution": profile.tone_distribution,
            "common_structures": profile.common_structures,
            "favorite_phrases": profile.favorite_phrases,
            "last_updated": profile.last_updated.isoformat() if profile.last_updated else None,
        }

    def _from_dict(self, data: dict) -> UserProfile:
        from datetime import datetime
        return UserProfile(
            user_id=data["user_id"],
            dominant_tone=data.get("dominant_tone"),
            tone_distribution=data.get("tone_distribution", {}),
            common_structures=data.get("common_structures", []),
            favorite_phrases=data.get("favorite_phrases", []),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None,
        ) 