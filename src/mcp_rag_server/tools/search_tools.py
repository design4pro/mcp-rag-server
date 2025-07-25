"""
Search and query tools for MCP RAG Server.

This module provides tools for searching documents and asking questions using RAG.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SearchTools:
    """Search and query tools for MCP RAG Server."""
    
    def __init__(self, rag_service):
        """Initialize search tools with RAG service."""
        self.rag_service = rag_service
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 5,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for documents using semantic search."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # Validate input
            if not query or not query.strip():
                return {"success": False, "error": "Search query cannot be empty"}
            
            if limit <= 0 or limit > 100:
                return {"success": False, "error": "Limit must be between 1 and 100"}
            
            results = await self.rag_service.search_documents(query, limit, user_id, filters)
            return {
                "success": True, 
                "results": results,
                "query": query,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {"success": False, "error": str(e)}
    
    async def ask_question(
        self, 
        question: str, 
        user_id: str = "default",
        session_id: Optional[str] = None,
        use_memory: bool = True,
        max_context_docs: int = 3
    ) -> Dict[str, Any]:
        """Ask a question using RAG with memory context."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # Validate input
            if not question or not question.strip():
                return {"success": False, "error": "Question cannot be empty"}
            
            if max_context_docs <= 0 or max_context_docs > 10:
                return {"success": False, "error": "max_context_docs must be between 1 and 10"}
            
            response = await self.rag_service.ask_question(
                question, 
                user_id, 
                session_id,
                use_memory, 
                max_context_docs
            )
            return {
                "success": True, 
                "answer": response,
                "question": question,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            return {"success": False, "error": str(e)}
    
    async def batch_search(
        self, 
        queries: List[str], 
        limit: int = 5,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform batch search for multiple queries."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # Validate input
            if not queries:
                return {"success": False, "error": "Queries list cannot be empty"}
            
            if len(queries) > 10:
                return {"success": False, "error": "Maximum 10 queries allowed per batch"}
            
            results = []
            for query in queries:
                if query and query.strip():
                    search_result = await self.rag_service.search_documents(
                        query, limit, user_id
                    )
                    results.append({
                        "query": query,
                        "results": search_result
                    })
            
            return {
                "success": True,
                "batch_results": results,
                "total_queries": len(queries),
                "successful_searches": len(results)
            }
        except Exception as e:
            logger.error(f"Error in batch search: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_search_suggestions(self, partial_query: str) -> Dict[str, Any]:
        """Get search suggestions based on partial query."""
        if not self.rag_service:
            raise RuntimeError("RAG service not initialized")
        
        try:
            # This is a placeholder for future implementation
            # Could be implemented using document titles, common queries, etc.
            suggestions = [
                f"{partial_query} documents",
                f"{partial_query} information",
                f"find {partial_query}",
                f"search {partial_query}"
            ]
            
            return {
                "success": True,
                "suggestions": suggestions,
                "partial_query": partial_query
            }
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return {"success": False, "error": str(e)} 