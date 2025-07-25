# System Architecture

## Overview

The MCP RAG Server follows a layered architecture pattern with clear separation of concerns. Each layer has specific responsibilities and communicates through well-defined interfaces.

## Architecture Layers

### 1. MCP Protocol Layer
The outermost layer that handles MCP protocol communication with clients.

**Components:**
- **FastMCP Server**: Main server implementation
- **Tools Registry**: MCP tools (actions) registration
- **Resources Registry**: MCP resources (data) registration
- **Protocol Handler**: Message routing and serialization

**Responsibilities:**
- Handle MCP protocol messages
- Route requests to appropriate services
- Manage client connections
- Provide standardized interface

### 2. Service Layer
Business logic layer that orchestrates the RAG pipeline.

**Components:**
- **RAGService**: Main orchestration service
- **GeminiService**: AI generation and embeddings
- **QdrantService**: Vector database operations
- **Mem0Service**: Memory management

**Responsibilities:**
- Coordinate between different services
- Implement business logic
- Handle data transformations
- Manage service lifecycle

### 3. External Services Layer
Integration layer for external APIs and services.

**Components:**
- **Google Gemini API**: Text generation and embeddings
- **Qdrant Vector Database**: Vector storage and search
- **Mem0 Memory Service**: Conversation memory

**Responsibilities:**
- Provide AI capabilities
- Store and retrieve vectors
- Manage conversation context

## Component Details

### MCPRAGServer
Main server class that initializes and manages all components.

```python
class MCPRAGServer:
    def __init__(self):
        self.mcp = FastMCP("MCP RAG Server")
        self.gemini_service: GeminiService
        self.qdrant_service: QdrantService
        self.mem0_service: Mem0Service
        self.rag_service: RAGService
```

### RAGService
Orchestrates the entire RAG pipeline.

**Key Methods:**
- `add_document()`: Document ingestion and indexing
- `search_documents()`: Semantic search
- `ask_question()`: RAG-based question answering
- `get_system_stats()`: System monitoring

### GeminiService
Handles all interactions with Google's Gemini API.

**Capabilities:**
- Text embedding generation
- Text generation with context
- Structured output generation
- Model configuration management

### QdrantService
Manages vector database operations.

**Features:**
- Document storage with metadata
- Semantic similarity search
- Filtering and pagination
- Collection management

### Mem0Service
Handles conversation memory and context.

**Features:**
- User-specific memory storage
- Memory relevance search
- Conversation context management
- Memory statistics

## Data Flow

### Document Ingestion Flow
```
1. Client → MCP Server → RAGService
2. RAGService → GeminiService (generate embedding)
3. RAGService → QdrantService (store document + embedding)
4. Response → Client
```

### Question Answering Flow
```
1. Client → MCP Server → RAGService
2. RAGService → Mem0Service (get relevant memories)
3. RAGService → GeminiService (generate query embedding)
4. RAGService → QdrantService (search similar documents)
5. RAGService → GeminiService (generate answer with context)
6. RAGService → Mem0Service (store conversation)
7. Response → Client
```

## Configuration Management

The system uses Pydantic Settings for type-safe configuration management.

**Configuration Classes:**
- `GeminiConfig`: API keys, models, parameters
- `QdrantConfig`: Database connection, collection settings
- `Mem0Config`: Memory service configuration
- `ServerConfig`: Server host, port, logging

## Error Handling

### Error Types
- **Service Initialization Errors**: Configuration or connection issues
- **API Errors**: External service failures
- **Validation Errors**: Invalid input data
- **Runtime Errors**: Unexpected system failures

### Error Handling Strategy
- Graceful degradation when optional services fail
- Detailed error logging for debugging
- User-friendly error messages
- Retry mechanisms for transient failures

## Security Considerations

### API Key Management
- Environment variable configuration
- Secure key storage
- Key rotation support

### Data Privacy
- User-specific data isolation
- Optional memory service
- Configurable data retention

### Access Control
- User ID-based filtering
- Document-level access control
- Memory isolation per user

## Performance Considerations

### Caching Strategy
- Embedding caching for repeated queries
- Memory caching for frequent access
- Connection pooling for external services

### Scalability
- Stateless service design
- Horizontal scaling support
- Database connection pooling
- Async/await for I/O operations

## Monitoring and Observability

### Metrics
- Request/response times
- Error rates
- Service health status
- Memory usage statistics

### Logging
- Structured logging with levels
- Request tracing
- Error context preservation
- Performance metrics

## Related Documentation

- [[Service Implementation Details]]
- [[Configuration Guide]]
- [[Performance Optimization]]
- [[Security Guidelines]]