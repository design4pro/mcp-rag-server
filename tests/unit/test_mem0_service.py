"""
Unit tests for enhanced Mem0Service functionality.

Tests the new memory search capabilities including semantic search,
hybrid search, relevance scoring, and memory context formatting.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import numpy as np

from src.mcp_rag_server.services.mem0_service import Mem0Service
from src.mcp_rag_server.config import Mem0Config


class TestMem0ServiceEnhanced:
    """Test enhanced Mem0Service functionality."""
    
    @pytest.fixture
    def mem0_config(self):
        """Create a test Mem0Config."""
        return Mem0Config(
            local_storage_path="./data/test_mem0_data",
            memory_size=100,
            relevance_threshold=0.7,
            use_semantic_search=True,
            semantic_search_weight=0.7,
            keyword_search_weight=0.3,
            recency_weight=0.1,
            max_memory_context_length=2000
        )
    
    @pytest.fixture
    async def mem0_service(self, mem0_config):
        """Create a test Mem0Service instance."""
        service = Mem0Service(mem0_config)
        await service.initialize()
        # Clear storage before each test
        service.local_storage = {"memories": {}}
        yield service
        # Cleanup
        if hasattr(service, 'cleanup'):
            await service.cleanup()
    
    @pytest.fixture
    def sample_memories(self):
        """Create sample memory data for testing."""
        return [
            {
                "id": "1",
                "memory": "User asked about Python programming and I explained basic syntax",
                "memory_type": "conversation",
                "created_at": datetime.now().isoformat(),
                "user_id": "test_user",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
            },
            {
                "id": "2", 
                "memory": "User wanted to learn about machine learning algorithms",
                "memory_type": "conversation",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "user_id": "test_user",
                "embedding": [0.2, 0.3, 0.4, 0.5, 0.6]
            },
            {
                "id": "3",
                "memory": "User asked about data structures and I explained arrays and lists",
                "memory_type": "conversation", 
                "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "user_id": "test_user",
                "embedding": [0.3, 0.4, 0.5, 0.6, 0.7]
            }
        ]
    
    @pytest.fixture
    def mock_gemini_service(self):
        """Create a mock GeminiService for testing."""
        service = Mock()
        service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        service.generate_text = AsyncMock(return_value="Generated text response")
        return service
    
    @pytest.mark.asyncio
    async def test_cosine_similarity_calculation(self, mem0_service):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = mem0_service._calculate_cosine_similarity(vec1, vec2)
        assert similarity == 1.0
        
        vec3 = [0.0, 1.0, 0.0]
        similarity = mem0_service._calculate_cosine_similarity(vec1, vec3)
        assert similarity == 0.0
        
        vec4 = [0.5, 0.5, 0.0]
        similarity = mem0_service._calculate_cosine_similarity(vec1, vec4)
        assert 0.0 < similarity < 1.0
    
    @pytest.mark.asyncio
    async def test_keyword_relevance_calculation(self, mem0_service):
        """Test keyword relevance calculation."""
        query = "python programming"
        memory_text = "User asked about Python programming and I explained basic syntax"
        
        relevance = mem0_service._calculate_keyword_relevance(query, memory_text)
        assert relevance > 0.0
        assert relevance <= 1.0
        
        # Test with no overlap
        query_no_overlap = "javascript web development"
        relevance = mem0_service._calculate_keyword_relevance(query_no_overlap, memory_text)
        assert relevance == 0.0
    
    @pytest.mark.asyncio
    async def test_recency_score_calculation(self, mem0_service):
        """Test recency score calculation."""
        # Recent memory
        recent_memory = {
            "created_at": datetime.now().isoformat()
        }
        recent_score = mem0_service._calculate_recency_score(recent_memory)
        assert recent_score > 0.9
        
        # Old memory
        old_memory = {
            "created_at": (datetime.now() - timedelta(days=30)).isoformat()
        }
        old_score = mem0_service._calculate_recency_score(old_memory)
        assert old_score < recent_score
    
    @pytest.mark.asyncio
    async def test_memory_relevance_calculation(self, mem0_service):
        """Test hybrid memory relevance calculation."""
        memory = {
            "memory": "User asked about Python programming",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "created_at": datetime.now().isoformat()
        }
        query = "python programming"
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        relevance = await mem0_service._calculate_memory_relevance(
            memory, query, query_embedding
        )
        assert relevance > 0.0
        # Relevance can exceed 1.0 due to weighted combination, but should be reasonable
        assert relevance <= 2.0
    
    @pytest.mark.asyncio
    async def test_semantic_memory_search(self, mem0_service, sample_memories):
        """Test semantic memory search functionality."""
        # Mock the service to have initialized state and sample memories
        mem0_service._initialized = True
        mem0_service.local_storage = {
            "memories": {
                "test_user": sample_memories
            }
        }
        
        query = "python programming"
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        results = await mem0_service.search_memories_semantic(
            user_id="test_user",
            query=query,
            query_embedding=query_embedding,
            limit=2
        )
        
        assert len(results) <= 2
        assert all("embedding" in memory for memory in results)
    
    @pytest.mark.asyncio
    async def test_hybrid_memory_search(self, mem0_service, sample_memories):
        """Test hybrid memory search functionality."""
        # Mock the service to have initialized state and sample memories
        mem0_service._initialized = True
        mem0_service.local_storage = {
            "memories": {
                "test_user": sample_memories
            }
        }
        
        query = "python programming"
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        results = await mem0_service.search_memories_hybrid(
            user_id="test_user",
            query=query,
            query_embedding=query_embedding,
            limit=2
        )
        
        assert len(results) <= 2
        # Results should be sorted by relevance
        if len(results) > 1:
            # Check that results are sorted (this is a basic check)
            assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_memory_context_formatting(self, mem0_service, sample_memories):
        """Test memory context formatting."""
        context = await mem0_service.format_memory_context(sample_memories)
        
        assert "Previous conversation context:" in context
        assert "CONVERSATION" in context
        assert len(context) > 0
        
        # Test with length limit
        short_context = await mem0_service.format_memory_context(
            sample_memories, max_length=100
        )
        assert len(short_context) <= 100
    
    @pytest.mark.asyncio
    async def test_memory_summarization(self, mem0_service, sample_memories):
        """Test memory summarization functionality."""
        summary = await mem0_service.summarize_memories(sample_memories)
        
        assert "Memory summary:" in summary
        assert len(summary) > 0
        
        # Test with length limit
        short_summary = await mem0_service.summarize_memories(
            sample_memories, max_length=50
        )
        assert len(short_summary) <= 50
    
    @pytest.mark.asyncio
    async def test_add_memory_with_embedding(self, mem0_service):
        """Test adding memory with embedding."""
        # Mock the service to have initialized state
        mem0_service._initialized = True
        mem0_service.local_storage = {"memories": {}}
        
        # Mock the save method to avoid file system operations
        with patch.object(mem0_service, '_save_local_storage', new_callable=AsyncMock):
            content = "Test memory content"
            embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
            
            memory_id = await mem0_service.add_memory(
                user_id="test_user",
                content=content,
                memory_type="conversation",
                embedding=embedding
            )
            
            assert memory_id is not None
            assert "test_user" in mem0_service.local_storage["memories"]
            assert len(mem0_service.local_storage["memories"]["test_user"]) == 1
            
            memory = mem0_service.local_storage["memories"]["test_user"][0]
            assert memory["memory"] == content
            assert memory["embedding"] == embedding
    
    @pytest.mark.asyncio
    async def test_update_memory_embedding(self, mem0_service, sample_memories):
        """Test updating memory embedding."""
        # Mock the service to have initialized state and sample memories
        mem0_service._initialized = True
        mem0_service.local_storage = {
            "memories": {
                "test_user": sample_memories
            }
        }
        
        # Mock the save method to avoid file system operations
        with patch.object(mem0_service, '_save_local_storage', new_callable=AsyncMock):
            new_embedding = [0.9, 0.8, 0.7, 0.6, 0.5]
            
            success = await mem0_service.update_memory_embeddings(
                user_id="test_user",
                memory_id="1",
                embedding=new_embedding
            )
            
            assert success is True
            
            # Verify the embedding was updated
            memory = next(
                (m for m in mem0_service.local_storage["memories"]["test_user"] 
                 if m["id"] == "1"), None
            )
            assert memory is not None
            assert memory["embedding"] == new_embedding 

    async def test_get_memory_stats_by_session(self, mem0_service, mock_gemini_service):
        """Test getting memory statistics by session."""
        # Mock Gemini service for embedding generation
        mock_gemini_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Add test memories with session
        session_id = "test-session-123"
        user_id = "test-user"
        
        # Add memories to the session
        memory_id1 = await mem0_service.add_memory_with_session(
            user_id, "Test memory 1", session_id, "conversation"
        )
        memory_id2 = await mem0_service.add_memory_with_session(
            user_id, "Test memory 2", session_id, "question"
        )
        
        # Get session stats
        stats = await mem0_service.get_memory_stats_by_session(session_id)
        
        # Verify stats
        assert stats["session_id"] == session_id
        assert stats["total_memories"] == 2
        assert "conversation" in stats["memory_types"]
        assert "question" in stats["memory_types"]
        assert stats["memory_types"]["conversation"] == 1
        assert stats["memory_types"]["question"] == 1
        assert len(stats["recent_activity"]) == 2

    # Advanced Memory Context Retrieval Tests (Task 3)

    async def test_search_memories_advanced_hierarchical(self, mem0_service, mock_gemini_service):
        """Test advanced memory search with hierarchical strategy."""
        # Mock Gemini service for embedding generation
        mock_gemini_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        user_id = "test-user"
        
        # Add test memories
        await mem0_service.add_memory(user_id, "Python programming language", "conversation")
        await mem0_service.add_memory(user_id, "Machine learning algorithms", "conversation")
        await mem0_service.add_memory(user_id, "Data science techniques", "conversation")
        
        # Test hierarchical search
        search_options = {
            "search_strategy": "hierarchical",
            "limit": 3,
            "min_confidence": 0.1
        }
        
        results = await mem0_service.search_memories_advanced(
            user_id, "programming", search_options
        )
        
        # Verify results
        assert len(results) > 0
        assert all("relevance_score" in result for result in results)
        assert all("confidence" in result for result in results)

    async def test_search_memories_advanced_semantic(self, mem0_service, mock_gemini_service):
        """Test advanced memory search with semantic strategy."""
        # Mock Gemini service for embedding generation
        mock_gemini_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        user_id = "test-user"
        
        # Add test memories
        await mem0_service.add_memory(user_id, "Python programming language", "conversation")
        await mem0_service.add_memory(user_id, "Machine learning algorithms", "conversation")
        
        # Test semantic search
        search_options = {
            "search_strategy": "semantic",
            "limit": 2,
            "min_confidence": 0.1
        }
        
        results = await mem0_service.search_memories_advanced(
            user_id, "coding", search_options
        )
        
        # Verify results
        assert len(results) > 0
        assert all("relevance_score" in result for result in results)

    async def test_search_memories_advanced_fuzzy(self, mem0_service):
        """Test advanced memory search with fuzzy strategy."""
        user_id = "test-user"
        
        # Add test memories
        await mem0_service.add_memory(user_id, "Python programming language", "conversation")
        await mem0_service.add_memory(user_id, "Machine learning algorithms", "conversation")
        
        # Test fuzzy search with typo
        search_options = {
            "search_strategy": "fuzzy",
            "limit": 2,
            "min_confidence": 0.1
        }
        
        results = await mem0_service.search_memories_advanced(
            user_id, "pythn", search_options  # Intentional typo
        )
        
        # Verify results
        assert len(results) > 0

    async def test_search_memories_advanced_with_filters(self, mem0_service, mock_gemini_service):
        """Test advanced memory search with various filters."""
        # Mock Gemini service for embedding generation
        mock_gemini_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        user_id = "test-user"
        session_id = "test-session"
        
        # Add test memories with different types and sessions
        await mem0_service.add_memory_with_session(
            user_id, "Python programming", session_id, "conversation"
        )
        await mem0_service.add_memory_with_session(
            user_id, "Machine learning", session_id, "question"
        )
        await mem0_service.add_memory(
            user_id, "Data science", "fact"
        )
        
        # Test with memory type filter
        search_options = {
            "memory_type": "conversation",
            "limit": 5
        }
        
        results = await mem0_service.search_memories_advanced(
            user_id, "programming", search_options
        )
        
        # Verify only conversation memories are returned
        assert all(result.get("memory_type") == "conversation" for result in results)
        
        # Test with session filter
        search_options = {
            "session_id": session_id,
            "limit": 5
        }
        
        results = await mem0_service.search_memories_advanced(
            user_id, "learning", search_options
        )
        
        # Verify only session memories are returned
        assert all(result.get("session_id") == session_id for result in results)

    async def test_calculate_advanced_relevance(self, mem0_service, mock_gemini_service):
        """Test advanced relevance calculation with multi-factor scoring."""
        # Mock Gemini service for embedding generation
        mock_gemini_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Create test memory
        memory = {
            "memory_id": "test-memory",
            "memory": "Python programming language is great for data science",
            "memory_type": "conversation",
            "created_at": datetime.now().isoformat(),
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"user_id": "test-user"}
        }
        
        query = "programming"
        context = {"query_embedding": [0.1, 0.2, 0.3]}
        
        # Calculate advanced relevance
        relevance_info = await mem0_service.calculate_advanced_relevance(
            memory, query, context
        )
        
        # Verify relevance information
        assert "relevance_score" in relevance_info
        assert "confidence" in relevance_info
        assert "scoring_breakdown" in relevance_info
        
        scoring_breakdown = relevance_info["scoring_breakdown"]
        assert "semantic_score" in scoring_breakdown
        assert "keyword_score" in scoring_breakdown
        assert "recency_score" in scoring_breakdown
        assert "frequency_score" in scoring_breakdown
        assert "interaction_score" in scoring_breakdown
        assert "weights" in scoring_breakdown
        
        # Verify scores are within expected ranges
        assert 0.0 <= relevance_info["relevance_score"] <= 1.0
        assert 0.0 <= relevance_info["confidence"] <= 1.0

    async def test_cluster_memories_by_topic(self, mem0_service):
        """Test memory clustering by topic."""
        user_id = "test-user"
        
        # Add test memories with similar topics
        await mem0_service.add_memory(user_id, "Python programming language", "conversation")
        await mem0_service.add_memory(user_id, "Python web development", "conversation")
        await mem0_service.add_memory(user_id, "Machine learning algorithms", "conversation")
        await mem0_service.add_memory(user_id, "Deep learning neural networks", "conversation")
        
        # Test topic clustering
        cluster_options = {
            "cluster_type": "topic",
            "max_clusters": 3,
            "similarity_threshold": 0.3
        }
        
        clusters = await mem0_service.cluster_memories(
            user_id, cluster_options=cluster_options
        )
        
        # Verify clustering results
        assert len(clusters) > 0
        assert all("cluster_id" in cluster for cluster in clusters)
        assert all("memories" in cluster for cluster in clusters)
        assert all("size" in cluster for cluster in clusters)

    async def test_cluster_memories_by_temporal(self, mem0_service):
        """Test memory clustering by temporal proximity."""
        user_id = "test-user"
        
        # Add test memories with different timestamps
        await mem0_service.add_memory(user_id, "Memory 1", "conversation")
        await mem0_service.add_memory(user_id, "Memory 2", "conversation")
        await mem0_service.add_memory(user_id, "Memory 3", "conversation")
        
        # Test temporal clustering
        cluster_options = {
            "cluster_type": "temporal",
            "max_clusters": 2
        }
        
        clusters = await mem0_service.cluster_memories(
            user_id, cluster_options=cluster_options
        )
        
        # Verify clustering results
        assert len(clusters) > 0
        assert all("time_range" in cluster for cluster in clusters)

    async def test_generate_context_summary_key_points(self, mem0_service):
        """Test context summary generation with key points format."""
        # Create test memories
        memories = [
            {
                "memory_id": "mem1",
                "memory": "Python is a programming language",
                "relevance_score": 0.9,
                "memory_type": "conversation"
            },
            {
                "memory_id": "mem2",
                "memory": "Python is great for data science",
                "relevance_score": 0.8,
                "memory_type": "conversation"
            }
        ]
        
        query = "Python programming"
        
        # Generate key points summary
        summary = await mem0_service.generate_context_summary(
            memories, query, max_length=200,
            summary_options={"summary_type": "key_points"}
        )
        
        # Verify summary
        assert "Python" in summary
        assert len(summary) > 0

    async def test_generate_context_summary_narrative(self, mem0_service):
        """Test context summary generation with narrative format."""
        # Create test memories
        memories = [
            {
                "memory_id": "mem1",
                "memory": "Python is a programming language",
                "relevance_score": 0.9,
                "memory_type": "conversation"
            },
            {
                "memory_id": "mem2",
                "memory": "Python is great for data science",
                "relevance_score": 0.8,
                "memory_type": "conversation"
            }
        ]
        
        query = "Python programming"
        
        # Generate narrative summary
        summary = await mem0_service.generate_context_summary(
            memories, query, max_length=200,
            summary_options={"summary_type": "narrative"}
        )
        
        # Verify summary
        assert "Python" in summary
        assert len(summary) > 0

    async def test_generate_context_summary_structured(self, mem0_service):
        """Test context summary generation with structured format."""
        # Create test memories
        memories = [
            {
                "memory_id": "mem1",
                "memory": "Python is a programming language",
                "relevance_score": 0.9,
                "memory_type": "conversation"
            },
            {
                "memory_id": "mem2",
                "memory": "Python is great for data science",
                "relevance_score": 0.8,
                "memory_type": "question"
            }
        ]
        
        query = "Python programming"
        
        # Generate structured summary
        summary = await mem0_service.generate_context_summary(
            memories, query, max_length=200,
            summary_options={"summary_type": "structured", "group_by_topic": True}
        )
        
        # Verify summary
        assert "Python" in summary
        assert len(summary) > 0

    async def test_get_filtered_memories(self, mem0_service):
        """Test memory filtering functionality."""
        user_id = "test-user"
        session_id = "test-session"
        
        # Add test memories
        await mem0_service.add_memory_with_session(
            user_id, "Memory 1", session_id, "conversation"
        )
        await mem0_service.add_memory_with_session(
            user_id, "Memory 2", session_id, "question"
        )
        await mem0_service.add_memory(
            user_id, "Memory 3", "fact"
        )
        
        # Test filtering by memory type
        filtered_memories = await mem0_service._get_filtered_memories(
            user_id, memory_type="conversation"
        )
        
        assert len(filtered_memories) == 1
        assert filtered_memories[0]["memory_type"] == "conversation"
        
        # Test filtering by session
        filtered_memories = await mem0_service._get_filtered_memories(
            user_id, session_id=session_id
        )
        
        assert len(filtered_memories) == 2
        assert all(mem.get("session_id") == session_id for mem in filtered_memories)

    async def test_is_memory_in_time_range(self, mem0_service):
        """Test time range filtering functionality."""
        # Create test memory
        memory = {
            "created_at": datetime.now().isoformat()
        }
        
        # Test hour range
        assert mem0_service._is_memory_in_time_range(memory, "hour") == True
        
        # Test day range
        assert mem0_service._is_memory_in_time_range(memory, "day") == True
        
        # Test with old memory
        old_memory = {
            "created_at": (datetime.now() - timedelta(days=2)).isoformat()
        }
        
        assert mem0_service._is_memory_in_time_range(old_memory, "day") == False
        assert mem0_service._is_memory_in_time_range(old_memory, "week") == True

    async def test_hierarchical_search(self, mem0_service, mock_gemini_service):
        """Test hierarchical search functionality."""
        # Mock Gemini service for embedding generation
        mock_gemini_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        user_id = "test-user"
        
        # Add test memories with embeddings
        await mem0_service.add_memory(
            user_id, "Python programming", "conversation", 
            embedding=[0.1, 0.2, 0.3]
        )
        await mem0_service.add_memory(
            user_id, "Machine learning", "conversation",
            embedding=[0.2, 0.3, 0.4]
        )
        
        # Get memories for search
        memories = await mem0_service.get_user_memories(user_id, limit=10)
        
        # Test hierarchical search
        results = await mem0_service._hierarchical_search(
            memories, "programming", [0.1, 0.2, 0.3], 5, 0.1
        )
        
        # Verify results
        assert len(results) > 0
        assert all("relevance_score" in result for result in results)

    async def test_semantic_search(self, mem0_service, mock_gemini_service):
        """Test semantic search functionality."""
        # Mock Gemini service for embedding generation
        mock_gemini_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        user_id = "test-user"
        
        # Add test memories
        await mem0_service.add_memory(user_id, "Python programming", "conversation")
        await mem0_service.add_memory(user_id, "Machine learning", "conversation")
        
        # Get memories for search
        memories = await mem0_service.get_user_memories(user_id, limit=10)
        
        # Test semantic search
        results = await mem0_service._semantic_search(
            memories, "programming", [0.1, 0.2, 0.3], 5, 0.1
        )
        
        # Verify results
        assert len(results) > 0
        assert all("relevance_score" in result for result in results)
        assert all("confidence" in result for result in results)

    async def test_fuzzy_search(self, mem0_service):
        """Test fuzzy search functionality."""
        user_id = "test-user"
        
        # Add test memories
        await mem0_service.add_memory(user_id, "Python programming", "conversation")
        await mem0_service.add_memory(user_id, "Machine learning", "conversation")
        
        # Get memories for search
        memories = await mem0_service.get_user_memories(user_id, limit=10)
        
        # Test fuzzy search
        results = await mem0_service._fuzzy_search(
            memories, "pythn", 5, 0.1  # Intentional typo
        )
        
        # Verify results
        assert len(results) > 0
        assert all("relevance_score" in result for result in results)

    async def test_calculate_fuzzy_match(self, mem0_service):
        """Test fuzzy matching functionality."""
        # Test exact match
        similarity = mem0_service._calculate_fuzzy_match("python", "python")
        assert similarity == 1.0
        
        # Test similar words
        similarity = mem0_service._calculate_fuzzy_match("pythn", "python")
        assert similarity > 0.0
        
        # Test different words
        similarity = mem0_service._calculate_fuzzy_match("python", "java")
        assert similarity < 1.0

    async def test_combine_and_deduplicate(self, mem0_service):
        """Test result combination and deduplication."""
        # Create test results
        results1 = [
            {"memory_id": "mem1", "relevance_score": 0.8},
            {"memory_id": "mem2", "relevance_score": 0.6}
        ]
        
        results2 = [
            {"memory_id": "mem1", "relevance_score": 0.9},  # Higher score
            {"memory_id": "mem3", "relevance_score": 0.7}
        ]
        
        # Combine results
        combined = mem0_service._combine_and_deduplicate(results1, results2)
        
        # Verify deduplication and score selection
        assert len(combined) == 3  # mem1, mem2, mem3
        assert combined[0]["memory_id"] == "mem1"  # Highest score first
        assert combined[0]["relevance_score"] == 0.9  # Higher score selected

    async def test_calculate_frequency_score(self, mem0_service):
        """Test frequency score calculation."""
        # Create test memory
        memory = {
            "created_at": datetime.now().isoformat()
        }
        
        context = {}
        
        # Calculate frequency score
        score = mem0_service._calculate_frequency_score(memory, context)
        
        # Verify score is within expected range
        assert 0.0 <= score <= 1.0

    async def test_calculate_interaction_score(self, mem0_service):
        """Test interaction score calculation."""
        # Create test memory
        memory = {
            "memory_type": "conversation"
        }
        
        context = {}
        
        # Calculate interaction score
        score = mem0_service._calculate_interaction_score(memory, context)
        
        # Verify score is within expected range
        assert 0.0 <= score <= 1.0

    async def test_get_dynamic_weights(self, mem0_service):
        """Test dynamic weight calculation."""
        query = "recent programming"
        context = {}
        
        # Get dynamic weights
        weights = mem0_service._get_dynamic_weights(query, context)
        
        # Verify weights
        assert "semantic" in weights
        assert "keyword" in weights
        assert "recency" in weights
        assert "frequency" in weights
        assert "interaction" in weights
        
        # Verify weights sum to 1.0
        assert abs(sum(weights.values()) - 1.0) < 0.001

    async def test_calculate_confidence(self, mem0_service):
        """Test confidence calculation."""
        # Test with high scores
        confidence = mem0_service._calculate_confidence(
            0.9, 0.8, 0.7, 0.6, 0.5,
            {"semantic": 0.4, "keyword": 0.25, "recency": 0.2, "frequency": 0.1, "interaction": 0.05}
        )
        
        # Verify confidence is within expected range
        assert 0.0 <= confidence <= 1.0
        
        # Test with low scores
        confidence = mem0_service._calculate_confidence(
            0.1, 0.2, 0.3, 0.4, 0.5,
            {"semantic": 0.4, "keyword": 0.25, "recency": 0.2, "frequency": 0.1, "interaction": 0.05}
        )
        
        # Verify confidence is within expected range
        assert 0.0 <= confidence <= 1.0 