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
from .services.rag_service import RAGService
from .tools.document_tools import DocumentTools
from .tools.search_tools import SearchTools
from .tools.memory_tools import MemoryTools
from .resources.document_resources import DocumentResources
from .resources.memory_resources import MemoryResources
from .validation import (
    validate_document_input, validate_search_input, validate_question_input,
    validate_memory_input, create_error_response, create_success_response,
    ValidationError
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
        self.rag_service: RAGService | None = None
        
        # Initialize tool and resource instances
        self.document_tools: DocumentTools | None = None
        self.search_tools: SearchTools | None = None
        self.memory_tools: MemoryTools | None = None
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
                        "rag": self.rag_service is not None
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
        async def ask_question(question: str, user_id: str = "default", use_memory: bool = True, max_context_docs: int = 3) -> dict:
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
            
            self.rag_service = RAGService(
                gemini_service=self.gemini_service,
                qdrant_service=self.qdrant_service,
                mem0_service=self.mem0_service
            )
            await self.rag_service.initialize()
            logger.info("RAG service initialized")
            
            # Initialize tools and resources
            self.document_tools = DocumentTools(self.rag_service)
            self.search_tools = SearchTools(self.rag_service)
            self.memory_tools = MemoryTools(self.mem0_service, self.rag_service)
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