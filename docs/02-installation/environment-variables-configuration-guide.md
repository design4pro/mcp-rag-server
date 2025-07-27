---
title: environment-variables-configuration-guide
type: note
permalink: docs/02-installation/environment-variables-configuration-guide
tags:
- '[''environment-variables'''
- configuration'
- docker'
- project-isolation
---

# Environment Variables Configuration Guide

## Overview

This guide provides comprehensive documentation for all available environment variables in the MCP RAG Server, including examples for different project configurations.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file with your configuration:**
   ```bash
   nano .env
   ```

3. **Start the services:**
   ```bash
   ./scripts/manage_docker.sh start
   ```

## Environment Variables Reference

### Gemini API Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `GEMINI_API_KEY` | - | Your Gemini API key from Google AI Studio | ✅ Yes |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model to use | No |
| `GEMINI_EMBEDDING_MODEL` | `text-embedding-004` | Embedding model for vectors | No |
| `GEMINI_MAX_TOKENS` | `4096` | Maximum tokens for generation | No |
| `GEMINI_TEMPERATURE` | `0.7` | Temperature for generation (0.0-1.0) | No |

### Qdrant Vector Database Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL | No |
| `QDRANT_COLLECTION_NAME` | `documents` | Base collection name | No |
| `QDRANT_COLLECTION_PREFIX` | `` | Prefix for project isolation | No |
| `QDRANT_VECTOR_SIZE` | `768` | Vector dimensions | No |
| `QDRANT_DISTANCE_METRIC` | `Cosine` | Distance metric (Cosine, Euclidean) | No |
| `QDRANT_SERVICE_HTTP_PORT` | `6333` | Qdrant HTTP port | No |
| `QDRANT_SERVICE_GRPC_PORT` | `6334` | Qdrant gRPC port | No |

### Mem0 Memory Layer Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `MEM0_SELF_HOSTED` | `true` | Use local storage instead of Mem0 API | No |
| `MEM0_LOCAL_STORAGE_PATH` | `./mem0_data` | Local storage path | No |
| `MEM0_PROJECT_NAMESPACE` | `` | Namespace for project isolation | No |
| `MEM0_DEFAULT_USER_ID` | `default` | Default user ID for the project | No |
| `MEM0_MEMORY_SIZE` | `1000` | Maximum memory entries per user | No |
| `MEM0_RELEVANCE_THRESHOLD` | `0.7` | Memory relevance threshold | No |
| `MEM0_MAX_TOKENS_PER_MEMORY` | `1000` | Maximum tokens per memory entry | No |
| `MEM0_USE_SEMANTIC_SEARCH` | `true` | Enable semantic search | No |
| `MEM0_SEMANTIC_SEARCH_WEIGHT` | `0.7` | Weight for semantic search | No |
| `MEM0_KEYWORD_SEARCH_WEIGHT` | `0.3` | Weight for keyword search | No |
| `MEM0_RECENCY_WEIGHT` | `0.1` | Weight for recency scoring | No |
| `MEM0_MAX_MEMORY_CONTEXT_LENGTH` | `2000` | Max memory context length | No |
| `MEM0_ENABLE_MEMORY_SUMMARIZATION` | `true` | Enable memory summarization | No |

### MCP Server Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `MCP_SERVER_HOST` | `localhost` | MCP server host | No |
| `MCP_SERVER_PORT` | `8000` | MCP server port | No |
| `FASTMCP_HOST` | `0.0.0.0` | FastMCP HTTP host | No |
| `FASTMCP_PORT` | `8001` | FastMCP HTTP port | No |
| `LOG_LEVEL` | `INFO` | Logging level | No |
| `DEBUG` | `false` | Enable debug mode | No |
| `MCP_SESSION_TIMEOUT_HOURS` | `24` | Session timeout in hours | No |
| `MCP_MAX_SESSIONS_PER_USER` | `10` | Max sessions per user | No |
| `MCP_SESSION_CLEANUP_INTERVAL_MINUTES` | `5` | Session cleanup interval | No |
| `MCP_ENABLE_SESSION_TRACKING` | `true` | Enable session tracking | No |

## Project Isolation Examples

### 1. Web Development Project

```bash
# .env for web development project
GEMINI_API_KEY=your_gemini_api_key_here

# Project isolation settings
QDRANT_COLLECTION_PREFIX=web_dev
MEM0_PROJECT_NAMESPACE=web_development
MEM0_DEFAULT_USER_ID=web_dev_team

# Other settings with defaults
QDRANT_URL=http://localhost:6333
MEM0_SELF_HOSTED=true
LOG_LEVEL=INFO
```

### 2. Mobile App Project

```bash
# .env for mobile app project
GEMINI_API_KEY=your_gemini_api_key_here

# Project isolation settings
QDRANT_COLLECTION_PREFIX=mobile_app
MEM0_PROJECT_NAMESPACE=mobile_development
MEM0_DEFAULT_USER_ID=mobile_dev_team

# Optimized for mobile development
MEM0_MEMORY_SIZE=2000
MEM0_RELEVANCE_THRESHOLD=0.8
GEMINI_TEMPERATURE=0.5
```

### 3. Client-Specific Project (Acme Corp)

```bash
# .env for Acme Corp client
GEMINI_API_KEY=your_gemini_api_key_here

# Client isolation settings
QDRANT_COLLECTION_PREFIX=client_acme
MEM0_PROJECT_NAMESPACE=acme_corp
MEM0_DEFAULT_USER_ID=acme_team

# Enhanced security and logging
LOG_LEVEL=DEBUG
MCP_SESSION_TIMEOUT_HOURS=12
MCP_MAX_SESSIONS_PER_USER=5
```

### 4. Multi-Project Docker Setup

```bash
# docker-compose.yml with multiple projects
version: '3.8'

services:
  # Web Development Project
  mcp-rag-web-dev:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QDRANT_COLLECTION_PREFIX=web_dev
      - MEM0_PROJECT_NAMESPACE=web_development
      - MEM0_DEFAULT_USER_ID=web_dev_team
      - FASTMCP_PORT=8001
    ports:
      - "8001:8001"

  # Mobile App Project
  mcp-rag-mobile:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QDRANT_COLLECTION_PREFIX=mobile_app
      - MEM0_PROJECT_NAMESPACE=mobile_development
      - MEM0_DEFAULT_USER_ID=mobile_dev_team
      - FASTMCP_PORT=8002
    ports:
      - "8002:8002"

  # Shared Qdrant instance
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
```

## Docker Compose Configuration

The `docker/docker-compose.yml` file includes all environment variables with sensible defaults:

```yaml
services:
  mcp-rag-server:
    environment:
      # Gemini API Configuration
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.0-flash-exp}
      - GEMINI_EMBEDDING_MODEL=${GEMINI_EMBEDDING_MODEL:-text-embedding-004}
      
      # Qdrant Configuration
      - QDRANT_URL=${QDRANT_URL:-http://qdrant:6333}
      - QDRANT_COLLECTION_PREFIX=${QDRANT_COLLECTION_PREFIX:-}
      
      # Mem0 Configuration
      - MEM0_PROJECT_NAMESPACE=${MEM0_PROJECT_NAMESPACE:-}
      - MEM0_DEFAULT_USER_ID=${MEM0_DEFAULT_USER_ID:-default}
      
      # Server Configuration
      - FASTMCP_PORT=${FASTMCP_PORT:-8001}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

## Best Practices

### 1. Project Isolation
- **Always use collection prefixes** for different projects
- **Use descriptive namespaces** for memory isolation
- **Set unique user IDs** for each project team

### 2. Security
- **Never commit API keys** to version control
- **Use environment-specific .env files**
- **Rotate API keys** regularly

### 3. Performance
- **Adjust memory size** based on project needs
- **Tune relevance thresholds** for better search results
- **Monitor session limits** for resource management

### 4. Monitoring
- **Set appropriate log levels** for debugging
- **Enable session tracking** for usage analytics
- **Configure cleanup intervals** for resource management

## Troubleshooting

### Common Issues

1. **API Key Errors**
   ```bash
   # Check if API key is set
   echo $GEMINI_API_KEY
   
   # Verify in .env file
   grep GEMINI_API_KEY .env
   ```

2. **Collection Not Found**
   ```bash
   # Check collection prefix
   echo $QDRANT_COLLECTION_PREFIX
   
   # Verify Qdrant connection
   curl http://localhost:6333/collections
   ```

3. **Memory Issues**
   ```bash
   # Check memory namespace
   echo $MEM0_PROJECT_NAMESPACE
   
   # Verify storage path
   ls -la ./mem0_data/
   ```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
./scripts/manage_docker.sh restart
```

## Migration Guide

### From Single Project to Multi-Project

1. **Backup existing data:**
   ```bash
   cp -r ./mem0_data ./mem0_data_backup
   ```

2. **Create project-specific .env files:**
   ```bash
   cp .env .env.project_a
   cp .env .env.project_b
   ```

3. **Configure isolation settings:**
   ```bash
   # Project A
   QDRANT_COLLECTION_PREFIX=project_a
   MEM0_PROJECT_NAMESPACE=project_a
   
   # Project B
   QDRANT_COLLECTION_PREFIX=project_b
   MEM0_PROJECT_NAMESPACE=project_b
   ```

4. **Start services with specific config:**
   ```bash
   # For Project A
   cp .env.project_a .env
   ./scripts/manage_docker.sh start
   
   # For Project B
   cp .env.project_b .env
   ./scripts/manage_docker.sh start
   ```

## Advanced Configuration

### Custom Vector Sizes

For different embedding models:

```bash
# For larger models
QDRANT_VECTOR_SIZE=1536

# For smaller models
QDRANT_VECTOR_SIZE=384
```

### Memory Optimization

For high-traffic projects:

```bash
# Increase memory capacity
MEM0_MEMORY_SIZE=5000

# Adjust relevance thresholds
MEM0_RELEVANCE_THRESHOLD=0.8

# Enable summarization
MEM0_ENABLE_MEMORY_SUMMARIZATION=true
```

### Session Management

For enterprise deployments:

```bash
# Shorter sessions for security
MCP_SESSION_TIMEOUT_HOURS=8

# Limit concurrent sessions
MCP_MAX_SESSIONS_PER_USER=5

# Frequent cleanup
MCP_SESSION_CLEANUP_INTERVAL_MINUTES=2
```

## Conclusion

This configuration guide provides all the tools needed to set up and manage MCP RAG Server for single or multi-project deployments. The environment variables offer fine-grained control over all aspects of the system, from basic API configuration to advanced project isolation and performance tuning.