FROM python:3.11-slim

# Set working directory
WORKDIR /app

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
COPY .env .

# Create directory for mem0 data
RUN mkdir -p /app/mem0_data

# Expose port (will be overridden by environment variable)
EXPOSE 8000

# Health check using environment variable for port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${MCP_SERVER_PORT:-8000}/mcp/ || exit 1

# Run the server
CMD ["python", "run_server_http.py"] 