FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Add metadata
LABEL org.opencontainers.image.title="MCP RAG Server"
LABEL org.opencontainers.image.description="Production-ready MCP RAG Server with advanced AI reasoning, memory management, and comprehensive MCP integration"
LABEL org.opencontainers.image.vendor="Design4Pro"
LABEL org.opencontainers.image.source="https://github.com/design4pro/mcp-rag-server"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies
RUN apt-get update && apt-get install -y \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY src/run_server_http.py ./run_server_http.py
COPY src/run_server.py ./run_server.py
COPY .env .

# Create directory for mem0 data
RUN mkdir -p /app/mem0_data

# Expose port (will be overridden by environment variable)
EXPOSE 8000

# Health check using environment variable for port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${MCP_SERVER_PORT:-8000}/mcp/ || exit 1

# Run the server (use run_server.py for stdio communication)
CMD ["python", "run_server.py"] 