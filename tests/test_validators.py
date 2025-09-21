import pytest
from utils.validators import validate_chat_input, validate_code_input

class TestValidators:
    """Test cases for input validators."""
    
    def test_validate_chat_input_valid(self):
        """Test valid chat input."""
        data = {"message": "Hello, how are you?"}
        result = validate_chat_input(data)
        
        assert result["valid"] is True
        assert result["message"] == "Hello, how are you?"
        assert "timestamp" in result
    
    def test_validate_chat_input_empty(self):
        """Test empty chat input."""
        data = {"message": ""}
        result = validate_chat_input(data)
        
        assert result["valid"] is False
        assert "nicht leer sein" in result["error"]
    
    def test_validate_chat_input_whitespace_only(self):
        """Test chat input with only whitespace."""
        data = {"message": "   \n\t   "}
        result = validate_chat_input(data)
        
        assert result["valid"] is False
        assert "nicht leer sein" in result["error"]
    
    def test_validate_chat_input_too_long(self):
        """Test chat input that is too long."""
        long_message = "x" * 6000  # Longer than 5000 character limit
        data = {"message": long_message}
        result = validate_chat_input(data)
        
        assert result["valid"] is False
        assert "zu lang" in result["error"]
    
    def test_validate_chat_input_suspicious_content(self):
        """Test chat input with suspicious content."""
        suspicious_messages = [
            "<script>alert('xss')</script>",
            "javascript:void(0)",
            "data:text/html,<script>alert(1)</script>",
            "eval('malicious code')",
            "__import__('os')"
        ]
        
        for message in suspicious_messages:
            data = {"message": message}
            result = validate_chat_input(data)
            assert result["valid"] is False
            assert "nicht erlaubte Inhalte" in result["error"]
    
    def test_validate_code_input_valid(self):
        """Test valid code input."""
        data = {"code": "print('Hello, World!')"}
        result = validate_code_input(data)
        
        assert result["valid"] is True
        assert result["code"] == "print('Hello, World!')"
        assert "timestamp" in result
    
    def test_validate_code_input_empty(self):
        """Test empty code input."""
        data = {"code": ""}
        result = validate_code_input(data)
        
        assert result["valid"] is False
        assert "nicht leer sein" in result["error"]
    
    def test_validate_code_input_too_long(self):
        """Test code input that is too long."""
        long_code = "print('x')\n" * 10000  # Much longer than 50000 characters
        data = {"code": long_code}
        result = validate_code_input(data)
        
        assert result["valid"] is False
        assert "zu lang" in result["error"]
    
    def test_validate_code_input_invalid_syntax(self):
        """Test code input with invalid syntax."""
        invalid_codes = [
            "print('hello'",  # Missing closing parenthesis
            "if True\n    print('test')",  # Missing colon
            "def func(\n    pass",  # Invalid function definition
        ]
        
        for code in invalid_codes:
            data = {"code": code}
            result = validate_code_input(data)
            assert result["valid"] is False
            assert "ungültige Python-Syntax" in result["error"]
    
    def test_validate_code_input_valid_complex_code(self):
        """Test valid complex code input."""
        complex_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
"""
        data = {"code": complex_code}
        result = validate_code_input(data)
        
        assert result["valid"] is True
        assert result["code"] == complex_code.strip()
    
    def test_validate_code_input_whitespace_handling(self):
        """Test code input whitespace handling."""
        code_with_whitespace = "   \n\nprint('hello')  \n\n   "
        data = {"code": code_with_whitespace}
        result = validate_code_input(data)
        
        assert result["valid"] is True
        assert result["code"] == "print('hello')"  # Stripped whitespace
    
    def test_validate_chat_input_missing_message(self):
        """Test chat input without message field."""
        data = {}
        result = validate_chat_input(data)
        
        assert result["valid"] is False
        assert "nicht leer sein" in result["error"]
    
    def test_validate_code_input_missing_code(self):
        """Test code input without code field."""
        data = {}
        result = validate_code_input(data)
        
        assert result["valid"] is False
        assert "nicht leer sein" in result["error"]