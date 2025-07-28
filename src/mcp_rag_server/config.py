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
    
    api_key: str = Field(..., description="Gemini API key")
    model: str = Field(default="gemini-2.0-flash-exp", description="Gemini model to use")
    embedding_model: str = Field(default="text-embedding-004", description="Embedding model")
    max_tokens: int = Field(default=4096, description="Maximum tokens for generation")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    
    class Config:
        env_prefix = "MCP_GEMINI_"


class QdrantConfig(BaseSettings):
    """Configuration for Qdrant vector database."""
    
    url: str = Field(default="http://localhost:6333")
    collection_name: str = Field(default="documents")
    collection_prefix: str = Field(default="", description="Prefix for collection names to support multi-project isolation")
    vector_size: int = Field(default=768)
    distance_metric: str = Field(default="Cosine", description="Distance metric for vectors")
    
    class Config:
        env_prefix = "MCP_QDRANT_"


class Mem0Config(BaseSettings):
    """Configuration for Mem0 memory layer."""
    
    # Local storage path (fallback when mem0 package is not available)
    local_storage_path: str = Field(default="./data/mem0_data")
    
    # Project isolation settings
    project_namespace: str = Field(default="", description="Namespace for project isolation in memory storage")
    default_user_id: str = Field(default="default", description="Default user ID for the project")
    
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


class SessionConfig(BaseSettings):
    """Configuration for session management."""
    
    timeout_hours: int = Field(default=24, description="Session timeout in hours")
    max_sessions_per_user: int = Field(default=10, description="Maximum sessions per user")
    cleanup_interval_minutes: int = Field(default=5, description="Session cleanup interval in minutes")
    enable_tracking: bool = Field(default=True, description="Enable session tracking")
    
    class Config:
        env_prefix = "MCP_SESSION_"


class PromptsConfig(BaseSettings):
    """Configuration for MCP Prompts functionality."""
    
    # Enable/disable prompts functionality
    enabled: bool = Field(default=True, description="Enable MCP prompts functionality")
    
    # Prompt management settings
    max_prompts_per_user: int = Field(default=50, description="Maximum custom prompts per user")
    max_prompt_length: int = Field(default=10000, description="Maximum prompt content length")
    enable_custom_prompts: bool = Field(default=True, description="Allow users to create custom prompts")
    
    # Code analysis settings
    enable_code_analysis: bool = Field(default=True, description="Enable code analysis in prompts")
    supported_languages: list = Field(default=["python", "javascript", "java", "rust", "go", "typescript"], 
                                    description="Supported programming languages for analysis")
    max_code_size: int = Field(default=50000, description="Maximum code size for analysis (characters)")
    
    # Prompt templates
    default_templates: list = Field(default=[
        "code_review",
        "code_analysis", 
        "architecture_review",
        "security_audit",
        "performance_analysis",
        "documentation_generation",
        "test_generation",
        "refactoring_suggestions"
    ], description="Default prompt templates to include")
    
    class Config:
        env_prefix = "MCP_PROMPTS_"


class HTTPIntegrationConfig(BaseSettings):
    """Configuration for HTTP integration features."""
    
    # HTTP client settings
    timeout_seconds: int = Field(default=30, description="HTTP request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum HTTP retries")
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent HTTP requests")
    
    # Content processing settings
    auto_add_to_rag: bool = Field(default=True, description="Automatically add fetched content to RAG")
    extract_metadata: bool = Field(default=True, description="Extract metadata from HTTP responses")
    max_content_size: int = Field(default=10485760, description="Maximum content size in bytes (10MB)")
    
    # User agent and headers
    user_agent: str = Field(default="MCP-RAG-Server/1.0", description="HTTP User-Agent string")
    
    class Config:
        env_prefix = "MCP_HTTP_"


class AdvancedFeaturesConfig(BaseSettings):
    """Configuration for advanced features."""
    
    # Batch processing settings
    default_batch_size: int = Field(default=10, description="Default batch size for processing")
    max_batch_size: int = Field(default=100, description="Maximum batch size")
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    
    # Streaming settings
    enable_streaming: bool = Field(default=True, description="Enable real-time streaming")
    stream_heartbeat_interval: int = Field(default=30, description="Stream heartbeat interval in seconds")
    max_active_streams: int = Field(default=50, description="Maximum active streams per user")
    
    # Webhook settings
    enable_webhooks: bool = Field(default=True, description="Enable webhook callbacks")
    webhook_timeout: int = Field(default=10, description="Webhook timeout in seconds")
    max_webhook_retries: int = Field(default=3, description="Maximum webhook retries")
    
    class Config:
        env_prefix = "MCP_ADVANCED_"


class ServerConfig(BaseSettings):
    """Configuration for MCP server."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=8000)
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)
    
    class Config:
        env_prefix = "MCP_"


class Config(BaseSettings):
    """Main configuration class combining all settings."""
    
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    mem0: Mem0Config = Field(default_factory=Mem0Config)
    session: SessionConfig = Field(default_factory=SessionConfig)
    prompts: PromptsConfig = Field(default_factory=PromptsConfig)
    http_integration: HTTPIntegrationConfig = Field(default_factory=HTTPIntegrationConfig)
    advanced_features: AdvancedFeaturesConfig = Field(default_factory=AdvancedFeaturesConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global configuration instance with error handling
def get_config() -> Config:
    """Get configuration with proper error handling."""
    try:
        return Config()
    except Exception as e:
        import os
        import sys
        
        # Print helpful error message
        print(f"Configuration error: {e}")
        print("Environment variables:")
        for key, value in os.environ.items():
            if key.startswith('MCP_'):
                print(f"  {key}: {value[:10]}..." if len(value) > 10 else f"  {key}: {value}")
        
        print("\nPlease check your .env file and ensure MCP_GEMINI_API_KEY is set.")
        sys.exit(1)

config = get_config()