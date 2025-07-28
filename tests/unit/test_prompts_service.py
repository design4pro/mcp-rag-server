"""
Unit tests for PromptsService.

This module tests the MCP Prompts functionality including prompt management,
code analysis, and argument substitution.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Set up environment variables for testing to avoid config validation errors
os.environ.setdefault("MCP_GEMINI_API_KEY", "test_api_key_for_testing")
os.environ.setdefault("MCP_QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("MCP_MEM0_STORAGE_PATH", "/tmp/test_mem0")
os.environ.setdefault("MCP_COLLECTION", "test_collection")
os.environ.setdefault("MCP_PROJECT_NAMESPACE", "test_namespace")
os.environ.setdefault("MCP_USER_ID", "test_user")
os.environ.setdefault("MCP_SERVER_PORT", "8000")
os.environ.setdefault("MCP_LOG_LEVEL", "INFO")

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the prompts service directly without importing config
from mcp_rag_server.services.prompts_service import (
    PromptsService, Prompt, PromptArgument, PromptMessage, PromptType, CodeAnalyzer
)


class TestCodeAnalyzer:
    """Test the CodeAnalyzer helper class."""
    
    def test_analyze_python_code_simple(self):
        """Test analyzing simple Python code."""
        code = """
def hello_world():
    print("Hello, World!")

class Calculator:
    def add(self, a, b):
        return a + b
"""
        analysis = CodeAnalyzer.analyze_python_code(code)
        
        assert "functions" in analysis
        assert "classes" in analysis
        assert "imports" in analysis
        assert "variables" in analysis
        assert "complexity" in analysis
        assert "lines" in analysis
        assert "characters" in analysis
        
        # The analyzer finds both the standalone function and the method in the class
        assert len(analysis["functions"]) == 2  # hello_world + add method
        assert analysis["functions"][0]["name"] == "hello_world"
        assert analysis["functions"][1]["name"] == "add"
        
        assert len(analysis["classes"]) == 1
        assert analysis["classes"][0]["name"] == "Calculator"
        assert "add" in analysis["classes"][0]["methods"]
        
        assert analysis["complexity"] == 3  # 2 functions + 1 class
    
    def test_analyze_python_code_with_imports(self):
        """Test analyzing Python code with imports."""
        code = """
import os
from typing import List, Dict
import numpy as np

def process_data(data: List[Dict]) -> List[Dict]:
    return [item for item in data if item.get('active')]
"""
        analysis = CodeAnalyzer.analyze_python_code(code)
        
        assert "os" in analysis["imports"]
        assert "typing.List" in analysis["imports"]
        assert "typing.Dict" in analysis["imports"]
        assert "numpy" in analysis["imports"]  # The implementation stores just "numpy", not "numpy.np"
        
        assert len(analysis["functions"]) == 1
        assert analysis["functions"][0]["name"] == "process_data"
    
    def test_analyze_python_code_invalid(self):
        """Test analyzing invalid Python code."""
        code = "def invalid syntax {"
        analysis = CodeAnalyzer.analyze_python_code(code)
        
        assert "error" in analysis
        assert isinstance(analysis["error"], str)
    
    def test_detect_language_python(self):
        """Test Python language detection."""
        code = """
def hello():
    print("Hello")
import os
"""
        language = CodeAnalyzer.detect_language(code)
        assert language == "python"
    
    def test_detect_language_javascript(self):
        """Test JavaScript language detection."""
        code = """
function hello() {
    console.log("Hello");
}
const x = 1;
"""
        language = CodeAnalyzer.detect_language(code)
        assert language == "javascript"
    
    def test_detect_language_java(self):
        """Test Java language detection."""
        code = """
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
import java.util.List;
"""
        language = CodeAnalyzer.detect_language(code)
        assert language == "java"
    
    def test_detect_language_rust(self):
        """Test Rust language detection."""
        code = """
fn hello() {
    println!("Hello");
}
use std::collections::HashMap;
"""
        language = CodeAnalyzer.detect_language(code)
        assert language == "rust"
    
    def test_detect_language_unknown(self):
        """Test unknown language detection."""
        code = "This is not code"
        language = CodeAnalyzer.detect_language(code)
        assert language == "unknown"


class TestPromptsService:
    """Test the PromptsService class."""
    
    @pytest.fixture
    def prompts_service(self):
        """Create a PromptsService instance for testing."""
        return PromptsService()
    
    def test_initialization(self, prompts_service):
        """Test service initialization."""
        assert prompts_service.prompts is not None
        assert len(prompts_service.prompts) > 0
        assert "code_review" in prompts_service.prompts
        assert "code_analysis" in prompts_service.prompts
        assert "architecture_review" in prompts_service.prompts
    
    def test_list_prompts(self, prompts_service):
        """Test listing prompts."""
        result = prompts_service.list_prompts()
        
        assert "prompts" in result
        assert "nextCursor" in result
        assert isinstance(result["prompts"], list)
        assert len(result["prompts"]) > 0
        
        # Check structure of first prompt
        first_prompt = result["prompts"][0]
        assert "name" in first_prompt
        assert "title" in first_prompt
        assert "description" in first_prompt
        assert "arguments" in first_prompt
        assert isinstance(first_prompt["arguments"], list)
    
    def test_get_prompt_existing(self, prompts_service):
        """Test getting an existing prompt."""
        # Provide required arguments for the code_review prompt
        arguments = {
            "code": "def test(): pass",
            "language": "python",
            "focus_areas": "all",
            "severity": "medium"
        }
        result = prompts_service.get_prompt("code_review", arguments)
        
        assert "description" in result
        assert "messages" in result
        assert isinstance(result["messages"], list)
        assert len(result["messages"]) > 0
        
        # Check message structure
        first_message = result["messages"][0]
        assert "role" in first_message
        assert "content" in first_message
        assert first_message["role"] == "user"
    
    def test_get_prompt_nonexistent(self, prompts_service):
        """Test getting a non-existent prompt."""
        with pytest.raises(ValueError, match="Prompt 'nonexistent' not found"):
            prompts_service.get_prompt("nonexistent")
    
    def test_get_prompt_with_arguments(self, prompts_service):
        """Test getting a prompt with argument substitution."""
        arguments = {
            "code": "def hello(): print('Hello')",
            "language": "python",
            "focus_areas": "security",
            "severity": "strict"
        }
        
        result = prompts_service.get_prompt("code_review", arguments)
        
        assert "messages" in result
        assert len(result["messages"]) > 0
        
        # Check that arguments were substituted
        message_content = result["messages"][0]["content"]["text"]
        assert "python" in message_content
        assert "def hello(): print('Hello')" in message_content
        assert "security" in message_content
        assert "strict" in message_content
    
    def test_get_prompt_with_auto_language_detection(self, prompts_service):
        """Test getting a prompt with auto language detection."""
        arguments = {
            "code": "def hello(): print('Hello')",
            "language": "auto"
        }
        
        result = prompts_service.get_prompt("code_review", arguments)
        
        assert "messages" in result
        message_content = result["messages"][0]["content"]["text"]
        # When language is "auto", it should be replaced with the detected language
        # The implementation should detect Python and replace "auto" with "python"
        assert "python" in message_content  # Should detect Python and replace "auto"
    
    def test_get_prompt_missing_required_argument(self, prompts_service):
        """Test getting a prompt with missing required arguments."""
        arguments = {
            "language": "python"  # Missing required "code" argument
        }
        
        with pytest.raises(ValueError, match="Required argument 'code' not provided"):
            prompts_service.get_prompt("code_review", arguments)
    
    def test_add_custom_prompt(self, prompts_service):
        """Test adding a custom prompt."""
        custom_prompt = Prompt(
            name="custom_test",
            title="Custom Test Prompt",
            description="A custom test prompt",
            arguments=[
                PromptArgument("input", "Test input", True, "string")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Test prompt with {input}"
                })
            ],
            prompt_type=PromptType.CODE_REVIEW
        )
        
        prompts_service.add_custom_prompt(custom_prompt)
        
        assert "custom_test" in prompts_service.prompts
        result = prompts_service.get_prompt("custom_test", {"input": "test_value"})
        assert "test_value" in result["messages"][0]["content"]["text"]
    
    def test_remove_prompt(self, prompts_service):
        """Test removing a prompt."""
        # First add a custom prompt
        custom_prompt = Prompt(
            name="to_remove",
            title="To Remove",
            description="A prompt to remove",
            arguments=[],
            messages=[],
            prompt_type=PromptType.CODE_REVIEW
        )
        prompts_service.add_custom_prompt(custom_prompt)
        
        # Then remove it
        prompts_service.remove_prompt("to_remove")
        
        assert "to_remove" not in prompts_service.prompts
    
    def test_remove_nonexistent_prompt(self, prompts_service):
        """Test removing a non-existent prompt."""
        with pytest.raises(ValueError, match="Prompt 'nonexistent' not found"):
            prompts_service.remove_prompt("nonexistent")
    
    def test_get_prompt_analysis(self, prompts_service):
        """Test getting prompt analysis."""
        code = """
def calculate_sum(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
        
        analysis = prompts_service.get_prompt_analysis("code_review", code)
        
        assert "code_structure" in analysis
        assert "language" in analysis
        # The language detection should work correctly for this Python code
        assert analysis["language"] == "python"
        
        code_structure = analysis["code_structure"]
        assert "functions" in code_structure
        assert "classes" in code_structure
        assert len(code_structure["functions"]) == 2  # calculate_sum + multiply method
        assert len(code_structure["classes"]) == 1
    
    def test_get_prompt_analysis_nonexistent_prompt(self, prompts_service):
        """Test getting analysis for non-existent prompt."""
        with pytest.raises(ValueError, match="Prompt 'nonexistent' not found"):
            prompts_service.get_prompt_analysis("nonexistent", "code")
    
    def test_prompt_types_coverage(self, prompts_service):
        """Test that all prompt types are covered."""
        expected_prompts = [
            "code_review",
            "code_analysis",
            "architecture_review",
            "security_audit",
            "performance_analysis",
            "documentation_generation",
            "test_generation",
            "refactoring_suggestions"
        ]
        
        for prompt_name in expected_prompts:
            assert prompt_name in prompts_service.prompts
            prompt = prompts_service.prompts[prompt_name]
            assert isinstance(prompt, Prompt)
            assert prompt.name == prompt_name
            assert len(prompt.arguments) > 0
            assert len(prompt.messages) > 0
    
    def test_prompt_argument_validation(self, prompts_service):
        """Test prompt argument validation."""
        # Test with valid arguments
        valid_args = {
            "code": "def test(): pass",
            "language": "python"
        }
        
        result = prompts_service.get_prompt("code_review", valid_args)
        assert result is not None
        
        # Test with invalid argument types
        invalid_args = {
            "code": 123,  # Should be string
            "language": "python"
        }
        
        # Should still work as we convert to string
        result = prompts_service.get_prompt("code_review", invalid_args)
        assert result is not None
    
    def test_prompt_message_structure(self, prompts_service):
        """Test prompt message structure."""
        # Provide required arguments for the code_review prompt
        arguments = {
            "code": "def test(): pass",
            "language": "python",
            "focus_areas": "all",
            "severity": "medium"
        }
        result = prompts_service.get_prompt("code_review", arguments)
        
        for message in result["messages"]:
            assert "role" in message
            assert "content" in message
            assert message["role"] in ["user", "assistant"]
            
            content = message["content"]
            assert "type" in content
            assert content["type"] == "text"
            assert "text" in content


class TestPromptDataStructures:
    """Test the data structures used by prompts."""
    
    def test_prompt_argument_creation(self):
        """Test PromptArgument creation."""
        arg = PromptArgument(
            name="test_arg",
            description="Test argument",
            required=True,
            type="string",
            default="default_value"
        )
        
        assert arg.name == "test_arg"
        assert arg.description == "Test argument"
        assert arg.required is True
        assert arg.type == "string"
        assert arg.default == "default_value"
    
    def test_prompt_message_creation(self):
        """Test PromptMessage creation."""
        content = {
            "type": "text",
            "text": "Test message"
        }
        
        message = PromptMessage("user", content)
        
        assert message.role == "user"
        assert message.content == content
    
    def test_prompt_creation(self):
        """Test Prompt creation."""
        arguments = [
            PromptArgument("input", "Input parameter", True, "string")
        ]
        
        messages = [
            PromptMessage("user", {
                "type": "text",
                "text": "Test prompt with {input}"
            })
        ]
        
        prompt = Prompt(
            name="test_prompt",
            title="Test Prompt",
            description="A test prompt",
            arguments=arguments,
            messages=messages,
            prompt_type=PromptType.CODE_REVIEW
        )
        
        assert prompt.name == "test_prompt"
        assert prompt.title == "Test Prompt"
        assert prompt.description == "A test prompt"
        assert len(prompt.arguments) == 1
        assert len(prompt.messages) == 1
        assert prompt.prompt_type == PromptType.CODE_REVIEW


if __name__ == "__main__":
    pytest.main([__file__]) 