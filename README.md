# MCP RAG Server

A Model Context Protocol (MCP) server that provides Retrieval-Augmented Generation (RAG) capabilities using Qdrant vector database, mem0 memory layer, and Gemini API.

## Features

- **Vector Search**: Semantic document search using Qdrant
- **Memory Management**: Conversation memory with self-hosted mem0
- **Text Generation**: AI-powered responses using Gemini API
- **Document Processing**: Automatic chunking and embedding generation
- **MCP Integration**: Full Model Context Protocol support
- **Multiple Deployment Options**: Process, Docker, or systemd service

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP RAG       │    │   Qdrant        │
│   (Cursor IDE)  │◄──►│   Server        │◄──►│   (Docker)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   mem0          │    │   Gemini API    │
                       │   (Self-hosted) │    │   (Embeddings)  │
                       └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for Qdrant)
- Gemini API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd mcp-rag
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your Gemini API key
```

### 3. Start Qdrant (Docker)

```bash
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

### 4. Start MCP RAG Server

Choose one of the deployment methods below.

## Deployment Options

### Option 1: Process Management (Recommended for Development)

Use the management script for easy process control:

```bash
# Start server
./scripts/manage_server.sh start

# Check status
./scripts/manage_server.sh status

# View logs
./scripts/manage_server.sh logs

# Stop server
./scripts/manage_server.sh stop

# Restart server
./scripts/manage_server.sh restart

# Health check
./scripts/manage_server.sh health
```

### Option 2: Docker Compose (Recommended for Production)

Full containerized deployment with Qdrant:

```bash
# Build and start all services
./scripts/manage_docker.sh build
./scripts/manage_docker.sh start

# Check status
./scripts/manage_docker.sh status

# View logs
./scripts/manage_docker.sh logs

# Stop services
./scripts/manage_docker.sh stop

# Cleanup
./scripts/manage_docker.sh cleanup
```

### Option 3: Manual Process

```bash
# Start server manually
python run_server_http.py

# Or with stdio transport
python run_server.py
```

### Option 4: Systemd Service (Linux/macOS)

```bash
# Copy service file
sudo cp mcp-rag-server.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable mcp-rag-server
sudo systemctl start mcp-rag-server

# Check status
sudo systemctl status mcp-rag-server

# View logs
sudo journalctl -u mcp-rag-server -f
```

## Cursor IDE Integration

1. **Configuration**: The server is pre-configured in `.cursor/mcpServers.json`
2. **Restart Cursor**: Restart Cursor IDE to load the MCP server
3. **Usage**: The server will be available as MCP tools in Cursor

### Available MCP Tools

- `health_check()` - Check server health
- `add_document(content, metadata)` - Add document to RAG
- `search_documents(query, limit)` - Search documents
- `ask_question(question, user_id)` - Ask RAG question

## Configuration

### Environment Variables

| Variable                  | Description          | Default                 |
| ------------------------- | -------------------- | ----------------------- |
| `GEMINI_API_KEY`          | Gemini API key       | Required                |
| `QDRANT_URL`              | Qdrant server URL    | `http://localhost:6333` |
| `MEM0_SELF_HOSTED`        | Use self-hosted mem0 | `true`                  |
| `MEM0_LOCAL_STORAGE_PATH` | mem0 data directory  | `./mem0_data`           |
| `FASTMCP_HOST`            | Server host          | `127.0.0.1`             |
| `FASTMCP_PORT`            | Server port          | `8001`                  |
| `LOG_LEVEL`               | Logging level        | `INFO`                  |

### Document Processing

| Variable                  | Description         | Default |
| ------------------------- | ------------------- | ------- |
| `CHUNK_SIZE`              | Document chunk size | `1000`  |
| `CHUNK_OVERLAP`           | Chunk overlap       | `200`   |
| `MAX_CHUNKS_PER_DOCUMENT` | Max chunks per doc  | `50`    |

## API Endpoints

- **MCP Endpoint**: `http://localhost:8001/mcp/`
- **Health Check**: `curl http://localhost:8001/mcp/` (expects 406 for MCP)

## Troubleshooting

### Common Issues

1. **Port Already in Use**

   ```bash
   lsof -i :8001
   kill -9 <PID>
   ```

2. **Qdrant Connection Failed**

   ```bash
   docker ps | grep qdrant
   docker logs <qdrant-container-id>
   ```

3. **Gemini API Errors**

   - Verify API key in `.env`
   - Check API quota and limits

4. **Graceful Shutdown Issues**
   - Use management scripts for proper signal handling
   - Check logs for cleanup errors

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
./scripts/manage_server.sh start
```

### Health Checks

```bash
# Check all services
./scripts/manage_server.sh health

# Manual checks
curl http://localhost:6333/health  # Qdrant
curl http://localhost:8001/mcp/    # MCP Server
```

## Development

### Project Structure

```
rag/
├── src/mcp_rag_server/          # Main application code
│   ├── config.py               # Configuration management
│   ├── server.py               # MCP server implementation
│   ├── run_server.py           # stdio transport runner
│   ├── run_server_http.py      # HTTP transport runner
│   └── services/               # Service layer
│       ├── document_processor.py
│       ├── gemini_service.py
│       ├── mem0_service.py
│       ├── qdrant_service.py
│       └── rag_service.py
├── docker/                     # Docker configuration
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── Dockerfile              # Docker image definition
│   └── README.md               # Docker documentation
├── scripts/                    # Management scripts
│   ├── manage_docker.sh       # Docker management
│   └── manage_server.sh       # Process management
├── tests/                      # Test files
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── README.md              # Test documentation
├── deployment/                 # Deployment files
│   ├── mcp-rag-server.service # Systemd service
│   ├── start_services.sh      # Startup script
│   └── README.md              # Deployment documentation
├── examples/                   # Example usage
├── docs/                       # Documentation
├── data/                       # Persistent data
│   ├── mem0_data/             # mem0 memory data
│   └── README.md              # Data documentation
├── logs/                       # Log files
│   └── README.md              # Log documentation
├── pyproject.toml             # Project configuration
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run unit tests only
python -m pytest tests/unit/

# Run integration tests only
python -m pytest tests/integration/

# Run with coverage
python -m pytest tests/ --cov=src/mcp_rag_server
```

## Performance

### Optimization Tips

1. **Chunk Size**: Adjust `CHUNK_SIZE` based on document characteristics
2. **Batch Processing**: Documents are processed in chunks for efficiency
3. **Memory Management**: Self-hosted mem0 uses local file storage
4. **Vector Search**: Qdrant provides fast similarity search

### Monitoring

- Check service logs: `./scripts/manage_server.sh logs`
- Monitor resource usage: `docker stats` (if using Docker)
- Health checks: `./scripts/manage_server.sh health`

## Contributing

1. Follow the phased development approach
2. Update documentation after changes
3. Test all deployment methods
4. Use English for all code and documentation

## License

[Add your license here]
