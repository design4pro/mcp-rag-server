---
title: MCP Prompts Implementation - Code Analysis and Review
type: note
permalink: docs/03-api/mcp-prompts-implementation-code-analysis-and-review
---

# MCP Prompts Implementation - Code Analysis and Review

## Overview

MCP RAG Server now includes comprehensive MCP Prompts functionality as specified in the [Model Context Protocol specification](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts). This enables rapid code analysis, code review, and other development tasks through structured prompt templates.

## 🚀 Features

### ✅ Implemented Capabilities

1. **MCP Prompts Protocol Compliance**
   - Full implementation of `prompts/list` and `prompts/get` methods
   - Support for `listChanged` capability
   - Proper argument validation and substitution
   - Error handling according to MCP specification

2. **Code Analysis Engine**
   - **Language Detection**: Automatic detection of Python, JavaScript, Java, Rust, Go, TypeScript
   - **AST Analysis**: Deep parsing of Python code structure
   - **Complexity Metrics**: Function/class counting, import analysis
   - **Structural Analysis**: Function signatures, class methods, dependencies

3. **Pre-built Prompt Templates**
   - **Code Review**: Comprehensive code quality assessment
   - **Code Analysis**: Structure and architecture analysis
   - **Architecture Review**: Design patterns and scalability
   - **Security Audit**: Vulnerability and security analysis
   - **Performance Analysis**: Optimization opportunities
   - **Documentation Generation**: API and user documentation
   - **Test Generation**: Comprehensive test case creation
   - **Refactoring Suggestions**: Code improvement recommendations

## 📋 Available Prompts

### 1. `code_review`
**Purpose**: Analyze code quality and suggest improvements
**Arguments**:
- `code` (required): The code to review
- `language` (optional): Programming language (auto-detected if "auto")
- `focus_areas` (optional): Areas to focus on (security, performance, style)
- `severity` (optional): Review severity (light, medium, strict)

### 2. `code_analysis`
**Purpose**: Analyze code structure, complexity, and architecture
**Arguments**:
- `code` (required): The code to analyze
- `language` (optional): Programming language
- `include_metrics` (optional): Include complexity metrics
- `include_suggestions` (optional): Include improvement suggestions

### 3. `architecture_review`
**Purpose**: Review software architecture and design patterns
**Arguments**:
- `code` (required): The code to review
- `context` (optional): Additional project context
- `scale` (optional): Project scale (small, medium, large)

### 4. `security_audit`
**Purpose**: Perform security analysis of code
**Arguments**:
- `code` (required): The code to audit
- `language` (optional): Programming language
- `context` (optional): Security context (web, mobile, desktop)

### 5. `performance_analysis`
**Purpose**: Analyze code performance and optimization opportunities
**Arguments**:
- `code` (required): The code to analyze
- `language` (optional): Programming language
- `use_case` (optional): Performance use case (cpu, memory, io, network)

### 6. `documentation_generation`
**Purpose**: Generate comprehensive documentation for code
**Arguments**:
- `code` (required): The code to document
- `language` (optional): Programming language
- `doc_type` (optional): Documentation type (api, user, developer)
- `format` (optional): Output format (markdown, html, text)

### 7. `test_generation`
**Purpose**: Generate comprehensive test cases for code
**Arguments**:
- `code` (required): The code to test
- `language` (optional): Programming language
- `test_framework` (optional): Test framework preference
- `coverage` (optional): Test coverage level (basic, comprehensive, exhaustive)

### 8. `refactoring_suggestions`
**Purpose**: Suggest code refactoring improvements
**Arguments**:
- `code` (required): The code to refactor
- `language` (optional): Programming language
- `goals` (optional): Refactoring goals (readability, performance, maintainability)
- `constraints` (optional): Refactoring constraints

## 🔧 Configuration

### Environment Variables

```bash
# Enable/disable prompts functionality
MCP_PROMPTS_ENABLED=true

# Prompt management settings
MCP_PROMPTS_MAX_PROMPTS_PER_USER=50
MCP_PROMPTS_MAX_PROMPT_LENGTH=10000
MCP_PROMPTS_ENABLE_CUSTOM_PROMPTS=true

# Code analysis settings
MCP_PROMPTS_ENABLE_CODE_ANALYSIS=true
MCP_PROMPTS_MAX_CODE_SIZE=50000
```

### Configuration Class

```python
class PromptsConfig(BaseSettings):
    enabled: bool = Field(default=True, env="MCP_PROMPTS_ENABLED")
    max_prompts_per_user: int = Field(default=50)
    max_prompt_length: int = Field(default=10000)
    enable_custom_prompts: bool = Field(default=True)
    enable_code_analysis: bool = Field(default=True)
    supported_languages: list = Field(default=["python", "javascript", "java", "rust", "go", "typescript"])
    max_code_size: int = Field(default=50000)
```

## 🛠️ Usage Examples

### Using MCP Prompts in Cursor IDE

1. **List Available Prompts**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "prompts/list"
   }
   ```

2. **Get Code Review Prompt**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 2,
     "method": "prompts/get",
     "params": {
       "name": "code_review",
       "arguments": {
         "code": "def hello():\n    print('world')",
         "language": "auto",
         "focus_areas": "security",
         "severity": "strict"
       }
     }
   }
   ```

### Programmatic Usage

```python
from src.mcp_rag_server.services.prompts_service import PromptsService

# Initialize service
prompts_service = PromptsService()

# List available prompts
prompts = prompts_service.list_prompts()

# Get a specific prompt with arguments
result = prompts_service.get_prompt("code_review", {
    "code": "def hello(): print('Hello')",
    "language": "python",
    "focus_areas": "security",
    "severity": "strict"
})

# Get code analysis
analysis = prompts_service.get_prompt_analysis("code_review", code)
```

## 🔍 Code Analysis Capabilities

### Language Detection
- **Python**: Detects `def`, `import`, `class` patterns
- **JavaScript**: Detects `function`, `const/let/var` patterns
- **Java**: Detects `public class`, `import java` patterns
- **Rust**: Detects `fn`, `use` patterns
- **Go**: Detects `func`, `import` patterns
- **TypeScript**: Detects TypeScript-specific patterns

### Python AST Analysis
- **Functions**: Name, arguments, line numbers, docstrings
- **Classes**: Name, methods, line numbers, docstrings
- **Imports**: All import statements and modules
- **Variables**: Variable assignments and names
- **Complexity**: Function and class count metrics

### Analysis Output
```json
{
  "functions": [
    {
      "name": "calculate_sum",
      "args": ["a", "b"],
      "lineno": 2,
      "docstring": "Calculate sum of two numbers"
    }
  ],
  "classes": [
    {
      "name": "Calculator",
      "methods": ["add", "multiply"],
      "lineno": 6,
      "docstring": "Simple calculator class"
    }
  ],
  "imports": ["os", "typing.List", "numpy.np"],
  "variables": ["result", "data"],
  "complexity": 3,
  "lines": 15,
  "characters": 450
}
```

## 🧪 Testing

Comprehensive test coverage includes:

- **CodeAnalyzer Tests**: Language detection and AST analysis
- **PromptsService Tests**: Prompt management and argument substitution
- **Data Structure Tests**: Prompt, PromptArgument, PromptMessage validation
- **Integration Tests**: Full MCP protocol compliance

Run tests with:
```bash
python -m pytest tests/unit/test_prompts_service.py -v
```

## 🔄 Integration with MCP RAG Server

### Server Registration
```python
def _register_prompts(self):
    """Register MCP prompts functionality."""
    self.prompts_service = PromptsService()
    
    @self.mcp.prompts.list
    async def list_prompts(cursor: str = None) -> dict:
        return self.prompts_service.list_prompts(cursor)
    
    @self.mcp.prompts.get
    async def get_prompt(name: str, arguments: dict = None) -> dict:
        return self.prompts_service.get_prompt(name, arguments)
```

### Health Check Integration
```python
def health_check() -> dict:
    return {
        "status": "healthy",
        "services": {
            # ... other services
            "prompts": self.prompts_service is not None
        }
    }
```

## 🚀 Benefits

1. **Rapid Development**: Quick access to code analysis and review
2. **Consistent Quality**: Standardized prompt templates for common tasks
3. **Language Agnostic**: Support for multiple programming languages
4. **Extensible**: Easy to add custom prompts and templates
5. **MCP Compliant**: Full compliance with Model Context Protocol
6. **Integration Ready**: Seamless integration with Cursor IDE and other MCP clients

## 📈 Future Enhancements

1. **Advanced Code Analysis**: Support for more languages and frameworks
2. **Custom Prompt Templates**: User-defined prompt templates
3. **Prompt Versioning**: Version control for prompt templates
4. **Performance Optimization**: Caching and optimization for large codebases
5. **Integration with RAG**: Combine prompts with document search and memory
6. **Real-time Analysis**: Live code analysis during development

## 🔗 Related Documentation

- **MCP Specification**: [Model Context Protocol Prompts](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts)
- **API Reference**: [[docs/03-api/api-reference]]
- **Installation Guide**: [[docs/02-installation/installation-guide]]
- **Development Phases**: [[docs/04-development/phases/development-phases-overview]]