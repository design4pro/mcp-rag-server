"""
Code Analysis Service for Advanced Project Understanding.

This service provides comprehensive code analysis capabilities including AST parsing,
function and class extraction, dependency analysis, and code metrics calculation.
"""

import ast
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Information about a function extracted from code."""
    name: str
    args: List[str]
    lineno: int
    complexity: int
    docstring: Optional[str]
    return_type: Optional[str]
    decorators: List[str]
    is_async: bool
    is_method: bool


@dataclass
class ClassInfo:
    """Information about a class extracted from code."""
    name: str
    methods: List[FunctionInfo]
    attributes: List[str]
    lineno: int
    complexity: int
    docstring: Optional[str]
    inheritance: List[str]
    decorators: List[str]


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    alias: Optional[str]
    lineno: int
    import_type: str  # "import" or "from"


@dataclass
class CodeMetrics:
    """Code quality and complexity metrics."""
    cyclomatic_complexity: int
    lines_of_code: int
    logical_lines: int
    comment_lines: int
    blank_lines: int
    maintainability_index: float
    function_count: int
    class_count: int
    average_function_complexity: float
    average_class_complexity: float


class CodeAnalysisService:
    """Service for analyzing source code and extracting structural information."""
    
    def __init__(self):
        """Initialize the code analysis service."""
        self.supported_languages = ["python", "javascript", "java", "rust", "go"]
        self.language_patterns = {
            "python": {
                "function": r'def\s+\w+\s*\(',
                "class": r'class\s+\w+',
                "import": r'import\s+\w+|from\s+\w+\s+import'
            },
            "javascript": {
                "function": r'function\s+\w+\s*\(|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(',
                "class": r'class\s+\w+',
                "import": r'import\s+.*from|const\s+\w+\s*=\s*require'
            },
            "java": {
                "function": r'public\s+\w+\s+\w+\s*\(|private\s+\w+\s+\w+\s*\(',
                "class": r'public\s+class\s+\w+|private\s+class\s+\w+',
                "import": r'import\s+\w+'
            },
            "rust": {
                "function": r'fn\s+\w+\s*\(',
                "class": r'struct\s+\w+|enum\s+\w+',
                "import": r'use\s+\w+'
            },
            "go": {
                "function": r'func\s+\w+\s*\(',
                "class": r'type\s+\w+\s+struct|type\s+\w+\s+interface',
                "import": r'import\s+\w+'
            }
        }
    
    async def analyze_source_code(self, file_path: str, language: str = "auto") -> Dict[str, Any]:
        """Analyze source code file and extract comprehensive information."""
        try:
            # Try different path resolutions
            path = None
            possible_paths = [
                Path(file_path),  # Direct path
                Path.cwd() / file_path,  # Relative to current working directory
                Path("/workspace") / file_path,  # Common Docker workspace
                Path("/app") / file_path,  # Common Docker app directory
                Path("/code") / file_path,  # Common code directory
            ]
            
            # Also try with common project root patterns
            if "/" in file_path:
                parts = file_path.split("/")
                if len(parts) > 1:
                    # Try with different root directories
                    for root in ["/workspace", "/app", "/code", "/src", Path.cwd()]:
                        possible_paths.append(Path(root) / file_path)
                        # Try without first directory (e.g., "apps/remind-tools/src/app/app.ts" -> "remind-tools/src/app/app.ts")
                        if len(parts) > 2:
                            possible_paths.append(Path(root) / "/".join(parts[1:]))
            
            # Find the first existing path
            for test_path in possible_paths:
                if test_path.exists():
                    path = test_path
                    break
            
            if path is None:
                # If no path found, try to provide helpful error message
                searched_paths = [str(p) for p in possible_paths[:10]]  # Limit to first 10 for readability
                raise FileNotFoundError(f"File not found: {file_path}. Searched in: {', '.join(searched_paths)}")
            
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            if language == "auto":
                language = self._detect_language(code, path.suffix)
            
            if language == "python":
                return await self.analyze_python_code(code)
            else:
                return await self.analyze_generic_code(code, language)
                
        except Exception as e:
            logger.error(f"Error analyzing source code {file_path}: {e}")
            return {"error": str(e), "file_path": file_path}
    
    async def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code using AST."""
        try:
            tree = ast.parse(code)
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "variables": [],
                "metrics": await self._calculate_python_metrics(tree, code),
                "language": "python"
            }
            
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = await self._extract_function_info(node)
                    analysis["functions"].append(func_info)
                elif isinstance(node, ast.AsyncFunctionDef):
                    func_info = await self._extract_function_info(node, is_async=True)
                    analysis["functions"].append(func_info)
                elif isinstance(node, ast.ClassDef):
                    class_info = await self._extract_class_info(node)
                    analysis["classes"].append(class_info)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = ImportInfo(
                            module=alias.name,
                            alias=alias.asname,
                            lineno=node.lineno,
                            import_type="import"
                        )
                        analysis["imports"].append(import_info)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        import_info = ImportInfo(
                            module=f"{module}.{alias.name}",
                            alias=alias.asname,
                            lineno=node.lineno,
                            import_type="from"
                        )
                        analysis["imports"].append(import_info)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis["variables"].append(target.id)
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing Python code: {e}")
            return {"error": str(e), "language": "python"}
    
    async def analyze_generic_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code using regex patterns for non-Python languages."""
        try:
            patterns = self.language_patterns.get(language, {})
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "variables": [],
                "metrics": await self._calculate_generic_metrics(code),
                "language": language
            }
            
            lines = code.split('\n')
            
            # Extract functions
            if "function" in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(patterns["function"], line):
                        func_name = self._extract_name_from_pattern(line, patterns["function"])
                        analysis["functions"].append({
                            "name": func_name,
                            "lineno": i,
                            "complexity": 1  # Default complexity
                        })
            
            # Extract classes
            if "class" in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(patterns["class"], line):
                        class_name = self._extract_name_from_pattern(line, patterns["class"])
                        analysis["classes"].append({
                            "name": class_name,
                            "lineno": i,
                            "complexity": 1  # Default complexity
                        })
            
            # Extract imports
            if "import" in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(patterns["import"], line):
                        analysis["imports"].append({
                            "module": line.strip(),
                            "lineno": i
                        })
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing {language} code: {e}")
            return {"error": str(e), "language": language}
    
    async def _extract_function_info(self, node: ast.FunctionDef, is_async: bool = False) -> FunctionInfo:
        """Extract detailed information about a function."""
        args = [arg.arg for arg in node.args.args]
        decorators = [ast.unparse(d) for d in node.decorator_list]
        
        # Determine return type annotation
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)
        
        # Calculate function complexity
        complexity = await self._calculate_node_complexity(node)
        
        return FunctionInfo(
            name=node.name,
            args=args,
            lineno=node.lineno,
            complexity=complexity,
            docstring=ast.get_docstring(node),
            return_type=return_type,
            decorators=decorators,
            is_async=is_async,
            is_method=False  # Will be set when processing classes
        )
    
    async def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract detailed information about a class."""
        methods = []
        attributes = []
        
        # Process class body
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = await self._extract_function_info(item, isinstance(item, ast.AsyncFunctionDef))
                func_info.is_method = True
                methods.append(func_info)
                
                # Check for attributes in __init__ method
                if func_info.name == '__init__':
                    for stmt in item.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    attributes.append(target.attr)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
                    elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        # Handle self.attribute assignments
                        attributes.append(target.attr)
        
        # Extract inheritance
        inheritance = []
        for base in node.bases:
            inheritance.append(ast.unparse(base))
        
        # Calculate class complexity
        complexity = await self._calculate_node_complexity(node)
        
        # Extract decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]
        
        return ClassInfo(
            name=node.name,
            methods=methods,
            attributes=attributes,
            lineno=node.lineno,
            complexity=complexity,
            docstring=ast.get_docstring(node),
            inheritance=inheritance,
            decorators=decorators
        )
    
    async def _calculate_node_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for an AST node."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
        
        return complexity
    
    async def _calculate_python_metrics(self, tree: ast.AST, code: str) -> CodeMetrics:
        """Calculate comprehensive metrics for Python code."""
        lines = code.split('\n')
        total_lines = len(lines)
        
        # Count different types of lines
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        blank_lines = sum(1 for line in lines if not line.strip())
        logical_lines = total_lines - blank_lines - comment_lines
        
        # Count functions and classes
        function_count = len([n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        
        # Calculate total complexity
        total_complexity = await self._calculate_node_complexity(tree)
        
        # Calculate averages
        avg_function_complexity = total_complexity / max(function_count, 1)
        avg_class_complexity = total_complexity / max(class_count, 1)
        
        # Calculate maintainability index (simplified)
        maintainability_index = max(0, min(100, 171 - 5.2 * total_complexity - 0.23 * logical_lines))
        
        return CodeMetrics(
            cyclomatic_complexity=total_complexity,
            lines_of_code=total_lines,
            logical_lines=logical_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            maintainability_index=maintainability_index,
            function_count=function_count,
            class_count=class_count,
            average_function_complexity=avg_function_complexity,
            average_class_complexity=avg_class_complexity
        )
    
    async def _calculate_generic_metrics(self, code: str) -> CodeMetrics:
        """Calculate basic metrics for non-Python code."""
        lines = code.split('\n')
        total_lines = len(lines)
        
        comment_lines = 0
        blank_lines = 0
        
        # Simple comment detection for different languages
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith(('//', '/*', '*', '#')):
                comment_lines += 1
        
        logical_lines = total_lines - blank_lines - comment_lines
        
        return CodeMetrics(
            cyclomatic_complexity=1,  # Default
            lines_of_code=total_lines,
            logical_lines=logical_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            maintainability_index=50.0,  # Default
            function_count=0,  # Will be calculated by regex
            class_count=0,  # Will be calculated by regex
            average_function_complexity=1.0,
            average_class_complexity=1.0
        )
    
    def _detect_language(self, code: str, file_extension: str) -> str:
        """Detect programming language from code and file extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.rs': 'rust',
            '.go': 'go'
        }
        
        # Try extension first
        if file_extension in extension_map:
            return extension_map[file_extension]
        
        # Fallback to code analysis
        for lang, patterns in self.language_patterns.items():
            if any(re.search(pattern, code) for pattern in patterns.values()):
                return lang
        
        return "unknown"
    
    def _extract_name_from_pattern(self, line: str, pattern: str) -> str:
        """Extract name from a line using a regex pattern."""
        match = re.search(pattern, line)
        if match:
            # For function patterns, try to extract the name from the matched part
            if 'def' in pattern:
                # Extract name from "def function_name("
                func_match = re.search(r'def\s+(\w+)', line)
                if func_match:
                    return func_match.group(1)
            elif 'function' in pattern:
                # Extract name from "function function_name("
                func_match = re.search(r'function\s+(\w+)', line)
                if func_match:
                    return func_match.group(1)
            else:
                # Try to extract the name after the pattern
                remaining = line[match.end():].strip()
                name_match = re.match(r'\w+', remaining)
                if name_match:
                    return name_match.group()
        return "unknown" 