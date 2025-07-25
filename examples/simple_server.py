#!/usr/bin/env python3
"""
Simple HTTP server for testing RAG functionality.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the src directory to the path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_rag_server.config import config
from mcp_rag_server.services.gemini_service import GeminiService
from mcp_rag_server.services.qdrant_service import QdrantService
from mcp_rag_server.services.mem0_service import Mem0Service
from mcp_rag_server.services.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.server.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RAGServer:
    """Simple RAG server for testing."""
    
    def __init__(self):
        """Initialize the RAG server."""
        self.gemini_service: GeminiService | None = None
        self.qdrant_service: QdrantService | None = None
        self.mem0_service: Mem0Service | None = None
        self.rag_service: RAGService | None = None
    
    async def initialize_services(self):
        """Initialize all services."""
        logger.info("Initializing RAG Server services...")
        
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
        logger.info("Cleaning up RAG Server services...")
        
        if self.rag_service:
            await self.rag_service.cleanup()
        if self.mem0_service:
            await self.mem0_service.cleanup()
        if self.qdrant_service:
            await self.qdrant_service.cleanup()
        if self.gemini_service:
            await self.gemini_service.cleanup()


# Global server instance
rag_server = RAGServer()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan."""
    await rag_server.initialize_services()
    try:
        yield
    finally:
        await rag_server.cleanup_services()


# Create FastAPI app
app = FastAPI(
    title="RAG Server",
    description="Simple RAG server for testing",
    version="0.1.0",
    lifespan=lifespan
)


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    services: dict[str, bool]


class AddDocumentRequest(BaseModel):
    content: str
    metadata: dict = {}


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class AskQuestionRequest(BaseModel):
    question: str
    user_id: str = "default"


class Response(BaseModel):
    success: bool
    data: dict = {}
    error: str = ""


# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health status of the RAG server."""
    return {
        "status": "healthy",
        "services": {
            "gemini": rag_server.gemini_service is not None,
            "qdrant": rag_server.qdrant_service is not None,
            "mem0": rag_server.mem0_service is not None,
            "rag": rag_server.rag_service is not None
        }
    }


@app.post("/add_document", response_model=Response)
async def add_document(request: AddDocumentRequest):
    """Add a document to the RAG system."""
    if not rag_server.rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        result = await rag_server.rag_service.add_document(request.content, request.metadata)
        return Response(success=True, data={"document_id": result["id"]})
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return Response(success=False, error=str(e))


@app.post("/search", response_model=Response)
async def search_documents(request: SearchRequest):
    """Search for documents using semantic search."""
    if not rag_server.rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        results = await rag_server.rag_service.search_documents(request.query, request.limit)
        return Response(success=True, data={"results": results})
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return Response(success=False, error=str(e))


@app.post("/ask", response_model=Response)
async def ask_question(request: AskQuestionRequest):
    """Ask a question using RAG."""
    if not rag_server.rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        response = await rag_server.rag_service.ask_question(request.question, request.user_id)
        return Response(success=True, data={"answer": response})
    except Exception as e:
        logger.error(f"Error asking question: {e}")
        return Response(success=False, error=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Server is running",
        "endpoints": {
            "health": "/health",
            "add_document": "/add_document",
            "search": "/search",
            "ask": "/ask"
        }
    }


def main():
    """Main entry point."""
    uvicorn.run(
        app,
        host=config.server.host,
        port=8001,
        log_level=config.server.log_level.lower()
    )


if __name__ == "__main__":
    main()