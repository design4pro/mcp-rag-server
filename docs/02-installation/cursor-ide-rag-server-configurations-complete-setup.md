---
title: Cursor IDE RAG Server Configurations - Complete Setup
type: note
permalink: docs/02-installation/cursor-ide-rag-server-configurations-complete-setup
---

# Cursor IDE RAG Server Configurations

## Overview
Complete configuration for 5 different RAG server instances that can be automatically managed by Cursor IDE.

## Available Configurations

### 1. `rag` - Default Instance
- **Port**: 8001
- **Collection**: `default`
- **Namespace**: `default`
- **User ID**: `default`
- **Volume**: `mcp_rag_mem0_data_default`

### 2. `rag-web-dev` - Web Development
- **Port**: 8002
- **Collection**: `web_dev`
- **Namespace**: `web_development`
- **User ID**: `web_dev_team`
- **Volume**: `mcp_rag_mem0_data_web_dev`

### 3. `rag-mobile` - Mobile Development
- **Port**: 8003
- **Collection**: `mobile_app`
- **Namespace**: `mobile_development`
- **User ID**: `mobile_dev_team`
- **Volume**: `mcp_rag_mem0_data_mobile`

### 4. `rag-acme` - ACME Corporation
- **Port**: 8004
- **Collection**: `client_acme`
- **Namespace**: `acme_corp`
- **User ID**: `acme_team`
- **Volume**: `mcp_rag_mem0_data_acme`
- **Features**: Debug logging, extended session timeout

### 5. `mcp-rag-remind-tools` - Remind Tools
- **Port**: 8005
- **Collection**: `remindtools`
- **Namespace**: `remind_tools`
- **User ID**: `remind_tools`
- **Volume**: `mcp_rag_mem0_data_remind_tools`

## Key Features

### Automatic Container Management
- Containers start when tool is enabled in Cursor IDE
- Containers stop when tool is disabled
- Each instance has isolated data storage
- Unique port mapping for each instance

### Project Isolation
- Separate Qdrant collections per project
- Isolated Mem0 storage volumes
- Different user IDs for data separation
- Project-specific namespaces

### Docker Configuration
- Uses `ghcr.io/design4pro/mcp-rag-server:latest`
- Connects to local Qdrant via `host.docker.internal:6333`
- Automatic container cleanup with `--rm`
- STDIO communication for Cursor IDE

## Usage Instructions

1. **Enable Tool**: In Cursor IDE, enable the desired RAG server tool
2. **Automatic Start**: Docker container starts automatically
3. **Use Tools**: RAG tools become available in Cursor IDE
4. **Disable Tool**: Container stops automatically when disabled

## Prerequisites

- Docker running locally
- Qdrant container running on port 6333
- Internet connection for pulling Docker image
- Valid Gemini API key configured

## Troubleshooting

### Common Issues
1. **Image not found**: Ensure GitHub Actions workflow completed successfully
2. **Qdrant connection failed**: Verify Qdrant is running on port 6333
3. **Port conflicts**: Each instance uses different ports (8001-8005)
4. **Volume issues**: Docker volumes are created automatically

### Verification Steps
1. Check Docker containers: `docker ps`
2. Verify Qdrant: `curl http://localhost:6333/collections`
3. Test RAG tools in Cursor IDE
4. Check logs: `docker logs <container-name>`

## Configuration Details

All configurations use the same base image but with different:
- Environment variables for project isolation
- Port mappings for concurrent operation
- Volume mounts for persistent data
- Collection names for data separation

This setup enables true multi-project development with complete data isolation.