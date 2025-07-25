"""
Mem0 memory service for conversation context management.

This service handles memory management for personalized AI interactions
using the mem0 memory layer.
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..config import Mem0Config

logger = logging.getLogger(__name__)


class Mem0Service:
    """Service for managing conversation memory with mem0."""
    
    def __init__(self, config: Mem0Config):
        """Initialize the mem0 service."""
        self.config = config
        self.memory = None
        self._initialized = False
        self.local_storage = {}
        self.storage_path = Path(config.local_storage_path)
    
    async def initialize(self):
        """Initialize the mem0 memory layer."""
        try:
            # Try to use mem0 package first (open source version)
            try:
                from mem0 import Memory
                # Open source mem0 doesn't require API key
                self.memory = Memory()
                self._initialized = True
                logger.info("Mem0 service initialized with open source package")
                return
            except ImportError:
                logger.warning("mem0 package not available, using local storage")
            
            # Fallback to local storage
            await self._initialize_local_storage()
                    
        except Exception as e:
            logger.error(f"Error initializing mem0 service: {e}")
            # Fallback to local storage
            await self._initialize_local_storage()
    
    async def _initialize_local_storage(self):
        """Initialize local file-based storage."""
        try:
            # Create storage directory if it doesn't exist
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing data
            await self._load_local_storage()
            
            self._initialized = True
            logger.info(f"Local storage initialized at {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Error initializing local storage: {e}")
            raise
    
    async def _load_local_storage(self):
        """Load data from local storage files."""
        try:
            # Load user memories
            memories_file = self.storage_path / "memories.json"
            if memories_file.exists():
                with open(memories_file, 'r', encoding='utf-8') as f:
                    self.local_storage = json.load(f)
            else:
                self.local_storage = {"memories": {}, "stats": {}}
                
        except Exception as e:
            logger.error(f"Error loading local storage: {e}")
            self.local_storage = {"memories": {}, "stats": {}}
    
    async def _save_local_storage(self):
        """Save data to local storage files."""
        try:
            memories_file = self.storage_path / "memories.json"
            with open(memories_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_storage, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving local storage: {e}")
            raise
    
    async def add_memory(
        self, 
        user_id: str, 
        content: str, 
        memory_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a memory entry for a user."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if self.memory:
                # Use mem0 package (open source)
                result = self.memory.add(
                    user_id=user_id,
                    memory=content,
                    memory_type=memory_type,
                    metadata=metadata or {}
                )
                memory_id = result.get("id", str(datetime.now().timestamp()))
            else:
                # Local storage
                memory_id = str(datetime.now().timestamp())
                
                # Initialize user memories if not exists
                if user_id not in self.local_storage["memories"]:
                    self.local_storage["memories"][user_id] = []
                
                # Create memory entry
                memory_entry = {
                    "id": memory_id,
                    "memory": content,
                    "memory_type": memory_type,
                    "metadata": metadata or {},
                    "created_at": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
                # Add to local storage
                self.local_storage["memories"][user_id].append(memory_entry)
                
                # Limit memory size
                if len(self.local_storage["memories"][user_id]) > self.config.memory_size:
                    self.local_storage["memories"][user_id] = self.local_storage["memories"][user_id][-self.config.memory_size:]
                
                # Save to disk
                await self._save_local_storage()
                
                logger.debug(f"Added local memory for user {user_id}: {content[:50]}...")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            raise
    
    async def search_memories(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories for a user."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if self.memory:
                # Use mem0 package (open source)
                result = self.memory.search(
                    query=query,
                    user_id=user_id,
                    limit=limit,
                    memory_type=memory_type
                )
                return result.get("results", [])
            else:
                # Local storage search
                if user_id not in self.local_storage["memories"]:
                    return []
                
                memories = self.local_storage["memories"][user_id]
                
                # Simple keyword-based search (can be improved with embeddings)
                relevant_memories = []
                query_lower = query.lower()
                
                for memory in memories:
                    if memory_type and memory.get("memory_type") != memory_type:
                        continue
                    
                    # Simple relevance scoring based on keyword matching
                    memory_text = memory.get("memory", "").lower()
                    relevance_score = 0
                    
                    # Count matching words
                    query_words = query_lower.split()
                    for word in query_words:
                        if word in memory_text:
                            relevance_score += 1
                    
                    if relevance_score > 0:
                        relevant_memories.append({
                            **memory,
                            "relevance": relevance_score / len(query_words)
                        })
                
                # Sort by relevance and limit results
                relevant_memories.sort(key=lambda x: x["relevance"], reverse=True)
                relevant_memories = relevant_memories[:limit]
                
                logger.debug(f"Local memory search for user {user_id}: {query[:50]}... (found {len(relevant_memories)} results)")
                return relevant_memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def get_user_memories(
        self, 
        user_id: str, 
        limit: int = 50,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all memories for a user."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if self.memory:
                # Use mem0 package (open source)
                result = self.memory.list(
                    user_id=user_id,
                    limit=limit,
                    memory_type=memory_type
                )
                return result.get("memories", [])
            else:
                # Local storage
                if user_id not in self.local_storage["memories"]:
                    return []
                
                memories = self.local_storage["memories"][user_id]
                
                # Filter by memory type if specified
                if memory_type:
                    memories = [m for m in memories if m.get("memory_type") == memory_type]
                
                # Limit results
                memories = memories[-limit:] if limit > 0 else memories
                
                logger.debug(f"Local memory list for user {user_id}: {len(memories)} memories")
                return memories
            
        except Exception as e:
            logger.error(f"Error getting user memories: {e}")
            return []
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific memory entry."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if self.memory and not self.config.self_hosted:
                # Use mem0 API
                self.memory.delete(memory_id=memory_id, user_id=user_id)
                logger.info(f"Deleted memory {memory_id} for user {user_id}")
            else:
                # Local storage
                if user_id in self.local_storage["memories"]:
                    memories = self.local_storage["memories"][user_id]
                    # Remove memory by ID
                    self.local_storage["memories"][user_id] = [
                        m for m in memories if m.get("id") != memory_id
                    ]
                    await self._save_local_storage()
                    logger.debug(f"Local memory deletion for user {user_id}, memory {memory_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False
    
    async def clear_user_memories(self, user_id: str, memory_type: Optional[str] = None) -> bool:
        """Clear all memories for a user."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if self.memory:
                # Use mem0 API
                self.memory.clear(user_id=user_id, memory_type=memory_type)
                logger.info(f"Cleared memories for user {user_id}")
            else:
                # Local fallback
                logger.debug(f"Local memory clear for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing user memories: {e}")
            return False
    
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if self.memory:
                # Use mem0 API
                stats = self.memory.stats(user_id=user_id)
                return stats
            else:
                # Local fallback
                return {
                    "user_id": user_id,
                    "total_memories": 0,
                    "memory_types": {},
                    "last_updated": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "total_memories": 0
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up mem0 service")
        # No specific cleanup needed for mem0
        pass