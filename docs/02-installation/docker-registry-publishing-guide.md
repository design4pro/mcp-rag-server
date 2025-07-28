---
title: docker-registry-publishing-guide-updated
type: note
permalink: docs/02-installation/docker-registry-publishing-guide-updated
tags:
- docker-registry
- ghcr-publishing
- deployment
---

# Docker Registry Publishing Guide

## Overview

The MCP RAG Server Docker image is now published to GitHub Container Registry (ghcr.io) for easy distribution and deployment. This enables users to run the server without building the image locally.

## Published Image

### Registry Information
- **Registry**: GitHub Container Registry (ghcr.io)
- **Repository**: `ghcr.io/design4pro/mcp-rag-server`
- **Latest Tag**: `ghcr.io/design4pro/mcp-rag-server:latest`
- **Version Tags**: `ghcr.io/design4pro/mcp-rag-server:v1.0.0`, `ghcr.io/design4pro/mcp-rag-server:v1.0`, etc.

### Image Details
- **Base Image**: `python:3.11-slim`
- **Size**: ~500MB (optimized)
- **Architecture**: Multi-platform (linux/amd64, linux/arm64)
- **License**: MIT

## Usage

### 1. Pull and Run (No Local Build Required)
```bash
# Pull the latest image
docker pull ghcr.io/design4pro/mcp-rag-server:latest

# Run with Cursor IDE configuration
# The image is automatically pulled when using mcp.json configuration
```

### 2. Cursor IDE Configuration
The `.cursor/mcp.json` file now uses the published image:
```json
{
  "mcpServers": {
    "rag-acme": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--name", "mcp-rag-acme",
        "-p", "8004:8000",
        // ... environment variables ...
        "ghcr.io/design4pro/mcp-rag-server:latest"
      ],
      "type": "stdio"
    }
  }
}
```

### 3. Manual Docker Run
```bash
# Run with default configuration
docker run -i --rm \
  -p 8001:8000 \
  -e MCP_GEMINI_API_KEY=your_api_key \
  -e MCP_USER_ID=default \
  -e MCP_QDRANT_URL=http://host.docker.internal:6333 \
  -v mcp_rag_mem0_data:/app/mem0_data \
  ghcr.io/design4pro/mcp-rag-server:latest

# Run with project-specific configuration
docker run -i --rm \
  -p 8004:8000 \
  -e MCP_GEMINI_API_KEY=your_api_key \
  -e MCP_USER_ID=acme_team \
  -e MCP_PROJECT_NAMESPACE=acme_corp \
  -e MCP_COLLECTION=client_acme \
  -e MCP_QDRANT_URL=http://host.docker.internal:6333 \
  -v mcp_rag_mem0_data_acme:/app/mem0_data \
  ghcr.io/design4pro/mcp-rag-server:latest
```

## Publishing Process

### 1. Automatic Publishing
The image is automatically published via GitHub Actions when:
- Code is pushed to `main` or `develop` branches
- Tags are created (e.g., `v1.0.0`)
- Pull requests are opened (for testing)

### 2. Workflow Steps
1. **Checkout**: Repository is checked out
2. **Setup**: Docker Buildx is configured
3. **Login**: Authentication to ghcr.io
4. **Metadata**: Image tags and labels are extracted
5. **Build**: Multi-platform image is built
6. **Push**: Image is pushed to registry
7. **Latest**: Latest tag is updated (main branch only)

### 3. Versioning Strategy
- **Latest**: Always points to the most recent stable version
- **Semantic**: `v1.0.0`, `v1.0`, `v1` for releases
- **Branch**: `main-abc123` for development builds
- **PR**: `pr-123-abc123` for pull request builds

## Benefits

### 1. Simplified Deployment
- No local Docker build required
- Consistent image across all environments
- Faster startup times

### 2. Version Management
- Automatic versioning with Git tags
- Rollback capability to previous versions
- Development and production image separation

### 3. Multi-Platform Support
- Linux AMD64 (x86_64)
- Linux ARM64 (Apple Silicon, ARM servers)
- Automatic platform detection

### 4. Security
- Automated security scanning
- Vulnerability detection
- Signed images (future enhancement)

## Local Development

### 1. Build Local Image
```bash
# Build for local development
docker build -f docker/Dockerfile -t mcp-rag-server:local .

# Use local image in mcp.json
"ghcr.io/design4pro/mcp-rag-server:latest" -> "mcp-rag-server:local"
```

### 2. Development Workflow
1. Make code changes
2. Test locally with local image
3. Push to GitHub
4. GitHub Actions builds and publishes new image
5. Update to use published image

## Troubleshooting

### 1. Image Pull Issues
```bash
# Check if image exists
docker pull ghcr.io/design4pro/mcp-rag-server:latest

# Check image details
docker inspect ghcr.io/design4pro/mcp-rag-server:latest

# List available tags
docker images ghcr.io/design4pro/mcp-rag-server
```

### 2. Permission Issues
```bash
# Login to ghcr.io (if needed)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### 3. Network Issues
```bash
# Check network connectivity
docker run --rm ghcr.io/design4pro/mcp-rag-server:latest curl -f http://host.docker.internal:6333
```

## Migration Guide

### From Local Images
1. **Update mcp.json**: Change image references to `ghcr.io/design4pro/mcp-rag-server:latest`
2. **Remove local builds**: `docker rmi mcp-rag-server:latest`
3. **Test**: Verify functionality with published image

### From Docker Compose
1. **Update compose files**: Change image to `ghcr.io/design4pro/mcp-rag-server:latest`
2. **Remove build sections**: No longer needed
3. **Test**: Verify all services work correctly

## Related Documentation

- [[../02-installation/cursor-ide-automatic-container-management|Cursor IDE Automatic Container Management]]
- [[../02-installation/installation-guide|Installation Guide]]
- [[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]
- [[../03-api/api-reference|API Reference]]