"""
Resources module for MCP RAG Server.

This module contains all MCP resources (data sources) that can be accessed by clients:
- Document resources
- Memory resources
- Search result resources
"""

from .document_resources import DocumentResources
from .memory_resources import MemoryResources

__all__ = ["DocumentResources", "MemoryResources"]