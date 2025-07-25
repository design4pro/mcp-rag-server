#!/usr/bin/env python3
"""
Simple health check test for MCP RAG Server.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_rag_server.server import MCPRAGServer


async def test_health():
    """Test the health check functionality."""
    print("🔍 Testing MCP RAG Server health...")
    
    # Create server instance
    server = MCPRAGServer()
    
    # Initialize services
    print("📡 Initializing services...")
    await server.initialize_services()
    
    # Test health check
    print("🏥 Running health check...")
    health = {
        "status": "healthy",
        "services": {
            "gemini": server.gemini_service is not None,
            "qdrant": server.qdrant_service is not None,
            "mem0": server.mem0_service is not None,
            "rag": server.rag_service is not None
        }
    }
    
    print("📊 Health Check Results:")
    print(f"   Status: {health['status']}")
    print(f"   Gemini: {'✅' if health['services']['gemini'] else '❌'}")
    print(f"   Qdrant: {'✅' if health['services']['qdrant'] else '❌'}")
    print(f"   Mem0:   {'✅' if health['services']['mem0'] else '❌'}")
    print(f"   RAG:    {'✅' if health['services']['rag'] else '❌'}")
    
    # Cleanup
    await server.cleanup_services()
    
    if all(health['services'].values()):
        print("\n🎉 All services are working correctly!")
        return True
    else:
        print("\n⚠️  Some services failed to initialize")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_health())
    sys.exit(0 if success else 1) 