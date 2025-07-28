---
title: mcp-vs-fastmcp-configuration-guide
type: note
permalink: docs/02-installation/mcp-vs-fastmcp-configuration-guide
tags:
- mcp
- fastmcp
- configuration
- cursor-editor
- project-isolation
- environment-variables
---

# MCP vs FastMCP Configuration Guide

## Overview

This guide explains the differences between MCP and FastMCP in the MCP RAG Server, and how to configure project-specific settings in the Cursor editor's `mcpServers` configuration.

## MCP vs FastMCP Differences

### Standard MCP (Model Context Protocol)

**Purpose**: Traditional MCP implementation using stdio transport
- **Transport**: Standard input/output (stdio)
- **Connection**: Direct process communication
- **Configuration**: Simple command-line arguments
- **Use Case**: Local development, simple integrations

**Example Configuration**:
```json
{
  "mcpServers": {
    "rag": {
      "command": "python",
      "args": ["run_server.py"],
      "env": {
        "GEMINI_API_KEY": "your_api_key"
      }
    }
  }
}
```

### FastMCP (Fast Model Context Protocol)

**Purpose**: Enhanced MCP implementation with HTTP transport
- **Transport**: HTTP/WebSocket
- **Connection**: Network-based communication
- **Configuration**: Environment variables and HTTP endpoints
- **Use Case**: Production deployments, multi-client access, Docker containers

**Example Configuration**:
```json
{
  "mcpServers": {
    "rag": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_api_key"
      }
    }
  }
}
```

## Environment Variables Differences

### MCP Server Variables (Standard MCP)

| Variable | Purpose | Default |
|----------|---------|---------|
| `MCP_SERVER_HOST` | MCP server host | `localhost` |
| `MCP_SERVER_PORT` | MCP server port | `8000` |
| `MCP_SESSION_TIMEOUT_HOURS` | Session timeout | `24` |
| `MCP_MAX_SESSIONS_PER_USER` | Max sessions per user | `10` |
| `MCP_SESSION_CLEANUP_INTERVAL_MINUTES` | Cleanup interval | `5` |
| `MCP_ENABLE_SESSION_TRACKING` | Enable session tracking | `true` |

### FastMCP Variables (HTTP Server)

| Variable | Purpose | Default |
|----------|---------|---------|
| `FASTMCP_HOST` | FastMCP HTTP host | `0.0.0.0` |
| `FASTMCP_PORT` | FastMCP HTTP port | `8001` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `false` |

## Project-Specific Configuration

### 1. Web Development Project

```json
{
  "mcpServers": {
    "rag-web-dev": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "web_dev",
        "MEM0_PROJECT_NAMESPACE": "web_development",
        "MEM0_DEFAULT_USER_ID": "web_dev_team",
        "QDRANT_URL": "http://localhost:6333",
        "MEM0_SELF_HOSTED": "true",
        "MEM0_LOCAL_STORAGE_PATH": "./mem0_data",
        "FASTMCP_HOST": "0.0.0.0",
        "FASTMCP_PORT": "8001",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. Mobile App Project

```json
{
  "mcpServers": {
    "rag-mobile": {
      "url": "http://localhost:8002/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "mobile_app",
        "MEM0_PROJECT_NAMESPACE": "mobile_development",
        "MEM0_DEFAULT_USER_ID": "mobile_dev_team",
        "QDRANT_URL": "http://localhost:6333",
        "MEM0_SELF_HOSTED": "true",
        "MEM0_LOCAL_STORAGE_PATH": "./mem0_data",
        "FASTMCP_HOST": "0.0.0.0",
        "FASTMCP_PORT": "8002",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Client-Specific Project (Acme Corp)

```json
{
  "mcpServers": {
    "rag-acme": {
      "url": "http://localhost:8003/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "client_acme",
        "MEM0_PROJECT_NAMESPACE": "acme_corp",
        "MEM0_DEFAULT_USER_ID": "acme_team",
        "QDRANT_URL": "http://localhost:6333",
        "MEM0_SELF_HOSTED": "true",
        "MEM0_LOCAL_STORAGE_PATH": "./mem0_data",
        "FASTMCP_HOST": "0.0.0.0",
        "FASTMCP_PORT": "8003",
        "LOG_LEVEL": "DEBUG",
        "MCP_SESSION_TIMEOUT_HOURS": "12",
        "MCP_MAX_SESSIONS_PER_USER": "5"
      }
    }
  }
}
```

## Multi-Project Setup

### Complete Configuration Example

```json
{
  "mcpServers": {
    "rag-web-dev": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "web_dev",
        "MEM0_PROJECT_NAMESPACE": "web_development",
        "MEM0_DEFAULT_USER_ID": "web_dev_team",
        "FASTMCP_PORT": "8001"
      }
    },
    "rag-mobile": {
      "url": "http://localhost:8002/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "mobile_app",
        "MEM0_PROJECT_NAMESPACE": "mobile_development",
        "MEM0_DEFAULT_USER_ID": "mobile_dev_team",
        "FASTMCP_PORT": "8002"
      }
    },
    "rag-acme": {
      "url": "http://localhost:8003/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "client_acme",
        "MEM0_PROJECT_NAMESPACE": "acme_corp",
        "MEM0_DEFAULT_USER_ID": "acme_team",
        "FASTMCP_PORT": "8003"
      }
    }
  }
}
```

## Docker-Based Configuration

### Single Project with Docker

```json
{
  "mcpServers": {
    "rag-docker": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "docker_project",
        "MEM0_PROJECT_NAMESPACE": "docker_development",
        "MEM0_DEFAULT_USER_ID": "docker_team"
      }
    }
  }
}
```

### Multi-Project Docker Setup

```json
{
  "mcpServers": {
    "rag-web-docker": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "web_dev",
        "MEM0_PROJECT_NAMESPACE": "web_development",
        "MEM0_DEFAULT_USER_ID": "web_dev_team"
      }
    },
    "rag-mobile-docker": {
      "url": "http://localhost:8002/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "QDRANT_COLLECTION_PREFIX": "mobile_app",
        "MEM0_PROJECT_NAMESPACE": "mobile_development",
        "MEM0_DEFAULT_USER_ID": "mobile_dev_team"
      }
    }
  }
}
```

## Configuration Best Practices

### 1. Project Isolation

**Always use unique identifiers**:
- `QDRANT_COLLECTION_PREFIX`: Unique for each project
- `MEM0_PROJECT_NAMESPACE`: Unique for each project
- `MEM0_DEFAULT_USER_ID`: Unique for each project team

### 2. Port Management

**Use different ports for different projects**:
- Project A: `FASTMCP_PORT=8001`
- Project B: `FASTMCP_PORT=8002`
- Project C: `FASTMCP_PORT=8003`

### 3. Security Considerations

**Environment-specific settings**:
- Development: `LOG_LEVEL=DEBUG`
- Production: `LOG_LEVEL=INFO`
- Client projects: `MCP_SESSION_TIMEOUT_HOURS=12`

### 4. Resource Management

**Optimize for project needs**:
- Small projects: `MCP_MAX_SESSIONS_PER_USER=5`
- Large projects: `MCP_MAX_SESSIONS_PER_USER=20`
- High-traffic: `MCP_SESSION_CLEANUP_INTERVAL_MINUTES=2`

## Setup Instructions

### 1. Create Project-Specific Docker Compose Files

**docker-compose.web-dev.yml**:
```yaml
services:
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
```

**docker-compose.mobile.yml**:
```yaml
services:
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
```

### 2. Start Project-Specific Services

```bash
# Start Web Development project
docker-compose -f docker-compose.web-dev.yml up -d

# Start Mobile App project
docker-compose -f docker-compose.mobile.yml up -d

# Check status
docker ps
```

### 3. Update Cursor Configuration

```json
{
  "mcpServers": {
    "rag-web-dev": {
      "url": "http://localhost:8001/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    },
    "rag-mobile": {
      "url": "http://localhost:8002/mcp",
      "type": "stdio",
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

## Troubleshooting

### 1. Port Conflicts

**Problem**: Port already in use
```bash
# Check what's using the port
lsof -i :8001

# Kill the process or change port
kill -9 <PID>
```

### 2. Collection Not Found

**Problem**: Wrong collection prefix
```bash
# Check collection name
curl http://localhost:6333/collections

# Verify prefix in environment
echo $QDRANT_COLLECTION_PREFIX
```

### 3. Memory Namespace Issues

**Problem**: Wrong memory namespace
```bash
# Check memory storage
ls -la ./mem0_data/

# Verify namespace in environment
echo $MEM0_PROJECT_NAMESPACE
```

### 4. Connection Issues

**Problem**: Can't connect to MCP server
```bash
# Check if server is running
curl http://localhost:8001/mcp/

# Check Docker logs
docker logs mcp-rag-server
```

## Migration Guide

### From Single Project to Multi-Project

1. **Backup existing data**:
   ```bash
   cp -r ./mem0_data ./mem0_data_backup
   ```

2. **Create project-specific configurations**:
   ```bash
   cp .env .env.web-dev
   cp .env .env.mobile
   ```

3. **Configure isolation settings**:
   ```bash
   # Web Development
   echo "QDRANT_COLLECTION_PREFIX=web_dev" >> .env.web-dev
   echo "MEM0_PROJECT_NAMESPACE=web_development" >> .env.web-dev
   
   # Mobile App
   echo "QDRANT_COLLECTION_PREFIX=mobile_app" >> .env.mobile
   echo "MEM0_PROJECT_NAMESPACE=mobile_development" >> .env.mobile
   ```

4. **Update Cursor configuration**:
   ```json
   {
     "mcpServers": {
       "rag-web-dev": {
         "url": "http://localhost:8001/mcp",
         "type": "stdio"
       },
       "rag-mobile": {
         "url": "http://localhost:8002/mcp",
         "type": "stdio"
       }
     }
   }
   ```

## Summary

### Key Differences

| Aspect | MCP | FastMCP |
|--------|-----|---------|
| **Transport** | stdio | HTTP/WebSocket |
| **Connection** | Direct process | Network-based |
| **Configuration** | Command-line args | Environment variables |
| **Use Case** | Local development | Production deployment |
| **Multi-client** | No | Yes |
| **Docker support** | Limited | Full |

### Project Isolation Benefits

1. **Data Separation**: Each project has its own collections and memory
2. **Context Cleanliness**: No cross-project data contamination
3. **Security**: Client data remains isolated
4. **Scalability**: Easy to add new projects
5. **Management**: Clear project boundaries

### Configuration Priority

1. **Collection Prefix**: Most important for data isolation
2. **Project Namespace**: Critical for memory separation
3. **User ID**: Important for session management
4. **Port Configuration**: Essential for multi-project setup

This configuration approach ensures complete project isolation while maintaining the flexibility to work with multiple projects simultaneously in the Cursor editor.