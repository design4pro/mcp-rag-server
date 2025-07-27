"""
Configuration management for MCP RAG Server.

This module handles all configuration settings using Pydantic Settings
for type safety and environment variable support.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class GeminiConfig(BaseSettings):
    """Configuration for Gemini API integration."""
    
    api_key: str = Field(..., env="MCP_GEMINI_API_KEY", description="Gemini API key")
    model: str = Field(default="gemini-2.0-flash-exp", description="Gemini model to use")
    embedding_model: str = Field(default="text-embedding-004", description="Embedding model")
    max_tokens: int = Field(default=4096, description="Maximum tokens for generation")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    
    class Config:
        env_prefix = "MCP_GEMINI_"


class QdrantConfig(BaseSettings):
    """Configuration for Qdrant vector database."""
    
    url: str = Field(default="http://localhost:6333", env="MCP_QDRANT_URL")
    collection_name: str = Field(default="documents", env="MCP_COLLECTION_NAME")
    collection_prefix: str = Field(default="", env="MCP_COLLECTION", description="Prefix for collection names to support multi-project isolation")
    vector_size: int = Field(default=768, env="MCP_VECTOR_SIZE")
    distance_metric: str = Field(default="Cosine", description="Distance metric for vectors")
    
    class Config:
        env_prefix = "MCP_QDRANT_"


class Mem0Config(BaseSettings):
    """Configuration for Mem0 memory layer."""
    
    # Local storage path (fallback when mem0 package is not available)
    local_storage_path: str = Field(default="./data/mem0_data", env="MCP_MEM0_STORAGE_PATH")
    
    # Project isolation settings
    project_namespace: str = Field(default="", env="MCP_PROJECT_NAMESPACE", description="Namespace for project isolation in memory storage")
    default_user_id: str = Field(default="default", env="MCP_USER_ID", description="Default user ID for the project")
    
    # Memory settings
    memory_size: int = Field(default=1000, description="Maximum memory entries per user")
    relevance_threshold: float = Field(default=0.7, description="Memory relevance threshold")
    max_tokens_per_memory: int = Field(default=1000, description="Maximum tokens per memory entry")
    
    # Memory search settings
    use_semantic_search: bool = Field(default=True, description="Use semantic search for memories")
    semantic_search_weight: float = Field(default=0.7, description="Weight for semantic search in hybrid scoring")
    keyword_search_weight: float = Field(default=0.3, description="Weight for keyword search in hybrid scoring")
    recency_weight: float = Field(default=0.1, description="Weight for recency in relevance scoring")
    max_memory_context_length: int = Field(default=2000, description="Maximum memory context length in tokens")
    enable_memory_summarization: bool = Field(default=True, description="Enable memory summarization for long contexts")
    
    class Config:
        env_prefix = "MCP_MEM0_"


class ServerConfig(BaseSettings):
    """Configuration for MCP server."""
    
    host: str = Field(default="localhost", env="MCP_SERVER_HOST")
    port: int = Field(default=8000, env="MCP_SERVER_PORT")
    log_level: str = Field(default="INFO", env="MCP_LOG_LEVEL")
    debug: bool = Field(default=False, env="MCP_DEBUG")
    
    # Session management settings
    session_timeout_hours: int = Field(default=24, description="Session timeout in hours")
    max_sessions_per_user: int = Field(default=10, description="Maximum sessions per user")
    session_cleanup_interval_minutes: int = Field(default=5, description="Session cleanup interval in minutes")
    enable_session_tracking: bool = Field(default=True, description="Enable session tracking")
    
    class Config:
        env_prefix = "MCP_"


class Config(BaseSettings):
    """Main configuration class combining all settings."""
    
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    mem0: Mem0Config = Field(default_factory=Mem0Config)
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global configuration instance
config = Config()