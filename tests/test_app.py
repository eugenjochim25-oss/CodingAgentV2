import pytest
import os
from unittest.mock import patch, Mock
from app import create_app

class TestApp:
    """Test cases for Flask application."""
    
    def setup_method(self):
        """Set up test environment."""
        # Mock the OpenAI API key
        os.environ['OPENAI_API_KEY'] = 'test-key'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_home_page(self):
        """Test the home page loads correctly."""
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'Ultimate AI Agent' in response.data
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'AI Agent'
    
    def test_404_error_handler(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        data = response.get_json()
        assert 'nicht gefunden' in data['error']
    
    @patch('routes.api_routes.ai_service')
    def test_chat_endpoint_success(self, mock_ai_service):
        """Test successful chat endpoint."""
        # Mock AI service response
        mock_ai_service.generate_response.return_value = "Test AI response"
        
        response = self.client.post('/api/chat', 
                                   json={'message': 'Hello AI'},
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['response'] == 'Test AI response'
        assert 'timestamp' in data
    
    def test_chat_endpoint_empty_message(self):
        """Test chat endpoint with empty message."""
        response = self.client.post('/api/chat',
                                   json={'message': ''},
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'nicht leer sein' in data['error']
    
    def test_chat_endpoint_no_json(self):
        """Test chat endpoint without JSON data."""
        response = self.client.post('/api/chat')
        
        assert response.status_code == 500  # Flask returns 500 for content-type issues
        data = response.get_json()
        assert 'error' in data
    
    @patch('routes.api_routes.code_service')
    def test_execute_endpoint_success(self, mock_code_service):
        """Test successful code execution endpoint."""
        # Mock code service response
        mock_code_service.execute_python_code.return_value = {
            'success': True,
            'output': 'Hello, World!',
            'error': '',
            'execution_time': 0.1
        }
        
        response = self.client.post('/api/execute',
                                   json={'code': 'print("Hello, World!")'},
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['output'] == 'Hello, World!'
    
    def test_execute_endpoint_empty_code(self):
        """Test execute endpoint with empty code."""
        response = self.client.post('/api/execute',
                                   json={'code': ''},
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'nicht leer sein' in data['error']
    
    @patch('routes.api_routes.ai_service')
    def test_analyze_endpoint_success(self, mock_ai_service):
        """Test successful code analysis endpoint."""
        # Mock AI service response
        mock_ai_service.analyze_code.return_value = "Code analysis result"
        
        response = self.client.post('/api/analyze',
                                   json={'code': 'print("test")'},
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['analysis'] == 'Code analysis result'
        assert 'timestamp' in data
    
    def test_analyze_endpoint_empty_code(self):
        """Test analyze endpoint with empty code."""
        response = self.client.post('/api/analyze',
                                   json={'code': ''},
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'nicht leer sein' in data['error']
    
    @patch('routes.api_routes.ai_service')
    def test_chat_endpoint_ai_service_error(self, mock_ai_service):
        """Test chat endpoint when AI service raises an error."""
        # Mock AI service to raise an exception
        mock_ai_service.generate_response.side_effect = Exception("AI Service Error")
        
        response = self.client.post('/api/chat',
                                   json={'message': 'Hello AI'},
                                   content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'Ein Fehler ist aufgetreten' in data['error']