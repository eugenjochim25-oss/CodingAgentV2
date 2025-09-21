from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "CodingAgentV2"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # AI service settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_CODE_MODEL: str = "gemini-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Code execution settings
    CODE_EXECUTION_ENABLED: bool = True
    CODE_EXECUTION_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings():
    return Settings()