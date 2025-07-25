# Deployment

This directory contains deployment-related files for the MCP RAG Server.

## Files

- `mcp-rag-server.service` - Systemd service file for Linux/macOS
- `start_services.sh` - Service startup script

## Systemd Service

To install the systemd service:

```bash
# Copy service file
sudo cp mcp-rag-server.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable mcp-rag-server
sudo systemctl start mcp-rag-server

# Check status
sudo systemctl status mcp-rag-server
```

## Manual Startup

```bash
# Run startup script
./start_services.sh
```

## Environment Variables

Make sure to set the required environment variables in the service file or startup script:

- `GEMINI_API_KEY` - Gemini API key
- `QDRANT_URL` - Qdrant server URL
- `MEM0_SELF_HOSTED` - Use self-hosted mem0
- `MEM0_LOCAL_STORAGE_PATH` - mem0 data directory
- `FASTMCP_HOST` - Server host
- `FASTMCP_PORT` - Server port
