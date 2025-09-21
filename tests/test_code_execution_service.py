import pytest
from services.code_execution_service import CodeExecutionService

class TestCodeExecutionService:
    """Test cases for CodeExecutionService."""
    
    def setup_method(self):
        """Set up test environment."""
        self.service = CodeExecutionService()
    
    def test_execute_empty_code(self):
        """Test execution with empty code."""
        result = self.service.execute_python_code("")
        
        assert result["success"] is False
        assert "Kein Code zum Ausführen bereitgestellt" in result["error"]
        assert result["execution_time"] == 0
    
    def test_execute_simple_code(self):
        """Test execution of simple valid code."""
        code = "print('Hello, World!')"
        result = self.service.execute_python_code(code)
        
        assert result["success"] is True
        assert "Hello, World!" in result["output"]
        assert result["execution_time"] > 0
    
    def test_execute_code_with_error(self):
        """Test execution of code that raises an error."""
        code = "print(undefined_variable)"
        result = self.service.execute_python_code(code)
        
        assert result["success"] is False
        assert "NameError" in result["error"]
        assert result["execution_time"] > 0
    
    def test_execute_dangerous_code(self):
        """Test that dangerous code is blocked."""
        dangerous_codes = [
            "import os",
            "import subprocess",
            "open('file.txt', 'w')",
            "exec('malicious code')",
            "eval('1+1')",
            "__import__('os')"
        ]
        
        for code in dangerous_codes:
            result = self.service.execute_python_code(code)
            assert result["success"] is False
            assert "Sicherheitswarnung" in result["error"]
    
    def test_execute_long_running_code(self):
        """Test timeout handling for long-running code."""
        # This code would run indefinitely
        code = "while True: pass"
        result = self.service.execute_python_code(code)
        
        assert result["success"] is False
        assert "Timeout" in result["error"]
        assert result["execution_time"] >= self.service.timeout
    
    def test_contains_dangerous_code(self):
        """Test dangerous code detection."""
        # Test safe code
        safe_code = "print('hello')\nx = 1 + 2\nfor i in range(10): print(i)"
        assert not self.service._contains_dangerous_code(safe_code)
        
        # Test dangerous code
        dangerous_code = "import os\nos.system('rm -rf /')"
        assert self.service._contains_dangerous_code(dangerous_code)
    
    def test_output_truncation(self):
        """Test that long output is truncated."""
        # Generate output longer than max_output_length
        code = f"print('x' * {self.service.max_output_length + 1000})"
        result = self.service.execute_python_code(code)
        
        assert result["success"] is True
        assert len(result["output"]) <= self.service.max_output_length + 100  # Allow for truncation message
        assert "gekürzt" in result["output"]
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        code = "print('hello'\n# Missing closing parenthesis"
        result = self.service.execute_python_code(code)
        
        assert result["success"] is False
        assert "SyntaxError" in result["error"]
    
    def test_multiple_print_statements(self):
        """Test code with multiple print statements."""
        code = """
print("Line 1")
print("Line 2")
print("Line 3")
"""
        result = self.service.execute_python_code(code)
        
        assert result["success"] is True
        assert "Line 1" in result["output"]
        assert "Line 2" in result["output"]
        assert "Line 3" in result["output"]
    
    def test_mathematical_operations(self):
        """Test mathematical operations."""
        # Test basic math operations without imports
        safe_code = """
result = 16 ** 0.5 + 3.14159
print(f"Result: {result}")
"""
        result = self.service.execute_python_code(safe_code)
        assert result["success"] is True
        assert "Result:" in result["output"]
        
        # Test dangerous import separately
        dangerous_code = "import math\nprint(math.sqrt(16))"
        result = self.service.execute_python_code(dangerous_code)
        assert result["success"] is False
        assert "Sicherheitswarnung" in result["error"]