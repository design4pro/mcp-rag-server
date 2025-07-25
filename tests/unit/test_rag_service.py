"""
Tests for RAG service functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from mcp_rag_server.services.rag_service import RAGService
from mcp_rag_server.services.gemini_service import GeminiService
from mcp_rag_server.services.qdrant_service import QdrantService
from mcp_rag_server.services.mem0_service import Mem0Service
from mcp_rag_server.services.session_service import SessionService


@pytest.fixture
def mock_gemini_service():
    """Create a mock Gemini service."""
    service = Mock(spec=GeminiService)
    service.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
    service.generate_text = AsyncMock(return_value="Test response")
    return service


@pytest.fixture
def mock_qdrant_service():
    """Create a mock Qdrant service."""
    service = Mock(spec=QdrantService)
    service.add_documents = AsyncMock(return_value=["test-doc-id"])
    service.search_documents = AsyncMock(return_value=[
        {
            "id": "test-chunk-id",
            "score": 0.95,
            "content": "Test document content",
            "metadata": {"source": "test", "document_id": "test-doc-id"}
        }
    ])
    service.delete_document = AsyncMock(return_value=True)
    service.get_document = AsyncMock(return_value={
        "id": "test-doc-id",
        "content": "Test document content",
        "metadata": {"source": "test"}
    })
    service.list_documents = AsyncMock(return_value=[
        {
            "id": "test-doc-id",
            "content": "Test document content",
            "metadata": {"source": "test"}
        }
    ])
    return service


@pytest.fixture
def mock_mem0_service():
    """Create a mock Mem0 service."""
    service = Mock(spec=Mem0Service)
    service.add_memory = AsyncMock(return_value="test-memory-id")
    service.add_memory_with_session = AsyncMock(return_value="test-memory-id")
    service.search_memories = AsyncMock(return_value=[
        {"memory": "Previous conversation", "relevance": 0.8}
    ])
    service.search_memories_hybrid = AsyncMock(return_value=[
        {"memory": "Previous conversation", "relevance": 0.8}
    ])
    service.search_memories_by_session = AsyncMock(return_value=[
        {"memory": "Previous conversation", "relevance": 0.8}
    ])
    service.format_memory_context = AsyncMock(return_value="Previous conversation")
    service.get_memory_stats = AsyncMock(return_value={
        "user_id": "test-user",
        "total_memories": 5
    })
    return service


@pytest.fixture
def mock_session_service():
    """Create a mock Session service."""
    service = Mock(spec=SessionService)
    service.record_interaction = AsyncMock(return_value=True)
    service.record_memory_creation = AsyncMock(return_value=True)
    return service


@pytest.fixture
def rag_service(mock_gemini_service, mock_qdrant_service, mock_mem0_service, mock_session_service):
    """Create a RAG service with mocked dependencies."""
    return RAGService(
        gemini_service=mock_gemini_service,
        qdrant_service=mock_qdrant_service,
        mem0_service=mock_mem0_service,
        session_service=mock_session_service
    )


@pytest.mark.asyncio
async def test_rag_service_initialization(rag_service):
    """Test RAG service initialization."""
    await rag_service.initialize()
    assert rag_service._initialized is True


@pytest.mark.asyncio
async def test_add_document(rag_service):
    """Test adding a document to the RAG system."""
    await rag_service.initialize()
    
    content = "Test document content"
    metadata = {"source": "test", "topic": "testing"}
    user_id = "test-user"
    
    result = await rag_service.add_document(content, metadata, user_id)
    
    assert result["success"] is True
    assert "id" in result
    assert result["metadata"]["user_id"] == user_id
    assert result["metadata"]["source"] == "test"


@pytest.mark.asyncio
async def test_search_documents(rag_service):
    """Test searching for documents."""
    await rag_service.initialize()
    
    query = "test query"
    results = await rag_service.search_documents(query, limit=5, user_id="test-user")
    
    assert len(results) == 1
    assert results[0]["document_id"] == "test-doc-id"
    assert len(results[0]["chunks"]) == 1
    assert results[0]["chunks"][0]["content"] == "Test document content"


@pytest.mark.asyncio
async def test_ask_question(rag_service):
    """Test asking a question with RAG."""
    await rag_service.initialize()
    
    question = "What is this about?"
    user_id = "test-user"
    
    response = await rag_service.ask_question(question, user_id)
    
    assert response == "Test response"
    # Verify that memory was added
    rag_service.mem0_service.add_memory.assert_called_once()


@pytest.mark.asyncio
async def test_delete_document(rag_service):
    """Test deleting a document."""
    await rag_service.initialize()
    
    document_id = "test-doc-id"
    result = await rag_service.delete_document(document_id)
    
    assert result is True
    rag_service.qdrant_service.delete_document.assert_called_once_with(document_id)


@pytest.mark.asyncio
async def test_get_document(rag_service):
    """Test getting a specific document."""
    await rag_service.initialize()
    
    document_id = "test-doc-id"
    document = await rag_service.get_document(document_id)
    
    assert document is not None
    assert document["id"] == document_id
    assert document["content"] == "Test document content"


@pytest.mark.asyncio
async def test_list_documents(rag_service):
    """Test listing documents."""
    await rag_service.initialize()
    
    documents = await rag_service.list_documents(user_id="test-user", limit=10)
    
    assert len(documents) == 1
    assert documents[0]["id"] == "test-doc-id"


@pytest.mark.asyncio
async def test_get_system_stats(rag_service):
    """Test getting system statistics."""
    await rag_service.initialize()
    
    stats = await rag_service.get_system_stats(user_id="test-user")
    
    assert "total_documents" in stats
    assert "memory_stats" in stats
    assert stats["user_id"] == "test-user"
    assert stats["total_documents"] == 1


@pytest.mark.asyncio
async def test_rag_service_without_memory():
    """Test RAG service without memory service."""
    mock_gemini = Mock(spec=GeminiService)
    mock_gemini.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
    mock_gemini.generate_text = AsyncMock(return_value="Test response")
    
    mock_qdrant = Mock(spec=QdrantService)
    mock_qdrant.search_documents = AsyncMock(return_value=[])
    
    rag_service = RAGService(
        gemini_service=mock_gemini,
        qdrant_service=mock_qdrant,
        mem0_service=None
    )
    
    await rag_service.initialize()
    
    # Should work without memory service
    response = await rag_service.ask_question("Test question", "test-user")
    assert response == "Test response"


@pytest.mark.asyncio
async def test_rag_service_cleanup(rag_service):
    """Test RAG service cleanup."""
    await rag_service.initialize()
    await rag_service.cleanup()
    # Should not raise any exceptions