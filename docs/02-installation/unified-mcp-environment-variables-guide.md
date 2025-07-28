---
title: unified-mcp-environment-variables-guide
type: note
permalink: docs/02-installation/unified-mcp-environment-variables-guide
tags:
- unified-variables
- mcp-prefix
- environment-variables
- configuration
- migration-guide
---

# Unified MCP Environment Variables Guide

## Overview

This guide documents the unified environment variables for the MCP RAG Server, all using the `MCP_` prefix for consistency and clarity.

## Unified Environment Variables

### Core MCP Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `MCP_GEMINI_API_KEY` | - | Your Gemini API key from Google AI Studio | ✅ Yes |
| `MCP_COLLECTION` | `` | Prefix for collection names (project isolation) | No |
| `MCP_PROJECT_NAMESPACE` | `` | Namespace for project isolation in memory | No |
| `MCP_USER_ID` | `default` | Default user ID for the project | No |
| `MCP_SERVER_PORT` | `8001` | MCP server port | No |
| `MCP_SERVER_HOST` | `localhost` | MCP server host | No |

### Gemini API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_GEMINI_API_KEY` | - | Gemini API key |
| `MCP_GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model to use |
| `MCP_GEMINI_EMBEDDING_MODEL` | `text-embedding-004` | Embedding model |
| `MCP_GEMINI_MAX_TOKENS` | `4096` | Maximum tokens for generation |
| `MCP_GEMINI_TEMPERATURE` | `0.7` | Temperature for generation |

### Qdrant Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `MCP_COLLECTION_NAME` | `documents` | Base collection name |
| `MCP_COLLECTION` | `` | Prefix for project isolation |
| `MCP_VECTOR_SIZE` | `768` | Vector dimensions |
| `MCP_QDRANT_DISTANCE_METRIC` | `Cosine` | Distance metric |

### Mem0 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_MEM0_SELF_HOSTED` | `true` | Use local storage |
| `MCP_MEM0_STORAGE_PATH` | `./data/mem0_data` | Local storage path |
| `MCP_PROJECT_NAMESPACE` | `` | Namespace for project isolation |
| `MCP_USER_ID` | `default` | Default user ID |
| `MCP_MEM0_MEMORY_SIZE` | `1000` | Maximum memory entries |
| `MCP_MEM0_RELEVANCE_THRESHOLD` | `0.7` | Memory relevance threshold |
| `MCP_MEM0_MAX_TOKENS_PER_MEMORY` | `1000` | Max tokens per memory |
| `MCP_MEM0_USE_SEMANTIC_SEARCH` | `true` | Enable semantic search |
| `MCP_MEM0_SEMANTIC_SEARCH_WEIGHT` | `0.7` | Semantic search weight |
| `MCP_MEM0_KEYWORD_SEARCH_WEIGHT` | `0.3` | Keyword search weight |
| `MCP_MEM0_RECENCY_WEIGHT` | `0.1` | Recency weight |
| `MCP_MEM0_MAX_MEMORY_CONTEXT_LENGTH` | `2000` | Max memory context length |
| `MCP_MEM0_ENABLE_MEMORY_SUMMARIZATION` | `true` | Enable memory summarization |

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_HOST` | `localhost` | MCP server host |
| `MCP_SERVER_PORT` | `8001` | MCP server port |
| `MCP_LOG_LEVEL` | `INFO` | Logging level |
| `MCP_DEBUG` | `false` | Enable debug mode |
| `MCP_SESSION_TIMEOUT_HOURS` | `24` | Session timeout in hours |
| `MCP_MAX_SESSIONS_PER_USER` | `10` | Max sessions per user |
| `MCP_SESSION_CLEANUP_INTERVAL_MINUTES` | `5` | Session cleanup interval |
| `MCP_ENABLE_SESSION_TRACKING` | `true` | Enable session tracking |

## Cursor Editor Configuration

### Basic Configuration

```json
{
  "mcpServers": {
    "rag": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "MCP_GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

### Project-Specific Configurations

#### Web Development Project

```json
{
  "mcpServers": {
    "rag-web-dev": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "MCP_GEMINI_API_KEY": "your_gemini_api_key_here",
        "MCP_COLLECTION": "web_dev",
        "MCP_PROJECT_NAMESPACE": "web_development",
        "MCP_USER_ID": "web_dev_team",
        "MCP_SERVER_PORT": "8001",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Mobile App Project

```json
{
  "mcpServers": {
    "rag-mobile": {
      "url": "http://localhost:8002/mcp",
      "type": "stdio",
      "env": {
        "MCP_GEMINI_API_KEY": "your_gemini_api_key_here",
        "MCP_COLLECTION": "mobile_app",
        "MCP_PROJECT_NAMESPACE": "mobile_development",
        "MCP_USER_ID": "mobile_dev_team",
        "MCP_SERVER_PORT": "8002",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Client Project (Acme Corp)

```json
{
  "mcpServers": {
    "rag-acme": {
      "url": "http://localhost:8003/mcp",
      "type": "stdio",
      "env": {
        "MCP_GEMINI_API_KEY": "your_gemini_api_key_here",
        "MCP_COLLECTION": "client_acme",
        "MCP_PROJECT_NAMESPACE": "acme_corp",
        "MCP_USER_ID": "acme_team",
        "MCP_SERVER_PORT": "8003",
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_SESSION_TIMEOUT_HOURS": "12",
        "MCP_MAX_SESSIONS_PER_USER": "5"
      }
    }
  }
}
```

## Docker Configuration

### Main Docker Compose

```yaml
services:
  mcp-rag-server:
    environment:
      # Gemini API Configuration
      - MCP_GEMINI_API_KEY=${MCP_GEMINI_API_KEY}
      - MCP_GEMINI_MODEL=${MCP_GEMINI_MODEL:-gemini-2.0-flash-exp}
      - MCP_GEMINI_EMBEDDING_MODEL=${MCP_GEMINI_EMBEDDING_MODEL:-text-embedding-004}
      
      # Qdrant Configuration
      - MCP_QDRANT_URL=${MCP_QDRANT_URL:-http://qdrant:6333}
      - MCP_COLLECTION_NAME=${MCP_COLLECTION_NAME:-documents}
      - MCP_COLLECTION=${MCP_COLLECTION:-}
      
      # Mem0 Configuration
      - MCP_MEM0_SELF_HOSTED=${MCP_MEM0_SELF_HOSTED:-true}
      - MCP_PROJECT_NAMESPACE=${MCP_PROJECT_NAMESPACE:-}
      - MCP_USER_ID=${MCP_USER_ID:-default}
      
      # Server Configuration
      - MCP_SERVER_PORT=${MCP_SERVER_PORT:-8001}
      - MCP_LOG_LEVEL=${MCP_LOG_LEVEL:-INFO}
```

### Project-Specific Docker Compose

#### Web Development

```yaml
services:
  mcp-rag-server:
    environment:
      - MCP_GEMINI_API_KEY=${MCP_GEMINI_API_KEY}
      - MCP_COLLECTION=web_dev
      - MCP_PROJECT_NAMESPACE=web_development
      - MCP_USER_ID=web_dev_team
      - MCP_SERVER_PORT=8001
```

#### Mobile App

```yaml
services:
  mcp-rag-server:
    environment:
      - MCP_GEMINI_API_KEY=${MCP_GEMINI_API_KEY}
      - MCP_COLLECTION=mobile_app
      - MCP_PROJECT_NAMESPACE=mobile_development
      - MCP_USER_ID=mobile_dev_team
      - MCP_SERVER_PORT=8002
```

## Migration from Old Variables

### Old vs New Variable Names

| Old Variable | New Variable |
|--------------|--------------|
| `GEMINI_API_KEY` | `MCP_GEMINI_API_KEY` |
| `QDRANT_COLLECTION_PREFIX` | `MCP_COLLECTION` |
| `MEM0_PROJECT_NAMESPACE` | `MCP_PROJECT_NAMESPACE` |
| `MEM0_DEFAULT_USER_ID` | `MCP_USER_ID` |
| `FASTMCP_PORT` | `MCP_SERVER_PORT` |
| `FASTMCP_HOST` | `MCP_SERVER_HOST` |
| `LOG_LEVEL` | `MCP_LOG_LEVEL` |
| `DEBUG` | `MCP_DEBUG` |

### Migration Steps

1. **Update .env file**:
   ```bash
   # Old
   GEMINI_API_KEY=your_key
   QDRANT_COLLECTION_PREFIX=web_dev
   MEM0_PROJECT_NAMESPACE=web_development
   
   # New
   MCP_GEMINI_API_KEY=your_key
   MCP_COLLECTION=web_dev
   MCP_PROJECT_NAMESPACE=web_development
   ```

2. **Update Cursor configuration**:
   ```json
   // Old
   "env": {
     "GEMINI_API_KEY": "your_key",
     "QDRANT_COLLECTION_PREFIX": "web_dev"
   }
   
   // New
   "env": {
     "MCP_GEMINI_API_KEY": "your_key",
     "MCP_COLLECTION": "web_dev"
   }
   ```

3. **Update Docker Compose**:
   ```yaml
   # Old
   environment:
     - GEMINI_API_KEY=${GEMINI_API_KEY}
     - QDRANT_COLLECTION_PREFIX=${QDRANT_COLLECTION_PREFIX}
   
   # New
   environment:
     - MCP_GEMINI_API_KEY=${MCP_GEMINI_API_KEY}
     - MCP_COLLECTION=${MCP_COLLECTION}
   ```

## Benefits of Unified Variables

### 1. Consistency
- All variables use the same `MCP_` prefix
- Clear identification of MCP-related configuration
- Reduced confusion about variable ownership

### 2. Simplicity
- Shorter, more readable variable names
- Easier to remember and type
- Less verbose configuration

### 3. Clarity
- Clear distinction between MCP and other system variables
- Self-documenting variable names
- Better organization in configuration files

### 4. Maintainability
- Easier to manage in large configurations
- Consistent naming patterns
- Reduced risk of naming conflicts

## Best Practices

### 1. Always Use MCP_ Prefix
```bash
# ✅ Good
MCP_GEMINI_API_KEY=your_key
MCP_COLLECTION=web_dev

# ❌ Avoid
GEMINI_API_KEY=your_key
QDRANT_COLLECTION_PREFIX=web_dev
```

### 2. Use Descriptive Names
```bash
# ✅ Good
MCP_PROJECT_NAMESPACE=web_development
MCP_USER_ID=web_dev_team

# ❌ Avoid
MCP_NS=web_dev
MCP_UID=team1
```

### 3. Group Related Variables
```bash
# Gemini API
MCP_GEMINI_API_KEY=your_key
MCP_GEMINI_MODEL=gemini-2.0-flash-exp

# Project Isolation
MCP_COLLECTION=web_dev
MCP_PROJECT_NAMESPACE=web_development
MCP_USER_ID=web_dev_team

# Server Configuration
MCP_SERVER_PORT=8001
MCP_LOG_LEVEL=INFO
```

### 4. Use Default Values
```bash
# ✅ Good - with defaults
MCP_SERVER_PORT=${MCP_SERVER_PORT:-8001}
MCP_LOG_LEVEL=${MCP_LOG_LEVEL:-INFO}

# ❌ Avoid - hardcoded
MCP_SERVER_PORT=8001
MCP_LOG_LEVEL=INFO
```

## Troubleshooting

### Common Issues

1. **Variable Not Found**
   ```bash
   # Check if variable is set
   echo $MCP_GEMINI_API_KEY
   
   # Verify in .env file
   grep MCP_GEMINI_API_KEY .env
   ```

2. **Wrong Variable Name**
   ```bash
   # Old variable names won't work
   GEMINI_API_KEY=your_key  # ❌ Won't work
   
   # Use new unified names
   MCP_GEMINI_API_KEY=your_key  # ✅ Works
   ```

3. **Configuration Not Applied**
   ```bash
   # Restart services after variable changes
   ./scripts/manage_docker.sh restart
   
   # Check configuration
   ./scripts/manage_projects.sh config web-dev
   ```

## Summary

The unified `MCP_` environment variables provide:

- **Consistency**: All variables use the same prefix
- **Simplicity**: Shorter, more readable names
- **Clarity**: Clear identification of MCP configuration
- **Maintainability**: Easier to manage and organize

This unified approach makes configuration more intuitive and reduces the complexity of managing multiple projects with different requirements.