"""
Email Address Value Object

Immutable email address with validation.
"""

from dataclasses import dataclass
from typing import ClassVar
import re

from ..exceptions.domain_exceptions import DomainValidationError


@dataclass(frozen=True)
class EmailAddress:
    """Email address value object with validation"""
    
    value: str
    
    # Email validation regex pattern
    EMAIL_PATTERN: ClassVar[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __post_init__(self):
        """Validate email address format"""
        if not self.value:
            raise DomainValidationError("Email address cannot be empty")
        
        if not re.match(self.EMAIL_PATTERN, self.value):
            raise DomainValidationError(f"Invalid email address format: {self.value}")
        
        if len(self.value) > 254:  # RFC 5321 limit
            raise DomainValidationError("Email address too long")
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Representation"""
        return f"EmailAddress('{self.value}')"
    
    @property
    def local_part(self) -> str:
        """Get local part (before @)"""
        return self.value.split('@')[0]
    
    @property
    def domain_part(self) -> str:
        """Get domain part (after @)"""
        return self.value.split('@')[1]
    
    def is_same_domain(self, other: 'EmailAddress') -> bool:
        """Check if two email addresses have the same domain"""
        return self.domain_part.lower() == other.domain_part.lower()
    
    @classmethod
    def create(cls, email: str) -> 'EmailAddress':
        """Factory method to create email address"""
        return cls(email.strip().lower()) 