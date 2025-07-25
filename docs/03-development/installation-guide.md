# Installation Guide

## Prerequisites

### System Requirements
- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space for dependencies

### Required Accounts and API Keys
- **Google AI Studio**: For Gemini API access
- **Qdrant Cloud** (optional): For hosted vector database
- **Mem0 Platform** (optional): For hosted memory service

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag
```

### 2. Set Up Python Environment

#### Using venv (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Using conda
```bash
conda create -n mcp-rag python=3.9
conda activate mcp-rag
```

### 3. Install Dependencies

#### Using pip
```bash
pip install -e .
```

#### Using uv (Recommended for development)
```bash
uv sync
```

### 4. Environment Configuration

#### Copy Environment Template
```bash
cp .env.example .env
```

#### Configure Required Variables
Edit `.env` file with your API keys:

```env
# Required: Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# Optional: Mem0 Configuration
MEM0_API_KEY=your_mem0_api_key_here

# Optional: Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
```

### 5. Set Up Qdrant

#### Option A: Local Qdrant (Recommended for development)

Using Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

Using Docker Compose:
```bash
docker-compose up -d qdrant
```

#### Option B: Qdrant Cloud
1. Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create a new cluster
3. Get your API key and URL
4. Update `.env` with cloud credentials

### 6. Verify Installation

#### Run Basic Test
```bash
python -c "from mcp_rag_server import MCPRAGServer; print('✅ Installation successful')"
```

#### Run Example
```bash
python examples/basic_usage.py
```

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 2. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 3. Configure IDE

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_rag_server

# Run specific test file
pytest tests/test_rag_service.py
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'mcp_rag_server'`

**Solution**: Ensure you're in the correct directory and have installed the package:
```bash
cd rag
pip install -e .
```

#### 2. API Key Errors
**Problem**: `AuthenticationError` or `Invalid API key`

**Solution**: Verify your API keys in `.env` file:
```bash
echo $GEMINI_API_KEY
echo $QDRANT_API_KEY
```

#### 3. Qdrant Connection Issues
**Problem**: `ConnectionError` when connecting to Qdrant

**Solution**: Check if Qdrant is running:
```bash
curl http://localhost:6333/collections
```

#### 4. Memory Issues
**Problem**: `OutOfMemoryError` during embedding generation

**Solution**: Reduce batch size or use smaller models:
```env
VECTOR_SIZE=384  # Instead of 768
```

### Getting Help

1. **Check Logs**: Look for detailed error messages in console output
2. **Verify Configuration**: Ensure all environment variables are set correctly
3. **Test Individual Services**: Run service-specific tests
4. **Check Documentation**: Review [[API Reference]] and [[Configuration Guide]]

## Next Steps

After successful installation:

1. **Read the Documentation**: Start with [[Project Overview]]
2. **Run Examples**: Try the [[Basic Usage Example]]
3. **Explore Features**: Check out [[Feature Guide]]
4. **Start Developing**: Follow the [[Development Guide]]

## Related Documentation

- [[Configuration Guide]]
- [[Development Guide]]
- [[API Reference]]
- [[Troubleshooting Guide]]