# MCP RAG Server

A comprehensive Retrieval-Augmented Generation (RAG) server built with the Model Context Protocol (MCP), featuring advanced memory management, session handling, AI reasoning capabilities, and multi-modal document processing.

## 🚀 Features

- **Document Management**: Add, search, and manage documents with automatic chunking and embedding
- **Memory Integration**: Advanced memory context retrieval with multi-factor scoring and pattern analysis
- **Session Management**: User session tracking and comprehensive statistics
- **AI Reasoning**: Advanced reasoning capabilities including deductive, inductive, abductive, and chain-of-thought reasoning
- **Context Understanding**: Deep context analysis with entity extraction and relationship mapping
- **MCP Integration**: Full Model Context Protocol support with comprehensive tools and resources
- **Vector Search**: Powered by Qdrant vector database with advanced search capabilities
- **AI Integration**: Gemini API for embeddings and text generation
- **Self-hosted Memory**: Local mem0 service for conversation memory
- **Performance Optimization**: Optimized reasoning engine with benchmarking capabilities

## 📊 Project Status

**All Development Phases Completed** ✅

| Phase | Name               | Status      | Progress |
| ----- | ------------------ | ----------- | -------- |
| 1     | Foundations        | ✅ Complete | 100%     |
| 2     | RAG Core           | ✅ Complete | 100%     |
| 3     | MCP Integration    | ✅ Complete | 100%     |
| 4     | Memory Integration | ✅ Complete | 100%     |
| 5     | Advanced Features  | ✅ Complete | 100%     |
| 6     | AI Reasoning       | ✅ Complete | 100%     |

## 🏗️ Project Structure

```
mcp-rag/
├── data/                    # All application data
│   ├── mem0_data/          # Memory storage
│   ├── session_data/       # Session storage
│   └── test_mem0_data/     # Test memory data
├── docs/                   # Comprehensive project documentation
│   ├── 00-overview/        # Project overview and documentation index
│   ├── 01-architecture/    # System architecture documentation
│   ├── 02-installation/    # Installation and setup guides
│   ├── 03-api/             # API reference documentation
│   ├── 04-development/     # Development phases and guides
│   └── 05-troubleshooting/ # Troubleshooting and support
├── src/                    # Source code
│   └── mcp_rag_server/     # Main application package
│       ├── services/       # Core services (RAG, Memory, AI, etc.)
│       ├── tools/          # MCP tools implementation
│       ├── resources/      # MCP resources implementation
│       └── validation.py   # Data validation schemas
├── tests/                  # Comprehensive test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docker/                 # Docker configuration
├── deployment/             # Deployment scripts and configurations
├── scripts/                # Management scripts
└── examples/               # Usage examples and demonstrations
```

## 📁 Data Organization

All application data is organized in the `data/` folder:

- **`data/mem0_data/`**: Stores conversation memories and user data
- **`data/session_data/`**: Stores user session information and statistics
- **`data/test_mem0_data/`**: Test-specific memory data for development

This centralized approach ensures clean project organization and easy data management.

## ⚡ Quick Start

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

# Option 1: Use Cursor IDE (Recommended)
# Enable RAG tools in Cursor IDE - containers start automatically

# Option 2: Manual Docker run
docker run -i --rm \
  -p 8001:8000 \
  -e MCP_GEMINI_API_KEY=your_api_key \
  -e MCP_QDRANT_URL=http://host.docker.internal:6333 \
  ghcr.io/design4pro/mcp-rag-server:latest

# Option 3: Use scripts
./scripts/manage_server.sh start
```

### 3. Verify Installation

```bash
# Health check
./scripts/manage_server.sh health

# Check status
./scripts/manage_server.sh status
```

## 🔧 Development

```bash
# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=src/mcp_rag_server

# Check logs
./scripts/manage_server.sh logs

# Stop server
./scripts/manage_server.sh stop
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **Documentation Index**: [[docs/00-overview/documentation-index.md]]
- **Project Overview**: [[docs/00-overview/project-overview.md]]
- **System Architecture**: [[docs/01-architecture/system-architecture.md]]
- **Installation Guide**: [[docs/02-installation/installation-guide.md]]
- **Cursor IDE Setup**: [[docs/02-installation/cursor-ide-automatic-container-management|Cursor IDE Automatic Container Management]]
- **Docker Registry**: [[docs/02-installation/docker-registry-publishing-guide|Docker Registry Publishing Guide]]
- **API Reference**: [[docs/03-api/api-reference.md]]
- **Development Phases**: [[docs/04-development/phases/development-phases-overview.md]]
- **Troubleshooting**: [[docs/05-troubleshooting/troubleshooting-guide.md]]

## 🧪 Testing

The project includes comprehensive test coverage:

- **Unit Tests**: 183 tests covering all core functionality
- **Integration Tests**: Complete MCP tool integration testing
- **Performance Tests**: Benchmarking and performance validation
- **Error Handling**: Comprehensive error scenario testing

Run tests with:

```bash
python -m pytest tests/ -v
```

## 🚀 Advanced Features

### AI Reasoning Capabilities

- **Deductive Reasoning**: Logical inference from premises to conclusions
- **Inductive Reasoning**: Pattern-based generalizations from observations
- **Abductive Reasoning**: Hypothesis generation from observations
- **Chain-of-Thought Reasoning**: Multi-step reasoning with intermediate conclusions
- **Multi-Hop Reasoning**: Iterative reasoning across multiple contexts

### Memory Management

- **Semantic Memory Search**: Advanced semantic search capabilities
- **Memory Clustering**: Automatic memory organization and clustering
- **Pattern Analysis**: Memory pattern identification and analysis
- **Context Retrieval**: Enhanced memory context with multi-factor scoring

### Session Management

- **User Session Tracking**: Comprehensive session management
- **Session Statistics**: Detailed usage analytics and statistics
- **Session Persistence**: Reliable session data storage
- **Cleanup Management**: Automatic session cleanup and maintenance

## 🤝 Contributing

1. Follow the phased development approach
2. Update documentation after changes
3. Test all deployment methods
4. Use English for all code and documentation
5. Ensure all tests pass before submitting changes

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support and troubleshooting:

1. Check the troubleshooting guide: [[docs/05-troubleshooting/troubleshooting-guide.md]]
2. Review the system architecture: [[docs/01-architecture/system-architecture.md]]
3. Consult the API reference: [[docs/03-api/api-reference.md]]

## 🔄 Version History

- **v1.0.0**: Complete implementation with all phases finished
  - Advanced AI reasoning capabilities
  - Comprehensive memory management
  - Full MCP integration
  - Performance optimization
  - Complete test coverage

---

**Project Status**: ✅ Production Ready  
**Last Updated**: 2025-01-25  
**Version**: 1.0.0
