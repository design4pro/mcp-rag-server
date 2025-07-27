---
title: installation-guide
type: note
permalink: docs/02-installation/installation-guide
tags:
  - "['installation'"
  - "'setup'"
  - configuration'
  - "'obsidian-compatible']"
---

# Installation Guide

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space for dependencies

### Required Accounts and API Keys

- **Google AI Studio**: For Gemini API access
- **Qdrant Cloud** (optional): For hosted vector database
- **Mem0 Platform** (optional): For hosted memory service

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag
```

### 2. Set Up Python Environment

#### Using venv (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Using conda

```bash
conda create -n mcp-rag python=3.9
conda activate mcp-rag
```

### 3. Install Dependencies

#### Using pip

```bash
pip install -e .
```

#### Using uv (Recommended for development)

```bash
uv sync
```

### 4. Environment Configuration

#### Copy Environment Template

```bash
cp .env.example .env
```

#### Configure Required Variables

Edit `.env` file with your API keys:

```env
# Required: Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# Optional: Mem0 Configuration
MEM0_API_KEY=your_mem0_api_key_here

# Optional: Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
```

### 5. Set Up Qdrant

#### Option A: Local Qdrant (Recommended for development)

Using Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Using Docker Compose:

```bash
docker-compose up -d qdrant
```

#### Option B: Qdrant Cloud

1. Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create a new cluster
3. Get your API key and URL
4. Update `.env` with cloud credentials

### 7. Docker Setup (Alternative Installation)

#### Prerequisites

- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher

#### Quick Start with Docker

```bash
# Clone repository
git clone <repository-url>
cd rag

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start all services with Docker
./scripts/manage_docker.sh start
```

**Note**: Health checks have been optimized for faster startup:

- Qdrant: 10s intervals, 5s timeout, 15s start period
- MCP Server: 30s intervals, 10s timeout, 3 retries

#### Docker Management Commands

```bash
# Start services
./scripts/manage_docker.sh start

# Stop services
./scripts/manage_docker.sh stop

# Restart services
./scripts/manage_docker.sh restart

# Show status
./scripts/manage_docker.sh status

# View logs
./scripts/manage_docker.sh logs

# Build Docker image (with cache)
./scripts/manage_docker.sh build

# Rebuild Docker image from scratch (no cache)
./scripts/manage_docker.sh rebuild

# Clean up Docker resources
./scripts/manage_docker.sh cleanup

# Show environment info
./scripts/manage_docker.sh env

# Show volume information and data
./scripts/manage_docker.sh volumes
```

#### Docker Rebuild Options

When you make changes to the code and want to update the Docker image:

**Option 1: Quick rebuild (with cache)**

```bash
./scripts/manage_docker.sh build
./scripts/manage_docker.sh restart
```

**Option 2: Fresh rebuild (no cache) - recommended for major changes**

```bash
./scripts/manage_docker.sh rebuild
```

This will:

- Stop running services
- Remove existing image
- Build completely fresh image
- Optionally start services

#### Data Persistence During Rebuild

**Important**: Your data is preserved during rebuild operations!

The following data is stored in Docker volumes and persists across rebuilds:

- **Mem0 memories**: Stored in `mem0_data` volume (`memories.json`)
- **Qdrant documents**: Stored in `qdrant_data` volume (collections, embeddings)
- **User sessions**: Preserved in persistent storage

**What gets removed during rebuild:**

- Docker image layers (code changes)
- Container state (temporary data)
- Build cache

**What stays preserved:**

- All user memories and conversations
- All uploaded documents and embeddings
- All user sessions and metadata
- Database collections and indexes

To completely clear all data, use the cleanup command:

```bash
./scripts/manage_docker.sh cleanup
# Then manually remove volumes if needed:
# docker volume rm mcp-rag_mem0_data mcp-rag_qdrant_data
```

#### Checking Data Status

To verify what data is stored in your volumes:

```bash
./scripts/manage_docker.sh volumes
```

This command shows:

- List of all project volumes
- File and directory counts in each volume
- Specific files like `memories.json` for Mem0
- Qdrant collections status
- Tips for data management

Example output:

```
📁 mcp-rag_mem0_data
   Contains: 1 files, 0 directories
   📄 memories.json exists

📁 mcp-rag_qdrant_data
   Contains: 172 files, 54 directories
   🗄️  Qdrant collections exist
```

### 8. Verify Installation

#### Run Basic Test

```bash
python -c "from mcp_rag_server import MCPRAGServer; print('✅ Installation successful')"
```

#### Run Example

```bash
python examples/basic_usage.py
```

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 2. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 3. Configure IDE

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_rag_server

# Run specific test file
pytest tests/test_rag_service.py
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'mcp_rag_server'`

**Solution**: Ensure you're in the correct directory and have installed the package:

```bash
cd rag
pip install -e .
```

#### 2. API Key Errors

**Problem**: `AuthenticationError` or `Invalid API key`

**Solution**: Verify your API keys in `.env` file:

```bash
echo $GEMINI_API_KEY
echo $QDRANT_API_KEY
```

#### 3. Qdrant Connection Issues

**Problem**: `ConnectionError` when connecting to Qdrant

**Solution**: Check if Qdrant is running:

```bash
curl http://localhost:6333/collections
```

#### 4. Memory Issues

**Problem**: `OutOfMemoryError` during embedding generation

**Solution**: Reduce batch size or use smaller models:

```env
VECTOR_SIZE=384  # Instead of 768
```

#### 5. Docker Issues

**Problem**: Docker containers not starting or failing

**Solution**: Check Docker setup and rebuild if needed:

```bash
# Check Docker status
./scripts/manage_docker.sh status

# View detailed logs
./scripts/manage_docker.sh logs

# Rebuild from scratch if needed
./scripts/manage_docker.sh rebuild
```

**Problem**: Docker image outdated after code changes

**Solution**: Rebuild the Docker image:

```bash
# For minor changes (with cache)
./scripts/manage_docker.sh build

# For major changes (no cache)
./scripts/manage_docker.sh rebuild
```

**Problem**: Port conflicts with Docker

**Solution**: Check and change ports in docker-compose.yml:

```yaml
ports:
  - "8001:8001" # Change 8001 to available port
```

**Problem**: Qdrant container shows "waiting" status for too long

**Solution**: This is usually a health check timing issue. The health check has been optimized with:

- Shorter intervals (10s instead of 30s)
- Faster timeouts (5s instead of 10s)
- Proper start period (15s)

If you still see "waiting" status, check:

```bash
# Check container logs
./scripts/manage_docker.sh logs-service qdrant

# Check health check manually
docker exec mcp-rag-qdrant timeout 3 bash -c '</dev/tcp/localhost/6333' && echo "OK" || echo "FAILED"
```

### Getting Help

1. **Check Logs**: Look for detailed error messages in console output
2. **Verify Configuration**: Ensure all environment variables are set correctly
3. **Test Individual Services**: Run service-specific tests
4. **Check Documentation**: Review [[../03-api/api-reference|API Reference]] and [[../01-architecture/system-architecture|Configuration Guide]]

## Next Steps

After successful installation:

1. **Read the Documentation**: Start with [[../00-overview/project-overview|Project Overview]]
2. **Run Examples**: Try the [[../03-api/api-reference|Basic Usage Example]]
3. **Explore Features**: Check out [[../04-development/development-phases|Feature Guide]]
4. **Start Developing**: Follow the [[../04-development/development-phases|Development Guide]]

## Related Documentation

- [[../01-architecture/system-architecture|Configuration Guide]]
- [[../04-development/development-phases|Development Guide]]
- [[../03-api/api-reference|API Reference]]
- [[../05-troubleshooting/troubleshooting-guide|Troubleshooting Guide]]
