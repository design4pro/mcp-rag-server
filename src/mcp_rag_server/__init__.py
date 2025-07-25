"""
MCP RAG Server - A Model Context Protocol server for RAG applications.

This package provides a complete RAG (Retrieval-Augmented Generation) server
that integrates with Qdrant vector database, mem0 memory layer, and Gemini API.
"""

__version__ = "0.1.0"
__author__ = "RAG Team"
__email__ = "team@example.com"

from .server import MCPRAGServer

__all__ = ["MCPRAGServer"]