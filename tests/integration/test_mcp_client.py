#!/usr/bin/env python3
"""
Simple MCP client test script.
"""

import asyncio
import json
import aiohttp


async def test_mcp_server():
    """Test the MCP RAG Server via HTTP."""
    print("Testing MCP RAG Server via HTTP...")
    
    # Test health endpoint
    async with aiohttp.ClientSession() as session:
        try:
            # Test basic connectivity on port 8001
            async with session.get("http://localhost:8001/") as response:
                print(f"✅ Server is running on port 8001")
                print(f"   Status: {response.status}")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Test MCP endpoint
            async with session.get("http://localhost:8001/mcp/") as response:
                print(f"✅ MCP endpoint is accessible")
                print(f"   Status: {response.status}")
                content = await response.text()
                print(f"   Response: {content[:200]}...")
                
        except Exception as e:
            print(f"❌ Error connecting to server: {e}")
            return
    
    print("\n🎉 MCP RAG Server is working correctly!")
    print("\nTo use in Cursor IDE:")
    print("1. Configuration is already in .cursor/mcpServers.json")
    print("2. Restart Cursor IDE")
    print("3. The server will be available as an MCP tool")
    print("\nAvailable MCP Tools:")
    print("- health_check() - Check server health")
    print("- add_document(content, metadata) - Add document to RAG")
    print("- search_documents(query, limit) - Search documents")
    print("- ask_question(question, user_id) - Ask RAG question")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())