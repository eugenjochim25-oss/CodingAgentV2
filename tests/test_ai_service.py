import pytest
import os
from unittest.mock import Mock, patch
from services.ai_service import AIService

class TestAIService:
    """Test cases for AIService."""
    
    def setup_method(self):
        """Set up test environment."""
        # Mock the OpenAI API key
        os.environ['OPENAI_API_KEY'] = 'test-key'
    
    def test_init_without_api_key(self):
        """Test AIService initialization without API key."""
        # Remove API key
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            AIService()
    
    @patch('services.ai_service.OpenAI')
    def test_init_with_api_key(self, mock_openai):
        """Test AIService initialization with API key."""
        service = AIService()
        
        # Verify OpenAI client was created with correct API key
        mock_openai.assert_called_once_with(api_key='test-key')
        assert service.model == "gpt-5"
    
    @patch('services.ai_service.OpenAI')
    def test_generate_response_success(self, mock_openai):
        """Test successful response generation."""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = AIService()
        response = service.generate_response("Test message")
        
        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('services.ai_service.OpenAI')
    def test_generate_response_with_history(self, mock_openai):
        """Test response generation with conversation history."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response with context"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = AIService()
        history = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"}
        ]
        
        response = service.generate_response("Current message", history)
        
        assert response == "Response with context"
        
        # Verify the messages passed to OpenAI include history
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        
        assert len(messages) >= 3  # System + history + current
        assert messages[-1]['content'] == "Current message"
    
    @patch('services.ai_service.OpenAI')
    def test_generate_response_error_handling(self, mock_openai):
        """Test error handling in response generation."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        service = AIService()
        response = service.generate_response("Test message")
        
        assert "Entschuldigung, es gab einen Fehler" in response
    
    @patch('services.ai_service.OpenAI')
    def test_analyze_code_success(self, mock_openai):
        """Test successful code analysis."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Code analysis result"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        service = AIService()
        analysis = service.analyze_code("print('hello')")
        
        assert analysis == "Code analysis result"
    
    @patch('services.ai_service.OpenAI')
    def test_analyze_code_error_handling(self, mock_openai):
        """Test error handling in code analysis."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        service = AIService()
        analysis = service.analyze_code("print('hello')")
        
        assert "Fehler bei der Code-Analyse" in analysis