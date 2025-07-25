# Troubleshooting Guide

This guide helps resolve common issues with the MCP RAG Server.

## Health Check Issues

### Problem: All services show `false` in health check

**Symptoms:**

```json
{
  "status": "healthy",
  "services": {
    "gemini": false,
    "qdrant": false,
    "mem0": false,
    "rag": false
  }
}
```

**Root Cause:** Services are not being initialized during server startup.

**Solution:**

1. Ensure you're using the latest version of the server
2. Check that the server is properly configured with lifespan management
3. Run the connection test script:
   ```bash
   python test_connections.py
   ```

### Problem: Gemini API connection fails

**Symptoms:**

- `gemini: false` in health check
- Error: "Gemini API key not found" or authentication errors

**Solution:**

1. Set the `GEMINI_API_KEY` environment variable:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
2. Or add it to your `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
3. Verify the API key is valid by testing the connection:
   ```bash
   python test_connections.py
   ```

### Problem: Qdrant connection fails

**Symptoms:**

- `qdrant: false` in health check
- Error: "Connection refused" or "Qdrant not available"

**Solution:**

1. Start Qdrant using Docker:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
2. Verify Qdrant is accessible:
   ```bash
   curl http://localhost:6333/health
   ```
3. Check the Qdrant configuration in your `.env`:
   ```env
   QDRANT_URL=http://localhost:6333
   ```
4. No API key is required for local Docker installation

### Problem: Mem0 connection fails

**Symptoms:**

- `mem0: false` in health check
- Error: "Mem0 service not available"

**Solution:**

1. Install mem0 package:
   ```bash
   pip install mem0ai
   ```
2. Mem0 will automatically use local storage if OpenAI API is not configured
3. For local storage configuration:
   ```env
   MEM0_LOCAL_STORAGE_PATH=./mem0_data
   ```

## Configuration Issues

### Problem: Environment variables not loaded

**Symptoms:**

- Configuration shows default values
- Services fail to initialize

**Solution:**

1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
2. Fill in your Gemini API key and configuration
3. Ensure the `.env` file is in the project root directory

### Problem: Wrong configuration values

**Symptoms:**

- Services connect but behave unexpectedly
- Errors about invalid parameters

**Solution:**

1. Check the configuration documentation in `docs/02-architecture/`
2. Verify all required fields are set
3. Use the test script to validate configuration:
   ```bash
   python test_connections.py
   ```

## Server Startup Issues

### Problem: Server fails to start

**Symptoms:**

- Error during server initialization
- Import errors or missing dependencies

**Solution:**

1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Check Python version (requires 3.9+):
   ```bash
   python --version
   ```
3. Verify all required packages are installed:
   ```bash
   pip list | grep -E "(mcp|qdrant|mem0|google-genai|fastapi|uvicorn)"
   ```
4. For HTTP server issues, try the simple server:
   ```bash
   python simple_server.py
   ```

### Problem: FastMCP lifespan errors

**Symptoms:**

- `TypeError: 'async_generator' object does not support the asynchronous context manager protocol`
- `RuntimeError: Task group is not initialized`
- `RuntimeError: Received request before initialization was complete`

**Solution:**

1. Use the simple HTTP server for testing:
   ```bash
   python simple_server.py
   ```
2. The simple server uses FastAPI with proper lifespan management
3. For MCP protocol, use the stdio transport:
   ```bash
   python run_server.py
   ```

### Problem: Server starts but tools don't work

**Symptoms:**

- Server runs but MCP tools return errors
- "RAG service not initialized" errors

**Solution:**

1. Check that services are properly initialized in the lifespan
2. Verify the server is using the correct configuration
3. Enable debug logging:
   ```bash
   LOG_LEVEL=DEBUG python run_server.py
   ```

## Performance Issues

### Problem: Slow response times

**Symptoms:**

- Long delays when adding documents or searching
- Timeout errors

**Solution:**

1. Check Qdrant performance:
   ```bash
   curl http://localhost:6333/collections
   ```
2. Monitor memory usage
3. Consider optimizing chunk sizes and batch processing

### Problem: Memory usage is high

**Symptoms:**

- Server consumes excessive memory
- Out of memory errors

**Solution:**

1. Reduce batch sizes in configuration
2. Limit concurrent operations
3. Monitor and optimize document chunking parameters

## Debugging

### Enable Debug Logging

Set the log level to DEBUG for detailed information:

```bash
LOG_LEVEL=DEBUG python run_server.py
```

### Test Individual Services

Use the test script to isolate issues:

```bash
python test_connections.py
```

### Check Service Logs

For Docker-based services like Qdrant:

```bash
docker logs <container_id>
```

### Common Error Messages

| Error                         | Cause                         | Solution                     |
| ----------------------------- | ----------------------------- | ---------------------------- |
| "Gemini API key not found"    | Missing API key               | Set `GEMINI_API_KEY`         |
| "Connection refused"          | Service not running           | Start required services      |
| "RAG service not initialized" | Service initialization failed | Check configuration and logs |
| "Invalid configuration"       | Wrong config values           | Verify `.env` file           |

## Getting Help

If you're still experiencing issues:

1. Check the logs with `LOG_LEVEL=DEBUG`
2. Run the connection test script
3. Verify your configuration matches the examples
4. Check that all required services are running
5. Review the architecture documentation in `docs/02-architecture/`
