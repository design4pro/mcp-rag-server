"""
Unit tests for Advanced Features.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from src.mcp_rag_server.tools.advanced_features import AdvancedFeatures, StreamType, StreamEvent


class TestAdvancedFeatures:
    """Test cases for AdvancedFeatures."""
    
    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service."""
        service = Mock()
        service.add_document = AsyncMock(return_value={
            "document_id": "test_doc_123",
            "chunks_created": 3
        })
        return service
    
    @pytest.fixture
    def mock_mem0_service(self):
        """Mock Mem0 service."""
        service = Mock()
        service.add_memory = AsyncMock(return_value="test_memory_123")
        return service
    
    @pytest.fixture
    def mock_session_service(self):
        """Mock Session service."""
        service = Mock()
        return service
    
    @pytest.fixture
    def advanced_features(self, mock_rag_service, mock_mem0_service, mock_session_service):
        """Advanced features instance with mocked dependencies."""
        return AdvancedFeatures(mock_rag_service, mock_mem0_service, mock_session_service)
    
    @pytest.mark.asyncio
    async def test_batch_add_documents_success(self, advanced_features):
        """Test successful batch document addition."""
        documents = [
            {
                "content": "Test document 1",
                "metadata": {"topic": "test1"}
            },
            {
                "content": "Test document 2", 
                "metadata": {"topic": "test2"}
            }
        ]
        
        result = await advanced_features.batch_add_documents(
            documents,
            user_id="test_user",
            batch_size=2,
            parallel_processing=True
        )
        
        assert result["success"] is True
        assert result["total_documents"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_batch_add_documents_empty_list(self, advanced_features):
        """Test batch document addition with empty list."""
        result = await advanced_features.batch_add_documents(
            [],
            user_id="test_user"
        )
        
        assert result["success"] is False
        assert "No documents provided" in result["error"]
    
    @pytest.mark.asyncio
    async def test_batch_add_documents_sequential(self, advanced_features):
        """Test sequential batch document processing."""
        documents = [
            {"content": "Test doc 1", "metadata": {}},
            {"content": "Test doc 2", "metadata": {}}
        ]
        
        result = await advanced_features.batch_add_documents(
            documents,
            user_id="test_user",
            parallel_processing=False
        )
        
        assert result["success"] is True
        assert result["total_documents"] == 2
        assert result["successful"] == 2
    
    @pytest.mark.asyncio
    async def test_batch_process_memories_success(self, advanced_features):
        """Test successful batch memory processing."""
        memories = [
            {
                "content": "Test memory 1",
                "metadata": {"context": "test1"},
                "session_id": "session_1"
            },
            {
                "content": "Test memory 2",
                "metadata": {"context": "test2"},
                "session_id": "session_2"
            }
        ]
        
        result = await advanced_features.batch_process_memories(
            memories,
            user_id="test_user",
            batch_size=2,
            memory_type="conversation"
        )
        
        assert result["success"] is True
        assert result["total_memories"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_batch_process_memories_empty_list(self, advanced_features):
        """Test batch memory processing with empty list."""
        result = await advanced_features.batch_process_memories(
            [],
            user_id="test_user"
        )
        
        assert result["success"] is False
        assert "No memories provided" in result["error"]
    
    @pytest.mark.asyncio
    async def test_start_streaming_success(self, advanced_features):
        """Test successful streaming start."""
        result = await advanced_features.start_streaming(
            StreamType.DOCUMENT_UPDATES,
            user_id="test_user",
            session_id="session_123",
            callback_url="https://webhook.site/test"
        )
        
        assert result["success"] is True
        assert result["stream_type"] == "document_updates"
        assert result["user_id"] == "test_user"
        assert result["session_id"] == "session_123"
        assert result["callback_url"] == "https://webhook.site/test"
        assert "stream_id" in result
    
    @pytest.mark.asyncio
    async def test_stop_streaming_success(self, advanced_features):
        """Test successful streaming stop."""
        # First start a stream
        start_result = await advanced_features.start_streaming(
            StreamType.DOCUMENT_UPDATES,
            user_id="test_user"
        )
        stream_id = start_result["stream_id"]
        
        # Then stop it
        result = await advanced_features.stop_streaming(stream_id)
        
        assert result["success"] is True
        assert result["stream_id"] == stream_id
        assert "stopped_at" in result
    
    @pytest.mark.asyncio
    async def test_stop_streaming_not_found(self, advanced_features):
        """Test stopping non-existent stream."""
        result = await advanced_features.stop_streaming("non_existent_stream")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_stream_status_success(self, advanced_features):
        """Test getting stream status."""
        # Start a stream
        start_result = await advanced_features.start_streaming(
            StreamType.MEMORY_UPDATES,
            user_id="test_user"
        )
        stream_id = start_result["stream_id"]
        
        # Get status
        result = await advanced_features.get_stream_status(stream_id)
        
        assert result["success"] is True
        assert result["stream_id"] == stream_id
        assert result["active"] is True
        assert result["stream_type"] == "memory_updates"
        assert result["user_id"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_get_stream_status_not_found(self, advanced_features):
        """Test getting status of non-existent stream."""
        result = await advanced_features.get_stream_status("non_existent_stream")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_active_streams(self, advanced_features):
        """Test listing active streams."""
        # Start multiple streams
        await advanced_features.start_streaming(
            StreamType.DOCUMENT_UPDATES,
            user_id="user1"
        )
        await advanced_features.start_streaming(
            StreamType.MEMORY_UPDATES,
            user_id="user2"
        )
        
        # List all streams
        result = await advanced_features.list_active_streams()
        
        assert result["success"] is True
        assert result["total_count"] >= 2
        
        # List streams for specific user
        user_result = await advanced_features.list_active_streams("user1")
        
        assert user_result["success"] is True
        assert all(stream["user_id"] == "user1" for stream in user_result["active_streams"])
    
    @pytest.mark.asyncio
    async def test_subscribe_to_updates_success(self, advanced_features):
        """Test subscribing to stream updates."""
        # Start a stream
        start_result = await advanced_features.start_streaming(
            StreamType.SYSTEM_EVENTS,
            user_id="test_user"
        )
        stream_id = start_result["stream_id"]
        
        # Subscribe
        callback = Mock()
        result = await advanced_features.subscribe_to_updates(stream_id, callback)
        
        assert result["success"] is True
        assert result["stream_id"] == stream_id
        assert result["subscribers_count"] == 1
    
    @pytest.mark.asyncio
    async def test_subscribe_to_updates_not_found(self, advanced_features):
        """Test subscribing to non-existent stream."""
        callback = Mock()
        result = await advanced_features.subscribe_to_updates("non_existent", callback)
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_stream_event_creation(self):
        """Test StreamEvent creation."""
        event = StreamEvent(
            event_id="test_event_123",
            event_type="document_updates",
            timestamp="2025-01-25T10:00:00Z",
            data={"operation": "document_added"},
            user_id="test_user",
            session_id="session_123"
        )
        
        assert event.event_id == "test_event_123"
        assert event.event_type == "document_updates"
        assert event.user_id == "test_user"
        assert event.session_id == "session_123"
    
    @pytest.mark.asyncio
    async def test_cleanup(self, advanced_features):
        """Test cleanup method."""
        # Start some streams
        await advanced_features.start_streaming(
            StreamType.DOCUMENT_UPDATES,
            user_id="test_user"
        )
        
        # Verify streams exist
        list_result = await advanced_features.list_active_streams()
        assert list_result["total_count"] > 0
        
        # Cleanup
        await advanced_features.cleanup()
        
        # Verify streams are cleaned up
        list_result_after = await advanced_features.list_active_streams()
        assert list_result_after["total_count"] == 0


class TestStreamType:
    """Test cases for StreamType enum."""
    
    def test_stream_type_values(self):
        """Test StreamType enum values."""
        assert StreamType.DOCUMENT_UPDATES.value == "document_updates"
        assert StreamType.MEMORY_UPDATES.value == "memory_updates"
        assert StreamType.SESSION_UPDATES.value == "session_updates"
        assert StreamType.RAG_QUERIES.value == "rag_queries"
        assert StreamType.SYSTEM_EVENTS.value == "system_events"
    
    def test_stream_type_from_string(self):
        """Test creating StreamType from string."""
        assert StreamType("document_updates") == StreamType.DOCUMENT_UPDATES
        assert StreamType("memory_updates") == StreamType.MEMORY_UPDATES
    
    def test_stream_type_invalid_value(self):
        """Test invalid StreamType value."""
        with pytest.raises(ValueError):
            StreamType("invalid_type")


if __name__ == "__main__":
    pytest.main([__file__]) 