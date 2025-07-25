# Docker Configuration

This directory contains Docker-related files for the MCP RAG Server.

## Files

- `docker-compose.yml` - Docker Compose configuration for running Qdrant and MCP RAG Server
- `Dockerfile` - Docker image definition for the MCP RAG Server

## Usage

```bash
# From project root
./scripts/manage_docker.sh start
./scripts/manage_docker.sh stop
./scripts/manage_docker.sh status
```

## Services

- **qdrant**: Vector database service
- **mcp-rag-server**: MCP RAG Server application

## Volumes

- `qdrant_data`: Persistent storage for Qdrant
- `mem0_data`: Persistent storage for mem0 memory layer
