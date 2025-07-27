---
title: cursor-ide-automatic-container-management
type: note
permalink: docs/02-installation/cursor-ide-automatic-container-management
tags:
- '[''cursor-ide'''
- docker
- ragproject-isolation'
- '''automatic-management'']'
---

# Cursor IDE Automatic Container Management for MCP RAG Server

## Overview

The MCP RAG Server configuration in Cursor IDE has been updated to automatically manage Docker container lifecycle. Each RAG server instance now uses `docker run` instead of `docker exec`, enabling automatic startup and shutdown when tools are enabled/disabled in Cursor IDE.

## Configuration Changes

### Before (Manual Container Management)
```json
"rag-acme": {
  "command": "docker",
  "args": ["exec", "-i", "mcp-rag-server", "python", "run_server.py"],
  "type": "stdio",
  "env": {
    "MCP_USER_ID": "acme_team",
    "MCP_PROJECT_NAMESPACE": "acme_corp"
  }
}
```

### After (Automatic Container Management)
```json
"rag-acme": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "--name", "mcp-rag-acme",
    "-p", "8004:8000",
    "-e", "MCP_USER_ID=acme_team",
    "-e", "MCP_PROJECT_NAMESPACE=acme_corp",
    "-e", "MCP_COLLECTION=client_acme",
    "-v", "mcp_rag_mem0_data_acme:/app/mem0_data",
    "mcp-rag-server:latest"
  ],
  "type": "stdio"
}
```

## Key Features

### 1. Automatic Container Lifecycle
- **Start**: Container starts automatically when RAG tool is enabled in Cursor IDE
- **Stop**: Container stops automatically when RAG tool is disabled
- **Cleanup**: `--rm` flag ensures containers are removed after stopping

### 2. Project Isolation
Each instance has unique configuration:
- **rag**: `default` project (Port 8001)
- **rag-web-dev**: `web_development` project (Port 8002)
- **rag-mobile**: `mobile_development` project (Port 8003)
- **rag-acme**: `acme_corp` project (Port 8004)

### 3. Persistent Data Storage
Each project uses separate Docker volumes:
- `mcp_rag_mem0_data_default` - Default project memories
- `mcp_rag_mem0_data_web_dev` - Web development memories
- `mcp_rag_mem0_data_mobile` - Mobile development memories
- `mcp_rag_mem0_data_acme` - Acme Corp memories

### 4. Environment Variables
Each instance receives project-specific environment variables:
- `MCP_USER_ID` - Unique user identifier for each project
- `MCP_PROJECT_NAMESPACE` - Project namespace for data isolation
- `MCP_COLLECTION` - Qdrant collection name for document storage
- `MCP_QDRANT_URL` - Points to host Qdrant instance
- `MCP_MEM0_STORAGE_PATH` - Memory storage path

## Usage Instructions

### 1. Build Docker Image
Before using the tools, build the Docker image:
```bash
# From project root
docker build -f docker/Dockerfile -t mcp-rag-server:latest .
```

### 2. Start Qdrant (Required)
Ensure Qdrant is running on host machine:
```bash
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

### 3. Enable RAG Tools in Cursor IDE
- Open Cursor IDE
- Go to MCP Servers configuration
- Enable desired RAG tool (rag, rag-web-dev, rag-mobile, or rag-acme)
- Container will start automatically

### 4. Verify Isolation
Test that each instance uses correct user_id:
```python
# Test rag-acme instance
mcp_rag-acme_get_document_stats(user_id="acme_team")

# Test rag-web-dev instance  
mcp_rag-web-dev_get_document_stats(user_id="web_dev_team")
```

## Technical Details

### Container Configuration
- **Base Image**: `python:3.11-slim`
- **Working Directory**: `/app`
- **Port Mapping**: Each instance maps to different host port
- **Volume Mounting**: Persistent memory storage per project
- **Network**: Uses `host.docker.internal` to connect to host Qdrant

### Environment Variables
- `MCP_GEMINI_API_KEY` - Gemini API key for embeddings and generation
- `MCP_USER_ID` - Project-specific user identifier
- `MCP_PROJECT_NAMESPACE` - Namespace for data isolation
- `MCP_COLLECTION` - Qdrant collection name
- `MCP_SERVER_PORT` - Internal server port (8000)
- `MCP_LOG_LEVEL` - Logging level (INFO/DEBUG)
- `MCP_QDRANT_URL` - Qdrant connection URL
- `MCP_MEM0_STORAGE_PATH` - Memory storage path

### Data Persistence
- **Memories**: Stored in Docker volumes per project
- **Documents**: Stored in Qdrant collections per project
- **Sessions**: Managed per user_id within each project

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check if image exists
docker images | grep mcp-rag-server

# Build image if missing
docker build -f docker/Dockerfile -t mcp-rag-server:latest .
```

#### 2. Port Conflicts
```bash
# Check which ports are in use
netstat -tulpn | grep :800

# Stop conflicting containers
docker stop $(docker ps -q)
```

#### 3. Qdrant Connection Issues
```bash
# Ensure Qdrant is running
docker ps | grep qdrant

# Start Qdrant if needed
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

#### 4. Volume Issues
```bash
# List volumes
docker volume ls | grep mcp_rag

# Create missing volumes
docker volume create mcp_rag_mem0_data_acme
docker volume create mcp_rag_mem0_data_web_dev
docker volume create mcp_rag_mem0_data_mobile
docker volume create mcp_rag_mem0_data_default
```

### Debug Commands
```bash
# Check container logs
docker logs mcp-rag-acme

# Check container status
docker ps -a | grep mcp-rag

# Check volume contents
docker run --rm -v mcp_rag_mem0_data_acme:/data alpine ls -la /data
```

## Benefits

### 1. Simplified Workflow
- No manual Docker management required
- Automatic startup/shutdown with Cursor IDE
- Clean container lifecycle management

### 2. Project Isolation
- Complete data separation between projects
- No risk of data mixing between different clients
- Independent configuration per project

### 3. Resource Efficiency
- Containers only run when needed
- Automatic cleanup prevents resource waste
- Isolated resource usage per project

### 4. Development Experience
- Seamless integration with Cursor IDE
- No need to remember Docker commands
- Consistent environment across team members

## Related Documentation

- [[../02-installation/installation-guide|Installation Guide]]
- [[../02-installation/project-isolation-configuration|Project Isolation Configuration]]
- [[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]
- [[../03-api/api-reference|API Reference]]