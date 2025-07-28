#!/usr/bin/env python3
"""
Comprehensive test script to verify all MCP RAG tools functionality.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_rag_server.config import config
from mcp_rag_server.server import MCPRAGServer


class MCPRAGToolsTester:
    """Comprehensive tester for all MCP RAG tools."""
    
    def __init__(self):
        self.server = MCPRAGServer()
        self.test_results = {}
        self.test_user_id = "test_user_123"
        self.test_session_id = None
        self.test_document_id = None
        self.test_memory_id = None
        
    async def initialize(self):
        """Initialize the server and services."""
        print("🚀 Initializing MCP RAG Server...")
        try:
            await self.server.initialize()
            print("✅ Server initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Server initialization failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup server resources."""
        try:
            await self.server.cleanup()
            print("✅ Server cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def log_test_result(self, tool_name: str, success: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {tool_name}")
        if details:
            print(f"      {details}")
        
        self.test_results[tool_name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    
    async def test_health_check(self):
        """Test health check tool."""
        print("\n🔍 Testing Health Check Tool...")
        try:
            # Get the health check function from the server
            health_check_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "health_check":
                    health_check_func = tool.func
                    break
            
            if health_check_func:
                result = await health_check_func()
                if result.get("success", False):
                    self.log_test_result("health_check", True, f"Services: {list(result.get('data', {}).keys())}")
                else:
                    self.log_test_result("health_check", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("health_check", False, "Tool not found")
        except Exception as e:
            self.log_test_result("health_check", False, str(e))
    
    async def test_document_tools(self):
        """Test document management tools."""
        print("\n📄 Testing Document Management Tools...")
        
        # Test add_document
        try:
            add_doc_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "add_document":
                    add_doc_func = tool.func
                    break
            
            if add_doc_func:
                result = await add_doc_func(
                    content="This is a test document for MCP RAG tools testing.",
                    metadata={"type": "test", "created_by": "tester"},
                    user_id=self.test_user_id
                )
                if result.get("success", False):
                    self.test_document_id = result.get("data", {}).get("document_id")
                    self.log_test_result("add_document", True, f"Document ID: {self.test_document_id}")
                else:
                    self.log_test_result("add_document", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("add_document", False, "Tool not found")
        except Exception as e:
            self.log_test_result("add_document", False, str(e))
        
        # Test list_documents
        try:
            list_docs_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "list_documents":
                    list_docs_func = tool.func
                    break
            
            if list_docs_func:
                result = await list_docs_func(user_id=self.test_user_id, limit=10)
                if result.get("success", False):
                    docs_count = len(result.get("data", {}).get("documents", []))
                    self.log_test_result("list_documents", True, f"Found {docs_count} documents")
                else:
                    self.log_test_result("list_documents", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("list_documents", False, "Tool not found")
        except Exception as e:
            self.log_test_result("list_documents", False, str(e))
        
        # Test get_document_stats
        try:
            stats_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "get_document_stats":
                    stats_func = tool.func
                    break
            
            if stats_func:
                result = await stats_func(user_id=self.test_user_id)
                if result.get("success", False):
                    stats = result.get("data", {})
                    self.log_test_result("get_document_stats", True, f"Stats: {stats}")
                else:
                    self.log_test_result("get_document_stats", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("get_document_stats", False, "Tool not found")
        except Exception as e:
            self.log_test_result("get_document_stats", False, str(e))
    
    async def test_search_tools(self):
        """Test search and query tools."""
        print("\n🔍 Testing Search and Query Tools...")
        
        # Test search_documents
        try:
            search_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "search_documents":
                    search_func = tool.func
                    break
            
            if search_func:
                result = await search_func(
                    query="test document",
                    limit=5,
                    user_id=self.test_user_id
                )
                if result.get("success", False):
                    results_count = len(result.get("data", {}).get("results", []))
                    self.log_test_result("search_documents", True, f"Found {results_count} results")
                else:
                    self.log_test_result("search_documents", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("search_documents", False, "Tool not found")
        except Exception as e:
            self.log_test_result("search_documents", False, str(e))
        
        # Test ask_question
        try:
            ask_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "ask_question":
                    ask_func = tool.func
                    break
            
            if ask_func:
                result = await ask_func(
                    question="What is this test document about?",
                    user_id=self.test_user_id,
                    use_memory=False
                )
                if result.get("success", False):
                    self.log_test_result("ask_question", True, "Question answered successfully")
                else:
                    self.log_test_result("ask_question", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("ask_question", False, "Tool not found")
        except Exception as e:
            self.log_test_result("ask_question", False, str(e))
    
    async def test_memory_tools(self):
        """Test memory management tools."""
        print("\n🧠 Testing Memory Management Tools...")
        
        # Test add_memory
        try:
            add_memory_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "add_memory":
                    add_memory_func = tool.func
                    break
            
            if add_memory_func:
                result = await add_memory_func(
                    content="This is a test memory for MCP RAG tools testing.",
                    memory_type="conversation",
                    user_id=self.test_user_id
                )
                if result.get("success", False):
                    self.test_memory_id = result.get("data", {}).get("memory_id")
                    self.log_test_result("add_memory", True, f"Memory ID: {self.test_memory_id}")
                else:
                    self.log_test_result("add_memory", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("add_memory", False, "Tool not found")
        except Exception as e:
            self.log_test_result("add_memory", False, str(e))
        
        # Test get_user_memories
        try:
            get_memories_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "get_user_memories":
                    get_memories_func = tool.func
                    break
            
            if get_memories_func:
                result = await get_memories_func(user_id=self.test_user_id, limit=10)
                if result.get("success", False):
                    memories_count = len(result.get("data", {}).get("memories", []))
                    self.log_test_result("get_user_memories", True, f"Found {memories_count} memories")
                else:
                    self.log_test_result("get_user_memories", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("get_user_memories", False, "Tool not found")
        except Exception as e:
            self.log_test_result("get_user_memories", False, str(e))
        
        # Test search_memories
        try:
            search_memories_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "search_memories":
                    search_memories_func = tool.func
                    break
            
            if search_memories_func:
                result = await search_memories_func(
                    query="test memory",
                    user_id=self.test_user_id,
                    limit=5
                )
                if result.get("success", False):
                    results_count = len(result.get("data", {}).get("results", []))
                    self.log_test_result("search_memories", True, f"Found {results_count} results")
                else:
                    self.log_test_result("search_memories", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("search_memories", False, "Tool not found")
        except Exception as e:
            self.log_test_result("search_memories", False, str(e))
    
    async def test_session_tools(self):
        """Test session management tools."""
        print("\n🔄 Testing Session Management Tools...")
        
        # Test create_session
        try:
            create_session_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "create_session":
                    create_session_func = tool.func
                    break
            
            if create_session_func:
                result = await create_session_func(
                    user_id=self.test_user_id,
                    session_name="Test Session"
                )
                if result.get("success", False):
                    self.test_session_id = result.get("data", {}).get("session_id")
                    self.log_test_result("create_session", True, f"Session ID: {self.test_session_id}")
                else:
                    self.log_test_result("create_session", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("create_session", False, "Tool not found")
        except Exception as e:
            self.log_test_result("create_session", False, str(e))
        
        # Test get_session
        if self.test_session_id:
            try:
                get_session_func = None
                for tool in self.server.mcp._tools:
                    if tool.name == "get_session":
                        get_session_func = tool.func
                        break
                
                if get_session_func:
                    result = await get_session_func(self.test_session_id)
                    if result.get("success", False):
                        self.log_test_result("get_session", True, "Session retrieved successfully")
                    else:
                        self.log_test_result("get_session", False, result.get("error", "Unknown error"))
                else:
                    self.log_test_result("get_session", False, "Tool not found")
            except Exception as e:
                self.log_test_result("get_session", False, str(e))
        
        # Test list_sessions
        try:
            list_sessions_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "list_sessions":
                    list_sessions_func = tool.func
                    break
            
            if list_sessions_func:
                result = await list_sessions_func(user_id=self.test_user_id, limit=10)
                if result.get("success", False):
                    sessions_count = len(result.get("data", {}).get("sessions", []))
                    self.log_test_result("list_sessions", True, f"Found {sessions_count} sessions")
                else:
                    self.log_test_result("list_sessions", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("list_sessions", False, "Tool not found")
        except Exception as e:
            self.log_test_result("list_sessions", False, str(e))
    
    async def test_ai_tools(self):
        """Test advanced AI tools."""
        print("\n🤖 Testing Advanced AI Tools...")
        
        # Test advanced_reasoning
        try:
            reasoning_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "advanced_reasoning":
                    reasoning_func = tool.func
                    break
            
            if reasoning_func:
                result = await reasoning_func(
                    query="What is the purpose of testing tools?",
                    reasoning_type="auto"
                )
                if result.get("success", False):
                    self.log_test_result("advanced_reasoning", True, "Reasoning completed successfully")
                else:
                    self.log_test_result("advanced_reasoning", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("advanced_reasoning", False, "Tool not found")
        except Exception as e:
            self.log_test_result("advanced_reasoning", False, str(e))
        
        # Test context_analysis
        try:
            context_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "context_analysis":
                    context_func = tool.func
                    break
            
            if context_func:
                result = await context_func(
                    query="Analyze the context of this test",
                    user_id=self.test_user_id
                )
                if result.get("success", False):
                    self.log_test_result("context_analysis", True, "Context analysis completed")
                else:
                    self.log_test_result("context_analysis", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("context_analysis", False, "Tool not found")
        except Exception as e:
            self.log_test_result("context_analysis", False, str(e))
    
    async def test_code_analysis_tools(self):
        """Test code analysis tools."""
        print("\n💻 Testing Code Analysis Tools...")
        
        # Test analyze_source_code
        try:
            analyze_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "analyze_source_code":
                    analyze_func = tool.func
                    break
            
            if analyze_func:
                # Test with a simple Python file
                test_code = """
def hello_world():
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42
"""
                result = await analyze_func(
                    file_path="test_file.py",
                    language="python"
                )
                if result.get("success", False):
                    self.log_test_result("analyze_source_code", True, "Code analysis completed")
                else:
                    self.log_test_result("analyze_source_code", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("analyze_source_code", False, "Tool not found")
        except Exception as e:
            self.log_test_result("analyze_source_code", False, str(e))
        
        # Test analyze_code_string
        try:
            code_string_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "analyze_code_string":
                    code_string_func = tool.func
                    break
            
            if code_string_func:
                test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
                result = await code_string_func(
                    code=test_code,
                    language="python"
                )
                if result.get("success", False):
                    self.log_test_result("analyze_code_string", True, "Code string analysis completed")
                else:
                    self.log_test_result("analyze_code_string", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("analyze_code_string", False, "Tool not found")
        except Exception as e:
            self.log_test_result("analyze_code_string", False, str(e))
    
    async def test_advanced_features(self):
        """Test advanced features."""
        print("\n🚀 Testing Advanced Features...")
        
        # Test batch_add_documents
        try:
            batch_add_func = None
            for tool in self.server.mcp._tools:
                if tool.name == "batch_add_documents":
                    batch_add_func = tool.func
                    break
            
            if batch_add_func:
                documents = [
                    {"content": "Test document 1", "metadata": {"type": "test"}},
                    {"content": "Test document 2", "metadata": {"type": "test"}}
                ]
                result = await batch_add_func(
                    documents=documents,
                    user_id=self.test_user_id
                )
                if result.get("success", False):
                    self.log_test_result("batch_add_documents", True, "Batch document addition completed")
                else:
                    self.log_test_result("batch_add_documents", False, result.get("error", "Unknown error"))
            else:
                self.log_test_result("batch_add_documents", False, "Tool not found")
        except Exception as e:
            self.log_test_result("batch_add_documents", False, str(e))
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test document
        if self.test_document_id:
            try:
                delete_doc_func = None
                for tool in self.server.mcp._tools:
                    if tool.name == "delete_document":
                        delete_doc_func = tool.func
                        break
                
                if delete_doc_func:
                    await delete_doc_func(self.test_document_id, self.test_user_id)
                    print("   ✅ Test document deleted")
            except Exception as e:
                print(f"   ⚠️  Could not delete test document: {e}")
        
        # Delete test session
        if self.test_session_id:
            try:
                delete_session_func = None
                for tool in self.server.mcp._tools:
                    if tool.name == "delete_session":
                        delete_session_func = tool.func
                        break
                
                if delete_session_func:
                    await delete_session_func(self.test_session_id)
                    print("   ✅ Test session deleted")
            except Exception as e:
                print(f"   ⚠️  Could not delete test session: {e}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("📊 MCP RAG TOOLS TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tools Tested: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for tool_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} {tool_name}")
            if result["details"]:
                print(f"      {result['details']}")
        
        if failed_tests == 0:
            print("\n🎉 All MCP RAG tools are working correctly!")
        else:
            print(f"\n⚠️  {failed_tests} tools have issues that need attention.")
        
        # Save results to file
        results_file = Path("test_results.json")
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting comprehensive MCP RAG tools testing...")
        print(f"📁 Working directory: {Path.cwd()}")
        print(f"🔧 Config loaded: {config}")
        
        # Initialize server
        if not await self.initialize():
            print("❌ Failed to initialize server. Exiting.")
            return
        
        try:
            # Run all test categories
            await self.test_health_check()
            await self.test_document_tools()
            await self.test_search_tools()
            await self.test_memory_tools()
            await self.test_session_tools()
            await self.test_ai_tools()
            await self.test_code_analysis_tools()
            await self.test_advanced_features()
            
            # Cleanup test data
            await self.cleanup_test_data()
            
            # Print summary
            self.print_summary()
            
        finally:
            # Always cleanup
            await self.cleanup()


async def main():
    """Main test runner."""
    tester = MCPRAGToolsTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 