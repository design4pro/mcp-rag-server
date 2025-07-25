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
    
    api_key: str = Field(..., env="GEMINI_API_KEY", description="Gemini API key")
    model: str = Field(default="gemini-2.0-flash-exp", description="Gemini model to use")
    embedding_model: str = Field(default="text-embedding-004", description="Embedding model")
    max_tokens: int = Field(default=4096, description="Maximum tokens for generation")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    
    class Config:
        env_prefix = "GEMINI_"


class QdrantConfig(BaseSettings):
    """Configuration for Qdrant vector database."""
    
    url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    collection_name: str = Field(default="documents", env="COLLECTION_NAME")
    vector_size: int = Field(default=768, env="VECTOR_SIZE")
    distance_metric: str = Field(default="Cosine", description="Distance metric for vectors")
    
    class Config:
        env_prefix = "QDRANT_"


class Mem0Config(BaseSettings):
    """Configuration for Mem0 memory layer."""
    
    # Local storage path (fallback when mem0 package is not available)
    local_storage_path: str = Field(default="./mem0_data", env="MEM0_LOCAL_STORAGE_PATH")
    
    # Memory settings
    memory_size: int = Field(default=1000, description="Maximum memory entries per user")
    relevance_threshold: float = Field(default=0.7, description="Memory relevance threshold")
    max_tokens_per_memory: int = Field(default=1000, description="Maximum tokens per memory entry")
    
    class Config:
        env_prefix = "MEM0_"


class ServerConfig(BaseSettings):
    """Configuration for MCP server."""
    
    host: str = Field(default="localhost", env="MCP_SERVER_HOST")
    port: int = Field(default=8000, env="MCP_SERVER_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")
    
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