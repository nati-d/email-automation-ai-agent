"""
Base Entity Class

Abstract base class for all domain entities.
"""

from abc import ABC
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid


class BaseEntity(ABC):
    """Base class for all domain entities with common attributes"""
    
    def __init__(self, id: Optional[str] = None, created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        """Initialize base entity fields"""
        self.id = id if id is not None else str(uuid.uuid4())
        self.created_at = created_at if created_at is not None else datetime.utcnow()
        self.updated_at = updated_at if updated_at is not None else datetime.utcnow()
    
    def mark_updated(self) -> None:
        """Mark entity as updated"""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other) -> bool:
        """Compare entities by ID"""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash entity by ID"""
        return hash(self.id) 