"""
Unit tests for SessionService functionality.

Tests session creation, management, expiration, and statistics.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
from pathlib import Path

from src.mcp_rag_server.services.session_service import SessionService
from src.mcp_rag_server.config import ServerConfig


class TestSessionService:
    """Test SessionService functionality."""
    
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
    def session_service(self, server_config):
        """Create a test SessionService instance."""
        service = SessionService(server_config)
        return service
    
    @pytest.fixture
    def temp_storage_path(self, tmp_path):
        """Create a temporary storage path."""
        return tmp_path / "data" / "session_data"
    
    @pytest.mark.asyncio
    async def test_session_creation(self, session_service, temp_storage_path):
        """Test session creation functionality."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_name = "Test Session"
        metadata = {"test": "data"}
        
        session_id = await session_service.create_session(
            user_id=user_id,
            session_name=session_name,
            metadata=metadata
        )
        
        # Verify session was created
        assert session_id is not None
        assert session_id in session_service.sessions
        
        session = session_service.sessions[session_id]
        assert session["user_id"] == user_id
        assert session["name"] == session_name
        assert session["status"] == "active"
        assert session["metadata"] == metadata
        assert session["interaction_count"] == 0
        assert session["memory_count"] == 0
        
        # Verify user sessions mapping
        assert user_id in session_service.user_sessions
        assert session_id in session_service.user_sessions[user_id]
        
        # Verify session stats
        assert session_id in session_service.session_stats
    
    @pytest.mark.asyncio
    async def test_get_session(self, session_service, temp_storage_path):
        """Test getting session information."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Get session
        session = await session_service.get_session(session_id)
        
        # Verify session info
        assert session is not None
        assert session["id"] == session_id
        assert session["user_id"] == user_id
        assert session["status"] == "active"
        
        # Test getting non-existent session
        non_existent_session = await session_service.get_session("non_existent")
        assert non_existent_session is None
    
    @pytest.mark.asyncio
    async def test_update_session(self, session_service, temp_storage_path):
        """Test session update functionality."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Update session
        updates = {
            "name": "Updated Session Name",
            "metadata": {"updated": "data"},
            "interaction_count": 5
        }
        
        success = await session_service.update_session(session_id, updates)
        assert success is True
        
        # Verify updates
        session = session_service.sessions[session_id]
        assert session["name"] == "Updated Session Name"
        assert session["metadata"] == {"updated": "data"}
        assert session["interaction_count"] == 5
    
    @pytest.mark.asyncio
    async def test_expire_session(self, session_service, temp_storage_path):
        """Test session expiration functionality."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Verify session is active
        session = session_service.sessions[session_id]
        assert session["status"] == "active"
        
        # Expire session
        success = await session_service.expire_session(session_id)
        assert success is True
        
        # Verify session is expired
        session = session_service.sessions[session_id]
        assert session["status"] == "expired"
        assert "expired_at" in session
        
        # Verify session is still in user sessions (for include_expired=True queries)
        assert session_id in session_service.user_sessions[user_id]
    
    @pytest.mark.asyncio
    async def test_get_user_sessions(self, session_service, temp_storage_path):
        """Test getting user sessions."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create multiple sessions for user
        user_id = "test_user"
        session_ids = []
        
        for i in range(3):
            session_id = await session_service.create_session(
                user_id=user_id,
                session_name=f"Session {i}"
            )
            session_ids.append(session_id)
        
        # Get user sessions
        sessions = await session_service.get_user_sessions(user_id)
        
        # Verify all sessions are returned
        assert len(sessions) == 3
        session_ids_returned = [s["id"] for s in sessions]
        assert all(sid in session_ids_returned for sid in session_ids)
        
        # Test with expired sessions
        await session_service.expire_session(session_ids[0])
        
        # Get active sessions only
        active_sessions = await session_service.get_user_sessions(user_id, include_expired=False)
        assert len(active_sessions) == 2
        
        # Get all sessions including expired
        all_sessions = await session_service.get_user_sessions(user_id, include_expired=True)
        assert len(all_sessions) == 3
    
    @pytest.mark.asyncio
    async def test_session_stats(self, session_service, temp_storage_path):
        """Test session statistics functionality."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Record interactions and memories
        await session_service.record_interaction(session_id)
        await session_service.record_interaction(session_id)
        await session_service.record_memory_creation(session_id)
        
        # Get session stats
        stats = await session_service.get_session_stats(session_id)
        
        # Verify stats
        assert stats is not None
        assert stats["interactions"] == 2
        assert stats["memories_created"] == 1
        assert "session_info" in stats
        
        # Test getting stats for non-existent session
        non_existent_stats = await session_service.get_session_stats("non_existent")
        assert non_existent_stats is None
    
    @pytest.mark.asyncio
    async def test_system_stats(self, session_service, temp_storage_path):
        """Test system statistics functionality."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
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
        
        # Record some interactions and memories
        for session_id in user1_sessions + user2_sessions:
            await session_service.record_interaction(session_id)
            await session_service.record_memory_creation(session_id)
        
        # Expire one session
        await session_service.expire_session(user1_sessions[0])
        
        # Get system stats
        system_stats = await session_service.get_system_stats()
        
        # Verify stats
        assert system_stats["active_sessions"] == 3  # 2 active from user1, 2 from user2, minus 1 expired
        assert system_stats["expired_sessions"] == 1
        assert system_stats["total_users"] == 2
        assert system_stats["total_interactions"] == 4
        assert system_stats["total_memories"] == 4
    
    @pytest.mark.asyncio
    async def test_session_cleanup(self, session_service, temp_storage_path):
        """Test session cleanup functionality."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Manually expire session
        await session_service.expire_session(session_id)
        
        # Verify session is expired
        session = session_service.sessions[session_id]
        assert session["status"] == "expired"
        
        # Clean up expired sessions
        cleaned_count = await session_service.cleanup_expired_sessions()
        
        # Should not clean up immediately expired sessions (they're kept for 7 days)
        assert cleaned_count == 0
        
        # Verify session still exists
        assert session_id in session_service.sessions
    
    @pytest.mark.asyncio
    async def test_max_sessions_per_user(self, session_service, temp_storage_path):
        """Test maximum sessions per user limit."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create more sessions than the limit
        user_id = "test_user"
        session_ids = []
        
        for i in range(12):  # More than max_sessions_per_user (10)
            session_id = await session_service.create_session(
                user_id=user_id,
                session_name=f"Session {i}"
            )
            session_ids.append(session_id)
        
        # Verify only the limit number of sessions exist
        user_sessions = await session_service.get_user_sessions(user_id)
        assert len(user_sessions) == 10  # max_sessions_per_user
        
        # Verify oldest sessions were expired
        expired_sessions = [s for s in session_service.sessions.values() 
                          if s["user_id"] == user_id and s["status"] == "expired"]
        assert len(expired_sessions) == 2  # 12 - 10 = 2 expired
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, session_service, temp_storage_path):
        """Test session persistence to storage."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Create session
        user_id = "test_user"
        session_id = await session_service.create_session(user_id=user_id)
        
        # Record some activity
        await session_service.record_interaction(session_id)
        await session_service.record_memory_creation(session_id)
        
        # Verify storage file exists
        sessions_file = temp_storage_path / "sessions.json"
        assert sessions_file.exists()
        
        # Read storage file
        with open(sessions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify data structure
        assert "sessions" in data
        assert "user_sessions" in data
        assert "session_stats" in data
        assert "last_updated" in data
        
        # Verify session data is stored
        assert session_id in data["sessions"]
        assert user_id in data["user_sessions"]
        assert session_id in data["session_stats"]
    
    @pytest.mark.asyncio
    async def test_cleanup_task(self, session_service, temp_storage_path):
        """Test background cleanup task."""
        # Mock storage path
        session_service.storage_path = temp_storage_path
        
        # Initialize service
        await session_service.initialize()
        
        # Verify cleanup task is started
        assert session_service._cleanup_task is not None
        assert not session_service._cleanup_task.done()
        
        # Cleanup
        await session_service.cleanup()
        
        # Verify cleanup task is cancelled
        assert session_service._cleanup_task.done() 