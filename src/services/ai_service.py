# src/services/ai_service.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env
load_dotenv()

class AIService:
    """
    Zentrale KI-Service-Klasse, die die Kommunikation mit dem Gemini-API übernimmt.
    """

    def __init__(self, config=None):
        # Verwende entweder das übergebene Config-Objekt oder lade direkt aus .env
        if config:
            self.api_key = config.get("GEMINI_API_KEY")
            self.model_name = config.get("GEMINI_CODE_MODEL", "gemini-1.5-pro")
        else:
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

        if not self.api_key:
            raise ValueError("❌ Kein GEMINI_API_KEY in .env gefunden!")

        # Gemini SDK konfigurieren
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def run(self, prompt: str) -> str:
        """
        Führt einen Prompt über Gemini aus und gibt die Antwort zurück.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            return f"❌ Fehler bei AI-Abfrage: {str(e)}"
    
    def generate_response(self, user_message: str, conversation_history: list) -> str:
        """
        Generiert eine AI-Antwort basierend auf der Benutzernachricht und Konversationshistorie.
        """
        # Bauen Sie den Prompt aus der Konversationshistorie und der aktuellen Nachricht
        prompt = self._build_prompt(conversation_history, user_message)
        return self.run(prompt)
    
    def analyze_code(self, code: str) -> str:
        """
        Analysiert den gegebenen Code und gibt Feedback.
        """
        prompt = f"""
        Analysiere den folgenden Code und gib Feedback:
        - Verbesserungsvorschläge
        - Mögliche Fehler
        - Best Practices
        
        Code:
        ```python
        {code}
        ```
        """
        return self.run(prompt)
    
    def _build_prompt(self, history: list, current_message: str) -> str:
        """
        Baut einen Prompt aus der Konversationshistorie und der aktuellen Nachricht.
        """
        prompt = ""
        
        for message in history:
            if message.get('role') == 'user':
                prompt += f"User: {message.get('content', '')}\n"
            else:
                prompt += f"Assistant: {message.get('content', '')}\n"
        
        prompt += f"User: {current_message}\nAssistant:"
        return prompt


# Globale Instanz (Singleton-Pattern)
# Diese wird nicht mehr verwendet, da wir Dependency Injection verwenden
# _ai_service = AIService()

def get_ai_service():
    """
    Gibt eine neue AIService-Instanz zurück.
    Wird für Dependency Injection verwendet.
    """
    from src.config.settings import get_settings
    settings = get_settings()
    return AIService(settings)