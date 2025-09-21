import time
from typing import Dict, Any

def validate_chat_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate chat input data.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Dictionary with validation result
    """
    if not data:
        return {
            "valid": False,
            "error": "Keine Daten empfangen",
            "timestamp": time.time()
        }
    
    if "message" not in data:
        return {
            "valid": False,
            "error": "Nachricht fehlt",
            "timestamp": time.time()
        }
    
    message = data.get("message", "").strip()
    if not message:
        return {
            "valid": False,
            "error": "Nachricht darf nicht leer sein",
            "timestamp": time.time()
        }
    
    return {
        "valid": True,
        "timestamp": time.time()
    }

def validate_code_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate code input data.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Dictionary with validation result
    """
    if not data:
        return {
            "valid": False,
            "error": "Keine Daten empfangen",
            "timestamp": time.time()
        }
    
    if "code" not in data:
        return {
            "valid": False,
            "error": "Code fehlt",
            "timestamp": time.time()
        }
    
    code = data.get("code", "").strip()
    if not code:
        return {
            "valid": False,
            "error": "Code darf nicht leer sein",
            "timestamp": time.time()
        }
    
    return {
        "valid": True,
        "timestamp": time.time()
    }