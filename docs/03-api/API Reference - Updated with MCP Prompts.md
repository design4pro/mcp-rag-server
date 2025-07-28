---
title: API Reference - Updated with MCP Prompts
type: note
permalink: docs/03-api/api-reference-updated-with-mcp-prompts
---

# API Reference - Updated with MCP Prompts

## Overview

This document provides a comprehensive reference for the MCP RAG Server API, including all tools, resources, and the new MCP Prompts functionality.

## 🚀 MCP Prompts

### Prompts List
**Method**: `prompts/list`  
**Description**: List available prompt templates  
**Parameters**:
- `cursor` (optional): Pagination cursor

**Response**:
```json
{
  "prompts": [
    {
      "name": "code_review",
      "title": "Request Code Review",
      "description": "Analyze code quality and suggest improvements",
      "arguments": [
        {
          "name": "code",
          "description": "The code to review",
          "required": true,
          "type": "string"
        }
      ]
    }
  ],
  "nextCursor": null
}
```

### Get Prompt
**Method**: `prompts/get`  
**Description**: Get a specific prompt with argument substitution  
**Parameters**:
- `name` (required): Prompt name
- `arguments` (optional): Arguments for substitution

**Response**:
```json
{
  "description": "Code review prompt",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "Please review this Python code:\ndef hello():\n    print('world')"
      }
    }
  ]
}
```

### Available Prompts

1. **`code_review`** - Comprehensive code quality assessment
2. **`code_analysis`** - Structure and architecture analysis  
3. **`architecture_review`** - Design patterns and scalability
4. **`security_audit`** - Vulnerability and security analysis
5. **`performance_analysis`** - Optimization opportunities
6. **`documentation_generation`** - API and user documentation
7. **`test_generation`** - Comprehensive test case creation
8. **`refactoring_suggestions`** - Code improvement recommendations

For detailed prompt documentation, see: [[docs/03-api/mcp-prompts-implementation-code-analysis-and-review|MCP Prompts Implementation]]

## 🛠️ Tools

### Health Check
**Method**: `health_check`  
**Description**: Check server health status  
**Parameters**: None  
**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "gemini": true,
      "qdrant": true,
      "mem0": true,
      "session": true,
      "rag": true,
      "reasoning": true,
      "context": true,
      "prompts": true
    }
  }
}
```

### Document Management

#### Add Document
**Method**: `add_document`  
**Description**: Add document to RAG system  
**Parameters**:
- `content` (required): Document content
- `metadata` (optional): Document metadata
- `user_id` (optional): User ID (default: "default")

#### Delete Document
**Method**: `delete_document`  
**Description**: Delete document from RAG system  
**Parameters**:
- `document_id` (required): Document ID
- `user_id` (optional): User ID (default: "default")

#### Get Document
**Method**: `get_document`  
**Description**: Get specific document by ID  
**Parameters**:
- `document_id` (required): Document ID

#### List Documents
**Method**: `list_documents`  
**Description**: List documents in RAG system  
**Parameters**:
- `user_id` (optional): User ID filter
- `limit` (optional): Maximum results (default: 100)

#### Get Document Stats
**Method**: `get_document_stats`  
**Description**: Get document statistics  
**Parameters**:
- `user_id` (optional): User ID filter

### Search and Query

#### Search Documents
**Method**: `search_documents`  
**Description**: Semantic document search  
**Parameters**:
- `query` (required): Search query
- `limit` (optional): Maximum results (default: 5)
- `user_id` (optional): User ID filter
- `filters` (optional): Search filters

#### Ask Question
**Method**: `ask_question`  
**Description**: Ask question using RAG with memory context  
**Parameters**:
- `question` (required): Question to ask
- `user_id` (optional): User ID (default: "default")
- `session_id` (optional): Session ID
- `use_memory` (optional): Use memory context (default: true)

### Memory Management

#### Add Memory
**Method**: `add_memory`  
**Description**: Add memory entry for user  
**Parameters**:
- `content` (required): Memory content
- `memory_type` (optional): Memory type (default: "conversation")
- `user_id` (optional): User ID (default: "default")
- `session_id` (optional): Session ID

#### Search Memories
**Method**: `search_memories`  
**Description**: Search for relevant memories  
**Parameters**:
- `query` (required): Search query
- `user_id` (optional): User ID (default: "default")
- `limit` (optional): Maximum results (default: 5)
- `memory_type` (optional): Memory type filter

#### Get User Memories
**Method**: `get_user_memories`  
**Description**: Get all memories for user  
**Parameters**:
- `user_id` (optional): User ID (default: "default")
- `limit` (optional): Maximum results (default: 50)
- `memory_type` (optional): Memory type filter

### Session Management

#### Create Session
**Method**: `create_session`  
**Description**: Create new session for user  
**Parameters**:
- `user_id` (optional): User ID (default: "default")
- `session_name` (optional): Session name

#### Get Session
**Method**: `get_session`  
**Description**: Get session information  
**Parameters**:
- `session_id` (required): Session ID

#### List Sessions
**Method**: `list_sessions`  
**Description**: List sessions for user  
**Parameters**:
- `user_id` (optional): User ID (default: "default")
- `limit` (optional): Maximum results (default: 10)

#### Delete Session
**Method**: `delete_session`  
**Description**: Delete session  
**Parameters**:
- `session_id` (required): Session ID

### Advanced AI Tools

#### Advanced Reasoning
**Method**: `advanced_reasoning`  
**Description**: Perform advanced reasoning on query  
**Parameters**:
- `query` (required): Query for reasoning
- `reasoning_type` (optional): Reasoning type (default: "auto")
- `context` (optional): Additional context

#### Context Analysis
**Method**: `context_analysis`  
**Description**: Analyze context for query  
**Parameters**:
- `query` (required): Query to analyze
- `user_id` (optional): User ID (default: "default")
- `additional_context` (optional): Additional context

## 📚 Resources

### Health Status
**URI**: `rag://health`  
**Description**: Server health status  
**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "gemini": true,
    "qdrant": true,
    "mem0": true,
    "session": true,
    "rag": true,
    "reasoning": true,
    "context": true,
    "prompts": true
  }
}
```

### Server Statistics
**URI**: `rag://stats`  
**Description**: Server statistics and features  
**Response**:
```json
{
  "version": "1.0.0",
  "uptime": "running",
  "features": [
    "document_management",
    "semantic_search",
    "memory_management",
    "session_management",
    "advanced_reasoning",
    "context_analysis",
    "mcp_prompts"
  ]
}
```

## 🔧 Configuration

### Environment Variables

#### Core Configuration
```bash
# Gemini API
MCP_GEMINI_API_KEY=your_api_key
MCP_GEMINI_MODEL=gemini-2.0-flash-exp
MCP_GEMINI_EMBEDDING_MODEL=text-embedding-004

# Qdrant
MCP_QDRANT_URL=http://localhost:6333
MCP_COLLECTION=your_collection_name
MCP_VECTOR_SIZE=768

# Mem0
MCP_MEM0_STORAGE_PATH=./data/mem0_data
MCP_PROJECT_NAMESPACE=your_project
MCP_USER_ID=your_user_id

# Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
MCP_LOG_LEVEL=INFO

# Session Management
MCP_SESSION_TIMEOUT_HOURS=24
MCP_MAX_SESSIONS_PER_USER=10

# Prompts
MCP_PROMPTS_ENABLED=true
MCP_PROMPTS_MAX_PROMPTS_PER_USER=50
MCP_PROMPTS_ENABLE_CODE_ANALYSIS=true
```

## 🚀 Quick Start Examples

### Using MCP Prompts for Code Review

```python
# List available prompts
response = await client.call("prompts/list")
print("Available prompts:", response["prompts"])

# Get code review prompt
code_review = await client.call("prompts/get", {
    "name": "code_review",
    "arguments": {
        "code": "def hello():\n    print('world')",
        "language": "python",
        "focus_areas": "security",
        "severity": "strict"
    }
})

# Use the prompt with an LLM
messages = code_review["messages"]
# Send to your preferred LLM for analysis
```

### Basic RAG Operations

```python
# Add a document
await client.call("add_document", {
    "content": "Your document content here",
    "metadata": {"source": "manual", "category": "docs"},
    "user_id": "developer1"
})

# Search documents
results = await client.call("search_documents", {
    "query": "How to implement authentication?",
    "limit": 5,
    "user_id": "developer1"
})

# Ask a question
answer = await client.call("ask_question", {
    "question": "What are the best practices for API design?",
    "user_id": "developer1",
    "use_memory": True
})
```

### Memory Management

```python
# Add memory
await client.call("add_memory", {
    "content": "User prefers Python for backend development",
    "memory_type": "preference",
    "user_id": "developer1"
})

# Search memories
memories = await client.call("search_memories", {
    "query": "programming language preferences",
    "user_id": "developer1"
})
```

### Session Management

```python
# Create session
session = await client.call("create_session", {
    "user_id": "developer1",
    "session_name": "API Development Session"
})

# Use session in questions
answer = await client.call("ask_question", {
    "question": "What was our previous discussion about?",
    "user_id": "developer1",
    "session_id": session["session_id"],
    "use_memory": True
})
```

## 🔍 Error Handling

All API methods return consistent error responses:

```json
{
  "success": false,
  "error": {
    "type": "ValidationError",
    "message": "Required parameter 'code' not provided",
    "details": {
      "parameter": "code",
      "expected": "string"
    }
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

### Common Error Codes

- **ValidationError**: Invalid or missing parameters
- **RuntimeError**: Service not initialized
- **ConnectionError**: External service connection failed
- **NotFoundError**: Resource not found
- **PermissionError**: Insufficient permissions

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "type": "ErrorType",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2025-01-25T10:30:00Z"
}
```

## 🔗 Related Documentation

- **MCP Prompts**: [[docs/03-api/mcp-prompts-implementation-code-analysis-and-review|MCP Prompts Implementation]]
- **Installation**: [[docs/02-installation/installation-guide|Installation Guide]]
- **Architecture**: [[docs/01-architecture/system-architecture|System Architecture]]
- **Troubleshooting**: [[docs/05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]