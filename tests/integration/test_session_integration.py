"""
Integration tests for SessionService functionality.

Tests session integration with RAG pipeline and memory management.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
from pathlib import Path

from src.mcp_rag_server.services.session_service import SessionService
from src.mcp_rag_server.services.mem0_service import Mem0Service
from src.mcp_rag_server.services.rag_service import RAGService
from src.mcp_rag_server.config import ServerConfig, Mem0Config


class TestSessionIntegration:
    """Test SessionService integration with other services."""
    
    @pytest.fixture
    def server_config(self):
        """Create a test ServerConfig."""
        return ServerConfig(
            host="localhost",
            port=8000,
            log_level="INFO",
            debug=False
        )
    
    @pytest.fixture
    def mem0_config(self):
        """Create a test Mem0Config."""
        return Mem0Config(
            local_storage_path="./data/test_mem0_data",
            memory_size=1000,
            relevance_threshold=0.7,
            max_tokens_per_memory=1000,
            use_semantic_search=True,
            semantic_search_weight=0.7,
            keyword_search_weight=0.3,
            recency_weight=0.1,
            max_memory_context_length=2000,
            enable_memory_summarization=True
        )
    
    @pytest.fixture
    def session_service(self, server_config, tmp_path):
        """Create a test SessionService instance."""
        service = SessionService(server_config)
        service.storage_path = tmp_path / "data" / "session_data"
        return service
    
    @pytest.fixture
    def mem0_service(self, mem0_config, tmp_path):
        """Create a test Mem0Service instance."""
        service = Mem0Service(mem0_config)
        service.storage_path = tmp_path / "data" / "mem0_data"
        return service
    
    @pytest.mark.asyncio
    async def test_session_memory_integration(self, session_service, mem0_service):
        """Test integration between session and memory services."""
        # Mock mem0 import to prevent API key issues
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: __import__(name, *args, **kwargs) if name != 'mem0' else ImportError("mem0 not available")):
            # Initialize services
            await session_service.initialize()
            await mem0_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(
            user_id=user_id,
            session_name="Test Session"
        )
        
        # Add memory with session context
        memory_content = "This is a test memory for the session"
        memory_id = await mem0_service.add_memory_with_session(
            user_id=user_id,
            content=memory_content,
            session_id=session_id,
            memory_type="conversation"
        )
        
        # Record memory creation in session (normally done by RAG service)
        await session_service.record_memory_creation(session_id)
        
        # Verify memory was added with session context
        session_memories = await mem0_service.get_session_memories(
            user_id=user_id,
            session_id=session_id
        )
        
        assert len(session_memories) == 1
        assert session_memories[0]["session_id"] == session_id
        assert session_memories[0]["memory"] == memory_content
        
        # Verify session stats were updated
        session_stats = await session_service.get_session_stats(session_id)
        assert session_stats["memories_created"] == 1
        
        # Test session memory search
        search_results = await mem0_service.search_memories_by_session(
            user_id=user_id,
            session_id=session_id,
            query="test memory"
        )
        
        assert len(search_results) == 1
        assert search_results[0]["memory"] == memory_content
    
    @pytest.mark.asyncio
    async def test_session_cleanup_integration(self, session_service, mem0_service):
        """Test session cleanup integration with memory cleanup."""
        # Mock mem0 import to prevent API key issues
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: __import__(name, *args, **kwargs) if name != 'mem0' else ImportError("mem0 not available")):
            # Initialize services
            await session_service.initialize()
            await mem0_service.initialize()
        
        # Create session and add memories
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Add multiple memories
        for i in range(3):
            await mem0_service.add_memory_with_session(
                user_id=user_id,
                content=f"Memory {i}",
                session_id=session_id
            )
            # Record memory creation in session
            await session_service.record_memory_creation(session_id)
        
        # Verify memories exist
        session_memories = await mem0_service.get_session_memories(
            user_id=user_id,
            session_id=session_id
        )
        assert len(session_memories) == 3
        
        # Expire session
        await session_service.expire_session(session_id)
        
        # Verify session is expired
        session = await session_service.get_session(session_id)
        assert session is None
        
        # Verify memories are still accessible for cleanup
        session_memories = await mem0_service.get_session_memories(
            user_id=user_id,
            session_id=session_id
        )
        assert len(session_memories) == 3
        
        # Clean up session memories
        cleaned_count = await mem0_service.cleanup_session_memories(session_id)
        assert cleaned_count == 3
        
        # Verify memories are gone
        session_memories = await mem0_service.get_session_memories(
            user_id=user_id,
            session_id=session_id
        )
        assert len(session_memories) == 0
    
    @pytest.mark.asyncio
    async def test_session_rag_integration(self, session_service, mem0_service):
        """Test session integration with RAG pipeline."""
        # Mock GeminiService and QdrantService for RAG
        mock_gemini_service = Mock()
        mock_gemini_service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        mock_gemini_service.generate_text = AsyncMock(return_value="This is a test response")
        
        mock_qdrant_service = Mock()
        mock_qdrant_service.search_documents = AsyncMock(return_value=[])
        
        # Mock mem0 import to prevent API key issues
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: __import__(name, *args, **kwargs) if name != 'mem0' else ImportError("mem0 not available")):
            # Initialize services
            await session_service.initialize()
            await mem0_service.initialize()
        
        # Create RAG service with session support
        rag_service = RAGService(
            gemini_service=mock_gemini_service,
            qdrant_service=mock_qdrant_service,
            mem0_service=mem0_service,
            session_service=session_service
        )
        await rag_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Add some memories to the session
        await mem0_service.add_memory_with_session(
            user_id=user_id,
            content="Previous conversation about AI",
            session_id=session_id
        )
        
        # Ask question with session context
        question = "What did we discuss before?"
        response = await rag_service.ask_question(
            question=question,
            user_id=user_id,
            session_id=session_id,
            use_memory=True
        )
        
        # Verify response was generated
        assert response is not None
        
        # Verify session interaction was recorded
        session_stats = await session_service.get_session_stats(session_id)
        assert session_stats["interactions"] == 1
        
        # Verify new memory was created with session context
        session_memories = await mem0_service.get_session_memories(
            user_id=user_id,
            session_id=session_id
        )
        assert len(session_memories) == 2  # Original + new Q&A memory
    
    @pytest.mark.asyncio
    async def test_session_statistics_integration(self, session_service, mem0_service):
        """Test session statistics integration."""
        # Mock mem0 import to prevent API key issues
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: __import__(name, *args, **kwargs) if name != 'mem0' else ImportError("mem0 not available")):
            # Initialize services
            await session_service.initialize()
            await mem0_service.initialize()
        
        # Create multiple sessions for different users
        user1_sessions = []
        user2_sessions = []
        
        for i in range(2):
            session_id = await session_service.create_session(
                user_id="user1",
                session_name=f"User1 Session {i}"
            )
            user1_sessions.append(session_id)
            
            session_id = await session_service.create_session(
                user_id="user2",
                session_name=f"User2 Session {i}"
            )
            user2_sessions.append(session_id)
        
        # Add memories and interactions to sessions
        for session_id in user1_sessions + user2_sessions:
            await mem0_service.add_memory_with_session(
                user_id="user1" if session_id in user1_sessions else "user2",
                content=f"Memory for session {session_id}",
                session_id=session_id
            )
            # Record memory creation and interaction
            await session_service.record_memory_creation(session_id)
            await session_service.record_interaction(session_id)
        
        # Get system stats
        system_stats = await session_service.get_system_stats()
        
        # Verify system stats
        assert system_stats["active_sessions"] == 4
        assert system_stats["total_users"] == 2
        assert system_stats["total_interactions"] == 4
        assert system_stats["total_memories"] == 4
        
        # Get memory stats by session
        for session_id in user1_sessions + user2_sessions:
            memory_stats = await mem0_service.get_memory_stats_by_session(session_id)
            assert memory_stats["total_memories"] == 1
            assert memory_stats["memory_types"]["conversation"] == 1
    
    @pytest.mark.asyncio
    async def test_session_persistence_integration(self, session_service, mem0_service, tmp_path):
        """Test session and memory persistence integration."""
        # Mock mem0 import to prevent API key issues
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: __import__(name, *args, **kwargs) if name != 'mem0' else ImportError("mem0 not available")):
            # Initialize services
            await session_service.initialize()
            await mem0_service.initialize()
        
        # Create session and add memories
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        await mem0_service.add_memory_with_session(
            user_id=user_id,
            content="Persistent memory",
            session_id=session_id
        )
        
        # Record memory creation and interaction
        await session_service.record_memory_creation(session_id)
        await session_service.record_interaction(session_id)
        
        # Verify data is persisted
        sessions_file = session_service.storage_path / "sessions.json"
        assert sessions_file.exists()
        
        mem0_file = mem0_service.storage_path / "memories.json"
        assert mem0_file.exists()
        
        # Read persisted data
        with open(sessions_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        with open(mem0_file, 'r', encoding='utf-8') as f:
            mem0_data = json.load(f)
        
        # Verify session data
        assert session_id in session_data["sessions"]
        assert user_id in session_data["user_sessions"]
        assert session_id in session_data["session_stats"]
        
        # Verify memory data
        assert user_id in mem0_data["memories"]
        assert len(mem0_data["memories"][user_id]) == 1
        assert mem0_data["memories"][user_id][0]["session_id"] == session_id 