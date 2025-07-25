"""
Validation and error handling for MCP RAG Server.

This module provides validation schemas and error handling utilities.
"""

import logging
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class DocumentInput(BaseModel):
    """Validation schema for document input."""
    content: str = Field(..., min_length=1, max_length=1000000)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_id: str = Field(default="default", min_length=1, max_length=100)
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Document content cannot be empty")
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()


class SearchInput(BaseModel):
    """Validation schema for search input."""
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=100)
    user_id: Optional[str] = Field(default=None, max_length=100)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()


class QuestionInput(BaseModel):
    """Validation schema for question input."""
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str = Field(default="default", min_length=1, max_length=100)
    use_memory: bool = Field(default=True)
    max_context_docs: int = Field(default=3, ge=1, le=10)
    
    @validator('question')
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class MemoryInput(BaseModel):
    """Validation schema for memory input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=10000)
    memory_type: str = Field(default="conversation", max_length=50)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Memory content cannot be empty")
        return v.strip()


def validate_document_input(data: Dict[str, Any]) -> DocumentInput:
    """Validate document input data."""
    try:
        return DocumentInput(**data)
    except Exception as e:
        logger.error(f"Document input validation failed: {e}")
        raise ValidationError(f"Invalid document input: {e}")


def validate_search_input(data: Dict[str, Any]) -> SearchInput:
    """Validate search input data."""
    try:
        return SearchInput(**data)
    except Exception as e:
        logger.error(f"Search input validation failed: {e}")
        raise ValidationError(f"Invalid search input: {e}")


def validate_question_input(data: Dict[str, Any]) -> QuestionInput:
    """Validate question input data."""
    try:
        return QuestionInput(**data)
    except Exception as e:
        logger.error(f"Question input validation failed: {e}")
        raise ValidationError(f"Invalid question input: {e}")


def validate_memory_input(data: Dict[str, Any]) -> MemoryInput:
    """Validate memory input data."""
    try:
        return MemoryInput(**data)
    except Exception as e:
        logger.error(f"Memory input validation failed: {e}")
        raise ValidationError(f"Invalid memory input: {e}")


def create_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """Create a standardized error response."""
    error_type = type(error).__name__
    error_message = str(error)
    
    response = {
        "success": False,
        "error": {
            "type": error_type,
            "message": error_message,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    logger.error(f"Error in {context}: {error_type}: {error_message}")
    return response


def create_success_response(data: Any, context: str = "") -> Dict[str, Any]:
    """Create a standardized success response."""
    response = {
        "success": True,
        "data": data,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"Success in {context}")
    return response 