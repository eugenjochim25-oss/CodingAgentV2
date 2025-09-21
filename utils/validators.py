import re
from datetime import datetime
from typing import Dict, Any

def validate_chat_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate chat input data.
    
    Args:
        data: Request data dictionary
        
    Returns:
        Dictionary with validation result
    """
    message = data.get("message", "")
    
    # Check if message exists and is not empty
    if not message or not message.strip():
        return {
            "valid": False,
            "error": "Nachricht darf nicht leer sein"
        }
    
    # Check message length
    if len(message) > 5000:
        return {
            "valid": False,
            "error": "Nachricht ist zu lang (maximal 5000 Zeichen)"
        }
    
    # Check for potentially malicious content
    if _contains_suspicious_content(message):
        return {
            "valid": False,
            "error": "Nachricht enthält nicht erlaubte Inhalte"
        }
    
    return {
        "valid": True,
        "message": message.strip(),
        "timestamp": datetime.now().isoformat()
    }

def validate_code_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate code input data.
    
    Args:
        data: Request data dictionary
        
    Returns:
        Dictionary with validation result
    """
    code = data.get("code", "")
    
    # Check if code exists
    if not code or not code.strip():
        return {
            "valid": False,
            "error": "Code darf nicht leer sein"
        }
    
    # Check code length
    if len(code) > 50000:
        return {
            "valid": False,
            "error": "Code ist zu lang (maximal 50000 Zeichen)"
        }
    
    # Basic syntax validation (very basic check)
    if not _is_valid_python_syntax(code):
        return {
            "valid": False,
            "error": "Code enthält ungültige Python-Syntax"
        }
    
    return {
        "valid": True,
        "code": code.strip(),
        "timestamp": datetime.now().isoformat()
    }

def _contains_suspicious_content(text: str) -> bool:
    """Check for suspicious content in text."""
    suspicious_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'data:text/html',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
    ]
    
    text_lower = text.lower()
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def _is_valid_python_syntax(code: str) -> bool:
    """Basic Python syntax validation."""
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False
    except Exception:
        # Other compilation errors (like undefined variables) are ok for syntax check
        return True