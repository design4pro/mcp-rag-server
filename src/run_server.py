#!/usr/bin/env python3
"""
Simple script to run the MCP RAG Server.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_rag_server.server import main

if __name__ == "__main__":
    main()