# MCP RAG Server

A comprehensive Retrieval-Augmented Generation (RAG) server built with the Model Context Protocol (MCP), featuring advanced memory management, session handling, and multi-modal document processing.

## Features

- **Document Management**: Add, search, and manage documents with automatic chunking and embedding
- **Memory Integration**: Advanced memory context retrieval with multi-factor scoring
- **Session Management**: User session tracking and statistics
- **MCP Integration**: Full Model Context Protocol support with tools and resources
- **Vector Search**: Powered by Qdrant vector database
- **AI Integration**: Gemini API for embeddings and text generation
- **Self-hosted Memory**: Local mem0 service for conversation memory

## Project Structure

```
mcp-rag/
├── data/                    # All application data
│   ├── mem0_data/          # Memory storage
│   ├── session_data/       # Session storage
│   └── test_mem0_data/     # Test memory data
├── docs/                   # Project documentation
├── src/                    # Source code
├── tests/                  # Test suite
├── docker/                 # Docker configuration
├── deployment/             # Deployment scripts
└── examples/               # Usage examples
```

## Data Organization

All application data is organized in the `data/` folder:
- **`data/mem0_data/`**: Stores conversation memories and user data
- **`data/session_data/`**: Stores user session information and statistics
- **`data/test_mem0_data/`**: Test-specific memory data for development

This centralized approach ensures clean project organization and easy data management.

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
