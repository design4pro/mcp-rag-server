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
from .tools.document_tools import DocumentTools
from .tools.search_tools import SearchTools
from .tools.memory_tools import MemoryTools
from .tools.session_tools import SessionTools
from .tools.ai_tools import AdvancedAITools
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
        # Create FastMCP without lifespan
        self.mcp = FastMCP("MCP RAG Server")
        self.gemini_service: GeminiService | None = None
        self.qdrant_service: QdrantService | None = None
        self.mem0_service: Mem0Service | None = None
        self.session_service: SessionService | None = None
        self.rag_service: RAGService | None = None
        self.reasoning_service: AdvancedReasoningEngine | None = None
        self.context_service: EnhancedContextService | None = None
        
        # Initialize tool and resource instances
        self.document_tools: DocumentTools | None = None
        self.search_tools: SearchTools | None = None
        self.memory_tools: MemoryTools | None = None
        self.session_tools: SessionTools | None = None
        self.ai_tools: AdvancedAITools | None = None
        self.document_resources: DocumentResources | None = None
        self.memory_resources: MemoryResources | None = None
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
    
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
                        "context": self.context_service is not None
                    }
                }, "health_check")
            except Exception as e:
                return create_error_response(e, "health_check")
        
        # Document management tools
        @self.mcp.tool()
        async def add_document(content: str, metadata: dict = None, user_id: str = "default") -> dict:
            """Add a document to the RAG system."""
            try:
                # Validate input
                validated_input = validate_document_input({
                    "content": content,
                    "metadata": metadata,
                    "user_id": user_id
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
        async def delete_document(document_id: str, user_id: str = "default") -> dict:
            """Delete a document from the RAG system."""
            try:
                if not self.document_tools:
                    raise RuntimeError("Document tools not initialized")
                
                result = await self.document_tools.delete_document(document_id, user_id)
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
        async def ask_question(question: str, user_id: str = "default", session_id: str = None, use_memory: bool = True, max_context_docs: int = 3) -> dict:
            """Ask a question using RAG with memory context."""
            try:
                # Validate input
                validated_input = validate_question_input({
                    "question": question,
                    "user_id": user_id,
                    "use_memory": use_memory,
                    "max_context_docs": max_context_docs
                })
                
                if not self.search_tools:
                    raise RuntimeError("Search tools not initialized")
                
                result = await self.search_tools.ask_question(
                    validated_input.question,
                    validated_input.user_id,
                    session_id,
                    validated_input.use_memory,
                    validated_input.max_context_docs
                )
                
                return result
            except ValidationError as e:
                return create_error_response(e, "ask_question")
            except Exception as e:
                return create_error_response(e, "ask_question")
        
        @self.mcp.tool()
        async def batch_search(queries: list, limit: int = 5, user_id: str = None) -> dict:
            """Perform batch search for multiple queries."""
            try:
                if not self.search_tools:
                    raise RuntimeError("Search tools not initialized")
                
                result = await self.search_tools.batch_search(queries, limit, user_id)
                return result
            except Exception as e:
                return create_error_response(e, "batch_search")
        
        @self.mcp.tool()
        async def get_search_suggestions(partial_query: str) -> dict:
            """Get search suggestions based on partial query."""
            try:
                if not self.search_tools:
                    raise RuntimeError("Search tools not initialized")
                
                result = await self.search_tools.get_search_suggestions(partial_query)
                return result
            except Exception as e:
                return create_error_response(e, "get_search_suggestions")
        
        # Memory management tools
        @self.mcp.tool()
        async def add_memory(user_id: str, content: str, memory_type: str = "conversation", metadata: dict = None) -> dict:
            """Add a memory entry for a user."""
            try:
                # Validate input
                validated_input = validate_memory_input({
                    "user_id": user_id,
                    "content": content,
                    "memory_type": memory_type,
                    "metadata": metadata
                })
                
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.add_memory(
                    validated_input.user_id,
                    validated_input.content,
                    validated_input.memory_type,
                    validated_input.metadata
                )
                
                return result
            except ValidationError as e:
                return create_error_response(e, "add_memory")
            except Exception as e:
                return create_error_response(e, "add_memory")
        
        @self.mcp.tool()
        async def get_user_memories(user_id: str, limit: int = 10, memory_type: str = None) -> dict:
            """Get memories for a specific user."""
            try:
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.get_user_memories(user_id, limit, memory_type)
                return result
            except Exception as e:
                return create_error_response(e, "get_user_memories")
        
        @self.mcp.tool()
        async def delete_memory(memory_id: str, user_id: str) -> dict:
            """Delete a specific memory entry."""
            try:
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.delete_memory(memory_id, user_id)
                return result
            except Exception as e:
                return create_error_response(e, "delete_memory")
        
        @self.mcp.tool()
        async def clear_user_memories(user_id: str) -> dict:
            """Clear all memories for a user."""
            try:
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.clear_user_memories(user_id)
                return result
            except Exception as e:
                return create_error_response(e, "clear_user_memories")
        
        @self.mcp.tool()
        async def get_memory_context(user_id: str, query: str, limit: int = 5) -> dict:
            """Get relevant memory context for a query."""
            try:
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.get_memory_context(user_id, query, limit)
                return result
            except Exception as e:
                return create_error_response(e, "get_memory_context")
        
        @self.mcp.tool()
        async def get_user_session_info(user_id: str) -> dict:
            """Get information about a user's session and memory usage."""
            try:
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.get_user_session_info(user_id)
                return result
            except Exception as e:
                return create_error_response(e, "get_user_session_info")

        # Advanced Memory Context Retrieval Tools (Task 3)
        
        @self.mcp.tool()
        async def search_memories_advanced(user_id: str, query: str, search_options: dict = None) -> dict:
            """Advanced memory search with enhanced relevance scoring and filtering."""
            try:
                # Validate input
                validated_input = validate_advanced_search_input({
                    "user_id": user_id,
                    "query": query,
                    "search_options": search_options
                })
                
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.search_memories_advanced(
                    validated_input.user_id,
                    validated_input.query,
                    validated_input.search_options
                )
                return result
            except Exception as e:
                return create_error_response(e, "search_memories_advanced")
        
        @self.mcp.tool()
        async def get_enhanced_memory_context(user_id: str, query: str, context_options: dict = None) -> dict:
            """Get enhanced memory context with advanced processing and summarization."""
            try:
                # Validate input
                validated_input = validate_enhanced_context_input({
                    "user_id": user_id,
                    "query": query,
                    "context_options": context_options
                })
                
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.get_enhanced_memory_context(
                    validated_input.user_id,
                    validated_input.query,
                    validated_input.context_options
                )
                return result
            except Exception as e:
                return create_error_response(e, "get_enhanced_memory_context")
        
        @self.mcp.tool()
        async def analyze_memory_patterns(user_id: str, time_range: str = None) -> dict:
            """Analyze memory patterns for a user."""
            try:
                # Validate input
                validated_input = validate_memory_pattern_analysis_input({
                    "user_id": user_id,
                    "time_range": time_range
                })
                
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.analyze_memory_patterns(
                    validated_input.user_id,
                    validated_input.time_range
                )
                return result
            except Exception as e:
                return create_error_response(e, "analyze_memory_patterns")
        
        @self.mcp.tool()
        async def cluster_user_memories(user_id: str, cluster_options: dict = None) -> dict:
            """Cluster user memories for better organization and analysis."""
            try:
                # Validate input
                validated_input = validate_memory_clustering_input({
                    "user_id": user_id,
                    "cluster_options": cluster_options
                })
                
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.cluster_user_memories(
                    validated_input.user_id,
                    validated_input.cluster_options
                )
                return result
            except Exception as e:
                return create_error_response(e, "cluster_user_memories")
        
        @self.mcp.tool()
        async def get_memory_insights(user_id: str, insight_type: str = "comprehensive") -> dict:
            """Get comprehensive memory insights for a user."""
            try:
                # Validate input
                validated_input = validate_memory_insights_input({
                    "user_id": user_id,
                    "insight_type": insight_type
                })
                
                if not self.memory_tools:
                    raise RuntimeError("Memory tools not initialized")
                
                result = await self.memory_tools.get_memory_insights(
                    validated_input.user_id,
                    validated_input.insight_type
                )
                return result
            except Exception as e:
                return create_error_response(e, "get_memory_insights")
        
        # Session management tools
        @self.mcp.tool()
        async def create_session(user_id: str, session_name: str = None, metadata: dict = None) -> dict:
            """Create a new session for a user."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                return await self.session_tools.create_session(user_id, session_name, metadata)
            except Exception as e:
                return create_error_response(e, "create_session")
        
        @self.mcp.tool()
        async def get_session_info(session_id: str) -> dict:
            """Get information about a specific session."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                return await self.session_tools.get_session_info(session_id)
            except Exception as e:
                return create_error_response(e, "get_session_info")
        
        @self.mcp.tool()
        async def list_user_sessions(user_id: str, include_expired: bool = False) -> dict:
            """List all sessions for a user."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                return await self.session_tools.list_user_sessions(user_id, include_expired)
            except Exception as e:
                return create_error_response(e, "list_user_sessions")
        
        @self.mcp.tool()
        async def expire_session(session_id: str) -> dict:
            """Manually expire a session."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                return await self.session_tools.expire_session(session_id)
            except Exception as e:
                return create_error_response(e, "expire_session")
        
        @self.mcp.tool()
        async def get_session_stats(session_id: str) -> dict:
            """Get statistics for a specific session."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                return await self.session_tools.get_session_stats(session_id)
            except Exception as e:
                return create_error_response(e, "get_session_stats")
        
        @self.mcp.tool()
        async def get_system_session_stats() -> dict:
            """Get overall system session statistics."""
            try:
                if not self.session_tools:
                    raise RuntimeError("Session tools not initialized")
                
                return await self.session_tools.get_system_session_stats()
            except Exception as e:
                return create_error_response(e, "get_system_session_stats")
        
        # Advanced AI Tools
        @self.mcp.tool()
        async def advanced_reasoning(query: str, context: dict = None, user_id: str = "default") -> dict:
            """Perform advanced reasoning on a query."""
            try:
                if not self.ai_tools:
                    return create_error_response("AI tools not initialized", "advanced_reasoning")
                
                result = await self.ai_tools.advanced_reasoning(query, context, user_id)
                return create_success_response(result, "advanced_reasoning")
            except Exception as e:
                return create_error_response(e, "advanced_reasoning")
        
        @self.mcp.tool()
        async def chain_of_thought_reasoning(query: str, context: dict = None, max_steps: int = None, user_id: str = "default") -> dict:
            """Perform chain-of-thought reasoning on a query."""
            try:
                if not self.ai_tools:
                    return create_error_response("AI tools not initialized", "chain_of_thought_reasoning")
                
                result = await self.ai_tools.chain_of_thought_reasoning(query, context, max_steps, user_id)
                return create_success_response(result, "chain_of_thought_reasoning")
            except Exception as e:
                return create_error_response(e, "chain_of_thought_reasoning")
        
        @self.mcp.tool()
        async def multi_hop_reasoning(query: str, context: dict = None, max_hops: int = 3, user_id: str = "default") -> dict:
            """Perform multi-hop reasoning on a query."""
            try:
                if not self.ai_tools:
                    return create_error_response("AI tools not initialized", "multi_hop_reasoning")
                
                result = await self.ai_tools.multi_hop_reasoning(query, context, max_hops, user_id)
                return create_success_response(result, "multi_hop_reasoning")
            except Exception as e:
                return create_error_response(e, "multi_hop_reasoning")
        
        @self.mcp.tool()
        async def analyze_context(query: str, additional_context: dict = None, user_id: str = "default") -> dict:
            """Analyze context for a query."""
            try:
                if not self.ai_tools:
                    return create_error_response("AI tools not initialized", "analyze_context")
                
                result = await self.ai_tools.analyze_context(query, additional_context, user_id)
                return create_success_response(result, "analyze_context")
            except Exception as e:
                return create_error_response(e, "analyze_context")
        
        @self.mcp.tool()
        async def extract_relevant_context(query: str, context: dict, relevance_threshold: float = 0.5, user_id: str = "default") -> dict:
            """Extract context relevant to a query."""
            try:
                if not self.ai_tools:
                    return create_error_response("AI tools not initialized", "extract_relevant_context")
                
                result = await self.ai_tools.extract_relevant_context(query, context, relevance_threshold, user_id)
                return create_success_response(result, "extract_relevant_context")
            except Exception as e:
                return create_error_response(e, "extract_relevant_context")
        
        @self.mcp.tool()
        async def contextual_question_answering(question: str, context: dict, user_id: str = "default") -> dict:
            """Answer a question using contextual understanding."""
            try:
                if not self.ai_tools:
                    return create_error_response("AI tools not initialized", "contextual_question_answering")
                
                result = await self.ai_tools.contextual_question_answering(question, context, user_id)
                return create_success_response(result, "contextual_question_answering")
            except Exception as e:
                return create_error_response(e, "contextual_question_answering")
        
        @self.mcp.tool()
        async def advanced_query_understanding(query: str, context: dict = None, user_id: str = "default") -> dict:
            """Perform advanced query understanding."""
            try:
                if not self.ai_tools:
                    return create_error_response("AI tools not initialized", "advanced_query_understanding")
                
                result = await self.ai_tools.advanced_query_understanding(query, context, user_id)
                return create_success_response(result, "advanced_query_understanding")
            except Exception as e:
                return create_error_response(e, "advanced_query_understanding")
    
    def _register_resources(self):
        """Register MCP resources."""
        
        @self.mcp.resource("rag://health")
        def get_health_status() -> dict:
            """Get the health status of the RAG server."""
            try:
                return {
                    "status": "healthy",
                    "version": "0.1.0",
                    "services": {
                        "gemini": self.gemini_service is not None,
                        "qdrant": self.qdrant_service is not None,
                        "mem0": self.mem0_service is not None,
                        "session": self.session_service is not None,
                        "rag": self.rag_service is not None
                    },
                    "timestamp": asyncio.get_event_loop().time()
                }
            except Exception as e:
                return create_error_response(e, "health_status")
        
        @self.mcp.resource("rag://documents/{document_id}")
        def get_document_resource(document_id: str) -> dict:
            """Get document resource by ID."""
            try:
                if not self.document_resources:
                    raise RuntimeError("Document resources not initialized")
                
                return self.document_resources.get_document_metadata(document_id)
            except Exception as e:
                return create_error_response(e, "document_resource")
        
        @self.mcp.resource("rag://documents/{document_id}/content")
        def get_document_content(document_id: str) -> dict:
            """Get document content by ID."""
            try:
                if not self.document_resources:
                    raise RuntimeError("Document resources not initialized")
                
                return self.document_resources.get_document_content(document_id)
            except Exception as e:
                return create_error_response(e, "document_content")
        
        @self.mcp.resource("rag://documents/{document_id}/chunks")
        def get_document_chunks(document_id: str) -> dict:
            """Get document chunks by ID."""
            try:
                if not self.document_resources:
                    raise RuntimeError("Document resources not initialized")
                
                return self.document_resources.get_document_chunks(document_id)
            except Exception as e:
                return create_error_response(e, "document_chunks")
        
        @self.mcp.resource("rag://search/{query}/{limit}")
        def get_search_results(query: str, limit: int = 5) -> dict:
            """Get search results for a query."""
            try:
                if not self.document_resources:
                    raise RuntimeError("Document resources not initialized")
                
                return self.document_resources.get_document_search_results(query, limit)
            except Exception as e:
                return create_error_response(e, "search_results")
        
        @self.mcp.resource("rag://statistics/{user_id}")
        def get_statistics(user_id: str = None) -> dict:
            """Get system statistics."""
            try:
                if not self.document_resources:
                    raise RuntimeError("Document resources not initialized")
                
                return self.document_resources.get_document_statistics(user_id)
            except Exception as e:
                return create_error_response(e, "statistics")
        
        @self.mcp.resource("rag://memories/{user_id}/{limit}")
        def get_user_memories_resource(user_id: str, limit: int = 10) -> dict:
            """Get user memories resource."""
            try:
                if not self.memory_resources:
                    raise RuntimeError("Memory resources not initialized")
                
                return self.memory_resources.get_user_memories(user_id, limit)
            except Exception as e:
                return create_error_response(e, "user_memories_resource")
        
        @self.mcp.resource("rag://memories/{user_id}/context/{query}")
        def get_memory_context_resource(user_id: str, query: str) -> dict:
            """Get memory context resource."""
            try:
                if not self.memory_resources:
                    raise RuntimeError("Memory resources not initialized")
                
                return self.memory_resources.get_memory_context(user_id, query)
            except Exception as e:
                return create_error_response(e, "memory_context_resource")
        
        @self.mcp.resource("rag://memories/{user_id}/statistics")
        def get_memory_statistics_resource(user_id: str) -> dict:
            """Get memory statistics resource."""
            try:
                if not self.memory_resources:
                    raise RuntimeError("Memory resources not initialized")
                
                return self.memory_resources.get_memory_statistics(user_id)
            except Exception as e:
                return create_error_response(e, "memory_statistics_resource")
        
        @self.mcp.resource("rag://session/{user_id}")
        def get_session_info_resource(user_id: str) -> dict:
            """Get session information resource."""
            try:
                if not self.memory_resources:
                    raise RuntimeError("Memory resources not initialized")
                
                return self.memory_resources.get_session_info(user_id)
            except Exception as e:
                return create_error_response(e, "session_info_resource")
    
    async def initialize_services(self):
        """Initialize all services and tools."""
        logger.info("Initializing MCP RAG Server services...")
        
        try:
            # Initialize core services
            self.gemini_service = GeminiService(config.gemini)
            await self.gemini_service.initialize()
            logger.info("Gemini service initialized")
            
            self.qdrant_service = QdrantService(config.qdrant)
            await self.qdrant_service.initialize()
            logger.info("Qdrant service initialized")
            
            self.mem0_service = Mem0Service(config.mem0)
            await self.mem0_service.initialize()
            logger.info("Mem0 service initialized")
            
            self.session_service = SessionService(config.server)
            await self.session_service.initialize()
            logger.info("Session service initialized")
            
            self.rag_service = RAGService(
                gemini_service=self.gemini_service,
                qdrant_service=self.qdrant_service,
                mem0_service=self.mem0_service,
                session_service=self.session_service
            )
            await self.rag_service.initialize()
            logger.info("RAG service initialized")
            
            # Initialize AI services
            reasoning_config = ReasoningConfig()
            self.reasoning_service = AdvancedReasoningEngine(reasoning_config)
            logger.info("Advanced reasoning service initialized")
            
            context_config = ContextConfig()
            self.context_service = EnhancedContextService(context_config)
            logger.info("Enhanced context service initialized")
            
            # Initialize tools and resources
            self.document_tools = DocumentTools(self.rag_service)
            self.search_tools = SearchTools(self.rag_service)
            self.memory_tools = MemoryTools(self.mem0_service, self.rag_service)
            self.session_tools = SessionTools(self.session_service)
            self.ai_tools = AdvancedAITools(self.reasoning_service, self.context_service)
            self.document_resources = DocumentResources(self.rag_service)
            self.memory_resources = MemoryResources(self.mem0_service)
            
            logger.info("All tools and resources initialized")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    async def cleanup_services(self):
        """Cleanup all services."""
        logger.info("Cleaning up MCP RAG Server services...")
        
        if self.rag_service:
            await self.rag_service.cleanup()
        if self.session_service:
            await self.session_service.cleanup()
        if self.mem0_service:
            await self.mem0_service.cleanup()
        if self.qdrant_service:
            await self.qdrant_service.cleanup()
        if self.gemini_service:
            await self.gemini_service.cleanup()
    
    def get_server(self) -> FastMCP:
        """Get the FastMCP server instance."""
        return self.mcp


def main():
    """Main entry point for the MCP RAG Server."""
    server = MCPRAGServer()
    
    # Initialize services
    asyncio.run(server.initialize_services())
    
    # Get the FastMCP server
    mcp_server = server.get_server()
    
    # Run the server using stdio (for MCP protocol)
    logger.info("Starting MCP RAG Server...")
    try:
        mcp_server.run(transport="stdio")
    finally:
        asyncio.run(server.cleanup_services())


if __name__ == "__main__":
    main()