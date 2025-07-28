"""
Main MCP RAG Server implementation.

This module provides the main MCP server that integrates Qdrant, mem0, and Gemini API
for a complete RAG (Retrieval-Augmented Generation) solution.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions

from .config import config
from .services.gemini_service import GeminiService
from .services.qdrant_service import QdrantService
from .services.mem0_service import Mem0Service
from .services.session_service import SessionService
from .services.rag_service import RAGService
from .services.reasoning_service import AdvancedReasoningEngine, ReasoningConfig
from .services.context_service import EnhancedContextService, ContextConfig
from .services.prompts_service import PromptsService
from .services.code_analysis_service import CodeAnalysisService
from .tools.document_tools import DocumentTools
from .tools.search_tools import SearchTools
from .tools.memory_tools import MemoryTools
from .tools.session_tools import SessionTools
from .tools.ai_tools import AdvancedAITools
from .tools.code_analysis_tools import CodeAnalysisTools
from .tools.http_tools import HTTPIntegrationTools
from .tools.advanced_features import AdvancedFeatures, StreamType
from .resources.document_resources import DocumentResources
from .resources.memory_resources import MemoryResources
from .validation import (
    validate_document_input, validate_search_input, validate_question_input,
    validate_memory_input, create_error_response, create_success_response,
    ValidationError, validate_advanced_search_input, validate_enhanced_context_input,
    validate_memory_pattern_analysis_input, validate_memory_clustering_input,
    validate_memory_insights_input
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.server.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPRAGServer:
    """Main MCP RAG Server class."""
    
    def __init__(self):
        """Initialize the MCP RAG Server."""
        # Create FastMCP with port configuration
        self.mcp = FastMCP(
            "MCP RAG Server",
            host=config.server.host,
            port=config.server.port
        )
        self.gemini_service: GeminiService | None = None
        self.qdrant_service: QdrantService | None = None
        self.mem0_service: Mem0Service | None = None
        self.session_service: SessionService | None = None
        self.rag_service: RAGService | None = None
        self.reasoning_service: AdvancedReasoningEngine | None = None
        self.context_service: EnhancedContextService | None = None
        self.prompts_service: PromptsService | None = None
        self.code_analysis_service: CodeAnalysisService | None = None
        
        # Initialize tool and resource instances
        self.document_tools: DocumentTools | None = None
        self.search_tools: SearchTools | None = None
        self.memory_tools: MemoryTools | None = None
        self.session_tools: SessionTools | None = None
        self.ai_tools: AdvancedAITools | None = None
        self.code_analysis_tools: CodeAnalysisTools | None = None
        self.http_tools: HTTPIntegrationTools | None = None
        self.advanced_features: AdvancedFeatures | None = None
        self.document_resources: DocumentResources | None = None
        self.memory_resources: MemoryResources | None = None
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
        self._register_prompts()
        self._register_advanced_tools()
    
    def _register_tools(self):
        """Register MCP tools with proper validation and error handling."""
        
        # Health check tool
        @self.mcp.tool()
        def health_check() -> dict:
            """Check the health status of the RAG server."""
            try:
                return create_success_response({
                    "status": "healthy",
                    "services": {
                        "gemini": self.gemini_service is not None,
                        "qdrant": self.qdrant_service is not None,
                        "mem0": self.mem0_service is not None,
                        "session": self.session_service is not None,
                        "rag": self.rag_service is not None,
                        "reasoning": self.reasoning_service is not None,
                        "context": self.context_service is not None,
                        "prompts": self.prompts_service is not None,
                        "code_analysis": self.code_analysis_service is not None
                    }
                }, "health_check")
            except Exception as e:
                return create_error_response(e, "health_check")
        
        # Document management tools
        @self.mcp.tool()
        async def add_document(content: str, metadata: dict = None, user_id: str = None) -> dict:
            """Add a document to the RAG system."""
            try:
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                # Validate input
                validated_input = validate_document_input({
                    "content": content,
                    "metadata": metadata,
                    "user_id": effective_user_id
                })
                
                if not self.document_tools:
                    raise RuntimeError("Document tools not initialized")
                
                result = await self.document_tools.add_document(
                    validated_input.content,
                    validated_input.metadata,
                    validated_input.user_id
                )
                
                return result
            except ValidationError as e:
                return create_error_response(e, "add_document")
            except Exception as e:
                return create_error_response(e, "add_document")
        
        @self.mcp.tool()
        async def delete_document(document_id: str, user_id: str = None) -> dict:
            """Delete a document from the RAG system."""
            try:
                if not self.document_tools:
                    raise RuntimeError("Document tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.document_tools.delete_document(document_id, effective_user_id)
                return result
            except Exception as e:
                return create_error_response(e, "delete_document")
        
        @self.mcp.tool()
        async def get_document(document_id: str) -> dict:
            """Get a specific document by ID."""
            try:
                if not self.document_tools:
                    raise RuntimeError("Document tools not initialized")
                
                result = await self.document_tools.get_document(document_id)
                return result
            except Exception as e:
                return create_error_response(e, "get_document")
        
        @self.mcp.tool()
        async def list_documents(user_id: str = None, limit: int = 100) -> dict:
            """List documents in the RAG system."""
            try:
                if not self.document_tools:
                    raise RuntimeError("Document tools not initialized")
                
                result = await self.document_tools.list_documents(user_id, limit)
                return result
            except Exception as e:
                return create_error_response(e, "list_documents")
        
        @self.mcp.tool()
        async def get_document_stats(user_id: str = None) -> dict:
            """Get statistics about documents in the system."""
            try:
                if not self.document_tools:
                    raise RuntimeError("Document tools not initialized")
                
                result = await self.document_tools.get_document_stats(user_id)
                return result
            except Exception as e:
                return create_error_response(e, "get_document_stats")
        
        # Search and query tools
        @self.mcp.tool()
        async def search_documents(query: str, limit: int = 5, user_id: str = None, filters: dict = None) -> dict:
            """Search for documents using semantic search."""
            try:
                # Validate input
                validated_input = validate_search_input({
                    "query": query,
                    "limit": limit,
                    "user_id": user_id,
                    "filters": filters
                })
                
                if not self.search_tools:
                    raise RuntimeError("Search tools not initialized")
                
                result = await self.search_tools.search_documents(
                    validated_input.query,
                    validated_input.limit,
                    validated_input.user_id,
                    validated_input.filters
                )
                
                return result
            except ValidationError as e:
                return create_error_response(e, "search_documents")
            except Exception as e:
                return create_error_response(e, "search_documents")
        
        @self.mcp.tool()
        async def ask_question(question: str, user_id: str = None, session_id: str = None, use_memory: bool = True) -> dict:
            """Ask a question using RAG with optional memory context."""
            try:
                # Validate input (validation will use configured default user_id if user_id is None)
                validated_input = validate_question_input({
                    "question": question,
                    "user_id": user_id,
                    "session_id": session_id,
                    "use_memory": use_memory
                })
                
                if not self.search_tools:
                    raise RuntimeError("Search tools not initialized")
                
                result = await self.search_tools.ask_question(
                    validated_input.question,
                    validated_input.user_id,
                    validated_input.session_id,
                    validated_input.use_memory
                )
                
                return result
            except ValidationError as e:
                return create_error_response(e, "ask_question")
            except Exception as e:
                return create_error_response(e, "ask_question")
        
        # Memory management tools
        @self.mcp.tool()
        async def add_memory(content: str, memory_type: str = "conversation", user_id: str = None, session_id: str = None) -> dict:
            """Add a memory entry for a user."""
            try:
                # Validate input
                validated_input = validate_memory_input({
                    "content": content,
                    "memory_type": memory_type,
                    "user_id": user_id,
                    "session_id": session_id
                })
                
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.add_memory(
                    validated_input.content,
                    validated_input.memory_type,
                    validated_input.user_id,
                    validated_input.session_id
                )
                
                return result
            except ValidationError as e:
                return create_error_response(e, "add_memory")
            except Exception as e:
                return create_error_response(e, "add_memory")
        
        @self.mcp.tool()
        async def search_memories(query: str, user_id: str = None, limit: int = 5, memory_type: str = None) -> dict:
            """Search for relevant memories for a user."""
            try:
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.memory_tools.search_memories(
                    query, effective_user_id, limit, memory_type
                )
                
                return result
            except Exception as e:
                return create_error_response(e, "search_memories")
        
        @self.mcp.tool()
        async def get_user_memories(user_id: str = None, limit: int = 50, memory_type: str = None) -> dict:
            """Get all memories for a user."""
            try:
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.memory_tools.get_user_memories(
                    effective_user_id, limit, memory_type
                )
                
                return result
            except Exception as e:
                return create_error_response(e, "get_user_memories")
        
        # Session management tools
        @self.mcp.tool()
        async def create_session(user_id: str = None, session_name: str = None) -> dict:
            """Create a new session for a user."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.session_tools.create_session(effective_user_id, session_name)
                return result
            except Exception as e:
                return create_error_response(e, "create_session")
        
        @self.mcp.tool()
        async def get_session(session_id: str) -> dict:
            """Get session information."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                result = await self.session_tools.get_session(session_id)
                return result
            except Exception as e:
                return create_error_response(e, "get_session")
        
        @self.mcp.tool()
        async def list_sessions(user_id: str = None, limit: int = 10) -> dict:
            """List sessions for a user."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.session_tools.list_sessions(effective_user_id, limit)
                return result
            except Exception as e:
                return create_error_response(e, "list_sessions")
        
        @self.mcp.tool()
        async def delete_session(session_id: str) -> dict:
            """Delete a session."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                result = await self.session_tools.delete_session(session_id)
                return result
            except Exception as e:
                return create_error_response(e, "delete_session")
        
        # Advanced AI tools
        @self.mcp.tool()
        async def advanced_reasoning(query: str, reasoning_type: str = "auto", context: dict = None) -> dict:
            """Perform advanced reasoning on a query."""
            try:
                if not self.ai_tools:
                    raise RuntimeError("AI tools not initialized")
                
                result = await self.ai_tools.advanced_reasoning(
                    query, reasoning_type, context
                )
                
                return result
            except Exception as e:
                return create_error_response(e, "advanced_reasoning")
        
        @self.mcp.tool()
        async def context_analysis(query: str, user_id: str = None, additional_context: dict = None) -> dict:
            """Analyze context for a given query."""
            try:
                if not self.ai_tools:
                    raise RuntimeError("AI tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.ai_tools.context_analysis(
                    query, effective_user_id, additional_context
                )
                
                return result
            except Exception as e:
                return create_error_response(e, "context_analysis")
        
        # Code Analysis Tools
        @self.mcp.tool()
        async def analyze_source_code(file_path: str, language: str = "auto") -> dict:
            """Analyze source code file and extract structural information."""
            try:
                if not self.code_analysis_tools:
                    return create_error_response("Code analysis tools not initialized", "analyze_source_code")
                
                result = await self.code_analysis_tools.handle_analyze_source_code({
                    "file_path": file_path,
                    "language": language
                })
                return create_success_response({"content": result.content[0].text}, "analyze_source_code")
            except Exception as e:
                logger.error(f"Error in analyze_source_code: {e}")
                return create_error_response(str(e), "analyze_source_code")
        
        @self.mcp.tool()
        async def analyze_code_string(code: str, language: str) -> dict:
            """Analyze code string and extract structural information."""
            try:
                if not self.code_analysis_tools:
                    return create_error_response("Code analysis tools not initialized", "analyze_code_string")
                
                result = await self.code_analysis_tools.handle_analyze_code_string({
                    "code": code,
                    "language": "python"
                })
                return create_success_response({"content": result.content[0].text}, "analyze_code_string")
            except Exception as e:
                logger.error(f"Error in analyze_code_string: {e}")
                return create_error_response(str(e), "analyze_code_string")
        
        @self.mcp.tool()
        async def calculate_code_metrics(file_path: str, language: str = "auto") -> dict:
            """Calculate comprehensive code metrics including complexity and quality indicators."""
            try:
                if not self.code_analysis_tools:
                    return create_error_response("Code analysis tools not initialized", "calculate_code_metrics")
                
                result = await self.code_analysis_tools.handle_calculate_code_metrics({
                    "file_path": file_path,
                    "language": language
                })
                return create_success_response({"content": result.content[0].text}, "calculate_code_metrics")
            except Exception as e:
                logger.error(f"Error in calculate_code_metrics: {e}")
                return create_error_response(str(e), "calculate_code_metrics")
        
        @self.mcp.tool()
        async def extract_functions(file_path: str, language: str = "auto") -> dict:
            """Extract function definitions and their metadata from source code."""
            try:
                if not self.code_analysis_tools:
                    return create_error_response("Code analysis tools not initialized", "extract_functions")
                
                result = await self.code_analysis_tools.handle_extract_functions({
                    "file_path": file_path,
                    "language": language
                })
                return create_success_response({"content": result.content[0].text}, "extract_functions")
            except Exception as e:
                logger.error(f"Error in extract_functions: {e}")
                return create_error_response(str(e), "extract_functions")
        
        @self.mcp.tool()
        async def extract_classes(file_path: str, language: str = "auto") -> dict:
            """Extract class definitions and their relationships from source code."""
            try:
                if not self.code_analysis_tools:
                    return create_error_response("Code analysis tools not initialized", "extract_classes")
                
                result = await self.code_analysis_tools.handle_extract_classes({
                    "file_path": file_path,
                    "language": language
                })
                return create_success_response({"content": result.content[0].text}, "extract_classes")
            except Exception as e:
                logger.error(f"Error in extract_classes: {e}")
                return create_error_response(str(e), "extract_classes")
        
        @self.mcp.tool()
        async def analyze_dependencies(file_path: str, language: str = "auto") -> dict:
            """Analyze import statements and dependencies in source code."""
            try:
                if not self.code_analysis_tools:
                    return create_error_response("Code analysis tools not initialized", "analyze_dependencies")
                
                result = await self.code_analysis_tools.handle_analyze_dependencies({
                    "file_path": file_path,
                    "language": language
                })
                return create_success_response({"content": result.content[0].text}, "analyze_dependencies")
            except Exception as e:
                logger.error(f"Error in analyze_dependencies: {e}")
                return create_error_response(str(e), "analyze_dependencies")
        
        @self.mcp.tool()
        async def detect_code_patterns(file_path: str, language: str = "auto") -> dict:
            """Detect common coding patterns and anti-patterns in source code."""
            try:
                if not self.code_analysis_tools:
                    return create_error_response("Code analysis tools not initialized", "detect_code_patterns")
                
                result = await self.code_analysis_tools.handle_detect_code_patterns({
                    "file_path": file_path,
                    "language": language
                })
                return create_success_response({"content": result.content[0].text}, "detect_code_patterns")
            except Exception as e:
                logger.error(f"Error in detect_code_patterns: {e}")
                return create_error_response(str(e), "detect_code_patterns")
    
    def _register_advanced_tools(self):
        """Register advanced MCP tools including HTTP integration and streaming."""
        
        # HTTP Integration Tools
        @self.mcp.tool()
        async def fetch_web_content(url: str, user_id: str = None, auto_add_to_rag: bool = True) -> dict:
            """Fetch content from URL and optionally add to RAG system."""
            try:
                if not self.http_tools:
                    raise RuntimeError("HTTP tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.http_tools.fetch_web_content(url, effective_user_id, auto_add_to_rag)
                return result
            except Exception as e:
                return create_error_response(e, "fetch_web_content")
        
        @self.mcp.tool()
        async def call_external_api(endpoint: str, method: str = "GET", data: dict = None, headers: dict = None, user_id: str = None) -> dict:
            """Call external API and optionally process response."""
            try:
                if not self.http_tools:
                    raise RuntimeError("HTTP tools not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.http_tools.call_external_api(endpoint, method, data, headers, effective_user_id)
                return result
            except Exception as e:
                return create_error_response(e, "call_external_api")
        
        @self.mcp.tool()
        async def batch_fetch_urls(urls: list, user_id: str = "default", max_concurrent: int = 5) -> dict:
            """Fetch content from multiple URLs in parallel."""
            try:
                if not self.http_tools:
                    raise RuntimeError("HTTP tools not initialized")
                
                result = await self.http_tools.batch_fetch_urls(urls, user_id, max_concurrent)
                return result
            except Exception as e:
                return create_error_response(e, "batch_fetch_urls")
        
        # Advanced Features - Batch Processing
        @self.mcp.tool()
        async def batch_add_documents(documents: list, user_id: str = None, batch_size: int = 10, parallel_processing: bool = True) -> dict:
            """Add multiple documents to RAG system in batch."""
            try:
                if not self.advanced_features:
                    raise RuntimeError("Advanced features not initialized")
                
                # Use configured default user_id if none provided
                effective_user_id = user_id or config.mem0.default_user_id
                
                result = await self.advanced_features.batch_add_documents(documents, effective_user_id, batch_size, parallel_processing)
                return result
            except Exception as e:
                return create_error_response(e, "batch_add_documents")
        
        @self.mcp.tool()
        async def batch_process_memories(memories: list, user_id: str = "default", batch_size: int = 20, memory_type: str = "conversation") -> dict:
            """Process multiple memories in batch."""
            try:
                if not self.advanced_features:
                    raise RuntimeError("Advanced features not initialized")
                
                result = await self.advanced_features.batch_process_memories(memories, user_id, batch_size, memory_type)
                return result
            except Exception as e:
                return create_error_response(e, "batch_process_memories")
        
        # Advanced Features - Streaming
        @self.mcp.tool()
        async def start_streaming(stream_type: str, user_id: str = "default", session_id: str = None, callback_url: str = None) -> dict:
            """Start real-time streaming for specified type."""
            try:
                if not self.advanced_features:
                    raise RuntimeError("Advanced features not initialized")
                
                # Convert string to StreamType enum
                try:
                    stream_type_enum = StreamType(stream_type)
                except ValueError:
                    return create_error_response(ValueError(f"Invalid stream type: {stream_type}"), "start_streaming")
                
                result = await self.advanced_features.start_streaming(stream_type_enum, user_id, session_id, callback_url)
                return result
            except Exception as e:
                return create_error_response(e, "start_streaming")
        
        @self.mcp.tool()
        async def stop_streaming(stream_id: str) -> dict:
            """Stop streaming for specified stream ID."""
            try:
                if not self.advanced_features:
                    raise RuntimeError("Advanced features not initialized")
                
                result = await self.advanced_features.stop_streaming(stream_id)
                return result
            except Exception as e:
                return create_error_response(e, "stop_streaming")
        
        @self.mcp.tool()
        async def get_stream_status(stream_id: str) -> dict:
            """Get status of streaming for specified stream ID."""
            try:
                if not self.advanced_features:
                    raise RuntimeError("Advanced features not initialized")
                
                result = await self.advanced_features.get_stream_status(stream_id)
                return result
            except Exception as e:
                return create_error_response(e, "get_stream_status")
        
        @self.mcp.tool()
        async def list_active_streams(user_id: str = None) -> dict:
            """List all active streams."""
            try:
                if not self.advanced_features:
                    raise RuntimeError("Advanced features not initialized")
                
                result = await self.advanced_features.list_active_streams(user_id)
                return result
            except Exception as e:
                return create_error_response(e, "list_active_streams")
    
    def _register_resources(self):
        """Register MCP resources."""
        @self.mcp.resource("rag://health")
        def get_health_status() -> dict:
            """Get the health status of the RAG server."""
            return {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "gemini": self.gemini_service is not None,
                    "qdrant": self.qdrant_service is not None,
                    "mem0": self.mem0_service is not None,
                    "session": self.session_service is not None,
                    "rag": self.rag_service is not None,
                    "reasoning": self.reasoning_service is not None,
                    "context": self.context_service is not None,
                    "prompts": self.prompts_service is not None
                }
            }
        
        @self.mcp.resource("rag://stats")
        def get_server_stats() -> dict:
            """Get server statistics."""
            return {
                "version": "1.0.0",
                "uptime": "running",
                "features": [
                    "document_management",
                    "semantic_search",
                    "memory_management",
                    "session_management",
                    "advanced_reasoning",
                    "context_analysis",
                    "mcp_prompts"
                ]
            }
    
    def _register_prompts(self):
        """Register MCP prompts functionality."""
        try:
            # Initialize prompts service
            self.prompts_service = PromptsService()
            
            # Register prompts using FastMCP @mcp.prompt() decorator
            @self.mcp.prompt()
            def ask_about_topic(topic: str) -> str:
                """Generates a user message asking for an explanation of a topic."""
                return f"Can you please explain the concept of '{topic}'?"
            
            @self.mcp.prompt()
            def generate_code_request(language: str, task_description: str) -> str:
                """Generates a user message requesting code generation."""
                return f"Write a {language} function that performs the following task: {task_description}"
            
            @self.mcp.prompt()
            def data_analysis_prompt(
                data_uri: str,
                analysis_type: str = "summary",
                include_charts: bool = False
            ) -> str:
                """Creates a request to analyze data with specific parameters."""
                prompt = f"Please perform a '{analysis_type}' analysis on the data found at {data_uri}."
                if include_charts:
                    prompt += " Include relevant charts and visualizations."
                return prompt
            
            @self.mcp.prompt()
            def document_search_prompt(query: str, limit: int = 5) -> str:
                """Generates a prompt for searching documents."""
                return f"Search for documents related to: '{query}'. Return up to {limit} relevant results."
            
            @self.mcp.prompt()
            def memory_context_prompt(user_id: str, query: str) -> str:
                """Generates a prompt for retrieving memory context."""
                return f"Retrieve relevant memories for user '{user_id}' related to: '{query}'"
            
            @self.mcp.prompt()
            def code_analysis_prompt(file_path: str, analysis_type: str = "comprehensive") -> str:
                """Generates a prompt for code analysis."""
                return f"Perform a {analysis_type} analysis of the code in file: {file_path}"
            
            logger.info("Prompts functionality initialized successfully with FastMCP")
                    
        except Exception as e:
            logger.warning(f"Prompts functionality not available: {e}")
            logger.info("Prompts functionality not supported in current MCP version")
    
    async def initialize(self):
        """Initialize all services."""
        await self._initialize_services()
    
    async def initialize_services(self):
        """Alias for initialize() for backward compatibility."""
        await self.initialize()
    
    async def _initialize_services(self):
        """Initialize all services."""
        try:
            logger.info("Initializing MCP RAG Server...")
            
            # Initialize Gemini service
            self.gemini_service = GeminiService(config.gemini)
            await self.gemini_service.initialize()
            logger.info("Gemini service initialized")
            
            # Initialize Qdrant service
            self.qdrant_service = QdrantService(config.qdrant)
            await self.qdrant_service.initialize()
            logger.info("Qdrant service initialized")
            
            # Initialize Mem0 service
            self.mem0_service = Mem0Service(config.mem0)
            await self.mem0_service.initialize()
            logger.info("Mem0 service initialized")
            
            # Initialize Session service
            self.session_service = SessionService(config.session)
            await self.session_service.initialize()
            logger.info("Session service initialized")
            
            # Initialize RAG service
            self.rag_service = RAGService(
                self.gemini_service,
                self.qdrant_service,
                self.mem0_service,
                self.session_service
            )
            await self.rag_service.initialize()
            logger.info("RAG service initialized")
            
            # Initialize Reasoning service
            reasoning_config = ReasoningConfig()
            self.reasoning_service = AdvancedReasoningEngine(reasoning_config)
            logger.info("Reasoning service initialized")
            
            # Initialize Context service
            context_config = ContextConfig()
            self.context_service = EnhancedContextService(context_config)
            logger.info("Context service initialized")
            
            # Initialize Prompts service
            self.prompts_service = PromptsService()
            logger.info("Prompts service initialized")
            
            # Initialize Code Analysis service
            self.code_analysis_service = CodeAnalysisService()
            logger.info("Code Analysis service initialized")
            
            # Initialize tool instances
            self.document_tools = DocumentTools(self.rag_service)
            self.search_tools = SearchTools(self.rag_service)
            self.memory_tools = MemoryTools(self.mem0_service, self.rag_service)
            self.session_tools = SessionTools(self.session_service)
            self.ai_tools = AdvancedAITools(
                self.reasoning_service,
                self.context_service
            )
            self.code_analysis_tools = CodeAnalysisTools(self.code_analysis_service)
            
            # Initialize advanced tools
            from .services.document_processor import DocumentProcessor
            document_processor = DocumentProcessor()
            self.http_tools = HTTPIntegrationTools(self.rag_service, document_processor)
            self.advanced_features = AdvancedFeatures(
                self.rag_service,
                self.mem0_service,
                self.session_service
            )
            
            # Initialize resource instances
            self.document_resources = DocumentResources(self.rag_service)
            self.memory_resources = MemoryResources(self.mem0_service)
            
            logger.info("MCP RAG Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MCP RAG Server: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup all services."""
        await self._cleanup_services()
    
    async def cleanup_services(self):
        """Alias for cleanup() for backward compatibility."""
        await self.cleanup()
    
    async def _cleanup_services(self):
        """Cleanup resources."""
        try:
            if self.gemini_service:
                await self.gemini_service.cleanup()
            if self.qdrant_service:
                await self.qdrant_service.cleanup()
            if self.mem0_service:
                await self.mem0_service.cleanup()
            if self.session_service:
                await self.session_service.cleanup()
            
            # Cleanup advanced tools
            if self.http_tools:
                await self.http_tools.cleanup()
            if self.advanced_features:
                await self.advanced_features.cleanup()
            
            logger.info("MCP RAG Server cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        """Manage server lifespan."""
        try:
            await self.initialize()
            yield
        finally:
            await self.cleanup()
    
    async def run(self):
        """Run the MCP server."""
        try:
            async with self.lifespan():
                await self.mcp.run()
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise


async def main():
    """Main entry point."""
    server = MCPRAGServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())