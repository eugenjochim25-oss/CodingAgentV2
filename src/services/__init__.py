from functools import lru_cache
from src.config.settings import get_settings
from src.services.ai_service import AIService
from src.services.code_execution_service import CodeExecutionService
from src.services.learning_service import LearningService

settings = get_settings()

@lru_cache()
def get_ai_service():
    if settings.GEMINI_API_KEY or settings.OPENAI_API_KEY:
        return AIService(settings)
    return None

@lru_cache()
def get_code_service():
    if settings.CODE_EXECUTION_ENABLED:
        return CodeExecutionService(settings)
    return None

@lru_cache()
def get_learning_service():
    return LearningService()