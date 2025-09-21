from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from utils.validators import validate_chat_input, validate_code_input
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from config import Config

logger = logging.getLogger(__name__)

def create_api_router(app):
    """
    Create API router with dependency injection for FastAPI.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        APIRouter instance
    """
    router = APIRouter(prefix="/api")
    
    # Get configuration from app state
    config = app.state.ai_config
    
    # Initialize services with configuration
    ai_service = None
    code_service = None
    learning_service = None
    
    if config and config.get('openai_available'):
        try:
            from services.ai_service import AIService
            ai_service = AIService(config)
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
    
    if config and config.get('code_execution_enabled'):
        try:
            from services.code_execution_service import CodeExecutionService
            code_service = CodeExecutionService(config)
        except Exception as e:
            logger.error(f"Failed to initialize code execution service: {e}")
    
    # Always try to initialize learning service
    try:
        from services.learning_service import LearningService
        learning_service = LearningService()
    except Exception as e:
        logger.error(f"Failed to initialize learning service: {e}")

    @router.post("/chat")
    async def chat(request: Request):
        """Handle chat requests with AI integration."""
        try:
            # Check if AI service is available
            if not ai_service:
                return JSONResponse(
                    status_code=503,
                    content={"error": "AI-Service ist nicht verfügbar. Bitte prüfen Sie die Konfiguration."}
                )
            
            # Get and validate input
            data = await request.json()
            if not data:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Keine gültigen JSON-Daten empfangen"}
                )
            
            validation_result = validate_chat_input(data)
            if not validation_result["valid"]:
                return JSONResponse(
                    status_code=400,
                    content={"error": validation_result["error"]}
                )
            
            user_message = data.get("message", "")
            conversation_history = data.get("history", [])
            
            # Generate AI response
            response = ai_service.generate_response(user_message, conversation_history)
            
            # Learn from chat interaction (default rating = 3)
            if learning_service:
                try:
                    learning_service.learn_from_chat(user_message, response, 3)
                except Exception as e:
                    logger.warning(f"Failed to record chat learning: {e}")
            
            return {
                "response": response,
                "timestamp": validation_result["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut."}
            )

    @router.post("/execute")
    async def execute_code(request: Request):
        """Handle code execution requests."""
        try:
            # Check if code execution is enabled
            if not code_service:
                return JSONResponse(
                    status_code=503,
                    content={
                        "success": False,
                        "output": "",
                        "error": "Code-Ausführung ist nicht verfügbar oder deaktiviert.",
                        "execution_time": 0
                    }
                )
            
            # Get and validate input
            data = await request.json()
            if not data:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "output": "",
                        "error": "Keine gültigen JSON-Daten empfangen",
                        "execution_time": 0
                    }
                )
            
            validation_result = validate_code_input(data)
            if not validation_result["valid"]:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "output": "",
                        "error": validation_result["error"],
                        "execution_time": 0
                    }
                )
            
            code = data.get("code", "")
            use_cache = data.get("use_cache", True)
            cache_ttl_hours = data.get("cache_ttl_hours")
            
            # Execute code with caching support
            result = code_service.execute_python_code(
                code=code,
                use_cache=use_cache,
                cache_ttl_hours=cache_ttl_hours
            )
            
            # Learn from code execution (skip cached results)
            if learning_service and not result.get("from_cache", False):
                try:
                    language = data.get("language", "python")  # Default to python
                    success = result.get("success", False)
                    execution_time = result.get("execution_time", 0.0)
                    error_msg = result.get("error", "") if not success else ""
                    
                    learning_service.analyze_code_execution(
                        code, language, success, execution_time, error_msg
                    )
                except Exception as e:
                    logger.warning(f"Failed to record code execution learning: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in execute endpoint: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "output": "",
                    "error": "Ein Fehler ist bei der Code-Ausführung aufgetreten.",
                    "execution_time": 0
                }
            )

    @router.post("/analyze")
    async def analyze_code(request: Request):
        """Handle code analysis requests."""
        try:
            # Check if AI service is available
            if not ai_service:
                return JSONResponse(
                    status_code=503,
                    content={"error": "AI-Service ist nicht verfügbar. Bitte prüfen Sie die Konfiguration."}
                )
            
            # Get and validate input
            data = await request.json()
            if not data:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Keine gültigen JSON-Daten empfangen"}
                )
            
            validation_result = validate_code_input(data)
            if not validation_result["valid"]:
                return JSONResponse(
                    status_code=400,
                    content={"error": validation_result["error"]}
                )
            
            code = data.get("code", "")
            
            # Analyze code
            analysis = ai_service.analyze_code(code)
            
            return {
                "analysis": analysis,
                "timestamp": validation_result["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error in analyze endpoint: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Ein Fehler ist bei der Code-Analyse aufgetreten."}
            )
    
    @router.get("/learning/stats")
    async def get_learning_stats():
        """Get learning statistics and progress."""
        try:
            if not learning_service:
                return JSONResponse(
                    status_code=503,
                    content={"error": "Lerndienst ist nicht verfügbar."}
                )
            
            stats = learning_service.get_learning_stats()
            return stats
        
        except Exception as e:
            logger.error(f"Error in learning stats endpoint: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Fehler beim Abrufen der Lernstatistiken."}
            )
    
    @router.post("/learning/suggestions")
    async def get_code_suggestions(request: Request):
        """Get code suggestions based on learning."""
        try:
            if not learning_service:
                return {
                    "suggestions": [], 
                    "error": "Lerndienst ist nicht verfügbar."
                }
            
            data = await request.json()
            if not data:
                return {
                    "suggestions": [], 
                    "error": "Keine gültigen JSON-Daten empfangen"
                }
            
            code = data.get("code", "")
            language = data.get("language", "python")
            
            suggestions = learning_service.get_code_suggestions(code, language)
            
            return {
                "suggestions": suggestions,
                "language": language
            }
        
        except Exception as e:
            logger.error(f"Error in suggestions endpoint: {e}")
            return {
                "suggestions": [], 
                "error": "Fehler beim Generieren von Vorschlägen."
            }
    
    @router.post("/learning/feedback")
    async def submit_feedback(request: Request):
        """Submit feedback for chat messages to improve learning."""
        try:
            if not learning_service:
                return JSONResponse(
                    status_code=503,
                    content={"success": False, "error": "Lerndienst ist nicht verfügbar."}
                )
            
            data = await request.json()
            if not data:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Keine gültigen JSON-Daten empfangen"}
                )
            
            user_question = data.get("user_question", "")
            ai_response = data.get("ai_response", "")
            rating = data.get("rating", 3)
            
            # Validate rating
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Bewertung muss zwischen 1 und 5 liegen."}
                )
            
            learning_service.learn_from_chat(user_question, ai_response, rating)
            
            return {
                "success": True,
                "message": "Feedback erfolgreich gespeichert."
            }
        
        except Exception as e:
            logger.error(f"Error in feedback endpoint: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Fehler beim Speichern des Feedbacks."}
            )
    
    @router.get("/learning/languages")
    async def get_language_recommendations():
        """Get language usage recommendations."""
        try:
            if not learning_service:
                return {
                    "recommendations": [], 
                    "error": "Lerndienst ist nicht verfügbar."
                }
            
            recommendations = learning_service.get_language_recommendations()
            
            return {
                "recommendations": recommendations
            }
        
        except Exception as e:
            logger.error(f"Error in language recommendations endpoint: {e}")
            return {
                "recommendations": [], 
                "error": "Fehler beim Abrufen der Sprachempfehlungen."
            }
    
    @router.get("/health")
    async def health_check():
        """API health check endpoint."""
        health_status = {
            "status": "healthy",
            "services": {
                "ai_service": "available" if ai_service else "unavailable",
                "code_service": "available" if code_service else "unavailable",
                "learning_service": "available" if learning_service else "unavailable"
            }
        }
        
        # Determine overall status
        if not ai_service and not code_service:
            health_status["status"] = "degraded"
            return JSONResponse(status_code=503, content=health_status)
        
        return health_status
    
    @router.post("/generate_code_and_tests")
    async def generate_code_and_tests(request: Request):
        """Generate code and tests using Gemini AI."""
        try:
            data = await request.json()
            prompt = data.get("prompt")
            
            if not prompt:
                raise HTTPException(status_code=400, detail="Prompt fehlt")
            
            # Get AI config from app state
            ai_config = app.state.ai_config
            
            # Configure Gemini
            genai.configure(api_key=ai_config["GEMINI_API_KEY"])
            model = genai.GenerativeModel(ai_config["GEMINI_CODE_MODEL"])
            
            # Create prompt for code and test generation
            full_prompt = (
                f"Generiere eine Python-Funktion und die dazugehörigen pytest-Tests "
                f"für die folgende Aufgabe: '{prompt}'. "
                f"Die Ausgabe muss ausschließlich aus zwei Code-Blöcken bestehen: "
                f"Der erste Block enthält die Funktion, der zweite die Tests. "
                f"Beide Blöcke müssen mit ```python und ``` umschlossen sein."
            )
            
            # Generation configuration
            generation_config = GenerationConfig(
                temperature=ai_config["GEMINI_TEMPERATURE"],
                max_output_tokens=ai_config["GEMINI_MAX_TOKENS"]
            )
            
            # API call
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Parse result
            parts = response.text.split("```python")
            if len(parts) >= 3:
                # First part is empty, second is code, third is tests
                code_content = parts[1].replace("```", "").strip()
                tests_content = parts[2].replace("```", "").strip()
                
                return {
                    "code": code_content,
                    "tests": tests_content,
                    "prompt": prompt
                }
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Konnte Code und Tests nicht korrekt parsen"
                )
                
        except Exception as e:
            logger.error(f"Error in generate_code_and_tests endpoint: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Interner Serverfehler: {str(e)}"
            )
    
    return router