import subprocess
import tempfile
import os
import logging
import uuid
from typing import Dict, Any, Optional
import signal
import time
from utils.code_analyzer import is_code_safe
from services.cache_service import get_cache_service

logger = logging.getLogger(__name__)

class CodeExecutionService:
    """Service for securely executing Python code with caching support."""
    
    def __init__(self, config=None):
        if config:
            self.timeout = config.get('CODE_EXECUTION_TIMEOUT', 10)
            self.max_output_length = config.get('MAX_OUTPUT_LENGTH', 10000)
            self.caching_enabled = config.get('CACHING_ENABLED', True)
        else:
            self.timeout = int(os.environ.get('CODE_EXECUTION_TIMEOUT', '10'))
            self.max_output_length = int(os.environ.get('MAX_OUTPUT_LENGTH', '10000'))
            self.caching_enabled = os.environ.get('CACHING_ENABLED', 'true').lower() == 'true'
        
        # Initialize cache service if enabled
        self.cache_service = get_cache_service() if self.caching_enabled else None
        
    def execute_python_code(self, code: str, use_cache: bool = True, 
                           cache_ttl_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute Python code in a secure environment with caching support.
        
        Args:
            code: Python code to execute
            use_cache: Whether to use caching for this execution
            cache_ttl_hours: Custom cache TTL in hours (optional)
            
        Returns:
            Dictionary with execution results including output, errors, and status
        """
        if not code or not code.strip():
            return {
                "success": False,
                "output": "",
                "error": "Kein Code zum Ausführen bereitgestellt",
                "execution_time": 0
            }
        
        # Check cache first if enabled
        cache_key = None
        cached_result = None
        
        if self.caching_enabled and use_cache and self.cache_service:
            cache_key = self.cache_service.generate_cache_key(
                code=code,
                language='python',
                inputs={'timeout': self.timeout, 'max_output_length': self.max_output_length}
            )
            
            cached_result = self.cache_service.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for code execution: {cache_key[:8]}...")
                # Add cache hit indicator to result
                cached_result['from_cache'] = True
                cached_result['cache_key'] = cache_key[:8]
                return cached_result
        
        # AST-based security analysis
        safety_check = is_code_safe(code)
        if not safety_check['safe']:
            return {
                "success": False,
                "output": "",
                "error": f"Sicherheitswarnung: {'; '.join(safety_check['issues'])}",
                "execution_time": 0,
                "security_issues": safety_check['issues']
            }
        
        # Create temporary file with unique name
        temp_file = None
        start_time = time.time()
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                temp_file = f.name
                f.write(code)
            
            # Execute code with timeout and capture output
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=tempfile.gettempdir()  # Run in temp directory for isolation
            )
            
            execution_time = time.time() - start_time
            
            # Get output
            output = result.stdout if result.stdout else ""
            error = result.stderr if result.stderr else ""
            
            # Truncate output if too long
            if len(output) > self.max_output_length:
                output = output[:self.max_output_length] + "\n... (Ausgabe gekürzt)"
            
            if len(error) > self.max_output_length:
                error = error[:self.max_output_length] + "\n... (Fehlerausgabe gekürzt)"
            
            success = result.returncode == 0
            
            execution_result = {
                "success": success,
                "output": output,
                "error": error,
                "execution_time": round(execution_time, 3),
                "from_cache": False,
                "cache_key": cache_key[:8] if cache_key else None
            }
            
            # Cache successful results if caching is enabled
            if self.caching_enabled and cache_key and self.cache_service and success:
                cache_ttl_seconds = (cache_ttl_hours * 3600) if cache_ttl_hours else None
                self.cache_service.set(cache_key, execution_result, cache_ttl_seconds)
                logger.debug(f"Result cached for: {cache_key[:8]}...")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "output": "",
                "error": f"Code-Ausführung unterbrochen (Timeout nach {self.timeout} Sekunden)",
                "execution_time": round(execution_time, 3),
                "from_cache": False,
                "cache_key": cache_key[:8] if cache_key else None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing code: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Ausführungsfehler: {str(e)}",
                "execution_time": round(execution_time, 3),
                "from_cache": False,
                "cache_key": cache_key[:8] if cache_key else None
            }
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except OSError as e:
                    logger.warning(f"Could not delete temp file {temp_file}: {e}")
    
    def _contains_dangerous_code(self, code: str) -> bool:
        """
        Check if code contains potentially dangerous operations.
        
        Args:
            code: Code to check
            
        Returns:
            True if code contains dangerous operations
        """
        dangerous_keywords = [
            'import os',
            'import sys',
            'import subprocess',
            'import shutil',
            'import socket',
            'import urllib',
            'import requests',
            'import http',
            'open(',
            'file(',
            'exec(',
            'eval(',
            '__import__',
            'compile(',
            'globals(',
            'locals(',
            'vars(',
            'dir(',
            'getattr(',
            'setattr(',
            'delattr(',
            'hasattr(',
        ]
        
        code_lower = code.lower()
        
        for keyword in dangerous_keywords:
            if keyword.lower() in code_lower:
                logger.warning(f"Dangerous code detected: {keyword}")
                return True
                
        return False