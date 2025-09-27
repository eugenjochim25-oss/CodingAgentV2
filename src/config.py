# src/config.py

import os
from typing import Dict, Any


class Config:
    """Application configuration class."""

    def __init__(self):
        # Security
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Upload-Limit
        self.ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5000").split(",")
        self.FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

        # AI-Konfiguration (Gemini)
        self.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
        self.GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self.GEMINI_CODE_MODEL = os.environ.get("GEMINI_CODE_MODEL", "gemini-1.5-pro")
        self.GEMINI_MAX_TOKENS = int(os.environ.get("GEMINI_MAX_TOKENS", "500"))
        self.GEMINI_TEMPERATURE = float(os.environ.get("GEMINI_TEMPERATURE", "0.7"))

        # Code-Execution
        self.CODE_EXECUTION_ENABLED = os.environ.get("CODE_EXECUTION_ENABLED", "true").lower() == "true"
        self.CODE_EXECUTION_TIMEOUT = int(os.environ.get("CODE_EXECUTION_TIMEOUT", "10"))
        self.MAX_OUTPUT_LENGTH = int(os.environ.get("MAX_OUTPUT_LENGTH", "10000"))

        # Optionales Caching
        self.CACHING_ENABLED = os.environ.get("CACHING_ENABLED", "false").lower() == "true"

        # Datenbank
        self.DATABASE_PATH = os.environ.get("DATABASE_PATH", "learning_data.db")

    def validate(self) -> Dict[str, Any]:
        """Validates configuration and returns a status dictionary."""
        issues = []

        # Security Checks
        if self.SECRET_KEY == "dev-secret-key-change-in-production":
            issues.append("SECRET_KEY sollte in Produktion geändert werden!")

        # AI Checks
        if not self.GEMINI_API_KEY:
            issues.append("GEMINI_API_KEY fehlt")

        if self.GEMINI_MAX_TOKENS < 100 or self.GEMINI_MAX_TOKENS > 4000:
            issues.append("GEMINI_MAX_TOKENS sollte zwischen 100 und 4000 liegen")

        if self.GEMINI_TEMPERATURE < 0 or self.GEMINI_TEMPERATURE > 2:
            issues.append("GEMINI_TEMPERATURE sollte zwischen 0 und 2 liegen")

        if self.CODE_EXECUTION_TIMEOUT < 1 or self.CODE_EXECUTION_TIMEOUT > 60:
            issues.append("CODE_EXECUTION_TIMEOUT sollte zwischen 1 und 60 Sekunden liegen")

        # AI-Konfig Dict
        self.AI_CONFIG = {
            "openai_available": bool(self.GEMINI_API_KEY),  # Legacy-Flag
            "code_execution_enabled": self.CODE_EXECUTION_ENABLED,
            "GEMINI_API_KEY": self.GEMINI_API_KEY,
            "GEMINI_MODEL": self.GEMINI_MODEL,
            "GEMINI_CODE_MODEL": self.GEMINI_CODE_MODEL,
            "GEMINI_MAX_TOKENS": self.GEMINI_MAX_TOKENS,
            "GEMINI_TEMPERATURE": self.GEMINI_TEMPERATURE,
            "CODE_EXECUTION_TIMEOUT": self.CODE_EXECUTION_TIMEOUT,
            "MAX_OUTPUT_LENGTH": self.MAX_OUTPUT_LENGTH,
            "CACHING_ENABLED": self.CACHING_ENABLED,
        }

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "ai_config": self.AI_CONFIG,
        }
