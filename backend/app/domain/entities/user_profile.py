"""
User Profile Entity

Aggregated profile of a user's email style, tone, and structure.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from .base import BaseEntity
from ..exceptions.domain_exceptions import DomainValidationError

@dataclass
class UserProfile(BaseEntity):
    """User profile entity for storing aggregated email style/tone/structure data"""
    user_id: str  # Reference to User entity
    # Aggregated fields
    dominant_tone: Optional[str] = None
    tone_distribution: Dict[str, int] = field(default_factory=dict)  # e.g., {"formal": 5, "friendly": 3}
    common_structures: List[str] = field(default_factory=list)  # e.g., ["greeting-closing", "bullet-points"]
    favorite_phrases: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        super().__init__()
        self._validate()

    def _validate(self) -> None:
        if not self.user_id:
            raise DomainValidationError("User ID cannot be empty for UserProfile")

    def update_profile(self, tone: Optional[str] = None, structure: Optional[str] = None, phrase: Optional[str] = None):
        """Update the profile with new tone, structure, or phrase data"""
        if tone:
            self.tone_distribution[tone] = self.tone_distribution.get(tone, 0) + 1
            # Update dominant tone
            self.dominant_tone = max(self.tone_distribution, key=self.tone_distribution.get)
        if structure and structure not in self.common_structures:
            self.common_structures.append(structure)
        if phrase and phrase not in self.favorite_phrases:
            self.favorite_phrases.append(phrase)
        self.last_updated = datetime.utcnow() 