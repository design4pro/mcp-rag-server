#!/usr/bin/env python3
"""
Test Phase 3 MCP Integration tools and resources.

This test verifies that all tools and resources are properly implemented
and working correctly.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_rag_server.server import MCPRAGServer
from mcp_rag_server.tools.document_tools import DocumentTools
from mcp_rag_server.tools.search_tools import SearchTools
from mcp_rag_server.tools.memory_tools import MemoryTools
from mcp_rag_server.resources.document_resources import DocumentResources
from mcp_rag_server.resources.memory_resources import MemoryResources
from mcp_rag_server.validation import (
    validate_document_input, validate_search_input, validate_question_input,
    validate_memory_input
)


async def test_validation():
    """Test validation functions."""
    print("🔍 Testing validation functions...")
    
    # Test document input validation
    try:
        doc_input = validate_document_input({
            "content": "Test document content",
            "metadata": {"source": "test"},
            "user_id": "test_user"
        })
        print("✅ Document input validation passed")
    except Exception as e:
        print(f"❌ Document input validation failed: {e}")
        return False
    
    # Test search input validation
    try:
        search_input = validate_search_input({
            "query": "test query",
            "limit": 5,
            "user_id": "test_user"
        })
        print("✅ Search input validation passed")
    except Exception as e:
        print(f"❌ Search input validation failed: {e}")
        return False
    
    # Test question input validation
    try:
        question_input = validate_question_input({
            "question": "What is this?",
            "user_id": "test_user",
            "use_memory": True,
            "max_context_docs": 3
        })
        print("✅ Question input validation passed")
    except Exception as e:
        print(f"❌ Question input validation failed: {e}")
        return False
    
    # Test memory input validation
    try:
        memory_input = validate_memory_input({
            "user_id": "test_user",
            "content": "Test memory content",
            "memory_type": "conversation"
        })
        print("✅ Memory input validation passed")
    except Exception as e:
        print(f"❌ Memory input validation failed: {e}")
        return False
    
    return True


async def test_tools():
    """Test tool classes."""
    print("\n🔧 Testing tool classes...")
    
    # Create server instance
    server = MCPRAGServer()
    
    try:
        # Initialize services
        await server.initialize_services()
        
        # Test document tools
        if server.document_tools:
            print("✅ Document tools initialized")
        else:
            print("❌ Document tools not initialized")
            return False
        
        # Test search tools
        if server.search_tools:
            print("✅ Search tools initialized")
        else:
            print("❌ Search tools not initialized")
            return False
        
        # Test memory tools
        if server.memory_tools:
            print("✅ Memory tools initialized")
        else:
            print("❌ Memory tools not initialized")
            return False
        
        # Test basic tool functionality
        result = await server.document_tools.add_document(
            "Test document for Phase 3",
            {"test": True},
            "test_user"
        )
        
        if result.get("success"):
            print("✅ Document tools functionality test passed")
            document_id = result.get("document_id")
            
            # Test search
            search_result = await server.search_tools.search_documents(
                "test document",
                5,
                "test_user"
            )
            
            if search_result.get("success"):
                print("✅ Search tools functionality test passed")
            else:
                print(f"❌ Search tools functionality test failed: {search_result}")
                return False
            
            # Test memory
            memory_result = await server.memory_tools.add_memory(
                "test_user",
                "Test memory entry",
                "conversation"
            )
            
            if memory_result.get("success"):
                print("✅ Memory tools functionality test passed")
            else:
                print(f"❌ Memory tools functionality test failed: {memory_result}")
                return False
            
        else:
            print(f"❌ Document tools functionality test failed: {result}")
            return False
        
        # Cleanup
        await server.cleanup_services()
        
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        await server.cleanup_services()
        return False
    
    return True


async def test_resources():
    """Test resource classes."""
    print("\n📚 Testing resource classes...")
    
    # Create server instance
    server = MCPRAGServer()
    
    try:
        # Initialize services
        await server.initialize_services()
        
        # Test document resources
        if server.document_resources:
            print("✅ Document resources initialized")
        else:
            print("❌ Document resources not initialized")
            return False
        
        # Test memory resources
        if server.memory_resources:
            print("✅ Memory resources initialized")
        else:
            print("❌ Memory resources not initialized")
            return False
        
        # Test resource functionality
        doc_metadata = server.document_resources.get_document_metadata("test_id")
        if "document_id" in doc_metadata:
            print("✅ Document resources functionality test passed")
        else:
            print(f"❌ Document resources functionality test failed: {doc_metadata}")
            return False
        
        mem_stats = server.memory_resources.get_memory_statistics("test_user")
        if "user_id" in mem_stats:
            print("✅ Memory resources functionality test passed")
        else:
            print(f"❌ Memory resources functionality test failed: {mem_stats}")
            return False
        
        # Cleanup
        await server.cleanup_services()
        
    except Exception as e:
        print(f"❌ Resources test failed: {e}")
        await server.cleanup_services()
        return False
    
    return True


async def test_mcp_integration():
    """Test MCP integration."""
    print("\n🔗 Testing MCP integration...")
    
    # Create server instance
    server = MCPRAGServer()
    
    try:
        # Initialize services
        await server.initialize_services()
        
        # Get MCP server
        mcp_server = server.get_server()
        
        if mcp_server:
            print("✅ MCP server created successfully")
        else:
            print("❌ MCP server creation failed")
            return False
        
        # Test that tools are registered
        # Note: We can't directly access the registered tools, but we can verify
        # that the server was created without errors
        
        # Cleanup
        await server.cleanup_services()
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        await server.cleanup_services()
        return False
    
    return True


async def main():
    """Run all Phase 3 tests."""
    print("🚀 Starting Phase 3 MCP Integration Tests...")
    
    tests = [
        ("Validation", test_validation),
        ("Tools", test_tools),
        ("Resources", test_resources),
        ("MCP Integration", test_mcp_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Phase 3 Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All Phase 3 tests passed!")
        return True
    else:
        print("⚠️  Some Phase 3 tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 