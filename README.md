# MCP RAG Server

A Model Context Protocol (MCP) server that provides Retrieval-Augmented Generation (RAG) capabilities using Qdrant vector database, mem0 memory layer, and Gemini API.

## Features

- **Vector Search**: Semantic document search using Qdrant
- **Memory Management**: Conversation memory with self-hosted mem0
- **Text Generation**: AI-powered responses using Gemini API
- **Document Processing**: Automatic chunking and embedding generation
- **MCP Integration**: Full Model Context Protocol support
- **Multiple Deployment Options**: Process, Docker, or systemd service

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for Qdrant)
- Gemini API key

### 1. Setup

```bash
git clone <repository-url>
cd mcp-rag
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Gemini API key
```

### 2. Start Services

```bash
# Start Qdrant
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest

# Start MCP RAG Server
./scripts/manage_server.sh start
```

### 3. Verify Installation

```bash
# Health check
./scripts/manage_server.sh health

# Check status
./scripts/manage_server.sh status
```

## Project Phases

The project is developed in phases:

- **Phase 1**: Foundations - ✅ Complete
- **Phase 2**: RAG Core - ✅ Complete
- **Phase 3**: MCP Integration - ✅ Complete
- **Phase 4**: Memory Integration - 🔄 In Progress (25% Complete)
- **Phase 5**: Advanced Features - ⏳ Pending

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **Documentation Index**: [[docs/00-overview/documentation-index.md]]
- **Project Overview**: [[docs/00-overview/project-overview.md]]
- **System Architecture**: [[docs/01-architecture/system-architecture.md]]
- **Installation Guide**: [[docs/02-installation/installation-guide.md]]
- **API Reference**: [[docs/03-api/api-reference.md]]
- **Development Phases**: [[docs/04-development/development-phases.md]]
- **Project Refactoring**: [[docs/04-development/project-refactoring.md]]
- **Troubleshooting**: [[docs/05-troubleshooting/troubleshooting-guide.md]]

## Development

```bash
# Run tests
python -m pytest tests/

# Check logs
./scripts/manage_server.sh logs

# Stop server
./scripts/manage_server.sh stop
```

## Contributing

1. Follow the phased development approach
2. Update documentation after changes
3. Test all deployment methods
4. Use English for all code and documentation

## License

[Add your license here]
