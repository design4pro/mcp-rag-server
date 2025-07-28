#!/usr/bin/env python3
"""
Simple test to list available MCP tools.
"""

import asyncio
import sys
import os
import json
import subprocess
from pathlib import Path


async def list_mcp_tools():
    """List available MCP tools."""
    print("🔍 Listing available MCP tools...")
    
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
                    "name": "MCP Tools Lister",
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
            else:
                print(f"❌ MCP initialization failed: {response}")
                return
        
        # Send list tools request
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        list_str = json.dumps(list_tools_request) + "\n"
        mcp_process.stdin.write(list_str)
        mcp_process.stdin.flush()
        
        # Read tools list response
        response_line = mcp_process.stdout.readline().strip()
        if response_line:
            response = json.loads(response_line)
            if "result" in response:
                tools = response["result"].get("tools", [])
                print(f"📋 Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
                    if 'inputSchema' in tool:
                        print(f"     Schema: {tool['inputSchema']}")
            else:
                print(f"❌ Failed to list tools: {response}")
        else:
            print("❌ No response from server")
        
        # Cleanup
        mcp_process.terminate()
        mcp_process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main function."""
    await list_mcp_tools()


if __name__ == "__main__":
    asyncio.run(main()) 