"""
Document management tools for MCP RAG Server.

This module provides tools for document ingestion, management, and retrieval.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentTools:
    """Document management tools for MCP RAG Server."""
    
    def __init__(self, rag_service):
        """Initialize document tools with RAG service."""
        self.rag_service = rag_service
    
    async def add_document(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """Add a document to the RAG system."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # Validate input
            if not content or not content.strip():
                return {"success": False, "error": "Document content cannot be empty"}
            
            # Add timestamp to metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "added_at": datetime.now().isoformat(),
                "user_id": user_id
            })
            
            result = await self.rag_service.add_document(content, doc_metadata, user_id)
            return {
                "success": True, 
                "document_id": result["id"],
                "chunks": result["chunks"],
                "metadata": result["metadata"]
            }
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_document(self, document_id: str, user_id: str = "default") -> Dict[str, Any]:
        """Delete a document from the RAG system."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            success = await self.rag_service.delete_document(document_id)
            return {"success": success, "document_id": document_id}
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a specific document by ID."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            document = await self.rag_service.get_document(document_id)
            if document:
                return {"success": True, "document": document}
            else:
                return {"success": False, "error": "Document not found"}
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_documents(
        self, 
        user_id: Optional[str] = None, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """List documents in the RAG system."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            documents = await self.rag_service.list_documents(user_id, limit)
            return {
                "success": True, 
                "documents": documents,
                "count": len(documents)
            }
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_document_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about documents in the system."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            stats = await self.rag_service.get_system_stats(user_id)
            return {"success": True, "stats": stats}
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {"success": False, "error": str(e)} 