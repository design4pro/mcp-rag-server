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


class SessionCreationInput(BaseModel):
    """Validation schema for session creation input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    session_name: Optional[str] = Field(default=None, max_length=200)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()
    
    @validator('session_name')
    def validate_session_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Session name cannot be empty if provided")
        return v.strip() if v else None


class SessionIdInput(BaseModel):
    """Validation schema for session ID input."""
    session_id: str = Field(..., min_length=1, max_length=100)
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()


class UserIdInput(BaseModel):
    """Validation schema for user ID input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()


# Advanced Memory Context Retrieval Validation Schemas (Task 3)

class AdvancedSearchInput(BaseModel):
    """Validation schema for advanced memory search input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=1, max_length=1000)
    search_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()
    
    @validator('search_options')
    def validate_search_options(cls, v):
        if v is None:
            return {}
        
        # Validate search options
        valid_strategies = ["hierarchical", "semantic", "hybrid", "fuzzy"]
        valid_time_ranges = ["hour", "day", "week", "month"]
        
        if "search_strategy" in v and v["search_strategy"] not in valid_strategies:
            raise ValueError(f"Invalid search strategy. Must be one of: {valid_strategies}")
        
        if "time_range" in v and v["time_range"] not in valid_time_ranges:
            raise ValueError(f"Invalid time range. Must be one of: {valid_time_ranges}")
        
        if "limit" in v and (not isinstance(v["limit"], int) or v["limit"] < 1 or v["limit"] > 100):
            raise ValueError("Limit must be an integer between 1 and 100")
        
        if "min_confidence" in v and (not isinstance(v["min_confidence"], (int, float)) or v["min_confidence"] < 0 or v["min_confidence"] > 1):
            raise ValueError("Min confidence must be a number between 0 and 1")
        
        return v


class EnhancedContextInput(BaseModel):
    """Validation schema for enhanced memory context input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=1, max_length=1000)
    context_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
    
    @validator('context_options')
    def validate_context_options(cls, v):
        if v is None:
            return {}
        
        # Validate context options
        valid_summary_types = ["key_points", "narrative", "structured"]
        
        if "summary_type" in v and v["summary_type"] not in valid_summary_types:
            raise ValueError(f"Invalid summary type. Must be one of: {valid_summary_types}")
        
        if "limit" in v and (not isinstance(v["limit"], int) or v["limit"] < 1 or v["limit"] > 100):
            raise ValueError("Limit must be an integer between 1 and 100")
        
        if "min_confidence" in v and (not isinstance(v["min_confidence"], (int, float)) or v["min_confidence"] < 0 or v["min_confidence"] > 1):
            raise ValueError("Min confidence must be a number between 0 and 1")
        
        return v


class MemoryPatternAnalysisInput(BaseModel):
    """Validation schema for memory pattern analysis input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    time_range: Optional[str] = Field(default=None, max_length=20)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()
    
    @validator('time_range')
    def validate_time_range(cls, v):
        if v is not None:
            valid_ranges = ["hour", "day", "week", "month", "all"]
            if v not in valid_ranges:
                raise ValueError(f"Invalid time range. Must be one of: {valid_ranges}")
        return v


class MemoryClusteringInput(BaseModel):
    """Validation schema for memory clustering input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    cluster_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()
    
    @validator('cluster_options')
    def validate_cluster_options(cls, v):
        if v is None:
            return {}
        
        # Validate clustering options
        valid_cluster_types = ["topic", "temporal", "semantic"]
        
        if "cluster_type" in v and v["cluster_type"] not in valid_cluster_types:
            raise ValueError(f"Invalid cluster type. Must be one of: {valid_cluster_types}")
        
        if "max_clusters" in v and (not isinstance(v["max_clusters"], int) or v["max_clusters"] < 1 or v["max_clusters"] > 50):
            raise ValueError("Max clusters must be an integer between 1 and 50")
        
        if "similarity_threshold" in v and (not isinstance(v["similarity_threshold"], (int, float)) or v["similarity_threshold"] < 0 or v["similarity_threshold"] > 1):
            raise ValueError("Similarity threshold must be a number between 0 and 1")
        
        return v


class MemoryInsightsInput(BaseModel):
    """Validation schema for memory insights input."""
    user_id: str = Field(..., min_length=1, max_length=100)
    insight_type: str = Field(default="comprehensive", max_length=20)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()
    
    @validator('insight_type')
    def validate_insight_type(cls, v):
        valid_types = ["comprehensive", "engagement", "topics", "sessions"]
        if v not in valid_types:
            raise ValueError(f"Invalid insight type. Must be one of: {valid_types}")
        return v


# Validation functions for advanced features

def validate_advanced_search_input(data: Dict[str, Any]) -> AdvancedSearchInput:
    """Validate advanced search input data."""
    try:
        return AdvancedSearchInput(**data)
    except Exception as e:
        raise ValidationError(f"Invalid advanced search input: {str(e)}")


def validate_enhanced_context_input(data: Dict[str, Any]) -> EnhancedContextInput:
    """Validate enhanced context input data."""
    try:
        return EnhancedContextInput(**data)
    except Exception as e:
        raise ValidationError(f"Invalid enhanced context input: {str(e)}")


def validate_memory_pattern_analysis_input(data: Dict[str, Any]) -> MemoryPatternAnalysisInput:
    """Validate memory pattern analysis input data."""
    try:
        return MemoryPatternAnalysisInput(**data)
    except Exception as e:
        raise ValidationError(f"Invalid memory pattern analysis input: {str(e)}")


def validate_memory_clustering_input(data: Dict[str, Any]) -> MemoryClusteringInput:
    """Validate memory clustering input data."""
    try:
        return MemoryClusteringInput(**data)
    except Exception as e:
        raise ValidationError(f"Invalid memory clustering input: {str(e)}")


def validate_memory_insights_input(data: Dict[str, Any]) -> MemoryInsightsInput:
    """Validate memory insights input data."""
    try:
        return MemoryInsightsInput(**data)
    except Exception as e:
        raise ValidationError(f"Invalid memory insights input: {str(e)}")


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


def validate_session_creation(data: Dict[str, Any]) -> SessionCreationInput:
    """Validate session creation input data."""
    try:
        return SessionCreationInput(**data)
    except Exception as e:
        logger.error(f"Session creation validation failed: {e}")
        raise ValidationError(f"Invalid session creation input: {e}")


def validate_session_id(data: Dict[str, Any]) -> SessionIdInput:
    """Validate session ID input data."""
    try:
        return SessionIdInput(**data)
    except Exception as e:
        logger.error(f"Session ID validation failed: {e}")
        raise ValidationError(f"Invalid session ID input: {e}")


def validate_user_id(data: Dict[str, Any]) -> UserIdInput:
    """Validate user ID input data."""
    try:
        return UserIdInput(**data)
    except Exception as e:
        logger.error(f"User ID validation failed: {e}")
        raise ValidationError(f"Invalid user ID input: {e}")


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