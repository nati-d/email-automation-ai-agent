"""
Domain Exceptions

Business-specific exceptions for domain logic.
"""

from typing import Optional, Dict, Any


class DomainException(Exception):
    """Base domain exception"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class DomainValidationError(DomainException):
    """Domain validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)
        self.field = field


class EntityNotFoundError(DomainException):
    """Entity not found error"""
    
    def __init__(self, entity_type: str, identifier: str, details: Optional[Dict[str, Any]] = None):
        message = f"{entity_type} with identifier '{identifier}' not found"
        super().__init__(message, code="ENTITY_NOT_FOUND", details=details)
        self.entity_type = entity_type
        self.identifier = identifier


class BusinessRuleViolationError(DomainException):
    """Business rule violation error"""
    
    def __init__(self, rule: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="BUSINESS_RULE_VIOLATION", details=details)
        self.rule = rule 