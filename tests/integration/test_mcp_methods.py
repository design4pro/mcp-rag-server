#!/usr/bin/env python3
"""
Test to check available MCP methods.
"""

import asyncio
import sys
import os
import json
import subprocess
from pathlib import Path


async def test_mcp_methods():
    """Test different MCP methods."""
    print("🔍 Testing MCP methods...")
    
    try:
        # Start MCP server process
        mcp_process = subprocess.Popen(
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
                    "name": "MCP Methods Tester",
                    "version": "1.0.0"
                }
            }
        }
        
        init_str = json.dumps(init_request) + "\n"
        mcp_process.stdin.write(init_str)
        mcp_process.stdin.flush()
        
        # Read initialization response
        response_line = mcp_process.stdout.readline().strip()
        if response_line:
            response = json.loads(response_line)
            if "result" in response:
                print("✅ MCP connection initialized successfully")
                print(f"Server info: {response['result']}")
            else:
                print(f"❌ MCP initialization failed: {response}")
                return
        
        # Test different method names
        methods_to_test = [
            "tools/list",
            "tools/list",
            "listTools",
            "tools.list",
            "list_tools"
        ]
        
        for i, method in enumerate(methods_to_test):
            print(f"\n🔍 Testing method: {method}")
            
            request = {
                "jsonrpc": "2.0",
                "id": i + 1,
                "method": method
            }
            
            request_str = json.dumps(request) + "\n"
            mcp_process.stdin.write(request_str)
            mcp_process.stdin.flush()
            
            # Read response
            response_line = mcp_process.stdout.readline().strip()
            if response_line:
                response = json.loads(response_line)
                print(f"Response: {response}")
            else:
                print("No response")
        
        # Cleanup
        mcp_process.terminate()
        mcp_process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main function."""
    await test_mcp_methods()


if __name__ == "__main__":
    asyncio.run(main()) 