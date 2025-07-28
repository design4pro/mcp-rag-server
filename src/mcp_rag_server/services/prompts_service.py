"""
MCP Prompts Service for Code Analysis and Code Review.

This service implements MCP Prompts functionality as specified in the Model Context Protocol,
providing structured prompt templates for code analysis, code review, and other development tasks.
"""

import logging
import json
import ast
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of prompts supported by the service."""
    CODE_REVIEW = "code_review"
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_REVIEW = "architecture_review"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    DOCUMENTATION_GENERATION = "documentation_generation"
    TEST_GENERATION = "test_generation"
    REFACTORING_SUGGESTIONS = "refactoring_suggestions"


@dataclass
class PromptArgument:
    """Represents a prompt argument."""
    name: str
    description: str
    required: bool = False
    type: str = "string"
    default: Optional[Any] = None


@dataclass
class PromptMessage:
    """Represents a message in a prompt."""
    role: str  # "user" or "assistant"
    content: Dict[str, Any]  # Content with type and text/data


@dataclass
class Prompt:
    """Represents a prompt definition."""
    name: str
    title: str
    description: str
    arguments: List[PromptArgument]
    messages: List[PromptMessage]
    prompt_type: PromptType


class CodeAnalyzer:
    """Helper class for analyzing code structure."""
    
    @staticmethod
    def analyze_python_code(code: str) -> Dict[str, Any]:
        """Analyze Python code and extract structural information."""
        try:
            tree = ast.parse(code)
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "variables": [],
                "complexity": 0,
                "lines": len(code.split('\n')),
                "characters": len(code)
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "lineno": node.lineno,
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "lineno": node.lineno,
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis["imports"].append(f"{module}.{alias.name}")
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis["variables"].append(target.id)
            
            # Calculate complexity (simple metric)
            analysis["complexity"] = len(analysis["functions"]) + len(analysis["classes"])
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing Python code: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def detect_language(code: str) -> str:
        """Detect programming language from code."""
        # Simple heuristics for language detection
        if re.search(r'def\s+\w+\s*\(', code):
            return "python"
        elif re.search(r'function\s+\w+\s*\(', code) and re.search(r'const\s+|let\s+|var\s+', code):
            return "javascript"
        elif re.search(r'public\s+class\s+\w+', code) and re.search(r'import\s+java', code):
            return "java"
        elif re.search(r'fn\s+\w+\s*\(', code) and re.search(r'use\s+\w+', code):
            return "rust"
        else:
            return "unknown"


class PromptsService:
    """Service for managing MCP Prompts."""
    
    def __init__(self):
        """Initialize the prompts service."""
        self.prompts: Dict[str, Prompt] = {}
        self.code_analyzer = CodeAnalyzer()
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize default prompts."""
        self._add_code_review_prompt()
        self._add_code_analysis_prompt()
        self._add_architecture_review_prompt()
        self._add_security_audit_prompt()
        self._add_performance_analysis_prompt()
        self._add_documentation_generation_prompt()
        self._add_test_generation_prompt()
        self._add_refactoring_suggestions_prompt()
    
    def _add_code_review_prompt(self):
        """Add code review prompt."""
        prompt = Prompt(
            name="code_review",
            title="Request Code Review",
            description="Analyze code quality and suggest improvements",
            arguments=[
                PromptArgument("code", "The code to review", True, "string"),
                PromptArgument("language", "Programming language", False, "string", "auto"),
                PromptArgument("focus_areas", "Areas to focus on (security, performance, style)", False, "string", "all"),
                PromptArgument("severity", "Review severity (light, medium, strict)", False, "string", "medium")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please perform a comprehensive code review of the following {language} code:\n\n```{language}\n{code}\n```\n\nFocus areas: {focus_areas}\nSeverity level: {severity}\n\nPlease provide:\n1. Code quality assessment\n2. Potential issues and bugs\n3. Security concerns\n4. Performance considerations\n5. Style and best practices\n6. Specific improvement suggestions"
                })
            ],
            prompt_type=PromptType.CODE_REVIEW
        )
        self.prompts["code_review"] = prompt
    
    def _add_code_analysis_prompt(self):
        """Add code analysis prompt."""
        prompt = Prompt(
            name="code_analysis",
            title="Code Structure Analysis",
            description="Analyze code structure, complexity, and architecture",
            arguments=[
                PromptArgument("code", "The code to analyze", True, "string"),
                PromptArgument("language", "Programming language", False, "string", "auto"),
                PromptArgument("include_metrics", "Include complexity metrics", False, "boolean", True),
                PromptArgument("include_suggestions", "Include improvement suggestions", False, "boolean", True)
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please analyze the structure and architecture of the following {language} code:\n\n```{language}\n{code}\n```\n\nPlease provide:\n1. Code structure overview\n2. Function and class analysis\n3. Dependencies and imports\n4. Complexity assessment\n5. Architecture patterns identified\n6. Potential refactoring opportunities\n7. Best practices compliance"
                })
            ],
            prompt_type=PromptType.CODE_ANALYSIS
        )
        self.prompts["code_analysis"] = prompt
    
    def _add_architecture_review_prompt(self):
        """Add architecture review prompt."""
        prompt = Prompt(
            name="architecture_review",
            title="Architecture Review",
            description="Review software architecture and design patterns",
            arguments=[
                PromptArgument("code", "The code to review", True, "string"),
                PromptArgument("context", "Additional context about the project", False, "string", ""),
                PromptArgument("scale", "Project scale (small, medium, large)", False, "string", "medium")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please review the architecture and design of the following code:\n\n```\n{code}\n```\n\nProject context: {context}\nProject scale: {scale}\n\nPlease provide:\n1. Architecture assessment\n2. Design patterns identified\n3. Scalability considerations\n4. Maintainability analysis\n5. Separation of concerns\n6. Potential architectural improvements\n7. Technology stack recommendations"
                })
            ],
            prompt_type=PromptType.ARCHITECTURE_REVIEW
        )
        self.prompts["architecture_review"] = prompt
    
    def _add_security_audit_prompt(self):
        """Add security audit prompt."""
        prompt = Prompt(
            name="security_audit",
            title="Security Code Audit",
            description="Perform security analysis of code",
            arguments=[
                PromptArgument("code", "The code to audit", True, "string"),
                PromptArgument("language", "Programming language", False, "string", "auto"),
                PromptArgument("context", "Security context (web, mobile, desktop)", False, "string", "web")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please perform a security audit of the following {language} code:\n\n```{language}\n{code}\n```\n\nContext: {context}\n\nPlease provide:\n1. Security vulnerabilities identified\n2. Input validation issues\n3. Authentication and authorization concerns\n4. Data protection issues\n5. Common security anti-patterns\n6. Security best practices recommendations\n7. Risk assessment and mitigation strategies"
                })
            ],
            prompt_type=PromptType.SECURITY_AUDIT
        )
        self.prompts["security_audit"] = prompt
    
    def _add_performance_analysis_prompt(self):
        """Add performance analysis prompt."""
        prompt = Prompt(
            name="performance_analysis",
            title="Performance Analysis",
            description="Analyze code performance and optimization opportunities",
            arguments=[
                PromptArgument("code", "The code to analyze", True, "string"),
                PromptArgument("language", "Programming language", False, "string", "auto"),
                PromptArgument("use_case", "Performance use case (cpu, memory, io, network)", False, "string", "general")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please analyze the performance characteristics of the following {language} code:\n\n```{language}\n{code}\n```\n\nUse case: {use_case}\n\nPlease provide:\n1. Performance bottlenecks identified\n2. Time complexity analysis\n3. Space complexity analysis\n4. I/O operations analysis\n5. Memory usage patterns\n6. Optimization opportunities\n7. Performance best practices recommendations"
                })
            ],
            prompt_type=PromptType.PERFORMANCE_ANALYSIS
        )
        self.prompts["performance_analysis"] = prompt
    
    def _add_documentation_generation_prompt(self):
        """Add documentation generation prompt."""
        prompt = Prompt(
            name="documentation_generation",
            title="Generate Code Documentation",
            description="Generate comprehensive documentation for code",
            arguments=[
                PromptArgument("code", "The code to document", True, "string"),
                PromptArgument("language", "Programming language", False, "string", "auto"),
                PromptArgument("doc_type", "Documentation type (api, user, developer)", False, "string", "api"),
                PromptArgument("format", "Output format (markdown, html, text)", False, "string", "markdown")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please generate comprehensive {doc_type} documentation for the following {language} code:\n\n```{language}\n{code}\n```\n\nFormat: {format}\n\nPlease provide:\n1. Function/class documentation\n2. Parameter descriptions\n3. Return value documentation\n4. Usage examples\n5. Edge cases and error handling\n6. Dependencies and requirements\n7. Installation and setup instructions"
                })
            ],
            prompt_type=PromptType.DOCUMENTATION_GENERATION
        )
        self.prompts["documentation_generation"] = prompt
    
    def _add_test_generation_prompt(self):
        """Add test generation prompt."""
        prompt = Prompt(
            name="test_generation",
            title="Generate Test Cases",
            description="Generate comprehensive test cases for code",
            arguments=[
                PromptArgument("code", "The code to test", True, "string"),
                PromptArgument("language", "Programming language", False, "string", "auto"),
                PromptArgument("test_framework", "Test framework preference", False, "string", "default"),
                PromptArgument("coverage", "Test coverage level (basic, comprehensive, exhaustive)", False, "string", "comprehensive")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please generate comprehensive test cases for the following {language} code:\n\n```{language}\n{code}\n```\n\nTest framework: {test_framework}\nCoverage level: {coverage}\n\nPlease provide:\n1. Unit tests for all functions/methods\n2. Edge case testing\n3. Error condition testing\n4. Integration test scenarios\n5. Mock/stub examples\n6. Test data generation\n7. Test execution instructions"
                })
            ],
            prompt_type=PromptType.TEST_GENERATION
        )
        self.prompts["test_generation"] = prompt
    
    def _add_refactoring_suggestions_prompt(self):
        """Add refactoring suggestions prompt."""
        prompt = Prompt(
            name="refactoring_suggestions",
            title="Refactoring Suggestions",
            description="Suggest code refactoring improvements",
            arguments=[
                PromptArgument("code", "The code to refactor", True, "string"),
                PromptArgument("language", "Programming language", False, "string", "auto"),
                PromptArgument("goals", "Refactoring goals (readability, performance, maintainability)", False, "string", "all"),
                PromptArgument("constraints", "Refactoring constraints", False, "string", "none")
            ],
            messages=[
                PromptMessage("user", {
                    "type": "text",
                    "text": "Please suggest refactoring improvements for the following {language} code:\n\n```{language}\n{code}\n```\n\nGoals: {goals}\nConstraints: {constraints}\n\nPlease provide:\n1. Code smell identification\n2. Refactoring opportunities\n3. Specific refactoring techniques\n4. Before/after code examples\n5. Impact assessment\n6. Implementation steps\n7. Testing considerations"
                })
            ],
            prompt_type=PromptType.REFACTORING_SUGGESTIONS
        )
        self.prompts["refactoring_suggestions"] = prompt
    
    def list_prompts(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        """List available prompts with pagination support."""
        try:
            prompts_list = []
            for prompt in self.prompts.values():
                prompt_dict = {
                    "name": prompt.name,
                    "title": prompt.title,
                    "description": prompt.description,
                    "arguments": [
                        {
                            "name": arg.name,
                            "description": arg.description,
                            "required": arg.required,
                            "type": arg.type,
                            "default": arg.default
                        }
                        for arg in prompt.arguments
                    ]
                }
                prompts_list.append(prompt_dict)
            
            # Simple pagination (in a real implementation, you'd use the cursor)
            return {
                "prompts": prompts_list,
                "nextCursor": None  # No pagination for now
            }
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            raise
    
    def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a specific prompt with optional argument substitution."""
        try:
            if name not in self.prompts:
                raise ValueError(f"Prompt '{name}' not found")
            
            prompt = self.prompts[name]
            arguments = arguments or {}
            
            # Validate required arguments
            for arg in prompt.arguments:
                if arg.required and arg.name not in arguments:
                    raise ValueError(f"Required argument '{arg.name}' not provided")
            
            # Substitute arguments in messages
            messages = []
            for msg in prompt.messages:
                content = msg.content.copy()
                if content["type"] == "text":
                    # Simple string substitution
                    text = content["text"]
                    
                    # Handle special cases first (before regular substitution)
                    if "language" in arguments and arguments["language"] == "auto":
                        # Auto-detect language
                        detected_lang = self.code_analyzer.detect_language(arguments.get("code", ""))
                        # Replace all occurrences of {language} with the detected language
                        text = text.replace("{language}", detected_lang)
                    
                    # Regular argument substitution
                    for arg_name, arg_value in arguments.items():
                        placeholder = "{" + arg_name + "}"
                        if placeholder in text:
                            text = text.replace(placeholder, str(arg_value))
                    
                    content["text"] = text
                
                messages.append({
                    "role": msg.role,
                    "content": content
                })
            
            return {
                "description": prompt.description,
                "messages": messages
            }
        except Exception as e:
            logger.error(f"Error getting prompt '{name}': {e}")
            raise
    
    def add_custom_prompt(self, prompt: Prompt) -> None:
        """Add a custom prompt to the service."""
        try:
            self.prompts[prompt.name] = prompt
            logger.info(f"Added custom prompt: {prompt.name}")
        except Exception as e:
            logger.error(f"Error adding custom prompt: {e}")
            raise
    
    def remove_prompt(self, name: str) -> None:
        """Remove a prompt from the service."""
        try:
            if name in self.prompts:
                del self.prompts[name]
                logger.info(f"Removed prompt: {name}")
            else:
                raise ValueError(f"Prompt '{name}' not found")
        except Exception as e:
            logger.error(f"Error removing prompt: {e}")
            raise
    
    def get_prompt_analysis(self, name: str, code: str) -> Dict[str, Any]:
        """Get additional analysis for a prompt based on code."""
        try:
            if name not in self.prompts:
                raise ValueError(f"Prompt '{name}' not found")
            
            prompt = self.prompts[name]
            analysis = {}
            
            # Add code analysis for relevant prompts
            if prompt.prompt_type in [PromptType.CODE_REVIEW, PromptType.CODE_ANALYSIS, 
                                    PromptType.PERFORMANCE_ANALYSIS, PromptType.REFACTORING_SUGGESTIONS]:
                analysis["code_structure"] = self.code_analyzer.analyze_python_code(code)
                analysis["language"] = self.code_analyzer.detect_language(code)
            
            return analysis
        except Exception as e:
            logger.error(f"Error getting prompt analysis: {e}")
            raise 