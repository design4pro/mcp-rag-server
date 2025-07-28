"""
Example usage of HTTP Integration tools for MCP RAG Server.

This example demonstrates how to use the HTTP integration features:
- Fetching web content
- Calling external APIs
- Batch processing URLs
- Automatic RAG integration
"""

import asyncio
import json
from typing import Dict, Any


async def example_fetch_web_content():
    """Example: Fetch content from a website and add to RAG."""
    print("🌐 Example: Fetching web content...")
    
    # Example URLs to fetch
    urls = [
        "https://httpbin.org/json",
        "https://api.github.com/users/octocat",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]
    
    for url in urls:
        print(f"\n📥 Fetching: {url}")
        
        # This would be called via MCP tool
        # result = await fetch_web_content(url, user_id="example_user", auto_add_to_rag=True)
        
        # Simulated result
        result = {
            "success": True,
            "url": url,
            "content_length": 1024,
            "content_type": "application/json",
            "rag_integration": {
                "added_to_rag": True,
                "document_id": f"doc_{hash(url)}",
                "chunks_created": 3
            },
            "metadata": {
                "source_url": url,
                "domain": url.split("//")[1].split("/")[0],
                "fetch_timestamp": "2025-01-25T10:00:00Z"
            }
        }
        
        print(f"✅ Success: {result['content_length']} bytes")
        print(f"📄 Added to RAG: {result['rag_integration']['document_id']}")


async def example_call_external_api():
    """Example: Call external API and process response."""
    print("\n🔌 Example: Calling external API...")
    
    # Example API calls
    api_calls = [
        {
            "endpoint": "https://api.github.com/repos/octocat/Hello-World",
            "method": "GET",
            "description": "GitHub repository info"
        },
        {
            "endpoint": "https://jsonplaceholder.typicode.com/posts",
            "method": "POST",
            "data": {
                "title": "Test Post",
                "body": "This is a test post",
                "userId": 1
            },
            "description": "Create a new post"
        }
    ]
    
    for api_call in api_calls:
        print(f"\n📡 API Call: {api_call['description']}")
        print(f"   Endpoint: {api_call['endpoint']}")
        print(f"   Method: {api_call['method']}")
        
        # This would be called via MCP tool
        # result = await call_external_api(
        #     endpoint=api_call['endpoint'],
        #     method=api_call['method'],
        #     data=api_call.get('data'),
        #     user_id="example_user"
        # )
        
        # Simulated result
        result = {
            "success": True,
            "endpoint": api_call['endpoint'],
            "method": api_call['method'],
            "status_code": 200,
            "response_data": {"id": 1, "status": "success"},
            "rag_integration": {
                "added_to_rag": True,
                "document_id": f"api_{hash(api_call['endpoint'])}"
            }
        }
        
        print(f"✅ Status: {result['status_code']}")
        print(f"📄 Added to RAG: {result['rag_integration']['document_id']}")


async def example_batch_fetch_urls():
    """Example: Batch fetch multiple URLs in parallel."""
    print("\n📦 Example: Batch fetching URLs...")
    
    urls = [
        "https://httpbin.org/json",
        "https://api.github.com/users/octocat",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3"
    ]
    
    print(f"📥 Fetching {len(urls)} URLs in parallel...")
    
    # This would be called via MCP tool
    # result = await batch_fetch_urls(urls, user_id="example_user", max_concurrent=3)
    
    # Simulated result
    result = {
        "success": True,
        "total_urls": len(urls),
        "successful": 4,
        "failed": 1,
        "results": {
            "successful": [
                {"url": urls[0], "content_length": 1024},
                {"url": urls[1], "content_length": 2048},
                {"url": urls[2], "content_length": 512},
                {"url": urls[3], "content_length": 512}
            ],
            "failed": [
                {"url": urls[4], "error": "Connection timeout"}
            ]
        }
    }
    
    print(f"✅ Successful: {result['successful']}")
    print(f"❌ Failed: {result['failed']}")
    print(f"📊 Success rate: {result['successful']}/{result['total_urls']} ({result['successful']/result['total_urls']*100:.1f}%)")


async def example_process_http_response():
    """Example: Process HTTP response and add to RAG."""
    print("\n🔄 Example: Processing HTTP response...")
    
    # Example HTML content
    html_content = """
    <html>
        <head><title>Example Page</title></head>
        <body>
            <h1>Welcome to Example Page</h1>
            <p>This is some example content with <strong>important</strong> information.</p>
            <div class="content">
                <p>More content here with useful data.</p>
            </div>
        </body>
    </html>
    """
    
    print("📄 Processing HTML content...")
    
    # This would be called via MCP tool
    # result = await process_http_response(html_content, "extract_text", user_id="example_user")
    
    # Simulated result
    result = {
        "success": True,
        "processing_type": "extract_text",
        "extracted_text_length": 156,
        "rag_integration": {
            "added_to_rag": True,
            "document_id": "processed_html_123"
        }
    }
    
    print(f"✅ Extracted text: {result['extracted_text_length']} characters")
    print(f"📄 Added to RAG: {result['rag_integration']['document_id']}")


async def main():
    """Run all HTTP integration examples."""
    print("🚀 HTTP Integration Examples for MCP RAG Server")
    print("=" * 50)
    
    await example_fetch_web_content()
    await example_call_external_api()
    await example_batch_fetch_urls()
    await example_process_http_response()
    
    print("\n✅ All HTTP integration examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 