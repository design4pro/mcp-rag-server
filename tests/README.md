# Tests

This directory contains tests for the MCP RAG Server.

## Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for the complete system

## Running Tests

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

## Test Files

### Unit Tests

- `test_rag_service.py` - Tests for RAG service functionality

### Integration Tests

- `test_connections.py` - Tests for service connections
- `test_health.py` - Health check tests
- `test_mcp_client.py` - MCP client integration tests
