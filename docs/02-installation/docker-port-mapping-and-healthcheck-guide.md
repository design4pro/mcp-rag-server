---
title: docker-port-mapping-and-healthcheck-guide
type: note
permalink: docs/02-installation/docker-port-mapping-and-healthcheck-guide
tags:
- docker
- port-mapping
- healthcheck
- fastmcp
- configuration
---

# Docker Port Mapping and Healthcheck Guide

## Overview

This guide explains how port mapping works in Docker containers and how healthcheck is configured for the MCP RAG Server.

## Port Mapping Architecture

### Docker Container Ports

When using Docker with the MCP RAG Server, there are two types of ports:

1. **Internal Port (Container Port)**: The port inside the Docker container where FastMCP runs
2. **External Port (Host Port)**: The port on the host machine that maps to the internal port

### Port Configuration

#### Internal Port (Container)
- **Default**: `8000` (FastMCP default)
- **Configurable**: Via `MCP_SERVER_PORT` environment variable
- **Location**: Inside the Docker container
- **Purpose**: Where FastMCP actually listens

#### External Port (Host)
- **Default**: `8001` (for main project)
- **Configurable**: Via Docker Compose port mapping
- **Location**: On the host machine
- **Purpose**: Where clients connect from outside

### Port Mapping Examples

#### Main Project
```yaml
ports:
  - "8001:8000"  # External:Internal
```

#### Web Development Project
```yaml
ports:
  - "8001:8000"  # External:Internal
```

#### Mobile App Project
```yaml
ports:
  - "8002:8000"  # External:Internal
```

#### Acme Corp Project
```yaml
ports:
  - "8003:8000"  # External:Internal
```

## Healthcheck Configuration

### Healthcheck in Dockerfile

The healthcheck in `docker/Dockerfile` uses the internal port:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${MCP_SERVER_PORT:-8000}/mcp/ || exit 1
```

### Healthcheck in Docker Compose

The healthcheck in Docker Compose files also uses the internal port:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:${MCP_SERVER_PORT:-8000}/mcp/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Why Internal Port for Healthcheck?

1. **Container Isolation**: Healthcheck runs inside the container
2. **Direct Access**: No need to go through port mapping
3. **Consistency**: Always checks the actual service port
4. **Reliability**: Works regardless of external port configuration

## FastMCP Port Configuration

### How FastMCP Uses Ports

FastMCP uses the port configuration passed during initialization:

```python
# In src/mcp_rag_server/server.py
self.mcp = FastMCP(
    "MCP RAG Server",
    host=config.server.host,
    port=config.server.port  # This is the internal port
)
```

### Environment Variable Flow

1. **Docker Compose**: Sets `MCP_SERVER_PORT=8000` (internal)
2. **Config**: Reads `MCP_SERVER_PORT` from environment
3. **FastMCP**: Uses the port from config
4. **Healthcheck**: Uses the same port via environment variable

## Configuration Examples

### Basic Configuration

```yaml
# docker-compose.yml
services:
  mcp-rag-server:
    ports:
      - "8001:8000"  # External:Internal
    environment:
      - MCP_SERVER_PORT=8000  # Internal port
      - MCP_SERVER_HOST=0.0.0.0
```

### Multi-Project Configuration

#### Project 1 (Web Development)
```yaml
# docker-compose.web-dev.yml
services:
  mcp-rag-server:
    ports:
      - "8001:8000"  # External:Internal
    environment:
      - MCP_SERVER_PORT=8000
      - MCP_COLLECTION=web_dev
```

#### Project 2 (Mobile App)
```yaml
# docker-compose.mobile.yml
services:
  mcp-rag-server:
    ports:
      - "8002:8000"  # External:Internal
    environment:
      - MCP_SERVER_PORT=8000
      - MCP_COLLECTION=mobile_app
```

#### Project 3 (Acme Corp)
```yaml
# docker-compose.acme.yml
services:
  mcp-rag-server:
    ports:
      - "8003:8000"  # External:Internal
    environment:
      - MCP_SERVER_PORT=8000
      - MCP_COLLECTION=client_acme
```

## Cursor Editor Configuration

### URL Configuration

The Cursor Editor connects to the **external port**:

```json
{
  "mcpServers": {
    "rag-web-dev": {
      "url": "http://localhost:8001/mcp",  // External port
      "type": "stdio",
      "env": {
        "MCP_SERVER_PORT": "8001"  // This is for reference only
      }
    }
  }
}
```

### Port Mapping Summary

| Project | External Port | Internal Port | Cursor URL |
|---------|---------------|---------------|------------|
| Main | 8001 | 8000 | `http://localhost:8001/mcp` |
| Web Dev | 8001 | 8000 | `http://localhost:8001/mcp` |
| Mobile | 8002 | 8000 | `http://localhost:8002/mcp` |
| Acme | 8003 | 8000 | `http://localhost:8003/mcp` |

## Troubleshooting

### Common Issues

#### 1. Healthcheck Fails
```bash
# Check if service is running on internal port
docker exec mcp-rag-server curl -f http://localhost:8000/mcp/

# Check environment variable
docker exec mcp-rag-server env | grep MCP_SERVER_PORT
```

#### 2. Port Already in Use
```bash
# Check what's using the external port
lsof -i :8001

# Use different external port
ports:
  - "8004:8000"  # Change external port
```

#### 3. Connection Refused
```bash
# Check if FastMCP is listening
docker exec mcp-rag-server netstat -tlnp | grep 8000

# Check logs
docker logs mcp-rag-server
```

### Debugging Commands

#### Check Container Ports
```bash
# List all port mappings
docker port mcp-rag-server

# Check internal port usage
docker exec mcp-rag-server netstat -tlnp
```

#### Check Healthcheck
```bash
# Manual healthcheck
docker exec mcp-rag-server curl -f http://localhost:8000/mcp/

# Check healthcheck status
docker inspect mcp-rag-server | grep -A 10 Health
```

#### Check Environment Variables
```bash
# Check all MCP variables
docker exec mcp-rag-server env | grep MCP_

# Check specific variable
docker exec mcp-rag-server env | grep MCP_SERVER_PORT
```

## Best Practices

### 1. Consistent Internal Port
- Always use `8000` as internal port
- Makes healthcheck consistent
- Simplifies configuration

### 2. Unique External Ports
- Use different external ports for each project
- Prevents port conflicts
- Enables parallel deployment

### 3. Environment Variable Usage
- Use `MCP_SERVER_PORT` for internal port
- Use Docker Compose port mapping for external port
- Keep configuration flexible

### 4. Healthcheck Configuration
- Always use internal port for healthcheck
- Use environment variable with fallback
- Test healthcheck manually if needed

## Summary

- **Internal Port**: Always `8000` (FastMCP default)
- **External Port**: Configurable per project (8001, 8002, 8003, etc.)
- **Healthcheck**: Uses internal port via environment variable
- **Cursor Editor**: Connects to external port
- **Configuration**: Flexible and project-specific

This architecture ensures that:
1. Healthcheck always works correctly
2. Multiple projects can run simultaneously
3. Port conflicts are avoided
4. Configuration is clear and maintainable