"""
MCP Tools for Code Analysis.

This module provides MCP tools for analyzing source code, extracting structural information,
and calculating code metrics.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from mcp import StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    ReadResourceRequest,
    ReadResourceResult,
    ListResourcesRequest,
    ListResourcesResult,
)

from ..services.code_analysis_service import CodeAnalysisService

logger = logging.getLogger(__name__)


class CodeAnalysisTools:
    """MCP Tools for code analysis functionality."""
    
    def __init__(self, code_analysis_service: CodeAnalysisService):
        """Initialize code analysis tools."""
        self.code_analysis_service = code_analysis_service
    
    def get_tools(self) -> List[Tool]:
        """Get list of available code analysis tools."""
        return [
            Tool(
                name="analyze_source_code",
                description="Analyze source code file and extract structural information including functions, classes, imports, and metrics.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the source code file to analyze"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (auto-detected if not specified)",
                            "enum": ["auto", "python", "javascript", "java", "rust", "go"]
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="analyze_code_string",
                description="Analyze code string and extract structural information.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Source code string to analyze"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "enum": ["python", "javascript", "java", "rust", "go"]
                        }
                    },
                    "required": ["code", "language"]
                }
            ),
            Tool(
                name="calculate_code_metrics",
                description="Calculate comprehensive code metrics including complexity, maintainability, and quality indicators.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the source code file"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (auto-detected if not specified)",
                            "enum": ["auto", "python", "javascript", "java", "rust", "go"]
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="extract_functions",
                description="Extract function definitions and their metadata from source code.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the source code file"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (auto-detected if not specified)",
                            "enum": ["auto", "python", "javascript", "java", "rust", "go"]
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="extract_classes",
                description="Extract class definitions and their relationships from source code.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the source code file"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (auto-detected if not specified)",
                            "enum": ["auto", "python", "javascript", "java", "rust", "go"]
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="analyze_dependencies",
                description="Analyze import statements and dependencies in source code.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the source code file"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (auto-detected if not specified)",
                            "enum": ["auto", "python", "javascript", "java", "rust", "go"]
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="detect_code_patterns",
                description="Detect common coding patterns and anti-patterns in source code.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the source code file"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (auto-detected if not specified)",
                            "enum": ["auto", "python", "javascript", "java", "rust", "go"]
                        }
                    },
                    "required": ["file_path"]
                }
            )
        ]
    
    async def handle_analyze_source_code(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle analyze_source_code tool call."""
        try:
            file_path = arguments["file_path"]
            language = arguments.get("language", "auto")
            
            result = await self.code_analysis_service.analyze_source_code(file_path, language)
            
            if "error" in result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error analyzing source code: {result['error']}"
                        )
                    ]
                )
            
            # Format the result for display
            formatted_result = self._format_analysis_result(result)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=formatted_result
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error in analyze_source_code tool: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error analyzing source code: {str(e)}"
                    )
                ]
            )
    
    async def handle_analyze_code_string(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle analyze_code_string tool call."""
        try:
            code = arguments["code"]
            language = arguments["language"]
            
            if language == "python":
                result = await self.code_analysis_service.analyze_python_code(code)
            else:
                result = await self.code_analysis_service.analyze_generic_code(code, language)
            
            if "error" in result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error analyzing code: {result['error']}"
                        )
                    ]
                )
            
            # Format the result for display
            formatted_result = self._format_analysis_result(result)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=formatted_result
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error in analyze_code_string tool: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error analyzing code: {str(e)}"
                    )
                ]
            )
    
    async def handle_calculate_code_metrics(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle calculate_code_metrics tool call."""
        try:
            file_path = arguments["file_path"]
            language = arguments.get("language", "auto")
            
            result = await self.code_analysis_service.analyze_source_code(file_path, language)
            
            if "error" in result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error calculating metrics: {result['error']}"
                        )
                    ]
                )
            
            metrics = result.get("metrics", {})
            formatted_metrics = self._format_metrics(metrics)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=formatted_metrics
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error in calculate_code_metrics tool: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error calculating metrics: {str(e)}"
                    )
                ]
            )
    
    async def handle_extract_functions(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle extract_functions tool call."""
        try:
            file_path = arguments["file_path"]
            language = arguments.get("language", "auto")
            
            result = await self.code_analysis_service.analyze_source_code(file_path, language)
            
            if "error" in result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error extracting functions: {result['error']}"
                        )
                    ]
                )
            
            functions = result.get("functions", [])
            formatted_functions = self._format_functions(functions)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=formatted_functions
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error in extract_functions tool: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error extracting functions: {str(e)}"
                    )
                ]
            )
    
    async def handle_extract_classes(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle extract_classes tool call."""
        try:
            file_path = arguments["file_path"]
            language = arguments.get("language", "auto")
            
            result = await self.code_analysis_service.analyze_source_code(file_path, language)
            
            if "error" in result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error extracting classes: {result['error']}"
                        )
                    ]
                )
            
            classes = result.get("classes", [])
            formatted_classes = self._format_classes(classes)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=formatted_classes
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error in extract_classes tool: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error extracting classes: {str(e)}"
                    )
                ]
            )
    
    async def handle_analyze_dependencies(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle analyze_dependencies tool call."""
        try:
            file_path = arguments["file_path"]
            language = arguments.get("language", "auto")
            
            result = await self.code_analysis_service.analyze_source_code(file_path, language)
            
            if "error" in result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error analyzing dependencies: {result['error']}"
                        )
                    ]
                )
            
            imports = result.get("imports", [])
            formatted_imports = self._format_imports(imports)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=formatted_imports
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error in analyze_dependencies tool: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error analyzing dependencies: {str(e)}"
                    )
                ]
            )
    
    async def handle_detect_code_patterns(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle detect_code_patterns tool call."""
        try:
            file_path = arguments["file_path"]
            language = arguments.get("language", "auto")
            
            result = await self.code_analysis_service.analyze_source_code(file_path, language)
            
            if "error" in result:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error detecting patterns: {result['error']}"
                        )
                    ]
                )
            
            # Basic pattern detection based on metrics
            patterns = self._detect_patterns(result)
            formatted_patterns = self._format_patterns(patterns)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=formatted_patterns
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error in detect_code_patterns tool: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error detecting patterns: {str(e)}"
                    )
                ]
            )
    
    def _format_analysis_result(self, result: Dict[str, Any]) -> str:
        """Format analysis result for display."""
        language = result.get("language", "unknown")
        functions = result.get("functions", [])
        classes = result.get("classes", [])
        imports = result.get("imports", [])
        metrics = result.get("metrics", {})
        
        output = f"# Code Analysis Results ({language.upper()})\n\n"
        
        # Metrics summary
        if metrics:
            output += f"## Metrics Summary\n"
            output += f"- Lines of Code: {metrics.lines_of_code}\n"
            output += f"- Logical Lines: {metrics.logical_lines}\n"
            output += f"- Functions: {metrics.function_count}\n"
            output += f"- Classes: {metrics.class_count}\n"
            output += f"- Cyclomatic Complexity: {metrics.cyclomatic_complexity}\n"
            output += f"- Maintainability Index: {metrics.maintainability_index:.1f}\n\n"
        
        # Functions
        if functions:
            output += f"## Functions ({len(functions)})\n"
            for func in functions:
                output += f"- **{func.name}** (line {func.lineno})\n"
                if func.args:
                    output += f"  - Arguments: {', '.join(func.args)}\n"
                if func.return_type:
                    output += f"  - Return Type: {func.return_type}\n"
                if func.complexity > 1:
                    output += f"  - Complexity: {func.complexity}\n"
                if func.docstring:
                    output += f"  - Docstring: {func.docstring[:100]}...\n"
                output += "\n"
        
        # Classes
        if classes:
            output += f"## Classes ({len(classes)})\n"
            for cls in classes:
                output += f"- **{cls.name}** (line {cls.lineno})\n"
                if cls.inheritance:
                    output += f"  - Inheritance: {', '.join(cls.inheritance)}\n"
                if cls.attributes:
                    output += f"  - Attributes: {', '.join(cls.attributes)}\n"
                if cls.methods:
                    output += f"  - Methods: {len(cls.methods)}\n"
                if cls.docstring:
                    output += f"  - Docstring: {cls.docstring[:100]}...\n"
                output += "\n"
        
        # Imports
        if imports:
            output += f"## Imports ({len(imports)})\n"
            for imp in imports:
                if hasattr(imp, 'module'):
                    output += f"- {imp.module}"
                    if hasattr(imp, 'alias') and imp.alias:
                        output += f" as {imp.alias}"
                    output += f" (line {imp.lineno})\n"
                else:
                    output += f"- {imp['module']} (line {imp['lineno']})\n"
        
        return output
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for display."""
        if not metrics:
            return "No metrics available."
        
        output = "# Code Metrics\n\n"
        output += f"## Complexity Metrics\n"
        output += f"- Cyclomatic Complexity: {metrics.cyclomatic_complexity}\n"
        output += f"- Average Function Complexity: {metrics.average_function_complexity:.2f}\n"
        output += f"- Average Class Complexity: {metrics.average_class_complexity:.2f}\n\n"
        
        output += f"## Size Metrics\n"
        output += f"- Lines of Code: {metrics.lines_of_code}\n"
        output += f"- Logical Lines: {metrics.logical_lines}\n"
        output += f"- Comment Lines: {metrics.comment_lines}\n"
        output += f"- Blank Lines: {metrics.blank_lines}\n\n"
        
        output += f"## Structure Metrics\n"
        output += f"- Function Count: {metrics.function_count}\n"
        output += f"- Class Count: {metrics.class_count}\n\n"
        
        output += f"## Quality Metrics\n"
        output += f"- Maintainability Index: {metrics.maintainability_index:.1f}\n"
        
        # Quality assessment
        if metrics.maintainability_index >= 80:
            quality = "Excellent"
        elif metrics.maintainability_index >= 60:
            quality = "Good"
        elif metrics.maintainability_index >= 40:
            quality = "Fair"
        else:
            quality = "Poor"
        
        output += f"- Quality Assessment: {quality}\n"
        
        return output
    
    def _format_functions(self, functions: List[Any]) -> str:
        """Format functions for display."""
        if not functions:
            return "No functions found."
        
        output = f"# Functions ({len(functions)})\n\n"
        
        for func in functions:
            output += f"## {func.name}\n"
            output += f"- **Line**: {func.lineno}\n"
            output += f"- **Arguments**: {', '.join(func.args) if func.args else 'None'}\n"
            output += f"- **Return Type**: {func.return_type or 'None'}\n"
            output += f"- **Complexity**: {func.complexity}\n"
            output += f"- **Async**: {'Yes' if func.is_async else 'No'}\n"
            output += f"- **Method**: {'Yes' if func.is_method else 'No'}\n"
            
            if func.decorators:
                output += f"- **Decorators**: {', '.join(func.decorators)}\n"
            
            if func.docstring:
                output += f"- **Docstring**: {func.docstring}\n"
            
            output += "\n"
        
        return output
    
    def _format_classes(self, classes: List[Any]) -> str:
        """Format classes for display."""
        if not classes:
            return "No classes found."
        
        output = f"# Classes ({len(classes)})\n\n"
        
        for cls in classes:
            output += f"## {cls.name}\n"
            output += f"- **Line**: {cls.lineno}\n"
            output += f"- **Complexity**: {cls.complexity}\n"
            
            if cls.inheritance:
                output += f"- **Inheritance**: {', '.join(cls.inheritance)}\n"
            
            if cls.attributes:
                output += f"- **Attributes**: {', '.join(cls.attributes)}\n"
            
            if cls.methods:
                output += f"- **Methods**: {len(cls.methods)}\n"
                for method in cls.methods:
                    output += f"  - {method.name} (line {method.lineno})\n"
            
            if cls.decorators:
                output += f"- **Decorators**: {', '.join(cls.decorators)}\n"
            
            if cls.docstring:
                output += f"- **Docstring**: {cls.docstring}\n"
            
            output += "\n"
        
        return output
    
    def _format_imports(self, imports: List[Any]) -> str:
        """Format imports for display."""
        if not imports:
            return "No imports found."
        
        output = f"# Imports ({len(imports)})\n\n"
        
        for imp in imports:
            if hasattr(imp, 'module'):
                output += f"- **{imp.module}**"
                if hasattr(imp, 'alias') and imp.alias:
                    output += f" as {imp.alias}"
                output += f" (line {imp.lineno}, {imp.import_type})\n"
            else:
                output += f"- **{imp['module']}** (line {imp['lineno']})\n"
        
        return output
    
    def _detect_patterns(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Detect patterns in code analysis result."""
        patterns = {
            "anti_patterns": [],
            "good_patterns": [],
            "suggestions": []
        }
        
        metrics = result.get("metrics", {})
        functions = result.get("functions", [])
        classes = result.get("classes", [])
        
        # Complexity patterns
        if metrics.cyclomatic_complexity > 10:
            patterns["anti_patterns"].append("High cyclomatic complexity - consider refactoring")
        
        if metrics.average_function_complexity > 5:
            patterns["anti_patterns"].append("High average function complexity")
        
        # Function patterns
        long_functions = [f for f in functions if f.complexity > 5]
        if long_functions:
            patterns["anti_patterns"].append(f"Found {len(long_functions)} complex functions")
        
        # Class patterns
        if classes:
            large_classes = [c for c in classes if len(c.methods) > 10]
            if large_classes:
                patterns["anti_patterns"].append("Large classes detected - consider splitting")
        
        # Good patterns
        if metrics.maintainability_index >= 80:
            patterns["good_patterns"].append("High maintainability index")
        
        if metrics.comment_lines > 0:
            patterns["good_patterns"].append("Code includes comments")
        
        # Suggestions
        if metrics.function_count > 20:
            patterns["suggestions"].append("Consider organizing functions into modules")
        
        if not any(f.docstring for f in functions):
            patterns["suggestions"].append("Consider adding docstrings to functions")
        
        return patterns
    
    def _format_patterns(self, patterns: Dict[str, Any]) -> str:
        """Format patterns for display."""
        output = "# Code Pattern Analysis\n\n"
        
        if patterns["anti_patterns"]:
            output += "## Anti-Patterns Detected\n"
            for pattern in patterns["anti_patterns"]:
                output += f"- ⚠️ {pattern}\n"
            output += "\n"
        
        if patterns["good_patterns"]:
            output += "## Good Patterns Found\n"
            for pattern in patterns["good_patterns"]:
                output += f"- ✅ {pattern}\n"
            output += "\n"
        
        if patterns["suggestions"]:
            output += "## Suggestions\n"
            for suggestion in patterns["suggestions"]:
                output += f"- 💡 {suggestion}\n"
            output += "\n"
        
        if not any(patterns.values()):
            output += "No specific patterns detected.\n"
        
        return output 