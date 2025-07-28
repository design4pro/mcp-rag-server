"""
Unit tests for HTTP Integration tools.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from src.mcp_rag_server.tools.http_tools import HTTPIntegrationTools


class TestHTTPIntegrationTools:
    """Test cases for HTTPIntegrationTools."""
    
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
    def mock_document_processor(self):
        """Mock document processor."""
        processor = Mock()
        processor.process_content = AsyncMock(return_value="processed content")
        return processor
    
    @pytest.fixture
    def http_tools(self, mock_rag_service, mock_document_processor):
        """HTTP tools instance with mocked dependencies."""
        return HTTPIntegrationTools(mock_rag_service, mock_document_processor)
    
    @pytest.mark.asyncio
    async def test_fetch_web_content_success(self, http_tools):
        """Test successful web content fetching."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.text = "<html><body>Test content</body></html>"
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = await http_tools.fetch_web_content(
                "https://example.com",
                user_id="test_user",
                auto_add_to_rag=True
            )
            
            assert result["success"] is True
            assert result["url"] == "https://example.com"
            assert result["content_length"] > 0
            assert result["rag_integration"]["added_to_rag"] is True
    
    @pytest.mark.asyncio
    async def test_fetch_web_content_invalid_url(self, http_tools):
        """Test fetching with invalid URL."""
        result = await http_tools.fetch_web_content(
            "invalid-url",
            user_id="test_user"
        )
        
        assert result["success"] is False
        assert "Invalid URL format" in result["error"]
    
    @pytest.mark.asyncio
    async def test_fetch_web_content_http_error(self, http_tools):
        """Test handling HTTP errors."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock HTTP error
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response
            
            result = await http_tools.fetch_web_content(
                "https://example.com/notfound",
                user_id="test_user"
            )
            
            assert result["success"] is False
            assert "404" in result["error"]
    
    @pytest.mark.asyncio
    async def test_call_external_api_get(self, http_tools):
        """Test GET API call."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.headers = {"content-type": "application/json"}
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = await http_tools.call_external_api(
                "https://api.example.com/data",
                method="GET",
                user_id="test_user"
            )
            
            assert result["success"] is True
            assert result["method"] == "GET"
            assert result["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_call_external_api_post(self, http_tools):
        """Test POST API call."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {"id": 1, "status": "created"}
            mock_response.headers = {"content-type": "application/json"}
            mock_response.status_code = 201
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = await http_tools.call_external_api(
                "https://api.example.com/create",
                method="POST",
                data={"name": "test"},
                user_id="test_user"
            )
            
            assert result["success"] is True
            assert result["method"] == "POST"
            assert result["status_code"] == 201
    
    @pytest.mark.asyncio
    async def test_call_external_api_unsupported_method(self, http_tools):
        """Test unsupported HTTP method."""
        result = await http_tools.call_external_api(
            "https://api.example.com/data",
            method="PATCH",
            user_id="test_user"
        )
        
        assert result["success"] is False
        assert "Unsupported HTTP method" in result["error"]
    
    @pytest.mark.asyncio
    async def test_batch_fetch_urls_success(self, http_tools):
        """Test batch URL fetching."""
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        
        with patch.object(http_tools, 'fetch_web_content') as mock_fetch:
            # Mock successful responses
            mock_fetch.side_effect = [
                {"success": True, "url": urls[0]},
                {"success": True, "url": urls[1]},
                {"success": False, "url": urls[2], "error": "Connection failed"}
            ]
            
            result = await http_tools.batch_fetch_urls(
                urls,
                user_id="test_user",
                max_concurrent=2
            )
            
            assert result["success"] is True
            assert result["total_urls"] == 3
            assert result["successful"] == 2
            assert result["failed"] == 1
    
    @pytest.mark.asyncio
    async def test_process_http_response_extract_text(self, http_tools):
        """Test HTML text extraction."""
        html_content = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        
        result = await http_tools.process_http_response(
            html_content,
            processing_type="extract_text",
            user_id="test_user"
        )
        
        assert result["success"] is True
        assert result["processing_type"] == "extract_text"
        assert result["extracted_text_length"] > 0
    
    @pytest.mark.asyncio
    async def test_process_http_response_json_to_text(self, http_tools):
        """Test JSON to text conversion."""
        json_data = {"name": "test", "value": 123, "active": True}
        
        result = await http_tools.process_http_response(
            json_data,
            processing_type="json_to_text",
            user_id="test_user"
        )
        
        assert result["success"] is True
        assert result["processing_type"] == "json_to_text"
        assert result["converted_text_length"] > 0
    
    @pytest.mark.asyncio
    async def test_process_http_response_unsupported_type(self, http_tools):
        """Test unsupported processing type."""
        result = await http_tools.process_http_response(
            "test content",
            processing_type="unsupported_type",
            user_id="test_user"
        )
        
        assert result["success"] is False
        assert "Unsupported processing type" in result["error"]
    
    @pytest.mark.asyncio
    async def test_cleanup(self, http_tools):
        """Test cleanup method."""
        with patch.object(http_tools.client, 'aclose') as mock_aclose:
            await http_tools.cleanup()
            mock_aclose.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 