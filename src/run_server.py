#!/usr/bin/env python3
"""
STDIO server script to run the MCP RAG Server.
"""

import sys
import os
import signal
import asyncio
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_rag_server.server import MCPRAGServer
from mcp_rag_server.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.server.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variable to track server instance
server_instance = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if server_instance:
        asyncio.create_task(server_instance.cleanup_services())
    sys.exit(0)

def main():
    """Main entry point for the MCP RAG Server."""
    global server_instance
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server = MCPRAGServer()
        server_instance = server
        
        # Initialize services
        asyncio.run(server.initialize_services())
        
        # Get the FastMCP server
        mcp_server = server.get_server()
        
        # Run the server using stdio transport
        logger.info("Starting MCP RAG Server on STDIO...")
        mcp_server.run(transport="stdio")
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)
    finally:
        if server_instance:
            asyncio.run(server_instance.cleanup_services())

if __name__ == "__main__":
    main()