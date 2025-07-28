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
import fnmatch
import os

from ..config import get_config

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
        self.config = get_config()
        self.language_patterns = {
            "javascript": {
                "function": r"function\s+(\w+)\s*\(",
                "class": r"class\s+(\w+)",
                "import": r"import\s+.*from\s+['\"]([^'\"]+)['\"]"
            },
            "typescript": {
                "function": r"(?:function\s+(\w+)|(\w+)\s*[:=]\s*(?:async\s+)?function)",
                "class": r"class\s+(\w+)",
                "import": r"import\s+.*from\s+['\"]([^'\"]+)['\"]"
            },
            "python": {
                "function": r"def\s+(\w+)\s*\(",
                "class": r"class\s+(\w+)",
                "import": r"(?:from\s+(\w+)|import\s+(\w+))"
            }
        }

    def find_project_root(self, start_path: str = None) -> Optional[Path]:
        """Find the root directory of the current project."""
        if start_path:
            current = Path(start_path)
        else:
            current = Path.cwd()
        
        # If project_root is configured, use it
        if self.config.code_analysis.project_root:
            project_root = Path(self.config.code_analysis.project_root)
            if project_root.exists():
                return project_root
        
        # Auto-detect project root by looking for common project files
        while current != current.parent:
            project_files = [
                "package.json", "pyproject.toml", "setup.py", "requirements.txt",
                "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Makefile",
                ".git", ".gitignore", "README.md", "LICENSE"
            ]
            
            for file in project_files:
                if (current / file).exists():
                    return current
            
            current = current.parent
        
        # If no project root found, try common directories
        for common_dir in self.config.code_analysis.common_project_dirs:
            if Path(common_dir).exists():
                return Path(common_dir)
        
        return None

    def find_file_in_project(self, file_path: str, project_root: Path = None) -> Optional[Path]:
        """Find a file within the project directory."""
        if not project_root:
            project_root = self.find_project_root()
            if not project_root:
                return None
        
        # Try direct path first
        full_path = project_root / file_path
        if full_path.exists():
            return full_path
        
        # Search recursively in project
        for pattern in self.config.code_analysis.search_patterns:
            for file in project_root.rglob(pattern):
                if file.name == Path(file_path).name or str(file).endswith(file_path):
                    return file
        
        return None

    def get_project_files(self, project_root: Path = None, file_type: str = None) -> List[Path]:
        """Get all files in the project matching the search patterns."""
        if not project_root:
            project_root = self.find_project_root()
            if not project_root:
                return []
        
        files = []
        patterns = self.config.code_analysis.search_patterns
        
        if file_type:
            # Filter patterns by file type
            patterns = [p for p in patterns if file_type in p]
        
        for pattern in patterns:
            for file in project_root.rglob(pattern):
                # Check if file should be excluded
                should_exclude = False
                for exclude_pattern in self.config.code_analysis.exclude_patterns:
                    if fnmatch.fnmatch(str(file), exclude_pattern):
                        should_exclude = True
                        break
                
                if not should_exclude and file.is_file():
                    # Check file size
                    if file.stat().st_size <= self.config.code_analysis.max_file_size:
                        files.append(file)
        
        return files

    def get_project_structure(self, project_root: Path = None, max_depth: int = None) -> Dict[str, Any]:
        """Get the structure of the project directory."""
        if not project_root:
            project_root = self.find_project_root()
            if not project_root:
                return {"error": "Project root not found"}
        
        if max_depth is None:
            max_depth = self.config.code_analysis.max_search_depth
        
        def build_tree(path: Path, depth: int = 0) -> Dict[str, Any]:
            if depth > max_depth:
                return {"type": "truncated"}
            
            if path.is_file():
                return {
                    "type": "file",
                    "name": path.name,
                    "size": path.stat().st_size,
                    "extension": path.suffix
                }
            
            result = {
                "type": "directory",
                "name": path.name,
                "children": {}
            }
            
            try:
                for item in path.iterdir():
                    # Skip excluded patterns
                    should_exclude = False
                    for exclude_pattern in self.config.code_analysis.exclude_patterns:
                        if fnmatch.fnmatch(str(item), exclude_pattern):
                            should_exclude = True
                            break
                    
                    if not should_exclude:
                        result["children"][item.name] = build_tree(item, depth + 1)
            except PermissionError:
                result["error"] = "Permission denied"
            
            return result
        
        return build_tree(project_root)
    
    async def analyze_source_code(self, file_path: str, language: str = "auto") -> Dict[str, Any]:
        """Analyze source code file and extract comprehensive information."""
        try:
            # First try to find the file in the project
            project_root = self.find_project_root()
            if project_root:
                found_path = self.find_file_in_project(file_path, project_root)
                if found_path:
                    path = found_path
                else:
                    # If not found in project, try the old method
                    path = None
                    possible_paths = [
                        Path(file_path),  # Direct path
                        Path.cwd() / file_path,  # Relative to current working directory
                        Path("/workspace") / file_path,  # Common Docker workspace
                        Path("/app") / file_path,  # Common Docker app directory
                        Path("/code") / file_path,  # Common Docker code directory
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
            else:
                # Fallback to old method if no project root found
                path = None
                possible_paths = [
                    Path(file_path),  # Direct path
                    Path.cwd() / file_path,  # Relative to current working directory
                    Path("/workspace") / file_path,  # Common Docker workspace
                    Path("/app") / file_path,  # Common Docker app directory
                    Path("/code") / file_path,  # Common Docker code directory
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
                project_info = f"Project root: {project_root}" if project_root else "No project root found"
                raise FileNotFoundError(f"File not found: {file_path}. {project_info}. Searched in: {', '.join(searched_paths)}")
            
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