---
title: project-overview
type: note
permalink: docs/00-overview/project-overview
tags:
- '[''overview'''
- '''project'
- architecture'
- '''obsidian-compatible'']'
---

# MCP RAG Server - Project Overview

## Introduction

The MCP RAG Server is a comprehensive Retrieval-Augmented Generation (RAG) solution built on the Model Context Protocol (MCP). It provides a standardized interface for LLM applications to access document storage, semantic search, and AI-powered question answering capabilities.

## Key Features

- **Vector Database Integration**: [[Qdrant]] for efficient similarity search and document storage
- **Memory Management**: [[Mem0]] for personalized conversation context and user memory
- **AI Generation**: [[Gemini API]] for embeddings and text generation
- **MCP Protocol**: Standardized interface for LLM applications
- **Multi-user Support**: User-specific document storage and memory management
- **Real-time Search**: Semantic search across stored documents with relevance scoring

## Technology Stack

### Core Technologies
- **Python 3.9+**: Main programming language
- **MCP (Model Context Protocol)**: Standardized AI application interface
- **FastMCP**: High-performance MCP server implementation

### AI & ML Services
- **Google Gemini API**: Text generation and embedding creation
- **Qdrant**: Vector database for similarity search
- **Mem0**: Memory layer for conversation context

### Development Tools
- **Pydantic**: Data validation and settings management
- **Pytest**: Testing framework
- **Black & Ruff**: Code formatting and linting

## Architecture Overview

The MCP RAG Server follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Server    │    │   RAG Service   │
│                 │◄──►│                 │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Gemini API     │    │  Qdrant DB      │
                       │  (Embeddings)   │    │  (Vectors)      │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Gemini API     │    │  mem0 Service   │
                       │  (Generation)   │    │  (Memory)       │
                       └─────────────────┘    └─────────────────┘
```

## Use Cases

### Document Management
- Store and index documents with metadata
- Semantic search across document collections
- Document versioning and management

### Question Answering
- RAG-based question answering with document context
- Personalized responses based on user history
- Multi-turn conversations with memory

### Knowledge Management
- Build knowledge bases from various document sources
- Intelligent document retrieval and ranking
- Context-aware information access

## Getting Started

See [[../02-installation/installation-guide|Installation Guide]] for detailed setup instructions.

## Development Status

The project follows a phased development approach with comprehensive documentation in the `../04-development/` directory:

- **Phase 1**: ✅ Foundation (Completed)
  - [[../04-development/phase1-foundations|Documentation]]
  - Project structure and dependencies
  - Basic MCP server implementation
  - Configuration management
  - Gemini API integration
  - Qdrant service implementation

- **Phase 2**: ✅ RAG Core (Completed)
  - [[../04-development/phase2-rag-core|Documentation]]
  - Document ingestion pipeline
  - Embedding generation service
  - Vector storage and retrieval
  - Basic search functionality
  - RAG query pipeline

- **Phase 3**: ✅ MCP Integration (Completed)
  - [[../04-development/phase3-mcp-integration|Documentation]]
  - Document management tools
  - Search and query tools
  - Memory management tools
  - Data access resources
  - Validation and error handling

- **Phase 4**: 🔄 Memory Integration (25% Complete)
  - [[../04-development/phase4-memory-integration|Documentation]]
  - [[../04-development/phase4-memory-integration-implementation|Implementation Plan]]
  - Memory-aware RAG queries
  - User session management
  - Advanced memory context retrieval

- **Phase 5**: ⏳ Advanced Features (Planned)
  - [[../04-development/phase5-advanced-features|Documentation]]
  - Advanced document processing
  - Performance monitoring
  - Production features

**Complete Phase Overview**: [[../04-development/development-phases|Project Phases Overview]]

## Related Documentation

- [[../01-architecture/system-architecture|Architecture Details]]
- [[../02-installation/installation-guide|Development Guide]]
- [[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]
- [[../04-development/development-phases|Project Phases]]