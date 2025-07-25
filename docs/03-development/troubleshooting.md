# Troubleshooting Guide

## Common Issues and Solutions

### Docker Build Issues

#### Issue: "failed to solve: failed to compute cache key: failed to calculate checksum of ref"

**Symptoms:**

```
ERROR: failed to solve: failed to compute cache key: failed to calculate checksum of ref 5ce827d0-f886-4873-84a8-17d7a22d7d56::k0v32hcvy7fczcn3y46xpq5by: "/run_server_http.py": not found
```

**Cause:** Docker build context is not set correctly. The Dockerfile expects files from the project root, but the build context is set to the `docker/` directory.

**Solution:**

1. Use the correct build context:

   ```bash
   # From project root
   docker build -f docker/Dockerfile -t mcp-rag-server .
   ```

2. Or use the fixed management script:
   ```bash
   ./scripts/manage_docker.sh start
   ```

#### Issue: Container name conflicts

**Symptoms:**

```
Error response from daemon: Conflict. The container name "/mcp-rag-server" is already in use
```

**Solution:**

```bash
# Remove existing containers
docker rm -f mcp-rag-server mcp-rag-qdrant

# Start fresh
./scripts/manage_docker.sh start
```

### Service Connection Issues

#### Issue: Qdrant connection refused

**Symptoms:**

```
[Errno 61] Connection refused
```

**Solution:**

1. Ensure Qdrant is running:

   ```bash
   docker ps | grep qdrant
   ```

2. Start Qdrant service:

   ```bash
   cd docker && docker-compose up -d qdrant
   ```

3. Check Qdrant health:
   ```bash
   curl http://localhost:6333/
   ```

#### Issue: Mem0 API key error

**Symptoms:**

```
Error initializing mem0 service: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
```

**Solution:**
This is expected for self-hosted mem0. The service will still work with local storage. If you want to use cloud mem0, set the `OPENAI_API_KEY` environment variable.

### MCP Server Issues

#### Issue: MCP endpoint returns 406

**Symptoms:**

```
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept text/event-stream"}}
```

**Solution:**
This is normal behavior. MCP endpoints require the `Accept: text/event-stream` header. Use proper MCP clients to connect.

#### Issue: Server not responding

**Symptoms:**

```
❌ MCP RAG Server health check failed (Status: 000)
```

**Solution:**

1. Check server logs:

   ```bash
   ./scripts/manage_docker.sh logs-service mcp-rag-server
   ```

2. Wait for server to fully start (may take 30-60 seconds)

3. Verify all services are healthy:
   ```bash
   ./scripts/manage_docker.sh status
   ```

### Environment Configuration Issues

#### Issue: Missing environment variables

**Symptoms:**

```
RuntimeError: GEMINI_API_KEY not set
```

**Solution:**

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Set your API keys in `.env`:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

#### Issue: Invalid configuration

**Symptoms:**

```
ValidationError: Invalid configuration
```

**Solution:**

1. Check your `.env` file format
2. Ensure all required variables are set
3. Verify URL formats (e.g., `http://localhost:6333`)

### Performance Issues

#### Issue: Slow response times

**Symptoms:**

- Long delays when adding documents
- Slow search results

**Solution:**

1. Check system resources:

   ```bash
   docker stats
   ```

2. Optimize chunk size in configuration
3. Consider increasing Docker memory limits

#### Issue: Memory usage high

**Symptoms:**

- Container crashes
- Out of memory errors

**Solution:**

1. Increase Docker memory limits
2. Optimize document chunking parameters
3. Monitor memory usage with `docker stats`

## Getting Help

### Debug Mode

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

### Health Checks

Run comprehensive health checks:

```bash
# Test all services
python tests/integration/test_health.py

# Test Phase 3 functionality
python tests/integration/test_phase3_tools.py
```

### Logs

View detailed logs:

```bash
# All services
./scripts/manage_docker.sh logs

# Specific service
./scripts/manage_docker.sh logs-service mcp-rag-server
```

### Environment Information

Check environment setup:

```bash
./scripts/manage_docker.sh env
```

## Related Documentation

- [[Installation Guide]]
- [[Configuration Guide]]
- [[System Architecture]]
