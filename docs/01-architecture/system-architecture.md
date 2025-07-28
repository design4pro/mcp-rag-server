---
title: system-architecture
type: note
permalink: docs/01-architecture/system-architecture
tags:
- architecture
- system-design
- components
- obsidian-compatible
---

# System Architecture

## Overview

The MCP RAG Server is a comprehensive Retrieval-Augmented Generation (RAG) system that integrates multiple services to provide intelligent document processing, search, and question-answering capabilities.

## Project Structure

The project follows a well-organized directory structure designed for maintainability and scalability:

```
rag/
├── src/                          # Source code
│   ├── mcp_rag_server/          # Main package
│   │   ├── services/            # Core services
│   │   ├── tools/               # MCP tools
│   │   ├── resources/           # MCP resources
│   │   └── validation.py        # Validation schemas
│   ├── run_server.py            # MCP server runner
│   └── run_server_http.py       # HTTP server runner
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── docker/                      # Docker configuration
│   ├── docker-compose.yml       # Service orchestration
│   └── Dockerfile               # Container definition
├── data/                        # Persistent data
│   └── mem0_data/               # Memory storage
├── logs/                        # Log files
├── scripts/                     # Management scripts
├── docs/                        # Documentation
└── examples/                    # Usage examples
```

For detailed information about the refactoring that established this structure, see [[../04-development/project-refactoring|project-refactoring]].

## Architecture Components

### Core Services

1. **Gemini Service** (`gemini_service.py`)

   - Handles text embeddings generation using Google's Gemini API
   - Manages API authentication and rate limiting
   - Provides batch embedding capabilities

2. **Qdrant Service** (`qdrant_service.py`)

   - Vector database management using Qdrant
   - Handles document storage, retrieval, and similarity search
   - Manages collections and indexes

3. **Mem0 Service** (`mem0_service.py`)

   - Conversation memory management using mem0
   - Stores and retrieves user conversation history
   - Provides context-aware memory retrieval

4. **RAG Service** (`rag_service.py`)

   - Orchestrates the complete RAG pipeline
   - Coordinates document processing, embedding, storage, and retrieval
   - Handles question-answering with context

5. **Document Processor** (`document_processor.py`)
   - Handles document chunking and preprocessing
   - Manages text splitting and tokenization
   - Provides document validation and metadata extraction

### MCP Integration Layer

#### Tools (Actions)

1. **Document Tools** (`tools/document_tools.py`)

   - `add_document`: Add documents to the RAG system
   - `delete_document`: Remove documents from the system
   - `get_document`: Retrieve specific documents
   - `list_documents`: List all documents
   - `get_document_stats`: Get system statistics

2. **Search Tools** (`tools/search_tools.py`)

   - `search_documents`: Semantic document search
   - `ask_question`: RAG-based question answering
   - `batch_search`: Multiple query processing
   - `get_search_suggestions`: Query suggestions

3. **Memory Tools** (`tools/memory_tools.py`)
   - `add_memory`: Store conversation memory
   - `get_user_memories`: Retrieve user memories
   - `delete_memory`: Remove specific memories
   - `clear_user_memories`: Clear all user memories
   - `get_memory_context`: Get relevant memory context
   - `get_user_session_info`: Session information

#### Resources (Data Sources)

1. **Document Resources** (`resources/document_resources.py`)

   - `rag://documents/{document_id}`: Document metadata
   - `rag://documents/{document_id}/content`: Document content
   - `rag://documents/{document_id}/chunks`: Document chunks
   - `rag://search/{query}/{limit}`: Search results
   - `rag://statistics/{user_id}`: System statistics

2. **Memory Resources** (`resources/memory_resources.py`)
   - `rag://memories/{user_id}/{limit}`: User memories
   - `rag://memories/{user_id}/context/{query}`: Memory context
   - `rag://memories/{user_id}/statistics`: Memory statistics
   - `rag://session/{user_id}`: Session information

### Validation and Error Handling

- **Validation System** (`validation.py`)
  - Pydantic-based input validation
  - Comprehensive error handling
  - Standardized response formats
  - Input sanitization and validation

## Data Flow

1. **Document Ingestion**:

   ```
   Document → Document Processor → Chunks → Embeddings → Qdrant Storage
   ```

2. **Search Process**:

   ```
   Query → Embedding → Qdrant Search → Results → RAG Service → Answer
   ```

3. **Memory Integration**:
   ```
   User Input → Memory Context → RAG Query → Enhanced Response
   ```

## Configuration

The system uses a centralized configuration system with environment variables:

- `GEMINI_API_KEY`: Google Gemini API key
- `QDRANT_URL`: Qdrant server URL
- `MEM0_SELF_HOSTED`: Enable self-hosted mem0
- `MEM0_LOCAL_STORAGE_PATH`: Local storage path for mem0
- `LOG_LEVEL`: Logging level

## Security and Performance

- **Security**: API key management, input validation, error sanitization
- **Performance**: Batch processing, connection pooling, caching
- **Scalability**: Modular design, service separation, async operations

## Current Status

- **Phase 1**: Foundations - ✅ Complete
  - [[../04-development/phase1-foundations|Documentation]]
- **Phase 2**: RAG Core - ✅ Complete
  - [[../04-development/phase2-rag-core|Documentation]]
- **Phase 3**: MCP Integration - ✅ Complete
  - [[../04-development/phase3-mcp-integration|Documentation]]
- **Phase 4**: Memory Integration - 🔄 In Progress (25% Complete)
  - [[../04-development/phase4-memory-integration|Documentation]]
  - [[../04-development/phase4-memory-integration-implementation|Implementation Plan]]
- **Phase 5**: Advanced Features - ⏳ Pending
  - [[../04-development/phase5-advanced-features|Documentation]]

**Complete Phase Overview**: [[../04-development/development-phases|Project Phases Overview]]

### Phase 4 Progress

- ✅ Basic mem0 service integration
- ✅ Memory storage infrastructure
- ✅ Basic memory CRUD operations
- 🔄 Memory-aware RAG queries (In Progress)
- ⏳ User session management (Pending)
- ⏳ Advanced memory context retrieval (Pending)

## Related Documentation

- [[../00-overview/project-overview|Project Overview]]
- [[../02-installation/installation-guide|Installation Guide]]
- [[../03-api/api-reference|API Reference]]
- [[../04-development/project-refactoring|Project Refactoring History]]