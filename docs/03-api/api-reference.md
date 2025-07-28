---
title: api-reference
type: note
permalink: docs/03-api/api-reference
tags:
- api-reference
- mcp-tools
- resources
- obsidian-compatible
---

# API Reference and Usage Guide

## MCP Tools Reference

### Document Management Tools

#### add_document
Add a document to the RAG system.

**Parameters:**
- `content` (string, required): Document content
- `metadata` (object, optional): Document metadata
- `user_id` (string, optional): User identifier (default: "default")

**Example:**
```json
{
  "content": "This is a sample document about machine learning.",
  "metadata": {
    "title": "ML Introduction",
    "author": "John Doe",
    "category": "technology"
  },
  "user_id": "user123"
}
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "status": "success",
  "chunks_created": 5
}
```

#### delete_document
Remove a document from the system.

**Parameters:**
- `document_id` (string, required): Document identifier
- `user_id` (string, optional): User identifier (default: "default")

#### get_document
Retrieve a specific document.

**Parameters:**
- `document_id` (string, required): Document identifier

**Response:**
```json
{
  "document_id": "doc_abc123",
  "content": "This is a sample document...",
  "metadata": {
    "title": "ML Introduction",
    "author": "John Doe"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "chunks": 5
}
```

#### list_documents
List all documents for a user.

**Parameters:**
- `user_id` (string, optional): User identifier (default: "default")
- `limit` (integer, optional): Maximum number of documents (default: 100)

#### get_document_stats
Get system statistics.

**Parameters:**
- `user_id` (string, optional): User identifier (default: "default")

**Response:**
```json
{
  "total_documents": 10,
  "total_chunks": 150,
  "total_memories": 25,
  "storage_size_mb": 45.2
}
```

### Search Tools

#### search_documents
Perform semantic search across documents.

**Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional): Maximum results (default: 5)
- `user_id` (string, optional): User identifier (default: "default")
- `filters` (object, optional): Search filters

**Example:**
```json
{
  "query": "machine learning algorithms",
  "limit": 10,
  "user_id": "user123",
  "filters": {
    "category": "technology",
    "date_after": "2024-01-01"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc_abc123",
      "content": "This document discusses machine learning...",
      "metadata": {
        "title": "ML Introduction",
        "author": "John Doe"
      },
      "score": 0.95,
      "chunk_index": 2
    }
  ],
  "total_found": 1
}
```

#### ask_question
Ask a question using RAG with memory context.

**Parameters:**
- `question` (string, required): Question to ask
- `user_id` (string, optional): User identifier (default: "default")
- `use_memory` (boolean, optional): Use memory context (default: true)
- `max_context_docs` (integer, optional): Maximum context documents (default: 3)

**Example:**
```json
{
  "question": "What are the main types of machine learning?",
  "user_id": "user123",
  "use_memory": true,
  "max_context_docs": 5
}
```

**Response:**
```json
{
  "answer": "Machine learning can be categorized into three main types: supervised learning, unsupervised learning, and reinforcement learning...",
  "sources": [
    {
      "document_id": "doc_abc123",
      "title": "ML Introduction",
      "score": 0.92
    }
  ],
  "memory_context": "Based on our previous conversation about AI..."
}
```

#### batch_search
Perform multiple searches simultaneously.

**Parameters:**
- `queries` (array, required): Array of search queries
- `limit` (integer, optional): Maximum results per query (default: 5)
- `user_id` (string, optional): User identifier (default: "default")

#### get_search_suggestions
Get search suggestions based on partial query.

**Parameters:**
- `partial_query` (string, required): Partial search query

**Response:**
```json
{
  "suggestions": [
    "machine learning",
    "machine learning algorithms",
    "machine learning applications",
    "machine learning vs deep learning"
  ]
}
```

### Memory Tools

#### add_memory
Store conversation memory.

**Parameters:**
- `user_id` (string, required): User identifier
- `content` (string, required): Memory content
- `memory_type` (string, optional): Memory type (default: "conversation")
- `metadata` (object, optional): Additional metadata

**Example:**
```json
{
  "user_id": "user123",
  "content": "User asked about machine learning types and showed interest in supervised learning",
  "memory_type": "conversation",
  "metadata": {
    "topic": "machine learning",
    "interest_level": "high"
  }
}
```

#### get_user_memories
Retrieve user memories.

**Parameters:**
- `user_id` (string, required): User identifier
- `limit` (integer, optional): Maximum memories (default: 10)
- `memory_type` (string, optional): Filter by memory type

#### delete_memory
Delete a specific memory.

**Parameters:**
- `memory_id` (string, required): Memory identifier
- `user_id` (string, required): User identifier

#### clear_user_memories
Clear all memories for a user.

**Parameters:**
- `user_id` (string, required): User identifier

#### get_memory_context
Get relevant memory context for a query.

**Parameters:**
- `user_id` (string, required): User identifier
- `query` (string, required): Query to find relevant memories
- `limit` (integer, optional): Maximum memories (default: 5)

**Response:**
```json
{
  "context": "Based on previous conversations, the user has shown interest in supervised learning and has asked about practical applications of machine learning algorithms.",
  "relevant_memories": [
    {
      "memory_id": "mem_xyz789",
      "content": "User asked about machine learning types...",
      "relevance_score": 0.95
    }
  ]
}
```

#### get_user_session_info
Get information about a user's session.

**Parameters:**
- `user_id` (string, required): User identifier

**Response:**
```json
{
  "user_id": "user123",
  "session_start": "2024-01-15T10:00:00Z",
  "total_queries": 15,
  "total_documents": 5,
  "total_memories": 8,
  "last_activity": "2024-01-15T10:30:00Z"
}
```

## MCP Resources Reference

### Document Resources

#### rag://documents/{document_id}
Get document metadata.

**Example:**
```
rag://documents/doc_abc123
```

#### rag://documents/{document_id}/content
Get document content.

**Example:**
```
rag://documents/doc_abc123/content
```

#### rag://documents/{document_id}/chunks
Get document chunks.

**Example:**
```
rag://documents/doc_abc123/chunks
```

#### rag://search/{query}/{limit}
Get search results.

**Example:**
```
rag://search/machine%20learning/5
```

#### rag://statistics/{user_id}
Get system statistics.

**Example:**
```
rag://statistics/user123
```

### Memory Resources

#### rag://memories/{user_id}/{limit}
Get user memories.

**Example:**
```
rag://memories/user123/10
```

#### rag://memories/{user_id}/context/{query}
Get memory context.

**Example:**
```
rag://memories/user123/context/machine%20learning
```

#### rag://memories/{user_id}/statistics
Get memory statistics.

**Example:**
```
rag://memories/user123/statistics
```

#### rag://session/{user_id}
Get session information.

**Example:**
```
rag://session/user123
```

## Error Handling

### Common Error Responses

#### Validation Error
```json
{
  "error": "validation_error",
  "message": "Invalid input parameters",
  "details": {
    "field": "content",
    "issue": "Field is required"
  }
}
```

#### Service Unavailable
```json
{
  "error": "service_unavailable",
  "message": "Qdrant service is not available",
  "retry_after": 30
}
```

#### Rate Limit Exceeded
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "retry_after": 60
}
```

#### Document Not Found
```json
{
  "error": "document_not_found",
  "message": "Document with ID 'doc_abc123' not found"
}
```

## Usage Examples

### Complete Workflow Example

```python
# 1. Add a document
response = mcp_client.call_tool("add_document", {
    "content": "Machine learning is a subset of artificial intelligence...",
    "metadata": {"title": "ML Basics", "category": "technology"},
    "user_id": "user123"
})

# 2. Search for information
search_results = mcp_client.call_tool("search_documents", {
    "query": "machine learning types",
    "limit": 5,
    "user_id": "user123"
})

# 3. Ask a question
answer = mcp_client.call_tool("ask_question", {
    "question": "What are the main types of machine learning?",
    "user_id": "user123",
    "use_memory": True
})

# 4. Store memory
mcp_client.call_tool("add_memory", {
    "user_id": "user123",
    "content": "User asked about machine learning types",
    "memory_type": "conversation"
})
```

### Integration with MCP Clients

```python
# Using MCP client
from mcp import ClientSession

async with ClientSession("localhost", 8001) as session:
    # Add document
    result = await session.call_tool("add_document", {
        "content": "Document content...",
        "user_id": "user123"
    })

    # Search documents
    results = await session.call_tool("search_documents", {
        "query": "search term",
        "user_id": "user123"
    })

    # Get resource
    document = await session.read_resource(
        "rag://documents/doc_abc123"
    )
```

## Related Documentation

- [[../01-architecture/system-architecture|System Architecture]]
- [[../02-installation/installation-guide|Installation Guide]]
- [[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]