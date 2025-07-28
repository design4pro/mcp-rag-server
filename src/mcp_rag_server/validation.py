"""
Validation schemas for MCP RAG Server.

This module contains Pydantic schemas for request/response validation
and data structure definitions.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

from .config import config


class DocumentRequest(BaseModel):
    """Schema for document addition requests."""
    
    content: str = Field(..., min_length=1, max_length=100000, description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Document metadata")
    user_id: str = Field(default=config.mem0.default_user_id, min_length=1, max_length=100, description="User ID for document ownership")
    
    class Config:
        extra = "ignore"


class SearchRequest(BaseModel):
    """Schema for search requests."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(default=5, ge=1, le=100, description="Maximum number of results")
    user_id: Optional[str] = Field(default=None, max_length=100, description="User ID for filtering results")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional search filters")
    
    class Config:
        extra = "ignore"


class MemoryRequest(BaseModel):
    """Schema for memory management requests."""
    
    content: str = Field(..., min_length=1, max_length=10000, description="Memory content")
    memory_type: str = Field(default="conversation", description="Type of memory")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Memory metadata")
    user_id: str = Field(default=config.mem0.default_user_id, min_length=1, max_length=100, description="User ID for memory ownership")
    session_id: Optional[str] = Field(default=None, max_length=100, description="Session ID for memory association")
    
    class Config:
        extra = "ignore"


class SessionCreationRequest(BaseModel):
    """Schema for session creation requests."""
    
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID for session")
    session_name: Optional[str] = Field(default=None, max_length=200, description="Optional session name")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Session metadata")
    
    class Config:
        extra = "ignore"


class SessionIdRequest(BaseModel):
    """Schema for session ID validation."""
    
    session_id: str = Field(..., min_length=1, max_length=100, description="Session ID")
    
    class Config:
        extra = "ignore"


class UserIdRequest(BaseModel):
    """Schema for user ID validation."""
    
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    
    class Config:
        extra = "ignore"


class QuestionRequest(BaseModel):
    """Schema for question asking requests."""
    
    question: str = Field(..., min_length=1, max_length=5000, description="Question to ask")
    user_id: str = Field(default=config.mem0.default_user_id, min_length=1, max_length=100, description="User ID")
    session_id: Optional[str] = Field(default=None, max_length=100, description="Session ID")
    use_memory: bool = Field(default=True, description="Whether to use memory context")
    max_context_docs: int = Field(default=3, ge=1, le=20, description="Maximum context documents")
    
    class Config:
        extra = "ignore"


class AdvancedSearchRequest(BaseModel):
    """Schema for advanced search requests."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    search_options: Optional[Dict[str, Any]] = Field(default=None, description="Advanced search options")
    user_id: str = Field(default=config.mem0.default_user_id, min_length=1, max_length=100, description="User ID")
    
    class Config:
        extra = "ignore"


class EnhancedContextRequest(BaseModel):
    """Schema for enhanced context requests."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Query for context")
    context_options: Optional[Dict[str, Any]] = Field(default=None, description="Context options")
    user_id: str = Field(default=config.mem0.default_user_id, min_length=1, max_length=100, description="User ID")
    
    class Config:
        extra = "ignore"


class MemoryPatternAnalysisRequest(BaseModel):
    """Schema for memory pattern analysis requests."""
    
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    time_range: Optional[str] = Field(default=None, max_length=100, description="Time range for analysis")
    
    class Config:
        extra = "ignore"


class MemoryClusteringRequest(BaseModel):
    """Schema for memory clustering requests."""
    
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    cluster_options: Optional[Dict[str, Any]] = Field(default=None, description="Clustering options")
    
    class Config:
        extra = "ignore"


class MemoryInsightsRequest(BaseModel):
    """Schema for memory insights requests."""
    
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    insight_type: str = Field(default="comprehensive", description="Type of insights to generate")
    
    class Config:
        extra = "ignore"


# Custom exception for validation errors
class ValidationError(Exception):
    """Custom validation error."""
    pass


# Response helper functions
def create_success_response(data: Any, operation: str) -> Dict[str, Any]:
    """Create a success response."""
    return {
        "success": True,
        "data": data,
        "operation": operation,
        "timestamp": datetime.now().isoformat()
    }


def create_error_response(error: Exception, operation: str) -> Dict[str, Any]:
    """Create an error response."""
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "operation": operation,
        "timestamp": datetime.now().isoformat()
    }


# Validation functions
def validate_document_input(data: Dict[str, Any]) -> DocumentRequest:
    """Validate document input data."""
    return DocumentRequest(**data)


def validate_search_input(data: Dict[str, Any]) -> SearchRequest:
    """Validate search input data."""
    return SearchRequest(**data)


def validate_question_input(data: Dict[str, Any]) -> QuestionRequest:
    """Validate question input data."""
    return QuestionRequest(**data)


def validate_memory_input(data: Dict[str, Any]) -> MemoryRequest:
    """Validate memory input data."""
    return MemoryRequest(**data)


def validate_session_creation(data: Dict[str, Any]) -> SessionCreationRequest:
    """Validate session creation data."""
    return SessionCreationRequest(**data)


def validate_session_id(data: Dict[str, Any]) -> SessionIdRequest:
    """Validate session ID data."""
    return SessionIdRequest(**data)


def validate_user_id(data: Dict[str, Any]) -> UserIdRequest:
    """Validate user ID data."""
    return UserIdRequest(**data)


def validate_advanced_search_input(data: Dict[str, Any]) -> AdvancedSearchRequest:
    """Validate advanced search input data."""
    return AdvancedSearchRequest(**data)


def validate_enhanced_context_input(data: Dict[str, Any]) -> EnhancedContextRequest:
    """Validate enhanced context input data."""
    return EnhancedContextRequest(**data)


def validate_memory_pattern_analysis_input(data: Dict[str, Any]) -> MemoryPatternAnalysisRequest:
    """Validate memory pattern analysis input data."""
    return MemoryPatternAnalysisRequest(**data)


def validate_memory_clustering_input(data: Dict[str, Any]) -> MemoryClusteringRequest:
    """Validate memory clustering input data."""
    return MemoryClusteringRequest(**data)


def validate_memory_insights_input(data: Dict[str, Any]) -> MemoryInsightsRequest:
    """Validate memory insights input data."""
    return MemoryInsightsRequest(**data) 