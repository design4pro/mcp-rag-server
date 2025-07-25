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
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
    

    
    def _register_tools(self):
        """Register MCP tools."""
        # Basic health check tool
        @self.mcp.tool()
        def health_check() -> dict:
            """Check the health status of the RAG server."""
            return {
                "status": "healthy",
                "services": {
                    "gemini": self.gemini_service is not None,
                    "qdrant": self.qdrant_service is not None,
                    "mem0": self.mem0_service is not None,
                    "rag": self.rag_service is not None
                }
            }
        
        # Document management tools
        @self.mcp.tool()
        async def add_document(content: str, metadata: dict = None) -> dict:
            """Add a document to the RAG system."""
            if not self.rag_service:
                raise RuntimeError("RAG service not initialized")
            
            try:
                result = await self.rag_service.add_document(content, metadata or {})
                return {"success": True, "document_id": result["id"]}
            except Exception as e:
                logger.error(f"Error adding document: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def search_documents(query: str, limit: int = 5) -> dict:
            """Search for documents using semantic search."""
            if not self.rag_service:
                raise RuntimeError("RAG service not initialized")
            
            try:
                results = await self.rag_service.search_documents(query, limit)
                return {"success": True, "results": results}
            except Exception as e:
                logger.error(f"Error searching documents: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def ask_question(question: str, user_id: str = "default") -> dict:
            """Ask a question using RAG with memory context."""
            if not self.rag_service:
                raise RuntimeError("RAG service not initialized")
            
            try:
                response = await self.rag_service.ask_question(question, user_id)
                return {"success": True, "answer": response}
            except Exception as e:
                logger.error(f"Error asking question: {e}")
                return {"success": False, "error": str(e)}
    
    def _register_resources(self):
        """Register MCP resources."""
        @self.mcp.resource("rag://health")
        def get_health_status() -> dict:
            """Get the health status of the RAG server."""
            return {
                "status": "healthy",
                "version": "0.1.0",
                "services": {
                    "gemini": self.gemini_service is not None,
                    "qdrant": self.qdrant_service is not None,
                    "mem0": self.mem0_service is not None,
                    "rag": self.rag_service is not None
                }
            }
    
    async def initialize_services(self):
        """Initialize all services."""
        logger.info("Initializing MCP RAG Server services...")
        
        try:
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
            
            # Initialize RAG service
            self.rag_service = RAGService(
                gemini_service=self.gemini_service,
                qdrant_service=self.qdrant_service,
                mem0_service=self.mem0_service
            )
            await self.rag_service.initialize()
            logger.info("RAG service initialized")
            
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