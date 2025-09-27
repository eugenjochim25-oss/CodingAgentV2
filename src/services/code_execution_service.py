import logging
import subprocess
import tempfile
import os
import time
from typing import Dict, Any

logger = logging.getLogger('CodingAgentV2')

class CodeExecutionService:
    """Service for executing code safely."""
    
    def __init__(self, config):
        self.config = config
        self.timeout = config.get('CODE_EXECUTION_TIMEOUT', 30)
    
    def execute_python_code(self, code: str, use_cache: bool = True, cache_ttl_hours: int = None) -> Dict[str, Any]:
        """Execute Python code and return the result."""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute the code
            start_time = time.time()
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            execution_time = time.time() - start_time
            
            # Clean up
            os.unlink(temp_file)
            
            # Prepare response
            output = result.stdout
            error = result.stderr
            
            return {
                "success": result.returncode == 0,
                "output": output,
                "error": error,
                "execution_time": execution_time,
                "from_cache": False
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Code execution timed out after {self.timeout} seconds.",
                "execution_time": self.timeout,
                "from_cache": False
            }
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Ein Fehler ist bei der Code-Ausführung aufgetreten: {str(e)}",
                "execution_time": 0,
                "from_cache": False
            }

# Neu hinzugefügte Factory-Funktion
def get_code_service() -> CodeExecutionService:
    """
    Returns an instance of the CodeExecutionService.
    This function acts as a dependency injection provider for FastAPI.
    """
    # Hier kannst du deine Konfiguration laden, z.B. aus einer Konfigurationsdatei oder Umgebungsvariablen.
    # Für dieses Beispiel verwenden wir eine leere Konfiguration.
    config = {}
    return CodeExecutionService(config)