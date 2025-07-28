#!/usr/bin/env python3
"""
Test script to verify all MCP RAG tools functionality using MCP protocol.
"""

import asyncio
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class MCPRAGToolsMCPTester:
    """Tester for MCP RAG tools using MCP protocol."""
    
    def __init__(self):
        self.test_results = {}
        self.test_user_id = "test_user_123"
        self.test_session_id = None
        self.test_document_id = None
        self.test_memory_id = None
        self.mcp_process = None
        
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
    
    async def send_mcp_request(self, method: str, params: dict = None) -> dict:
        """Send MCP request and get response."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send request to MCP server
            request_str = json.dumps(request) + "\n"
            self.mcp_process.stdin.write(request_str)
            self.mcp_process.stdin.flush()
            
            # Read response
            response_line = self.mcp_process.stdout.readline().strip()
            if response_line:
                return json.loads(response_line)
            else:
                return {"error": "No response from server"}
        except Exception as e:
            return {"error": str(e)}
    
    async def initialize_mcp_connection(self):
        """Initialize MCP connection."""
        print("🔌 Initializing MCP connection...")
        try:
            # Start MCP server process
            self.mcp_process = subprocess.Popen(
                ["docker", "exec", "-i", "mcp-rag-server-http", "python", "run_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "MCP RAG Tools Tester",
                        "version": "1.0.0"
                    }
                }
            }
            
            init_str = json.dumps(init_request) + "\n"
            self.mcp_process.stdin.write(init_str)
            self.mcp_process.stdin.flush()
            
            # Read initialization response
            response_line = self.mcp_process.stdout.readline().strip()
            if response_line:
                response = json.loads(response_line)
                if "result" in response:
                    print("✅ MCP connection initialized successfully")
                    return True
                else:
                    print(f"❌ MCP initialization failed: {response}")
                    return False
            else:
                print("❌ No response from MCP server")
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize MCP connection: {e}")
            return False
    
    async def test_health_check(self):
        """Test health check tool."""
        print("\n🔍 Testing Health Check Tool...")
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "health_check",
                "arguments": {}
            })
            
            if "result" in result and result["result"].get("success", False):
                services = list(result["result"].get("data", {}).get("services", {}).keys())
                self.log_test_result("health_check", True, f"Services: {services}")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("health_check", False, error)
        except Exception as e:
            self.log_test_result("health_check", False, str(e))
    
    async def test_document_tools(self):
        """Test document management tools."""
        print("\n📄 Testing Document Management Tools...")
        
        # Test add_document
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "add_document",
                "arguments": {
                    "content": "This is a test document for MCP RAG tools testing.",
                    "metadata": {"type": "test", "created_by": "tester"},
                    "user_id": self.test_user_id
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.test_document_id = result["result"].get("data", {}).get("document_id")
                self.log_test_result("add_document", True, f"Document ID: {self.test_document_id}")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("add_document", False, error)
        except Exception as e:
            self.log_test_result("add_document", False, str(e))
        
        # Test list_documents
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "list_documents",
                "arguments": {
                    "user_id": self.test_user_id,
                    "limit": 10
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                docs_count = len(result["result"].get("data", {}).get("documents", []))
                self.log_test_result("list_documents", True, f"Found {docs_count} documents")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("list_documents", False, error)
        except Exception as e:
            self.log_test_result("list_documents", False, str(e))
        
        # Test get_document_stats
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "get_document_stats",
                "arguments": {
                    "user_id": self.test_user_id
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                stats = result["result"].get("data", {})
                self.log_test_result("get_document_stats", True, f"Stats: {stats}")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("get_document_stats", False, error)
        except Exception as e:
            self.log_test_result("get_document_stats", False, str(e))
    
    async def test_search_tools(self):
        """Test search and query tools."""
        print("\n🔍 Testing Search and Query Tools...")
        
        # Test search_documents
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "search_documents",
                "arguments": {
                    "query": "test document",
                    "limit": 5,
                    "user_id": self.test_user_id
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                results_count = len(result["result"].get("data", {}).get("results", []))
                self.log_test_result("search_documents", True, f"Found {results_count} results")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("search_documents", False, error)
        except Exception as e:
            self.log_test_result("search_documents", False, str(e))
        
        # Test ask_question
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "ask_question",
                "arguments": {
                    "question": "What is this test document about?",
                    "user_id": self.test_user_id,
                    "use_memory": False
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.log_test_result("ask_question", True, "Question answered successfully")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("ask_question", False, error)
        except Exception as e:
            self.log_test_result("ask_question", False, str(e))
    
    async def test_memory_tools(self):
        """Test memory management tools."""
        print("\n🧠 Testing Memory Management Tools...")
        
        # Test add_memory
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "add_memory",
                "arguments": {
                    "content": "This is a test memory for MCP RAG tools testing.",
                    "memory_type": "conversation",
                    "user_id": self.test_user_id
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.test_memory_id = result["result"].get("data", {}).get("memory_id")
                self.log_test_result("add_memory", True, f"Memory ID: {self.test_memory_id}")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("add_memory", False, error)
        except Exception as e:
            self.log_test_result("add_memory", False, str(e))
        
        # Test get_user_memories
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "get_user_memories",
                "arguments": {
                    "user_id": self.test_user_id,
                    "limit": 10
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                memories_count = len(result["result"].get("data", {}).get("memories", []))
                self.log_test_result("get_user_memories", True, f"Found {memories_count} memories")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("get_user_memories", False, error)
        except Exception as e:
            self.log_test_result("get_user_memories", False, str(e))
        
        # Test search_memories
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "search_memories",
                "arguments": {
                    "query": "test memory",
                    "user_id": self.test_user_id,
                    "limit": 5
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                results_count = len(result["result"].get("data", {}).get("results", []))
                self.log_test_result("search_memories", True, f"Found {results_count} results")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("search_memories", False, error)
        except Exception as e:
            self.log_test_result("search_memories", False, str(e))
    
    async def test_session_tools(self):
        """Test session management tools."""
        print("\n🔄 Testing Session Management Tools...")
        
        # Test create_session
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "create_session",
                "arguments": {
                    "user_id": self.test_user_id,
                    "session_name": "Test Session"
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.test_session_id = result["result"].get("data", {}).get("session_id")
                self.log_test_result("create_session", True, f"Session ID: {self.test_session_id}")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("create_session", False, error)
        except Exception as e:
            self.log_test_result("create_session", False, str(e))
        
        # Test list_sessions
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "list_sessions",
                "arguments": {
                    "user_id": self.test_user_id,
                    "limit": 10
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                sessions_count = len(result["result"].get("data", {}).get("sessions", []))
                self.log_test_result("list_sessions", True, f"Found {sessions_count} sessions")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("list_sessions", False, error)
        except Exception as e:
            self.log_test_result("list_sessions", False, str(e))
    
    async def test_ai_tools(self):
        """Test advanced AI tools."""
        print("\n🤖 Testing Advanced AI Tools...")
        
        # Test advanced_reasoning
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "advanced_reasoning",
                "arguments": {
                    "query": "What is the purpose of testing tools?",
                    "reasoning_type": "auto"
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.log_test_result("advanced_reasoning", True, "Reasoning completed successfully")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("advanced_reasoning", False, error)
        except Exception as e:
            self.log_test_result("advanced_reasoning", False, str(e))
        
        # Test context_analysis
        try:
            result = await self.send_mcp_request("tools/call", {
                "name": "context_analysis",
                "arguments": {
                    "query": "Analyze the context of this test",
                    "user_id": self.test_user_id
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.log_test_result("context_analysis", True, "Context analysis completed")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("context_analysis", False, error)
        except Exception as e:
            self.log_test_result("context_analysis", False, str(e))
    
    async def test_code_analysis_tools(self):
        """Test code analysis tools."""
        print("\n💻 Testing Code Analysis Tools...")
        
        # Test analyze_code_string
        try:
            test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
            result = await self.send_mcp_request("tools/call", {
                "name": "analyze_code_string",
                "arguments": {
                    "code": test_code,
                    "language": "python"
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.log_test_result("analyze_code_string", True, "Code string analysis completed")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("analyze_code_string", False, error)
        except Exception as e:
            self.log_test_result("analyze_code_string", False, str(e))
    
    async def test_advanced_features(self):
        """Test advanced features."""
        print("\n🚀 Testing Advanced Features...")
        
        # Test batch_add_documents
        try:
            documents = [
                {"content": "Test document 1", "metadata": {"type": "test"}},
                {"content": "Test document 2", "metadata": {"type": "test"}}
            ]
            result = await self.send_mcp_request("tools/call", {
                "name": "batch_add_documents",
                "arguments": {
                    "documents": documents,
                    "user_id": self.test_user_id
                }
            })
            
            if "result" in result and result["result"].get("success", False):
                self.log_test_result("batch_add_documents", True, "Batch document addition completed")
            else:
                error = result.get("error", "Unknown error")
                self.log_test_result("batch_add_documents", False, error)
        except Exception as e:
            self.log_test_result("batch_add_documents", False, str(e))
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test document
        if self.test_document_id:
            try:
                result = await self.send_mcp_request("tools/call", {
                    "name": "delete_document",
                    "arguments": {
                        "document_id": self.test_document_id,
                        "user_id": self.test_user_id
                    }
                })
                if "result" in result and result["result"].get("success", False):
                    print("   ✅ Test document deleted")
                else:
                    print(f"   ⚠️  Could not delete test document: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"   ⚠️  Could not delete test document: {e}")
        
        # Delete test session
        if self.test_session_id:
            try:
                result = await self.send_mcp_request("tools/call", {
                    "name": "delete_session",
                    "arguments": {
                        "session_id": self.test_session_id
                    }
                })
                if "result" in result and result["result"].get("success", False):
                    print("   ✅ Test session deleted")
                else:
                    print(f"   ⚠️  Could not delete test session: {result.get('error', 'Unknown error')}")
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
        results_file = Path("test_results_mcp.json")
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    
    async def cleanup(self):
        """Cleanup MCP connection."""
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            except:
                self.mcp_process.kill()
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting comprehensive MCP RAG tools testing via MCP protocol...")
        print(f"📁 Working directory: {Path.cwd()}")
        
        try:
            # Initialize MCP connection
            if not await self.initialize_mcp_connection():
                print("❌ Failed to initialize MCP connection. Exiting.")
                return
            
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
        finally:
            await self.cleanup()


async def main():
    """Main test runner."""
    tester = MCPRAGToolsMCPTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 