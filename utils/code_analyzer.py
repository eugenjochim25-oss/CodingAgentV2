import ast
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

class CodeSecurityAnalyzer:
    """AST-based code security analyzer for detecting potentially dangerous operations."""
    
    def __init__(self):
        # Dangerous imports that should be blocked
        self.dangerous_imports = {
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'urllib2', 'urllib3',
            'requests', 'http', 'ftplib', 'smtplib', 'telnetlib', 'pathlib', 'glob',
            'tempfile', 'shlex', 'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3',
            'ctypes', 'multiprocessing', 'threading', 'asyncio', 'concurrent',
            'importlib', '__builtin__', 'builtins', 'imp', 'pkgutil', 'modulefinder'
        }
        
        # Dangerous functions that should be blocked
        self.dangerous_functions = {
            'eval', 'exec', 'compile', '__import__', 'open', 'file', 'input', 'raw_input',
            'execfile', 'reload', 'getattr', 'setattr', 'delattr', 'hasattr', 'callable',
            'vars', 'dir', 'globals', 'locals', 'help', 'copyright', 'credits', 'license',
            'quit', 'exit'
        }
        
        # Dangerous attributes that should be blocked
        self.dangerous_attributes = {
            '__class__', '__bases__', '__subclasses__', '__mro__', '__globals__',
            '__dict__', '__code__', '__func__', '__self__', '__module__', '__qualname__',
            '__annotations__', '__closure__', '__defaults__', '__kwdefaults__'
        }
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code for security issues using AST.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Initialize analysis results
            issues = []
            imports = set()
            function_calls = set()
            attribute_accesses = set()
            
            # Walk through the AST
            for node in ast.walk(tree):
                self._analyze_node(node, issues, imports, function_calls, attribute_accesses)
            
            # Determine if code is safe
            is_safe = len(issues) == 0
            
            return {
                'safe': is_safe,
                'issues': issues,
                'imports': list(imports),
                'function_calls': list(function_calls),
                'attribute_accesses': list(attribute_accesses),
                'complexity_score': self._calculate_complexity(tree)
            }
            
        except SyntaxError as e:
            return {
                'safe': False,
                'issues': [f'Syntax error: {str(e)}'],
                'imports': [],
                'function_calls': [],
                'attribute_accesses': [],
                'complexity_score': 0
            }
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {
                'safe': False,
                'issues': [f'Analysis error: {str(e)}'],
                'imports': [],
                'function_calls': [],
                'attribute_accesses': [],
                'complexity_score': 0
            }
    
    def _analyze_node(self, node: ast.AST, issues: List[str], imports: Set[str], 
                     function_calls: Set[str], attribute_accesses: Set[str]):
        """Analyze individual AST node for security issues."""
        
        # Check imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            self._check_imports(node, issues, imports)
        
        # Check function calls
        elif isinstance(node, ast.Call):
            self._check_function_calls(node, issues, function_calls)
        
        # Check attribute access
        elif isinstance(node, ast.Attribute):
            self._check_attribute_access(node, issues, attribute_accesses)
        
        # Check for dangerous names
        elif isinstance(node, ast.Name):
            self._check_name_access(node, issues)
    
    def _check_imports(self, node: ast.AST, issues: List[str], imports: Set[str]):
        """Check for dangerous imports."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                imports.add(module_name)
                if module_name in self.dangerous_imports:
                    issues.append(f"Dangerous import detected: {module_name}")
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split('.')[0]
                imports.add(module_name)
                if module_name in self.dangerous_imports:
                    issues.append(f"Dangerous import detected: {module_name}")
                
                # Check for dangerous functions from modules
                for alias in node.names:
                    if alias.name in self.dangerous_functions:
                        issues.append(f"Dangerous function import: {alias.name} from {module_name}")
    
    def _check_function_calls(self, node: ast.Call, issues: List[str], function_calls: Set[str]):
        """Check for dangerous function calls."""
        func_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name:
            function_calls.add(func_name)
            if func_name in self.dangerous_functions:
                issues.append(f"Dangerous function call detected: {func_name}")
    
    def _check_attribute_access(self, node: ast.Attribute, issues: List[str], 
                               attribute_accesses: Set[str]):
        """Check for dangerous attribute access."""
        attr_name = node.attr
        attribute_accesses.add(attr_name)
        
        if attr_name in self.dangerous_attributes:
            issues.append(f"Dangerous attribute access detected: {attr_name}")
    
    def _check_name_access(self, node: ast.Name, issues: List[str]):
        """Check for dangerous name access."""
        if node.id in self.dangerous_functions:
            issues.append(f"Dangerous name access detected: {node.id}")
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate a simple complexity score for the code."""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 2
            elif isinstance(node, ast.ClassDef):
                complexity += 3
        
        return complexity

def is_code_safe(code: str) -> Dict[str, Any]:
    """
    Quick safety check for code using AST analysis.
    
    Args:
        code: Python code to check
        
    Returns:
        Dictionary with safety status and details
    """
    analyzer = CodeSecurityAnalyzer()
    return analyzer.analyze_code(code)