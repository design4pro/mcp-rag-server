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
    
    class Config:
        extra = "ignore" 