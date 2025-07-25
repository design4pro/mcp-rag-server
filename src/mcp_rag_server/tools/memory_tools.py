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
        """Get session information for a specific user."""
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Get user memories to analyze session patterns
            memories = await self.mem0_service.get_user_memories(user_id, limit=100)
            
            # Group by session
            sessions = {}
            for memory in memories:
                session_id = memory.get("session_id", "unknown")
                if session_id not in sessions:
                    sessions[session_id] = {
                        "session_id": session_id,
                        "memories": [],
                        "memory_types": {},
                        "created_at": memory.get("created_at"),
                        "last_activity": memory.get("created_at")
                    }
                
                sessions[session_id]["memories"].append(memory)
                mem_type = memory.get("memory_type", "unknown")
                sessions[session_id]["memory_types"][mem_type] = sessions[session_id]["memory_types"].get(mem_type, 0) + 1
                
                # Update last activity
                if memory.get("created_at") > sessions[session_id]["last_activity"]:
                    sessions[session_id]["last_activity"] = memory.get("created_at")
            
            # Calculate session statistics
            session_list = []
            for session_data in sessions.values():
                session_list.append({
                    "session_id": session_data["session_id"],
                    "memory_count": len(session_data["memories"]),
                    "memory_types": session_data["memory_types"],
                    "created_at": session_data["created_at"],
                    "last_activity": session_data["last_activity"]
                })
            
            return {
                "success": True,
                "user_id": user_id,
                "total_sessions": len(session_list),
                "sessions": session_list
            }
        except Exception as e:
            logger.error(f"Error getting user session info: {e}")
            return {"success": False, "error": str(e)}

    # Advanced Memory Context Retrieval Tools (Task 3)

    async def search_memories_advanced(
        self,
        user_id: str,
        query: str,
        search_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Validate input
            if not user_id or not query:
                return {"success": False, "error": "User ID and query are required"}
            
            # Perform advanced search
            results = await self.mem0_service.search_memories_advanced(
                user_id, query, search_options
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "query": query,
                "results": results,
                "count": len(results),
                "search_options": search_options or {}
            }
        except Exception as e:
            logger.error(f"Error in advanced memory search: {e}")
            return {"success": False, "error": str(e)}

    async def get_enhanced_memory_context(
        self,
        user_id: str,
        query: str,
        context_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get enhanced memory context with advanced processing and summarization.
        
        Args:
            user_id: User identifier
            query: Query for context retrieval
            context_options: Context options including:
                - limit: Maximum number of memories to consider
                - summary_type: 'key_points', 'narrative', 'structured'
                - include_relevance: Include relevance scores
                - group_by_topic: Group related memories
                - min_confidence: Minimum confidence threshold
        """
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Validate input
            if not user_id or not query:
                return {"success": False, "error": "User ID and query are required"}
            
            options = context_options or {}
            limit = options.get("limit", 10)
            summary_type = options.get("summary_type", "key_points")
            include_relevance = options.get("include_relevance", True)
            group_by_topic = options.get("group_by_topic", True)
            min_confidence = options.get("min_confidence", 0.1)
            
            # Get relevant memories using advanced search
            search_options = {
                "limit": limit,
                "min_confidence": min_confidence,
                "search_strategy": "hierarchical",
                "include_metadata": True
            }
            
            memories = await self.mem0_service.search_memories_advanced(
                user_id, query, search_options
            )
            
            if not memories:
                return {
                    "success": True,
                    "user_id": user_id,
                    "query": query,
                    "context": "No relevant memories found.",
                    "memory_count": 0,
                    "summary_type": summary_type
                }
            
            # Generate context summary
            summary_options = {
                "summary_type": summary_type,
                "include_relevance": include_relevance,
                "group_by_topic": group_by_topic
            }
            
            context_summary = await self.mem0_service.generate_context_summary(
                memories, query, max_length=500, summary_options=summary_options
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "query": query,
                "context": context_summary,
                "memory_count": len(memories),
                "summary_type": summary_type,
                "memories": memories[:5] if include_relevance else [],  # Include top 5 for reference
                "context_options": context_options or {}
            }
        except Exception as e:
            logger.error(f"Error getting enhanced memory context: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_memory_patterns(
        self,
        user_id: str,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze memory patterns for a user.
        
        Args:
            user_id: User identifier
            time_range: Time range for analysis (hour, day, week, month, all)
        """
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Validate input
            if not user_id:
                return {"success": False, "error": "User ID is required"}
            
            # Get user memories
            memories = await self.mem0_service.get_user_memories(user_id, limit=1000)
            
            if not memories:
                return {
                    "success": True,
                    "user_id": user_id,
                    "patterns": {
                        "total_memories": 0,
                        "memory_types": {},
                        "temporal_distribution": {},
                        "session_analysis": {}
                    }
                }
            
            # Filter by time range if specified
            if time_range and time_range != "all":
                filtered_memories = []
                for memory in memories:
                    if self._is_memory_in_time_range(memory, time_range):
                        filtered_memories.append(memory)
                memories = filtered_memories
            
            # Analyze memory types
            memory_types = {}
            for memory in memories:
                mem_type = memory.get("memory_type", "unknown")
                memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
            
            # Analyze temporal distribution
            temporal_distribution = self._analyze_temporal_distribution(memories)
            
            # Analyze session patterns
            session_analysis = self._analyze_session_patterns(memories)
            
            # Calculate engagement metrics
            engagement_metrics = self._calculate_engagement_metrics(memories)
            
            return {
                "success": True,
                "user_id": user_id,
                "time_range": time_range or "all",
                "patterns": {
                    "total_memories": len(memories),
                    "memory_types": memory_types,
                    "temporal_distribution": temporal_distribution,
                    "session_analysis": session_analysis,
                    "engagement_metrics": engagement_metrics
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing memory patterns: {e}")
            return {"success": False, "error": str(e)}

    async def cluster_user_memories(
        self,
        user_id: str,
        cluster_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cluster user memories for better organization and analysis.
        
        Args:
            user_id: User identifier
            cluster_options: Clustering options including:
                - cluster_type: 'topic', 'temporal', 'semantic'
                - max_clusters: Maximum number of clusters
                - similarity_threshold: Minimum similarity for clustering
        """
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Validate input
            if not user_id:
                return {"success": False, "error": "User ID is required"}
            
            # Get user memories
            memories = await self.mem0_service.get_user_memories(user_id, limit=500)
            
            if not memories:
                return {
                    "success": True,
                    "user_id": user_id,
                    "clusters": [],
                    "cluster_count": 0
                }
            
            # Perform clustering
            clusters = await self.mem0_service.cluster_memories(
                user_id, memories, cluster_options
            )
            
            return {
                "success": True,
                "user_id": user_id,
                "clusters": clusters,
                "cluster_count": len(clusters),
                "total_memories": len(memories),
                "cluster_options": cluster_options or {}
            }
        except Exception as e:
            logger.error(f"Error clustering user memories: {e}")
            return {"success": False, "error": str(e)}

    async def get_memory_insights(
        self,
        user_id: str,
        insight_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Get comprehensive memory insights for a user.
        
        Args:
            user_id: User identifier
            insight_type: Type of insights ('comprehensive', 'engagement', 'topics', 'sessions')
        """
        if not self.mem0_service:
            return {"success": False, "error": "Mem0 service not initialized"}
        
        try:
            # Validate input
            if not user_id:
                return {"success": False, "error": "User ID is required"}
            
            # Get user memories
            memories = await self.mem0_service.get_user_memories(user_id, limit=1000)
            
            if not memories:
                return {
                    "success": True,
                    "user_id": user_id,
                    "insights": {
                        "total_memories": 0,
                        "message": "No memories found for analysis."
                    }
                }
            
            insights = {}
            
            if insight_type in ["comprehensive", "engagement"]:
                insights["engagement"] = self._calculate_engagement_metrics(memories)
            
            if insight_type in ["comprehensive", "topics"]:
                insights["topics"] = self._analyze_topic_distribution(memories)
            
            if insight_type in ["comprehensive", "sessions"]:
                insights["sessions"] = self._analyze_session_patterns(memories)
            
            if insight_type == "comprehensive":
                insights["temporal"] = self._analyze_temporal_distribution(memories)
                insights["patterns"] = self._identify_memory_patterns(memories)
            
            return {
                "success": True,
                "user_id": user_id,
                "insight_type": insight_type,
                "total_memories": len(memories),
                "insights": insights
            }
        except Exception as e:
            logger.error(f"Error getting memory insights: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods for advanced analysis

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

    def _analyze_temporal_distribution(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal distribution of memories."""
        try:
            distribution = {
                "hour": {},
                "day": {},
                "week": {},
                "month": {}
            }
            
            for memory in memories:
                created_at = memory.get("created_at")
                if not created_at:
                    continue
                
                if isinstance(created_at, str):
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_time = created_at
                
                # Hour distribution
                hour = created_time.strftime("%H")
                distribution["hour"][hour] = distribution["hour"].get(hour, 0) + 1
                
                # Day distribution
                day = created_time.strftime("%A")
                distribution["day"][day] = distribution["day"].get(day, 0) + 1
                
                # Week distribution (week number)
                week = created_time.strftime("%U")
                distribution["week"][week] = distribution["week"].get(week, 0) + 1
                
                # Month distribution
                month = created_time.strftime("%B")
                distribution["month"][month] = distribution["month"].get(month, 0) + 1
            
            return distribution
        except Exception as e:
            logger.error(f"Error analyzing temporal distribution: {e}")
            return {}

    def _analyze_session_patterns(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze session patterns in memories."""
        try:
            sessions = {}
            
            for memory in memories:
                session_id = memory.get("session_id", "unknown")
                if session_id not in sessions:
                    sessions[session_id] = {
                        "memory_count": 0,
                        "memory_types": {},
                        "duration": None,
                        "first_memory": None,
                        "last_memory": None
                    }
                
                sessions[session_id]["memory_count"] += 1
                
                mem_type = memory.get("memory_type", "unknown")
                sessions[session_id]["memory_types"][mem_type] = sessions[session_id]["memory_types"].get(mem_type, 0) + 1
                
                created_at = memory.get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_time = created_at
                    
                    if sessions[session_id]["first_memory"] is None or created_time < sessions[session_id]["first_memory"]:
                        sessions[session_id]["first_memory"] = created_time
                    
                    if sessions[session_id]["last_memory"] is None or created_time > sessions[session_id]["last_memory"]:
                        sessions[session_id]["last_memory"] = created_time
            
            # Calculate session durations
            for session_data in sessions.values():
                if session_data["first_memory"] and session_data["last_memory"]:
                    duration = session_data["last_memory"] - session_data["first_memory"]
                    session_data["duration"] = duration.total_seconds() / 60  # in minutes
            
            return {
                "total_sessions": len(sessions),
                "avg_memories_per_session": sum(s["memory_count"] for s in sessions.values()) / len(sessions) if sessions else 0,
                "avg_session_duration": sum(s["duration"] or 0 for s in sessions.values()) / len(sessions) if sessions else 0,
                "session_details": sessions
            }
        except Exception as e:
            logger.error(f"Error analyzing session patterns: {e}")
            return {}

    def _calculate_engagement_metrics(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate engagement metrics for memories."""
        try:
            if not memories:
                return {
                    "total_memories": 0,
                    "avg_memories_per_day": 0,
                    "most_active_day": None,
                    "memory_type_distribution": {},
                    "engagement_score": 0.0
                }
            
            # Memory type distribution
            memory_types = {}
            for memory in memories:
                mem_type = memory.get("memory_type", "unknown")
                memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
            
            # Calculate daily activity
            daily_activity = {}
            for memory in memories:
                created_at = memory.get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_time = created_at
                    
                    date = created_time.strftime("%Y-%m-%d")
                    daily_activity[date] = daily_activity.get(date, 0) + 1
            
            # Find most active day
            most_active_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else None
            
            # Calculate engagement score
            total_days = len(daily_activity)
            total_memories = len(memories)
            avg_memories_per_day = total_memories / total_days if total_days > 0 else 0
            
            # Simple engagement score based on activity consistency
            engagement_score = min(1.0, avg_memories_per_day / 5.0)  # Normalize to 0-1
            
            return {
                "total_memories": total_memories,
                "total_active_days": total_days,
                "avg_memories_per_day": avg_memories_per_day,
                "most_active_day": most_active_day,
                "memory_type_distribution": memory_types,
                "engagement_score": engagement_score
            }
        except Exception as e:
            logger.error(f"Error calculating engagement metrics: {e}")
            return {}

    def _analyze_topic_distribution(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze topic distribution in memories."""
        try:
            # Simple keyword-based topic analysis
            topic_keywords = {
                "questions": ["what", "how", "why", "when", "where", "who", "?"],
                "instructions": ["help", "show", "explain", "tell", "guide"],
                "preferences": ["like", "prefer", "favorite", "best", "want"],
                "facts": ["is", "are", "was", "were", "has", "have"],
                "conversation": ["said", "talked", "discussed", "mentioned"]
            }
            
            topic_counts = {topic: 0 for topic in topic_keywords}
            
            for memory in memories:
                content = memory.get("memory", "").lower()
                
                for topic, keywords in topic_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        topic_counts[topic] += 1
            
            # Find dominant topics
            dominant_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "topic_distribution": topic_counts,
                "dominant_topics": dominant_topics[:3],
                "total_topics_identified": sum(topic_counts.values())
            }
        except Exception as e:
            logger.error(f"Error analyzing topic distribution: {e}")
            return {}

    def _identify_memory_patterns(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify patterns in memory creation and usage."""
        try:
            patterns = {
                "creation_patterns": {},
                "content_patterns": {},
                "session_patterns": {}
            }
            
            # Analyze creation patterns
            creation_times = []
            for memory in memories:
                created_at = memory.get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_time = created_at
                    creation_times.append(created_time.hour)
            
            if creation_times:
                # Find peak activity hours
                hour_counts = {}
                for hour in creation_times:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                
                peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                patterns["creation_patterns"]["peak_hours"] = peak_hours
            
            # Analyze content patterns
            content_lengths = [len(memory.get("memory", "")) for memory in memories]
            if content_lengths:
                patterns["content_patterns"] = {
                    "avg_length": sum(content_lengths) / len(content_lengths),
                    "min_length": min(content_lengths),
                    "max_length": max(content_lengths)
                }
            
            # Analyze session patterns
            session_memory_counts = {}
            for memory in memories:
                session_id = memory.get("session_id", "unknown")
                session_memory_counts[session_id] = session_memory_counts.get(session_id, 0) + 1
            
            if session_memory_counts:
                patterns["session_patterns"] = {
                    "avg_memories_per_session": sum(session_memory_counts.values()) / len(session_memory_counts),
                    "session_count": len(session_memory_counts)
                }
            
            return patterns
        except Exception as e:
            logger.error(f"Error identifying memory patterns: {e}")
            return {} 