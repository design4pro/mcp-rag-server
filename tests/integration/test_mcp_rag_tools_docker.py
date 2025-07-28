#!/usr/bin/env python3
"""
Test script to verify all MCP RAG tools functionality using running Docker services.
"""

import asyncio
import sys
import os
import json
import httpx
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_rag_server.config import config


class MCPRAGToolsDockerTester:
    """Tester for MCP RAG tools using Docker services."""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.test_results = {}
        self.test_user_id = "test_user_123"
        self.test_session_id = None
        self.test_document_id = None
        self.test_memory_id = None
        
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
        """Test health check endpoint."""
        print("\n🔍 Testing Health Check...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        services = list(data.get("services", {}).keys())
                        self.log_test_result("health_check", True, f"Services: {services}")
                    else:
                        self.log_test_result("health_check", False, "Health check failed")
                else:
                    self.log_test_result("health_check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("health_check", False, str(e))
    
    async def test_document_tools(self):
        """Test document management tools."""
        print("\n📄 Testing Document Management Tools...")
        
        # Test add_document
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/documents",
                    json={
                        "content": "This is a test document for MCP RAG tools testing.",
                        "metadata": {"type": "test", "created_by": "tester"},
                        "user_id": self.test_user_id
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.test_document_id = data.get("data", {}).get("document_id")
                        self.log_test_result("add_document", True, f"Document ID: {self.test_document_id}")
                    else:
                        self.log_test_result("add_document", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("add_document", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("add_document", False, str(e))
        
        # Test list_documents
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/documents",
                    params={"user_id": self.test_user_id, "limit": 10}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        docs_count = len(data.get("data", {}).get("documents", []))
                        self.log_test_result("list_documents", True, f"Found {docs_count} documents")
                    else:
                        self.log_test_result("list_documents", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("list_documents", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("list_documents", False, str(e))
        
        # Test get_document_stats
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/documents/stats",
                    params={"user_id": self.test_user_id}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        stats = data.get("data", {})
                        self.log_test_result("get_document_stats", True, f"Stats: {stats}")
                    else:
                        self.log_test_result("get_document_stats", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("get_document_stats", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("get_document_stats", False, str(e))
    
    async def test_search_tools(self):
        """Test search and query tools."""
        print("\n🔍 Testing Search and Query Tools...")
        
        # Test search_documents
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "query": "test document",
                        "limit": 5,
                        "user_id": self.test_user_id
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        results_count = len(data.get("data", {}).get("results", []))
                        self.log_test_result("search_documents", True, f"Found {results_count} results")
                    else:
                        self.log_test_result("search_documents", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("search_documents", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("search_documents", False, str(e))
        
        # Test ask_question
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/ask",
                    json={
                        "question": "What is this test document about?",
                        "user_id": self.test_user_id,
                        "use_memory": False
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.log_test_result("ask_question", True, "Question answered successfully")
                    else:
                        self.log_test_result("ask_question", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("ask_question", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("ask_question", False, str(e))
    
    async def test_memory_tools(self):
        """Test memory management tools."""
        print("\n🧠 Testing Memory Management Tools...")
        
        # Test add_memory
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/memories",
                    json={
                        "content": "This is a test memory for MCP RAG tools testing.",
                        "memory_type": "conversation",
                        "user_id": self.test_user_id
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.test_memory_id = data.get("data", {}).get("memory_id")
                        self.log_test_result("add_memory", True, f"Memory ID: {self.test_memory_id}")
                    else:
                        self.log_test_result("add_memory", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("add_memory", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("add_memory", False, str(e))
        
        # Test get_user_memories
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/memories",
                    params={"user_id": self.test_user_id, "limit": 10}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        memories_count = len(data.get("data", {}).get("memories", []))
                        self.log_test_result("get_user_memories", True, f"Found {memories_count} memories")
                    else:
                        self.log_test_result("get_user_memories", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("get_user_memories", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("get_user_memories", False, str(e))
        
        # Test search_memories
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/memories/search",
                    json={
                        "query": "test memory",
                        "user_id": self.test_user_id,
                        "limit": 5
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        results_count = len(data.get("data", {}).get("results", []))
                        self.log_test_result("search_memories", True, f"Found {results_count} results")
                    else:
                        self.log_test_result("search_memories", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("search_memories", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("search_memories", False, str(e))
    
    async def test_session_tools(self):
        """Test session management tools."""
        print("\n🔄 Testing Session Management Tools...")
        
        # Test create_session
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sessions",
                    json={
                        "user_id": self.test_user_id,
                        "session_name": "Test Session"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.test_session_id = data.get("data", {}).get("session_id")
                        self.log_test_result("create_session", True, f"Session ID: {self.test_session_id}")
                    else:
                        self.log_test_result("create_session", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("create_session", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("create_session", False, str(e))
        
        # Test get_session
        if self.test_session_id:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}/sessions/{self.test_session_id}")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success", False):
                            self.log_test_result("get_session", True, "Session retrieved successfully")
                        else:
                            self.log_test_result("get_session", False, data.get("error", "Unknown error"))
                    else:
                        self.log_test_result("get_session", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test_result("get_session", False, str(e))
        
        # Test list_sessions
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/sessions",
                    params={"user_id": self.test_user_id, "limit": 10}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        sessions_count = len(data.get("data", {}).get("sessions", []))
                        self.log_test_result("list_sessions", True, f"Found {sessions_count} sessions")
                    else:
                        self.log_test_result("list_sessions", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("list_sessions", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("list_sessions", False, str(e))
    
    async def test_ai_tools(self):
        """Test advanced AI tools."""
        print("\n🤖 Testing Advanced AI Tools...")
        
        # Test advanced_reasoning
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/ai/reasoning",
                    json={
                        "query": "What is the purpose of testing tools?",
                        "reasoning_type": "auto"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.log_test_result("advanced_reasoning", True, "Reasoning completed successfully")
                    else:
                        self.log_test_result("advanced_reasoning", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("advanced_reasoning", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("advanced_reasoning", False, str(e))
        
        # Test context_analysis
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/ai/context",
                    json={
                        "query": "Analyze the context of this test",
                        "user_id": self.test_user_id
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.log_test_result("context_analysis", True, "Context analysis completed")
                    else:
                        self.log_test_result("context_analysis", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("context_analysis", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("context_analysis", False, str(e))
    
    async def test_code_analysis_tools(self):
        """Test code analysis tools."""
        print("\n💻 Testing Code Analysis Tools...")
        
        # Test analyze_code_string
        try:
            async with httpx.AsyncClient() as client:
                test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
                response = await client.post(
                    f"{self.base_url}/code/analyze",
                    json={
                        "code": test_code,
                        "language": "python"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.log_test_result("analyze_code_string", True, "Code string analysis completed")
                    else:
                        self.log_test_result("analyze_code_string", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("analyze_code_string", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("analyze_code_string", False, str(e))
    
    async def test_advanced_features(self):
        """Test advanced features."""
        print("\n🚀 Testing Advanced Features...")
        
        # Test batch_add_documents
        try:
            async with httpx.AsyncClient() as client:
                documents = [
                    {"content": "Test document 1", "metadata": {"type": "test"}},
                    {"content": "Test document 2", "metadata": {"type": "test"}}
                ]
                response = await client.post(
                    f"{self.base_url}/documents/batch",
                    json={
                        "documents": documents,
                        "user_id": self.test_user_id
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        self.log_test_result("batch_add_documents", True, "Batch document addition completed")
                    else:
                        self.log_test_result("batch_add_documents", False, data.get("error", "Unknown error"))
                else:
                    self.log_test_result("batch_add_documents", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("batch_add_documents", False, str(e))
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test document
        if self.test_document_id:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"{self.base_url}/documents/{self.test_document_id}",
                        params={"user_id": self.test_user_id}
                    )
                    if response.status_code == 200:
                        print("   ✅ Test document deleted")
                    else:
                        print(f"   ⚠️  Could not delete test document: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Could not delete test document: {e}")
        
        # Delete test session
        if self.test_session_id:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.delete(f"{self.base_url}/sessions/{self.test_session_id}")
                    if response.status_code == 200:
                        print("   ✅ Test session deleted")
                    else:
                        print(f"   ⚠️  Could not delete test session: HTTP {response.status_code}")
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
        results_file = Path("test_results_docker.json")
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting comprehensive MCP RAG tools testing via Docker...")
        print(f"📁 Working directory: {Path.cwd()}")
        print(f"🌐 Testing against: {self.base_url}")
        
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
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")


async def main():
    """Main test runner."""
    tester = MCPRAGToolsDockerTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 