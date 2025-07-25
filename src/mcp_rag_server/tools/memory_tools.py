"""
Memory management tools for MCP RAG Server.

This module provides tools for managing conversation memory and user sessions.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryTools:
    """Memory management tools for MCP RAG Server."""
    
    def __init__(self, mem0_service, rag_service):
        """Initialize memory tools with mem0 and RAG services."""
        self.mem0_service = mem0_service
        self.rag_service = rag_service
    
    async def add_memory(
        self, 
        user_id: str, 
        content: str, 
        memory_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a memory entry for a user."""
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Validate input
            if not user_id or not content:
                return {"success": False, "error": "User ID and content are required"}
            
            # Add timestamp to metadata
            mem_metadata = metadata or {}
            mem_metadata.update({
                "added_at": datetime.now().isoformat(),
                "memory_type": memory_type
            })
            
            # Add to mem0
            memory_id = await self.mem0_service.add_memory(
                user_id, content, mem_metadata
            )
            
            return {
                "success": True,
                "memory_id": memory_id,
                "user_id": user_id,
                "memory_type": memory_type
            }
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_memories(
        self, 
        user_id: str, 
        limit: int = 10,
        memory_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get memories for a specific user."""
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            memories = await self.mem0_service.get_memories(
                user_id, limit, memory_type
            )
            return {
                "success": True,
                "memories": memories,
                "user_id": user_id,
                "count": len(memories)
            }
        except Exception as e:
            logger.error(f"Error getting user memories: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_memory(self, memory_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a specific memory entry."""
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            success = await self.mem0_service.delete_memory(memory_id, user_id)
            return {
                "success": success,
                "memory_id": memory_id,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return {"success": False, "error": str(e)}
    
    async def clear_user_memories(self, user_id: str) -> Dict[str, Any]:
        """Clear all memories for a user."""
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            success = await self.mem0_service.clear_memories(user_id)
            return {
                "success": success,
                "user_id": user_id,
                "action": "cleared_all_memories"
            }
        except Exception as e:
            logger.error(f"Error clearing user memories: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_memory_context(
        self, 
        user_id: str, 
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get relevant memory context for a query."""
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            context = await self.mem0_service.get_relevant_memories(
                user_id, query, limit
            )
            return {
                "success": True,
                "context": context,
                "user_id": user_id,
                "query": query,
                "count": len(context)
            }
        except Exception as e:
            logger.error(f"Error getting memory context: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_session_info(self, user_id: str) -> Dict[str, Any]:
        """Get information about a user's session and memory usage."""
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Get memory count
            memories = await self.mem0_service.get_memories(user_id, limit=1000)
            
            # Get document stats if RAG service is available
            doc_stats = None
            if self.rag_service:
                doc_stats = await self.rag_service.get_system_stats(user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "memory_count": len(memories),
                "document_stats": doc_stats,
                "session_active": True
            }
        except Exception as e:
            logger.error(f"Error getting user session info: {e}")
            return {"success": False, "error": str(e)} 