"""
Resources module for MCP RAG Server.

This module contains all MCP resources (data sources) that can be accessed by clients:
- Document resources
- Search result resources
- Memory context resources
"""

from .document_resources import DocumentResources

__all__ = ["DocumentResources"]