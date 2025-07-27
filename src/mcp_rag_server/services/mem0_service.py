"""
Mem0 memory service for conversation context management.

This service handles memory management for personalized AI interactions
using the mem0 memory layer.
"""

import logging
import json
import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
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
        self.storage_path = self._get_storage_path()
    
    def _get_storage_path(self) -> Path:
        """Get storage path with project namespace for isolation."""
        base_path = Path(self.config.local_storage_path)
        if self.config.project_namespace:
            return base_path / self.config.project_namespace
        return base_path
    
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
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        session_id: Optional[str] = None
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
                
                # Add session_id if provided
                if session_id:
                    memory_entry["session_id"] = session_id
                
                # Add embedding if provided
                if embedding:
                    memory_entry["embedding"] = embedding
                
                # Add to local storage
                self.local_storage["memories"][user_id].append(memory_entry)
                
                # Limit memory size
                if len(self.local_storage["memories"][user_id]) > self.config.memory_size:
                    self.local_storage["memories"][user_id] = self.local_storage["memories"][user_id][-self.config.memory_size:]
                
                # Save to disk
                await self._save_local_storage()
                
                logger.debug(f"Added local memory for user {user_id}: {content[:50]}... (with embedding: {embedding is not None})")
            
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
    
    async def get_memories(
        self, 
        user_id: str, 
        limit: int = 50,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Alias for get_user_memories for compatibility."""
        return await self.get_user_memories(user_id, limit, memory_type)
    
    async def get_relevant_memories(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get relevant memories for a query (alias for search_memories)."""
        return await self.search_memories(user_id, query, limit, memory_type)
    
    async def clear_memories(
        self, 
        user_id: str, 
        memory_type: Optional[str] = None
    ) -> bool:
        """Alias for clear_user_memories for compatibility."""
        return await self.clear_user_memories(user_id, memory_type)
    
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
    
    # Enhanced memory search methods
    
    async def generate_memory_embedding(self, content: str) -> Optional[List[float]]:
        """Generate embedding for memory content."""
        try:
            # This method will be called from RAGService with GeminiService
            # For now, return None to indicate embedding needs to be generated externally
            return None
        except Exception as e:
            logger.error(f"Error generating memory embedding: {e}")
            return None
    
    async def search_memories_semantic(
        self, 
        user_id: str, 
        query: str, 
        query_embedding: List[float],
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories using semantic similarity."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if user_id not in self.local_storage["memories"]:
                return []
            
            memories = self.local_storage["memories"][user_id]
            
            # Filter by memory type if specified
            if memory_type:
                memories = [m for m in memories if m.get("memory_type") == memory_type]
            
            # Calculate semantic similarity for memories with embeddings
            memory_scores = []
            for memory in memories:
                if "embedding" in memory and memory["embedding"]:
                    similarity = self._calculate_cosine_similarity(
                        query_embedding, memory["embedding"]
                    )
                    memory_scores.append((memory, similarity))
            
            # Sort by similarity and limit results
            memory_scores.sort(key=lambda x: x[1], reverse=True)
            relevant_memories = [memory for memory, score in memory_scores[:limit]]
            
            logger.debug(f"Semantic memory search for user {user_id}: {query[:50]}... (found {len(relevant_memories)} results)")
            return relevant_memories
            
        except Exception as e:
            logger.error(f"Error in semantic memory search: {e}")
            return []
    
    async def search_memories_hybrid(
        self, 
        user_id: str, 
        query: str, 
        query_embedding: Optional[List[float]] = None,
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories using hybrid approach (semantic + keyword)."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if user_id not in self.local_storage["memories"]:
                return []
            
            memories = self.local_storage["memories"][user_id]
            
            # Filter by memory type if specified
            if memory_type:
                memories = [m for m in memories if m.get("memory_type") == memory_type]
            
            # Calculate hybrid relevance scores
            memory_scores = []
            for memory in memories:
                relevance_score = await self._calculate_memory_relevance(
                    memory, query, query_embedding
                )
                if relevance_score > 0:
                    memory_scores.append((memory, relevance_score))
            
            # Sort by relevance and limit results
            memory_scores.sort(key=lambda x: x[1], reverse=True)
            relevant_memories = [memory for memory, score in memory_scores[:limit]]
            
            logger.debug(f"Hybrid memory search for user {user_id}: {query[:50]}... (found {len(relevant_memories)} results)")
            return relevant_memories
            
        except Exception as e:
            logger.error(f"Error in hybrid memory search: {e}")
            return []
    
    async def _calculate_memory_relevance(
        self, 
        memory: Dict[str, Any], 
        query: str, 
        query_embedding: Optional[List[float]] = None
    ) -> float:
        """Calculate hybrid relevance score for a memory."""
        try:
            semantic_score = 0.0
            keyword_score = 0.0
            recency_score = 0.0
            
            # Calculate semantic score if embedding is available
            if query_embedding and "embedding" in memory and memory["embedding"]:
                semantic_score = self._calculate_cosine_similarity(
                    query_embedding, memory["embedding"]
                )
            
            # Calculate keyword score
            keyword_score = self._calculate_keyword_relevance(
                query, memory.get("memory", "")
            )
            
            # Calculate recency score
            recency_score = self._calculate_recency_score(memory)
            
            # Combine scores using configured weights
            final_score = (
                semantic_score * self.config.semantic_search_weight +
                keyword_score * self.config.keyword_search_weight +
                recency_score * self.config.recency_weight
            )
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating memory relevance: {e}")
            return 0.0
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            dot_product = np.dot(vec1_array, vec2_array)
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _calculate_keyword_relevance(self, query: str, memory_text: str) -> float:
        """Calculate keyword-based relevance score."""
        try:
            query_lower = query.lower()
            memory_lower = memory_text.lower()
            
            query_words = set(query_lower.split())
            memory_words = set(memory_lower.split())
            
            if not query_words:
                return 0.0
            
            # Calculate word overlap
            overlap = len(query_words.intersection(memory_words))
            return overlap / len(query_words)
            
        except Exception as e:
            logger.error(f"Error calculating keyword relevance: {e}")
            return 0.0
    
    def _calculate_recency_score(self, memory: Dict[str, Any]) -> float:
        """Calculate recency score for a memory."""
        try:
            created_at = memory.get("created_at")
            if not created_at:
                return 0.0
            
            # Parse creation time
            if isinstance(created_at, str):
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_time = created_at
            
            # Calculate days since creation
            days_old = (datetime.now() - created_time).days
            
            # Exponential decay: newer memories get higher scores
            decay_factor = 0.95
            recency_score = decay_factor ** days_old
            
            return recency_score
            
        except Exception as e:
            logger.error(f"Error calculating recency score: {e}")
            return 0.0
    
    async def update_memory_embeddings(self, user_id: str, memory_id: str, embedding: List[float]) -> bool:
        """Update embedding for a specific memory."""
        try:
            if user_id in self.local_storage["memories"]:
                memories = self.local_storage["memories"][user_id]
                for memory in memories:
                    if memory.get("id") == memory_id:
                        memory["embedding"] = embedding
                        await self._save_local_storage()
                        logger.debug(f"Updated embedding for memory {memory_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating memory embedding: {e}")
            return False
    
    async def format_memory_context(
        self, 
        memories: List[Dict[str, Any]], 
        max_length: Optional[int] = None
    ) -> str:
        """Format memories into context string with length management."""
        try:
            if not memories:
                return ""
            
            max_length = max_length or self.config.max_memory_context_length
            
            # Format memories
            context_parts = ["Previous conversation context:"]
            current_length = len(context_parts[0])
            
            for i, memory in enumerate(memories):
                memory_text = memory.get("memory", "")
                memory_type = memory.get("memory_type", "conversation")
                created_at = memory.get("created_at", "")
                
                # Format memory entry
                memory_entry = f"\n{i+1}. [{memory_type.upper()}] {memory_text}"
                
                # Check if adding this memory would exceed length limit
                if current_length + len(memory_entry) > max_length:
                    # Add truncation indicator
                    context_parts.append(f"\n... (showing {i} of {len(memories)} memories)")
                    break
                
                context_parts.append(memory_entry)
                current_length += len(memory_entry)
            
            context = "".join(context_parts)
            
            # If context is still too long, truncate it
            if len(context) > max_length:
                context = context[:max_length-3] + "..."
            
            return context
            
        except Exception as e:
            logger.error(f"Error formatting memory context: {e}")
            return ""
    
    async def summarize_memories(
        self, 
        memories: List[Dict[str, Any]], 
        max_length: int = 1000
    ) -> str:
        """Summarize a list of memories to fit within length constraints."""
        try:
            if not memories:
                return ""
            
            # Simple summarization: take key points from each memory
            summary_parts = ["Memory summary:"]
            
            for memory in memories:
                memory_text = memory.get("memory", "")
                memory_type = memory.get("memory_type", "conversation")
                
                # Extract first sentence or key phrase
                sentences = memory_text.split('.')
                key_phrase = sentences[0] if sentences else memory_text[:100]
                
                summary_parts.append(f"\n- [{memory_type.upper()}] {key_phrase}")
            
            summary = "".join(summary_parts)
            
            # Truncate if still too long
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing memories: {e}")
            return ""
    
    # Session-aware memory methods
    
    async def add_memory_with_session(
        self, 
        user_id: str, 
        content: str, 
        session_id: str,
        memory_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None
    ) -> str:
        """Add a memory entry with session context."""
        return await self.add_memory(
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            metadata=metadata,
            embedding=embedding,
            session_id=session_id
        )
    
    async def get_session_memories(
        self, 
        user_id: str, 
        session_id: str,
        limit: int = 50,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all memories for a specific session."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            if user_id not in self.local_storage["memories"]:
                return []
            
            memories = self.local_storage["memories"][user_id]
            
            # Filter by session_id
            session_memories = [m for m in memories if m.get("session_id") == session_id]
            
            # Filter by memory type if specified
            if memory_type:
                session_memories = [m for m in session_memories if m.get("memory_type") == memory_type]
            
            # Limit results
            session_memories = session_memories[-limit:] if limit > 0 else session_memories
            
            logger.debug(f"Retrieved {len(session_memories)} memories for session {session_id}")
            return session_memories
            
        except Exception as e:
            logger.error(f"Error getting session memories: {e}")
            return []
    
    async def search_memories_by_session(
        self, 
        user_id: str, 
        session_id: str,
        query: str, 
        query_embedding: Optional[List[float]] = None,
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories within a specific session."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            # Get session memories first
            session_memories = await self.get_session_memories(
                user_id=user_id,
                session_id=session_id,
                limit=0,  # Get all memories for the session
                memory_type=memory_type
            )
            
            if not session_memories:
                return []
            
            # Use hybrid search on session memories
            memory_scores = []
            for memory in session_memories:
                relevance_score = await self._calculate_memory_relevance(
                    memory, query, query_embedding
                )
                if relevance_score > 0:
                    memory_scores.append((memory, relevance_score))
            
            # Sort by relevance and limit results
            memory_scores.sort(key=lambda x: x[1], reverse=True)
            relevant_memories = [memory for memory, score in memory_scores[:limit]]
            
            logger.debug(f"Session memory search for session {session_id}: {query[:50]}... (found {len(relevant_memories)} results)")
            return relevant_memories
            
        except Exception as e:
            logger.error(f"Error searching session memories: {e}")
            return []
    
    async def cleanup_session_memories(self, session_id: str) -> int:
        """Clean up all memories for a specific session."""
        if not self._initialized:
            raise RuntimeError("Mem0 service not initialized")
        
        try:
            cleaned_count = 0
            
            # Remove memories for this session from all users
            for user_id in self.local_storage["memories"]:
                memories = self.local_storage["memories"][user_id]
                original_count = len(memories)
                
                # Filter out memories for this session
                self.local_storage["memories"][user_id] = [
                    m for m in memories if m.get("session_id") != session_id
                ]
                
                cleaned_count += original_count - len(self.local_storage["memories"][user_id])
            
            if cleaned_count > 0:
                await self._save_local_storage()
                logger.info(f"Cleaned up {cleaned_count} memories for session {session_id}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up session memories: {e}")
            return 0
    
    async def get_memory_stats_by_session(self, session_id: str) -> Dict[str, Any]:
        """Get memory statistics for a specific session."""
        try:
            if not self._initialized:
                return {"error": "Service not initialized"}
            
            session_memories = []
            total_memories = 0
            
            # Collect memories for this session
            for user_id, user_data in self.local_storage.get("memories", {}).items():
                # Handle both dictionary and list structures
                if isinstance(user_data, dict):
                    # Dictionary structure: {memory_id: memory_data}
                    for memory_id, memory in user_data.items():
                        if memory.get("session_id") == session_id:
                            session_memories.append(memory)
                            total_memories += 1
                elif isinstance(user_data, list):
                    # List structure: [memory_data]
                    for memory in user_data:
                        if memory.get("session_id") == session_id:
                            session_memories.append(memory)
                            total_memories += 1
            
            if not session_memories:
                return {
                    "session_id": session_id,
                    "total_memories": 0,
                    "memory_types": {},
                    "recent_activity": None
                }
            
            # Calculate statistics
            memory_types = {}
            for memory in session_memories:
                mem_type = memory.get("memory_type", "unknown")
                memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
            
            # Get recent activity
            recent_memories = sorted(
                session_memories,
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )[:5]
            
            return {
                "session_id": session_id,
                "total_memories": total_memories,
                "memory_types": memory_types,
                "recent_activity": [
                    {
                        "memory_id": mem.get("memory_id"),
                        "content": mem.get("memory", "")[:100] + "...",
                        "created_at": mem.get("created_at"),
                        "memory_type": mem.get("memory_type")
                    }
                    for mem in recent_memories
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting memory stats by session: {e}")
            return {"error": str(e)}

    # Advanced Memory Context Retrieval Methods (Task 3)

    async def search_memories_advanced(
        self, 
        user_id: str, 
        query: str,
        search_options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Advanced memory search with enhanced relevance scoring and filtering.
        
        Args:
            user_id: User identifier
            query: Search query
            search_options: Advanced search options including:
                - limit: Maximum number of results (default: 5)
                - memory_type: Filter by memory type
                - time_range: Filter by time range (hour, day, week, month)
                - session_id: Filter by session
                - min_confidence: Minimum confidence threshold
                - search_strategy: 'hierarchical', 'semantic', 'hybrid', 'fuzzy'
                - include_metadata: Include metadata in results
        """
        try:
            if not self._initialized:
                return []
            
            options = search_options or {}
            limit = options.get("limit", 5)
            memory_type = options.get("memory_type")
            time_range = options.get("time_range")
            session_id = options.get("session_id")
            min_confidence = options.get("min_confidence", 0.1)
            search_strategy = options.get("search_strategy", "hierarchical")
            include_metadata = options.get("include_metadata", True)
            
            # Get user memories with filtering
            memories = await self._get_filtered_memories(
                user_id, memory_type, time_range, session_id
            )
            
            if not memories:
                return []
            
            # Generate query embedding for semantic search
            query_embedding = None
            if search_strategy in ["hierarchical", "semantic", "hybrid"]:
                query_embedding = await self.generate_memory_embedding(query)
            
            # Apply search strategy
            if search_strategy == "hierarchical":
                results = await self._hierarchical_search(
                    memories, query, query_embedding, limit, min_confidence
                )
            elif search_strategy == "semantic":
                results = await self._semantic_search(
                    memories, query, query_embedding, limit, min_confidence
                )
            elif search_strategy == "hybrid":
                results = await self._hybrid_search(
                    memories, query, query_embedding, limit, min_confidence
                )
            elif search_strategy == "fuzzy":
                results = await self._fuzzy_search(
                    memories, query, limit, min_confidence
                )
            else:
                results = await self._hierarchical_search(
                    memories, query, query_embedding, limit, min_confidence
                )
            
            # Process results
            processed_results = []
            for result in results:
                processed_result = {
                    "memory_id": result["memory_id"],
                    "content": result["memory"],
                    "relevance_score": result["relevance_score"],
                    "confidence": result.get("confidence", 0.0),
                    "memory_type": result.get("memory_type"),
                    "created_at": result.get("created_at"),
                    "session_id": result.get("session_id")
                }
                
                if include_metadata:
                    processed_result["metadata"] = result.get("metadata", {})
                    processed_result["scoring_breakdown"] = result.get("scoring_breakdown", {})
                
                processed_results.append(processed_result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in advanced memory search: {e}")
            return []

    async def calculate_advanced_relevance(
        self,
        memory: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate advanced multi-factor relevance score with confidence.
        
        Args:
            memory: Memory object to score
            query: Search query
            context: Additional context (session info, user preferences, etc.)
        
        Returns:
            Dictionary with relevance score, confidence, and scoring breakdown
        """
        try:
            context = context or {}
            
            # Generate query embedding if not provided
            query_embedding = context.get("query_embedding")
            if not query_embedding:
                query_embedding = await self.generate_memory_embedding(query)
            
            # Calculate individual scores
            semantic_score = 0.0
            if query_embedding and "embedding" in memory and memory["embedding"]:
                semantic_score = self._calculate_cosine_similarity(
                    query_embedding, memory["embedding"]
                )
            
            keyword_score = self._calculate_keyword_relevance(
                query, memory.get("memory", "")
            )
            
            recency_score = self._calculate_recency_score(memory)
            
            frequency_score = self._calculate_frequency_score(memory, context)
            
            interaction_score = self._calculate_interaction_score(memory, context)
            
            # Dynamic weight adjustment based on query type and context
            weights = self._get_dynamic_weights(query, context)
            
            # Calculate weighted score
            final_score = (
                semantic_score * weights["semantic"] +
                keyword_score * weights["keyword"] +
                recency_score * weights["recency"] +
                frequency_score * weights["frequency"] +
                interaction_score * weights["interaction"]
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                semantic_score, keyword_score, recency_score, 
                frequency_score, interaction_score, weights
            )
            
            return {
                "relevance_score": final_score,
                "confidence": confidence,
                "scoring_breakdown": {
                    "semantic_score": semantic_score,
                    "keyword_score": keyword_score,
                    "recency_score": recency_score,
                    "frequency_score": frequency_score,
                    "interaction_score": interaction_score,
                    "weights": weights
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating advanced relevance: {e}")
            return {
                "relevance_score": 0.0,
                "confidence": 0.0,
                "scoring_breakdown": {}
            }

    async def cluster_memories(
        self,
        user_id: str,
        memories: Optional[List[Dict[str, Any]]] = None,
        cluster_options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Cluster related memories for better context understanding.
        
        Args:
            user_id: User identifier
            memories: List of memories to cluster (if None, uses all user memories)
            cluster_options: Clustering options including:
                - cluster_type: 'topic', 'temporal', 'semantic'
                - max_clusters: Maximum number of clusters
                - similarity_threshold: Minimum similarity for clustering
        
        Returns:
            List of memory clusters
        """
        try:
            if not self._initialized:
                return []
            
            options = cluster_options or {}
            cluster_type = options.get("cluster_type", "topic")
            max_clusters = options.get("max_clusters", 5)
            similarity_threshold = options.get("similarity_threshold", 0.7)
            
            # Get memories if not provided
            if memories is None:
                memories = await self.get_user_memories(user_id, limit=100)
            
            if not memories:
                return []
            
            # Apply clustering based on type
            if cluster_type == "topic":
                clusters = await self._cluster_by_topic(memories, max_clusters, similarity_threshold)
            elif cluster_type == "temporal":
                clusters = await self._cluster_by_temporal(memories, max_clusters)
            elif cluster_type == "semantic":
                clusters = await self._cluster_by_semantic(memories, max_clusters, similarity_threshold)
            else:
                clusters = await self._cluster_by_topic(memories, max_clusters, similarity_threshold)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering memories: {e}")
            return []

    async def generate_context_summary(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        max_length: int = 500,
        summary_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate intelligent context summary from memories.
        
        Args:
            memories: List of memories to summarize
            query: Original query for context
            max_length: Maximum summary length
            summary_options: Summary options including:
                - summary_type: 'key_points', 'narrative', 'structured'
                - include_relevance: Include relevance scores
                - group_by_topic: Group related memories
        
        Returns:
            Context summary string
        """
        try:
            if not memories:
                return "No relevant memories found."
            
            options = summary_options or {}
            summary_type = options.get("summary_type", "key_points")
            include_relevance = options.get("include_relevance", False)
            group_by_topic = options.get("group_by_topic", True)
            
            # Sort memories by relevance if available
            sorted_memories = sorted(
                memories,
                key=lambda x: x.get("relevance_score", 0.0),
                reverse=True
            )
            
            # Generate summary based on type
            if summary_type == "key_points":
                summary = await self._generate_key_points_summary(
                    sorted_memories, query, max_length, include_relevance
                )
            elif summary_type == "narrative":
                summary = await self._generate_narrative_summary(
                    sorted_memories, query, max_length, include_relevance
                )
            elif summary_type == "structured":
                summary = await self._generate_structured_summary(
                    sorted_memories, query, max_length, include_relevance, group_by_topic
                )
            else:
                summary = await self._generate_key_points_summary(
                    sorted_memories, query, max_length, include_relevance
                )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating context summary: {e}")
            return "Error generating context summary."

    # Helper methods for advanced features

    async def _get_filtered_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        time_range: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get memories with advanced filtering."""
        try:
            user_memories = self.local_storage.get("memories", {}).get(user_id, {})
            filtered_memories = []
            
            # Handle both dictionary and list structures
            if isinstance(user_memories, dict):
                # Dictionary structure: {memory_id: memory_data}
                for memory_id, memory in user_memories.items():
                    # Apply filters
                    if memory_type and memory.get("memory_type") != memory_type:
                        continue
                    
                    if session_id and memory.get("session_id") != session_id:
                        continue
                    
                    if time_range:
                        if not self._is_memory_in_time_range(memory, time_range):
                            continue
                    
                    # Add memory_id to memory object
                    memory["memory_id"] = memory_id
                    filtered_memories.append(memory)
            elif isinstance(user_memories, list):
                # List structure: [memory_data]
                for i, memory in enumerate(user_memories):
                    # Apply filters
                    if memory_type and memory.get("memory_type") != memory_type:
                        continue
                    
                    if session_id and memory.get("session_id") != session_id:
                        continue
                    
                    if time_range:
                        if not self._is_memory_in_time_range(memory, time_range):
                            continue
                    
                    # Add memory_id to memory object
                    memory["memory_id"] = memory.get("memory_id", f"memory_{i}")
                    filtered_memories.append(memory)
            
            return filtered_memories
            
        except Exception as e:
            logger.error(f"Error filtering memories: {e}")
            return []

    def _is_memory_in_time_range(self, memory: Dict[str, Any], time_range: str) -> bool:
        """Check if memory is within specified time range."""
        try:
            created_at = memory.get("created_at")
            if not created_at:
                return False
            
            if isinstance(created_at, str):
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_time = created_at
            
            now = datetime.now()
            
            if time_range == "hour":
                return (now - created_time).total_seconds() < 3600
            elif time_range == "day":
                return (now - created_time).days < 1
            elif time_range == "week":
                return (now - created_time).days < 7
            elif time_range == "month":
                return (now - created_time).days < 30
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error checking time range: {e}")
            return False

    async def _hierarchical_search(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        query_embedding: Optional[List[float]],
        limit: int,
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Perform hierarchical search with fallback strategies."""
        try:
            # Primary search: semantic + hybrid
            if query_embedding:
                results = await self._semantic_search(
                    memories, query, query_embedding, limit * 2, min_confidence
                )
                
                if len(results) >= limit:
                    return results[:limit]
            
            # Secondary search: keyword + fuzzy
            keyword_results = await self._keyword_search(memories, query, limit * 2, min_confidence)
            
            if query_embedding:
                # Combine and deduplicate
                combined = self._combine_and_deduplicate(results, keyword_results)
                return combined[:limit]
            else:
                return keyword_results[:limit]
                
        except Exception as e:
            logger.error(f"Error in hierarchical search: {e}")
            return []

    async def _semantic_search(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        query_embedding: List[float],
        limit: int,
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Perform semantic search with advanced relevance scoring."""
        try:
            scored_memories = []
            
            for memory in memories:
                relevance_info = await self.calculate_advanced_relevance(
                    memory, query, {"query_embedding": query_embedding}
                )
                
                if relevance_info["confidence"] >= min_confidence:
                    memory["relevance_score"] = relevance_info["relevance_score"]
                    memory["confidence"] = relevance_info["confidence"]
                    memory["scoring_breakdown"] = relevance_info["scoring_breakdown"]
                    scored_memories.append(memory)
            
            # Sort by relevance score
            scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    async def _hybrid_search(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        query_embedding: Optional[List[float]],
        limit: int,
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword approaches."""
        try:
            semantic_results = []
            keyword_results = []
            
            # Get semantic results if embedding available
            if query_embedding:
                semantic_results = await self._semantic_search(
                    memories, query, query_embedding, limit, min_confidence
                )
            
            # Get keyword results
            keyword_results = await self._keyword_search(memories, query, limit, min_confidence)
            
            # Combine results
            combined = self._combine_and_deduplicate(semantic_results, keyword_results)
            return combined[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []

    async def _keyword_search(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        limit: int,
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search with fuzzy matching."""
        try:
            scored_memories = []
            query_lower = query.lower()
            
            for memory in memories:
                memory_text = memory.get("memory", "").lower()
                
                # Calculate keyword relevance
                keyword_score = self._calculate_keyword_relevance(query, memory_text)
                
                # Add fuzzy matching score
                fuzzy_score = self._calculate_fuzzy_match(query_lower, memory_text)
                
                # Combine scores
                combined_score = (keyword_score * 0.7) + (fuzzy_score * 0.3)
                
                if combined_score >= min_confidence:
                    memory["relevance_score"] = combined_score
                    memory["confidence"] = combined_score
                    scored_memories.append(memory)
            
            # Sort by relevance score
            scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []

    async def _fuzzy_search(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        limit: int,
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Perform fuzzy search for typos and variations."""
        try:
            scored_memories = []
            query_lower = query.lower()
            
            for memory in memories:
                memory_text = memory.get("memory", "").lower()
                
                # Calculate fuzzy match score
                fuzzy_score = self._calculate_fuzzy_match(query_lower, memory_text)
                
                if fuzzy_score >= min_confidence:
                    memory["relevance_score"] = fuzzy_score
                    memory["confidence"] = fuzzy_score
                    scored_memories.append(memory)
            
            # Sort by relevance score
            scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error in fuzzy search: {e}")
            return []

    def _calculate_fuzzy_match(self, query: str, text: str) -> float:
        """Calculate fuzzy matching score using simple string similarity."""
        try:
            query_words = query.split()
            text_words = text.split()
            
            if not query_words:
                return 0.0
            
            # Calculate word-level similarity
            total_similarity = 0.0
            for query_word in query_words:
                best_match = 0.0
                for text_word in text_words:
                    similarity = self._calculate_word_similarity(query_word, text_word)
                    best_match = max(best_match, similarity)
                total_similarity += best_match
            
            return total_similarity / len(query_words)
            
        except Exception as e:
            logger.error(f"Error calculating fuzzy match: {e}")
            return 0.0

    def _calculate_word_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words using Levenshtein distance."""
        try:
            if word1 == word2:
                return 1.0
            
            # Simple character overlap for performance
            common_chars = len(set(word1) & set(word2))
            total_chars = len(set(word1) | set(word2))
            
            if total_chars == 0:
                return 0.0
            
            return common_chars / total_chars
            
        except Exception as e:
            logger.error(f"Error calculating word similarity: {e}")
            return 0.0

    def _combine_and_deduplicate(
        self,
        results1: List[Dict[str, Any]],
        results2: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine and deduplicate search results."""
        try:
            combined = {}

            # Helper to get a unique memory identifier
            def get_mem_id(result):
                return result.get("memory_id") or result.get("id")

            # Add results from first list
            for result in results1:
                memory_id = get_mem_id(result)
                if memory_id:
                    combined[memory_id] = result

            # Add results from second list (keep higher scores)
            for result in results2:
                memory_id = get_mem_id(result)
                if memory_id:
                    if memory_id not in combined or result.get("relevance_score", 0) > combined[memory_id].get("relevance_score", 0):
                        combined[memory_id] = result

            # Convert back to list
            return list(combined.values())
        except Exception as e:
            print(f"Error combining and deduplicating results: {e}")
            return []

    def _calculate_frequency_score(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate frequency score based on memory occurrence patterns."""
        try:
            # For now, return a simple score based on memory age
            # In a full implementation, this would track memory access patterns
            created_at = memory.get("created_at")
            if not created_at:
                return 0.0
            
            if isinstance(created_at, str):
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_time = created_at
            
            # Simple frequency score based on recency (newer = higher frequency)
            days_old = (datetime.now() - created_time).days
            frequency_score = max(0.0, 1.0 - (days_old / 30.0))  # Decay over 30 days
            
            return frequency_score
            
        except Exception as e:
            logger.error(f"Error calculating frequency score: {e}")
            return 0.0

    def _calculate_interaction_score(self, memory: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate interaction score based on user engagement patterns."""
        try:
            # For now, return a simple score based on memory type
            # In a full implementation, this would track user interactions
            memory_type = memory.get("memory_type", "conversation")
            
            # Assign higher scores to more interactive memory types
            type_scores = {
                "conversation": 0.8,
                "question": 0.9,
                "instruction": 0.7,
                "fact": 0.6,
                "preference": 0.8
            }
            
            return type_scores.get(memory_type, 0.5)
            
        except Exception as e:
            logger.error(f"Error calculating interaction score: {e}")
            return 0.5

    def _get_dynamic_weights(self, query: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Get dynamic weights based on query type and context."""
        try:
            # Default weights
            weights = {
                "semantic": 0.4,
                "keyword": 0.25,
                "recency": 0.2,
                "frequency": 0.1,
                "interaction": 0.05
            }
            
            # Adjust weights based on query characteristics
            query_lower = query.lower()
            
            # If query is short, increase keyword weight
            if len(query.split()) <= 2:
                weights["keyword"] += 0.1
                weights["semantic"] -= 0.1
            
            # If query contains specific terms, adjust weights
            if any(word in query_lower for word in ["recent", "latest", "new"]):
                weights["recency"] += 0.1
                weights["semantic"] -= 0.1
            
            if any(word in query_lower for word in ["often", "frequent", "common"]):
                weights["frequency"] += 0.1
                weights["recency"] -= 0.1
            
            # Normalize weights
            total = sum(weights.values())
            weights = {k: v / total for k, v in weights.items()}
            
            return weights
            
        except Exception as e:
            logger.error(f"Error getting dynamic weights: {e}")
            return {
                "semantic": 0.4,
                "keyword": 0.25,
                "recency": 0.2,
                "frequency": 0.1,
                "interaction": 0.05
            }

    def _calculate_confidence(
        self,
        semantic_score: float,
        keyword_score: float,
        recency_score: float,
        frequency_score: float,
        interaction_score: float,
        weights: Dict[str, float]
    ) -> float:
        """Calculate confidence level for relevance scoring."""
        try:
            # Calculate weighted average of individual scores
            weighted_score = (
                semantic_score * weights["semantic"] +
                keyword_score * weights["keyword"] +
                recency_score * weights["recency"] +
                frequency_score * weights["frequency"] +
                interaction_score * weights["interaction"]
            )
            
            # Calculate confidence based on score consistency
            scores = [semantic_score, keyword_score, recency_score, frequency_score, interaction_score]
            score_variance = np.var(scores) if len(scores) > 1 else 0.0
            
            # Higher variance = lower confidence
            confidence = weighted_score * (1.0 - score_variance)
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5

    async def _cluster_by_topic(
        self,
        memories: List[Dict[str, Any]],
        max_clusters: int,
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Cluster memories by topic using semantic similarity."""
        try:
            if not memories:
                return []
            
            # Simple clustering based on keyword overlap
            clusters = []
            used_memories = set()
            
            for memory in memories:
                if memory.get("memory_id") in used_memories:
                    continue
                
                # Start new cluster
                cluster = {
                    "cluster_id": f"cluster_{len(clusters)}",
                    "topic": memory.get("memory", "")[:50] + "...",
                    "memories": [memory],
                    "size": 1,
                    "avg_relevance": memory.get("relevance_score", 0.0)
                }
                
                used_memories.add(memory.get("memory_id"))
                
                # Find similar memories
                memory_text = memory.get("memory", "").lower()
                memory_words = set(memory_text.split())
                
                for other_memory in memories:
                    if other_memory.get("memory_id") in used_memories:
                        continue
                    
                    other_text = other_memory.get("memory", "").lower()
                    other_words = set(other_text.split())
                    
                    # Calculate similarity
                    if memory_words and other_words:
                        similarity = len(memory_words & other_words) / len(memory_words | other_words)
                        
                        if similarity >= similarity_threshold:
                            cluster["memories"].append(other_memory)
                            cluster["size"] += 1
                            cluster["avg_relevance"] += other_memory.get("relevance_score", 0.0)
                            used_memories.add(other_memory.get("memory_id"))
                
                # Calculate average relevance
                if cluster["size"] > 0:
                    cluster["avg_relevance"] /= cluster["size"]
                
                clusters.append(cluster)
                
                if len(clusters) >= max_clusters:
                    break
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering by topic: {e}")
            return []

    async def _cluster_by_temporal(
        self,
        memories: List[Dict[str, Any]],
        max_clusters: int
    ) -> List[Dict[str, Any]]:
        """Cluster memories by temporal proximity."""
        try:
            if not memories:
                return []
            
            # Sort memories by creation time
            sorted_memories = sorted(
                memories,
                key=lambda x: x.get("created_at", "")
            )
            
            clusters = []
            current_cluster = None
            
            for memory in sorted_memories:
                created_at = memory.get("created_at")
                if not created_at:
                    continue
                
                if isinstance(created_at, str):
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_time = created_at
                
                if current_cluster is None:
                    # Start new cluster
                    current_cluster = {
                        "cluster_id": f"temporal_{len(clusters)}",
                        "time_range": created_time.strftime("%Y-%m-%d"),
                        "memories": [memory],
                        "size": 1,
                        "avg_relevance": memory.get("relevance_score", 0.0)
                    }
                else:
                    # Check if memory is within 24 hours of cluster
                    cluster_start = datetime.fromisoformat(current_cluster["time_range"])
                    time_diff = abs((created_time - cluster_start).total_seconds())
                    
                    if time_diff <= 86400:  # 24 hours
                        current_cluster["memories"].append(memory)
                        current_cluster["size"] += 1
                        current_cluster["avg_relevance"] += memory.get("relevance_score", 0.0)
                    else:
                        # Finalize current cluster
                        if current_cluster["size"] > 0:
                            current_cluster["avg_relevance"] /= current_cluster["size"]
                        clusters.append(current_cluster)
                        
                        # Start new cluster
                        current_cluster = {
                            "cluster_id": f"temporal_{len(clusters)}",
                            "time_range": created_time.strftime("%Y-%m-%d"),
                            "memories": [memory],
                            "size": 1,
                            "avg_relevance": memory.get("relevance_score", 0.0)
                        }
                
                if len(clusters) >= max_clusters:
                    break
            
            # Add final cluster
            if current_cluster and current_cluster["size"] > 0:
                current_cluster["avg_relevance"] /= current_cluster["size"]
                clusters.append(current_cluster)
            
            return clusters[:max_clusters]
            
        except Exception as e:
            logger.error(f"Error clustering by temporal: {e}")
            return []

    async def _cluster_by_semantic(
        self,
        memories: List[Dict[str, Any]],
        max_clusters: int,
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Cluster memories by semantic similarity using embeddings."""
        try:
            if not memories:
                return []
            
            # For now, use topic clustering as fallback
            # In a full implementation, this would use embedding similarity
            return await self._cluster_by_topic(memories, max_clusters, similarity_threshold)
            
        except Exception as e:
            logger.error(f"Error clustering by semantic: {e}")
            return []

    async def _generate_key_points_summary(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        max_length: int,
        include_relevance: bool
    ) -> str:
        """Generate key points summary from memories."""
        try:
            if not memories:
                return "No relevant memories found."
            
            summary_parts = [f"Based on {len(memories)} relevant memories:"]
            
            for i, memory in enumerate(memories[:5], 1):  # Limit to top 5
                content = memory.get("memory", "")
                if len(content) > 100:
                    content = content[:100] + "..."
                
                point = f"{i}. {content}"
                
                if include_relevance:
                    relevance = memory.get("relevance_score", 0.0)
                    point += f" (relevance: {relevance:.2f})"
                
                summary_parts.append(point)
            
            summary = "\n".join(summary_parts)
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating key points summary: {e}")
            return "Error generating summary."

    async def _generate_narrative_summary(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        max_length: int,
        include_relevance: bool
    ) -> str:
        """Generate narrative summary from memories."""
        try:
            if not memories:
                return "No relevant memories found."
            
            # Sort by creation time for narrative flow
            sorted_memories = sorted(
                memories,
                key=lambda x: x.get("created_at", "")
            )
            
            summary_parts = [f"Context from {len(memories)} memories:"]
            
            for memory in sorted_memories[:3]:  # Limit to top 3 for narrative
                content = memory.get("memory", "")
                if len(content) > 150:
                    content = content[:150] + "..."
                
                summary_parts.append(content)
            
            summary = " ".join(summary_parts)
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating narrative summary: {e}")
            return "Error generating summary."

    async def _generate_structured_summary(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        max_length: int,
        include_relevance: bool,
        group_by_topic: bool
    ) -> str:
        """Generate structured summary from memories."""
        try:
            if not memories:
                return "No relevant memories found."
            
            if group_by_topic:
                # Group memories by type
                memory_types = {}
                for memory in memories:
                    mem_type = memory.get("memory_type", "general")
                    if mem_type not in memory_types:
                        memory_types[mem_type] = []
                    memory_types[mem_type].append(memory)
                
                summary_parts = [f"Structured context from {len(memories)} memories:"]
                
                for mem_type, type_memories in memory_types.items():
                    summary_parts.append(f"\n{mem_type.title()} memories:")
                    for memory in type_memories[:2]:  # Limit per type
                        content = memory.get("memory", "")
                        if len(content) > 80:
                            content = content[:80] + "..."
                        summary_parts.append(f"- {content}")
            else:
                # Simple structured format
                summary_parts = [f"Context summary ({len(memories)} memories):"]
                for i, memory in enumerate(memories[:4], 1):
                    content = memory.get("memory", "")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    summary_parts.append(f"{i}. {content}")
            
            summary = "\n".join(summary_parts)
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating structured summary: {e}")
            return "Error generating summary."