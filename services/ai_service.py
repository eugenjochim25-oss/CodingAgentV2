import os
import logging
from typing import Optional
import json

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

logger = logging.getLogger(__name__)

class AIService:
    """Service for handling AI chat interactions using Google Gemini AI."""
    
    def __init__(self, config=None):
        if config:
            api_key = config.get('GEMINI_API_KEY')
            self.model = config.get('GEMINI_MODEL', 'gemini-2.5-flash')
            self.max_tokens = config.get('GEMINI_MAX_TOKENS', 500)
            self.temperature = config.get('GEMINI_TEMPERATURE', 0.7)
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            self.model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
            self.max_tokens = int(os.environ.get('GEMINI_MAX_TOKENS', '500'))
            self.temperature = float(os.environ.get('GEMINI_TEMPERATURE', '0.7'))
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Gemini library not available. Install with: pip install google-genai")
        
        self.client = genai.Client(api_key=api_key)
    
    def generate_response(self, user_message: str, conversation_history: Optional[list] = None) -> str:
        """
        Generate an AI response to the user's message using Gemini AI.
        
        Args:
            user_message: The user's input message
            conversation_history: Optional list of previous messages for context
            
        Returns:
            AI-generated response string
        """
        try:
            # Build conversation context with system instruction
            system_instruction = ("Du bist ein hilfsreicher KI-Assistent und Code-Experte. "
                                "Antworte auf Deutsch und sei freundlich und professionell. "
                                "Hilf bei Programmieraufgaben und beantworte Fragen präzise.")
            
            # Build conversation content
            conversation_content = []
            
            # Add conversation history if available with robust None checks
            if conversation_history and isinstance(conversation_history, list):
                for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                    if msg and isinstance(msg, dict):
                        role = msg.get('role', 'user')
                        content = msg.get('content', '')
                        if content:  # Only add if content is not empty
                            if role == 'user':
                                conversation_content.append(f"User: {content}")
                            elif role == 'assistant':
                                conversation_content.append(f"Assistant: {content}")
            
            # Add current user message
            conversation_content.append(f"User: {user_message}")
            
            # Combine all content
            full_prompt = "\n".join(conversation_content)
            
            # Use Replit-blueprint recommended approach with higher token limit
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=self.temperature,
                    max_output_tokens=min(2000, self.max_tokens * 4)  # Increase token limit
                )
            )
            
            # Simple response handling as per Replit blueprint
            if response.text:
                return response.text.strip()
            else:
                logger.warning(f"Empty response from Gemini: {response}")
                return "Entschuldigung, ich erhielt eine leere Antwort. Bitte versuchen Sie eine andere Formulierung."
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Anfrage: {str(e)}"
    
    def analyze_code(self, code: str) -> str:
        """
        Analyze code and provide feedback using Gemini AI.
        
        Args:
            code: The code to analyze
            
        Returns:
            Analysis and feedback string
        """
        try:
            system_instruction = ("Du bist ein Experte für Code-Analyse. Analysiere den gegebenen Code "
                                "und gib konstruktives Feedback zu Verbesserungen, Fehlern oder "
                                "Optimierungsmöglichkeiten. Antworte auf Deutsch.")
            
            prompt = f"Bitte analysiere diesen Code:\n\n```python\n{code}\n```"
            
            # Use Replit-blueprint recommended approach with higher token limit  
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    max_output_tokens=min(1500, self.max_tokens * 3)  # Increase for code analysis
                )
            )
            
            # Simple response handling as per Replit blueprint
            if response.text:
                return response.text.strip()
            else:
                logger.warning(f"Empty response from Gemini for code analysis: {response}")
                return "Code-Analyse konnte nicht abgeschlossen werden. Bitte versuchen Sie kürzeren Code."
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return f"Fehler bei der Code-Analyse: {str(e)}"