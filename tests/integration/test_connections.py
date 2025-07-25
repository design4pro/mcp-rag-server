#!/usr/bin/env python3
"""
Test script to check connections to all RAG services.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_rag_server.config import config
from mcp_rag_server.services.gemini_service import GeminiService
from mcp_rag_server.services.qdrant_service import QdrantService
from mcp_rag_server.services.mem0_service import Mem0Service


async def test_gemini():
    """Test Gemini service connection."""
    print("🔍 Testing Gemini service...")
    try:
        service = GeminiService(config.gemini)
        await service.initialize()
        print("✅ Gemini service connected successfully")
        await service.cleanup()
        return True
    except Exception as e:
        print(f"❌ Gemini service failed: {e}")
        return False


async def test_qdrant():
    """Test Qdrant service connection."""
    print("🔍 Testing Qdrant service...")
    try:
        service = QdrantService(config.qdrant)
        await service.initialize()
        print("✅ Qdrant service connected successfully")
        await service.cleanup()
        return True
    except Exception as e:
        print(f"❌ Qdrant service failed: {e}")
        return False


async def test_mem0():
    """Test Mem0 service connection."""
    print("🔍 Testing Mem0 service...")
    try:
        service = Mem0Service(config.mem0)
        await service.initialize()
        print("✅ Mem0 service connected successfully")
        await service.cleanup()
        return True
    except Exception as e:
        print(f"❌ Mem0 service failed: {e}")
        return False


async def main():
    """Run all connection tests."""
    print("🚀 Testing RAG service connections...")
    print(f"📁 Working directory: {Path.cwd()}")
    print(f"🔧 Config loaded: {config}")
    print()
    
    results = []
    
    # Test each service
    results.append(await test_gemini())
    print()
    results.append(await test_qdrant())
    print()
    results.append(await test_mem0())
    print()
    
    # Summary
    print("📊 Connection Test Summary:")
    print(f"   Gemini: {'✅' if results[0] else '❌'}")
    print(f"   Qdrant: {'✅' if results[1] else '❌'}")
    print(f"   Mem0:   {'✅' if results[2] else '❌'}")
    
    if all(results):
        print("\n🎉 All services are working correctly!")
    else:
        print("\n⚠️  Some services failed. Check your configuration and ensure services are running.")
        print("\n💡 Make sure to:")
        print("   1. Copy .env.example to .env and fill in your Gemini API key")
        print("   2. Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
        print("   3. Mem0 is automatically configured (open source)")


if __name__ == "__main__":
    asyncio.run(main()) 