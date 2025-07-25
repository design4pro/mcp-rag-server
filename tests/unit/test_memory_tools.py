"""
Unit tests for memory tools.

This module tests the memory management tools functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from mcp_rag_server.tools.memory_tools import MemoryTools


class TestMemoryTools:
    """Test cases for MemoryTools class."""
    
    @pytest.fixture
    def mock_mem0_service(self):
        """Create a mock Mem0Service."""
        service = Mock()
        service.add_memory = AsyncMock(return_value="test-memory-id")
        service.delete_memory = AsyncMock(return_value=True)
        
        # Fix method names to match what MemoryTools actually calls
        service.get_memories = AsyncMock(return_value=[
            {
                "memory_id": "mem1",
                "memory": "Test memory 1",
                "memory_type": "conversation",
                "created_at": datetime.now().isoformat(),
                "session_id": "session1"
            },
            {
                "memory_id": "mem2",
                "memory": "Test memory 2",
                "memory_type": "question",
                "created_at": datetime.now().isoformat(),
                "session_id": "session1"
            }
        ])
        
        # Add get_user_memories for advanced tools and session info
        service.get_user_memories = AsyncMock(return_value=[
            {
                "memory_id": "mem1",
                "memory": "Test memory 1",
                "memory_type": "conversation",
                "created_at": datetime.now().isoformat(),
                "session_id": "session1"
            },
            {
                "memory_id": "mem2",
                "memory": "Test memory 2",
                "memory_type": "question",
                "created_at": datetime.now().isoformat(),
                "session_id": "session1"
            }
        ])
        
        service.clear_memories = AsyncMock(return_value=True)
        service.get_relevant_memories = AsyncMock(return_value=[
            {"memory": "Previous conversation", "relevance": 0.8}
        ])
        service.format_memory_context = AsyncMock(return_value="Previous conversation")
        service.search_memories_advanced = AsyncMock(return_value=[
            {
                "memory_id": "mem1",
                "content": "Test memory 1",
                "relevance_score": 0.9,
                "confidence": 0.8,
                "memory_type": "conversation"
            }
        ])
        service.generate_context_summary = AsyncMock(return_value="Test context summary")
        service.cluster_memories = AsyncMock(return_value=[
            {
                "cluster_id": "cluster1",
                "topic": "Test topic",
                "memories": [{"memory_id": "mem1", "memory": "Test memory"}],
                "size": 1,
                "avg_relevance": 0.8
            }
        ])
        
        return service
    
    @pytest.fixture
    def mock_rag_service(self):
        """Create a mock RAGService."""
        service = Mock()
        service.ask_question = AsyncMock(return_value={"answer": "Test answer"})
        return service
    
    @pytest.fixture
    def memory_tools(self, mock_mem0_service, mock_rag_service):
        """Create MemoryTools instance with mocked services."""
        return MemoryTools(mock_mem0_service, mock_rag_service)

    # Basic Memory Tools Tests

    async def test_add_memory_success(self, memory_tools):
        """Test successful memory addition."""
        result = await memory_tools.add_memory(
            "test-user", "Test memory content", "conversation"
        )
        
        assert result["success"] is True
        assert result["memory_id"] == "test-memory-id"
        assert result["user_id"] == "test-user"
        assert result["memory_type"] == "conversation"

    async def test_add_memory_validation_error(self, memory_tools):
        """Test memory addition with validation error."""
        result = await memory_tools.add_memory("", "", "conversation")
        
        assert result["success"] is False
        assert "error" in result

    async def test_add_memory_service_error(self, memory_tools, mock_mem0_service):
        """Test memory addition with service error."""
        mock_mem0_service.add_memory.side_effect = Exception("Service error")
        
        result = await memory_tools.add_memory(
            "test-user", "Test memory content", "conversation"
        )
        
        assert result["success"] is False
        assert "error" in result

    async def test_get_user_memories_success(self, memory_tools):
        """Test successful memory retrieval."""
        result = await memory_tools.get_user_memories("test-user", limit=10)
        
        assert result["success"] is True
        assert "memories" in result
        assert result["count"] == 2
        assert result["user_id"] == "test-user"

    async def test_get_user_memories_service_error(self, memory_tools, mock_mem0_service):
        """Test memory retrieval with service error."""
        mock_mem0_service.get_memories.side_effect = Exception("Service error")
    
        result = await memory_tools.get_user_memories("test-user", limit=10)
    
        assert result["success"] is False
        assert "error" in result

    async def test_delete_memory_success(self, memory_tools):
        """Test successful memory deletion."""
        result = await memory_tools.delete_memory("test-memory-id", "test-user")
        
        assert result["success"] is True
        assert result["memory_id"] == "test-memory-id"
        assert result["user_id"] == "test-user"

    async def test_delete_memory_service_error(self, memory_tools, mock_mem0_service):
        """Test memory deletion with service error."""
        mock_mem0_service.delete_memory.side_effect = Exception("Service error")
        
        result = await memory_tools.delete_memory("test-memory-id", "test-user")
        
        assert result["success"] is False
        assert "error" in result

    async def test_clear_user_memories_success(self, memory_tools):
        """Test successful memory clearing."""
        result = await memory_tools.clear_user_memories("test-user")
        
        assert result["success"] is True
        assert result["user_id"] == "test-user"

    async def test_clear_user_memories_service_error(self, memory_tools, mock_mem0_service):
        """Test memory clearing with service error."""
        mock_mem0_service.clear_memories.side_effect = Exception("Service error")
    
        result = await memory_tools.clear_user_memories("test-user")
    
        assert result["success"] is False
        assert "error" in result

    async def test_get_memory_context_success(self, memory_tools):
        """Test successful memory context retrieval."""
        result = await memory_tools.get_memory_context("test-user", "test query", limit=5)
        
        assert result["success"] is True
        assert "context" in result
        assert result["user_id"] == "test-user"
        assert result["query"] == "test query"

    async def test_get_memory_context_service_error(self, memory_tools, mock_mem0_service):
        """Test memory context retrieval with service error."""
        mock_mem0_service.get_relevant_memories.side_effect = Exception("Service error")
    
        result = await memory_tools.get_memory_context("test-user", "test query", limit=5)
    
        assert result["success"] is False
        assert "error" in result

    async def test_get_user_session_info_success(self, memory_tools):
        """Test successful user session info retrieval."""
        result = await memory_tools.get_user_session_info("test-user")
        
        assert result["success"] is True
        assert "total_sessions" in result
        assert "sessions" in result
        assert result["user_id"] == "test-user"

    async def test_get_user_session_info_service_error(self, memory_tools, mock_mem0_service):
        """Test user session info retrieval with service error."""
        mock_mem0_service.get_user_memories.side_effect = Exception("Service error")
        
        result = await memory_tools.get_user_session_info("test-user")
        
        assert result["success"] is False
        assert "error" in result

    # Advanced Memory Context Retrieval Tests (Task 3)

    async def test_search_memories_advanced_success(self, memory_tools):
        """Test successful advanced memory search."""
        search_options = {
            "search_strategy": "hierarchical",
            "limit": 5,
            "min_confidence": 0.1
        }
        
        result = await memory_tools.search_memories_advanced(
            "test-user", "test query", search_options
        )
        
        assert result["success"] is True
        assert "results" in result
        assert "count" in result
        assert result["user_id"] == "test-user"
        assert result["query"] == "test query"
        assert result["search_options"] == search_options

    async def test_search_memories_advanced_validation_error(self, memory_tools):
        """Test advanced memory search with validation error."""
        result = await memory_tools.search_memories_advanced("", "", {})
        
        assert result["success"] is False
        assert "error" in result

    async def test_search_memories_advanced_service_error(self, memory_tools, mock_mem0_service):
        """Test advanced memory search with service error."""
        mock_mem0_service.search_memories_advanced.side_effect = Exception("Service error")
        
        result = await memory_tools.search_memories_advanced(
            "test-user", "test query", {"limit": 5}
        )
        
        assert result["success"] is False
        assert "error" in result

    async def test_get_enhanced_memory_context_success(self, memory_tools):
        """Test successful enhanced memory context retrieval."""
        context_options = {
            "summary_type": "key_points",
            "include_relevance": True,
            "limit": 10
        }
        
        result = await memory_tools.get_enhanced_memory_context(
            "test-user", "test query", context_options
        )
        
        assert result["success"] is True
        assert "context" in result
        assert "memory_count" in result
        assert "summary_type" in result
        assert result["user_id"] == "test-user"
        assert result["query"] == "test query"
        assert result["context_options"] == context_options

    async def test_get_enhanced_memory_context_no_memories(self, memory_tools, mock_mem0_service):
        """Test enhanced memory context with no memories."""
        mock_mem0_service.search_memories_advanced.return_value = []
        
        result = await memory_tools.get_enhanced_memory_context(
            "test-user", "test query", {"limit": 10}
        )
        
        assert result["success"] is True
        assert result["context"] == "No relevant memories found."
        assert result["memory_count"] == 0

    async def test_get_enhanced_memory_context_validation_error(self, memory_tools):
        """Test enhanced memory context with validation error."""
        result = await memory_tools.get_enhanced_memory_context("", "", {})
        
        assert result["success"] is False
        assert "error" in result

    async def test_get_enhanced_memory_context_service_error(self, memory_tools, mock_mem0_service):
        """Test enhanced memory context with service error."""
        mock_mem0_service.search_memories_advanced.side_effect = Exception("Service error")
        
        result = await memory_tools.get_enhanced_memory_context(
            "test-user", "test query", {"limit": 10}
        )
        
        assert result["success"] is False
        assert "error" in result

    async def test_analyze_memory_patterns_success(self, memory_tools):
        """Test successful memory pattern analysis."""
        result = await memory_tools.analyze_memory_patterns("test-user", "week")
        
        assert result["success"] is True
        assert "patterns" in result
        assert result["user_id"] == "test-user"
        assert result["time_range"] == "week"
        
        patterns = result["patterns"]
        assert "total_memories" in patterns
        assert "memory_types" in patterns
        assert "temporal_distribution" in patterns
        assert "session_analysis" in patterns
        assert "engagement_metrics" in patterns

    async def test_analyze_memory_patterns_no_memories(self, memory_tools, mock_mem0_service):
        """Test memory pattern analysis with no memories."""
        mock_mem0_service.get_user_memories = AsyncMock(return_value=[])
        
        result = await memory_tools.analyze_memory_patterns("test-user", "week")
        
        assert result["success"] is True
        assert result["patterns"]["total_memories"] == 0

    async def test_analyze_memory_patterns_validation_error(self, memory_tools):
        """Test memory pattern analysis with validation error."""
        result = await memory_tools.analyze_memory_patterns("", "invalid_range")
        
        assert result["success"] is False
        assert "error" in result

    async def test_analyze_memory_patterns_service_error(self, memory_tools, mock_mem0_service):
        """Test memory pattern analysis with service error."""
        mock_mem0_service.get_user_memories.side_effect = Exception("Service error")
        
        result = await memory_tools.analyze_memory_patterns("test-user", "week")
        
        assert result["success"] is False
        assert "error" in result

    async def test_cluster_user_memories_success(self, memory_tools):
        """Test successful memory clustering."""
        cluster_options = {
            "cluster_type": "topic",
            "max_clusters": 5,
            "similarity_threshold": 0.7
        }
        
        result = await memory_tools.cluster_user_memories("test-user", cluster_options)
        
        assert result["success"] is True
        assert "clusters" in result
        assert "cluster_count" in result
        assert "total_memories" in result
        assert result["user_id"] == "test-user"
        assert result["cluster_options"] == cluster_options

    async def test_cluster_user_memories_no_memories(self, memory_tools, mock_mem0_service):
        """Test memory clustering with no memories."""
        mock_mem0_service.get_user_memories = AsyncMock(return_value=[])
        
        result = await memory_tools.cluster_user_memories("test-user", {})
        
        assert result["success"] is True
        assert result["clusters"] == []
        assert result["cluster_count"] == 0

    async def test_cluster_user_memories_validation_error(self, memory_tools):
        """Test memory clustering with validation error."""
        result = await memory_tools.cluster_user_memories("", {"cluster_type": "invalid"})
        
        assert result["success"] is False
        assert "error" in result

    async def test_cluster_user_memories_service_error(self, memory_tools, mock_mem0_service):
        """Test memory clustering with service error."""
        mock_mem0_service.cluster_memories.side_effect = Exception("Service error")
        
        result = await memory_tools.cluster_user_memories("test-user", {})
        
        assert result["success"] is False
        assert "error" in result

    async def test_get_memory_insights_comprehensive(self, memory_tools):
        """Test comprehensive memory insights."""
        result = await memory_tools.get_memory_insights("test-user", "comprehensive")
        
        assert result["success"] is True
        assert "insights" in result
        assert "total_memories" in result
        assert result["user_id"] == "test-user"
        assert result["insight_type"] == "comprehensive"
        
        insights = result["insights"]
        assert "engagement" in insights
        assert "topics" in insights
        assert "sessions" in insights
        assert "temporal" in insights
        assert "patterns" in insights

    async def test_get_memory_insights_engagement_only(self, memory_tools):
        """Test engagement-only memory insights."""
        result = await memory_tools.get_memory_insights("test-user", "engagement")
        
        assert result["success"] is True
        assert "insights" in result
        assert "engagement" in result["insights"]
        assert "topics" not in result["insights"]
        assert "sessions" not in result["insights"]

    async def test_get_memory_insights_no_memories(self, memory_tools, mock_mem0_service):
        """Test memory insights with no memories."""
        mock_mem0_service.get_user_memories = AsyncMock(return_value=[])
        
        result = await memory_tools.get_memory_insights("test-user", "comprehensive")
        
        assert result["success"] is True
        assert result["insights"]["total_memories"] == 0
        assert "message" in result["insights"]

    async def test_get_memory_insights_validation_error(self, memory_tools):
        """Test memory insights with validation error."""
        result = await memory_tools.get_memory_insights("", "invalid_type")
        
        assert result["success"] is False
        assert "error" in result

    async def test_get_memory_insights_service_error(self, memory_tools, mock_mem0_service):
        """Test memory insights with service error."""
        mock_mem0_service.get_user_memories.side_effect = Exception("Service error")
        
        result = await memory_tools.get_memory_insights("test-user", "comprehensive")
        
        assert result["success"] is False
        assert "error" in result

    # Helper Method Tests

    def test_is_memory_in_time_range_hour(self, memory_tools):
        """Test time range filtering for hour."""
        memory = {"created_at": datetime.now().isoformat()}
        
        assert memory_tools._is_memory_in_time_range(memory, "hour") is True

    def test_is_memory_in_time_range_day(self, memory_tools):
        """Test time range filtering for day."""
        memory = {"created_at": datetime.now().isoformat()}
        
        assert memory_tools._is_memory_in_time_range(memory, "day") is True

    def test_is_memory_in_time_range_old_memory(self, memory_tools):
        """Test time range filtering for old memory."""
        old_time = (datetime.now() - timedelta(days=2)).isoformat()
        memory = {"created_at": old_time}
        
        assert memory_tools._is_memory_in_time_range(memory, "day") is False
        assert memory_tools._is_memory_in_time_range(memory, "week") is True

    def test_analyze_temporal_distribution(self, memory_tools):
        """Test temporal distribution analysis."""
        memories = [
            {"created_at": datetime.now().isoformat()},
            {"created_at": (datetime.now() - timedelta(hours=1)).isoformat()}
        ]
        
        distribution = memory_tools._analyze_temporal_distribution(memories)
        
        assert "hour" in distribution
        assert "day" in distribution
        assert "week" in distribution
        assert "month" in distribution

    def test_analyze_session_patterns(self, memory_tools):
        """Test session pattern analysis."""
        memories = [
            {
                "session_id": "session1",
                "memory_type": "conversation",
                "created_at": datetime.now().isoformat()
            },
            {
                "session_id": "session1",
                "memory_type": "question",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        patterns = memory_tools._analyze_session_patterns(memories)
        
        assert "total_sessions" in patterns
        assert "avg_memories_per_session" in patterns
        assert "avg_session_duration" in patterns
        assert "session_details" in patterns

    def test_calculate_engagement_metrics(self, memory_tools):
        """Test engagement metrics calculation."""
        memories = [
            {
                "memory_type": "conversation",
                "created_at": datetime.now().isoformat()
            },
            {
                "memory_type": "question",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        metrics = memory_tools._calculate_engagement_metrics(memories)
        
        assert "total_memories" in metrics
        assert "total_active_days" in metrics
        assert "avg_memories_per_day" in metrics
        assert "memory_type_distribution" in metrics
        assert "engagement_score" in metrics

    def test_calculate_engagement_metrics_no_memories(self, memory_tools):
        """Test engagement metrics with no memories."""
        metrics = memory_tools._calculate_engagement_metrics([])
        
        assert metrics["total_memories"] == 0
        assert metrics["avg_memories_per_day"] == 0
        assert metrics["engagement_score"] == 0.0

    def test_analyze_topic_distribution(self, memory_tools):
        """Test topic distribution analysis."""
        memories = [
            {"memory": "What is Python?"},
            {"memory": "How to use Python for data science?"},
            {"memory": "I like Python programming"}
        ]
        
        topics = memory_tools._analyze_topic_distribution(memories)
        
        assert "topic_distribution" in topics
        assert "dominant_topics" in topics
        assert "total_topics_identified" in topics

    def test_identify_memory_patterns(self, memory_tools):
        """Test memory pattern identification."""
        memories = [
            {
                "memory": "Test memory 1",
                "created_at": datetime.now().isoformat(),
                "session_id": "session1"
            },
            {
                "memory": "Test memory 2",
                "created_at": datetime.now().isoformat(),
                "session_id": "session1"
            }
        ]
        
        patterns = memory_tools._identify_memory_patterns(memories)
        
        assert "creation_patterns" in patterns
        assert "content_patterns" in patterns
        assert "session_patterns" in patterns

    # Error Handling Tests

    async def test_memory_tools_no_mem0_service(self, mock_rag_service):
        """Test memory tools without Mem0Service."""
        memory_tools = MemoryTools(None, mock_rag_service)
        
        result = await memory_tools.add_memory("test-user", "test content", "conversation")
        
        assert result["success"] is False
        assert "Mem0 service not initialized" in result["error"]

    async def test_memory_tools_no_rag_service(self, mock_mem0_service):
        """Test memory tools without RAGService."""
        memory_tools = MemoryTools(mock_mem0_service, None)
        
        # This should still work as RAG service is not required for basic memory operations
        result = await memory_tools.add_memory("test-user", "test content", "conversation")
        
        assert result["success"] is True 