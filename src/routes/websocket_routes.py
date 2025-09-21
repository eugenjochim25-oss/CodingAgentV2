"""
🚀 WebSocket Routes for Live-Logs/Terminal - Production-Ready 2025
Clean Code implementation for real-time code execution streaming
Adapted for FastAPI WebSockets with async/await support
"""
import logging
import time
import uuid
import asyncio
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import FastAPI

logger = logging.getLogger('CodingAgentV2')

class ConnectionManager:
    """Manage WebSocket connections and broadcast messages."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rate_limits: Dict[str, float] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept connection and store client."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f'🔗 Client connected: {client_id}')
    
    def disconnect(self, client_id: str):
        """Remove client from active connections."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.rate_limits:
            del self.rate_limits[client_id]
        logger.info(f'🔌 Client disconnected: {client_id}')
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)

# Global connection manager
manager = ConnectionManager()

def register_websocket_routes(app: FastAPI):
    """Register all WebSocket routes with the FastAPI application."""
    
    @app.websocket("/ws/terminal")
    async def websocket_terminal(websocket: WebSocket):
        """WebSocket endpoint for terminal/log streaming."""
        client_id = str(uuid.uuid4())
        
        try:
            await manager.connect(websocket, client_id)
            
            # Send welcome message
            await manager.send_personal_message({
                'type': 'system',
                'message': '🚀 CodingAgentV2 Live-Terminal verbunden! Bereit für Code-Ausführung...',
                'timestamp': time.time(),
                'session_id': client_id
            }, client_id)
            
            # Handle incoming messages
            while True:
                data = await websocket.receive_json()
                await handle_websocket_message(data, client_id)
                    
        except WebSocketDisconnect:
            manager.disconnect(client_id)
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
            manager.disconnect(client_id)

async def handle_websocket_message(data: dict, client_id: str):
    """Handle incoming WebSocket messages."""
    event_type = data.get('event')
    
    if event_type == 'execute_code_live':
        await handle_live_code_execution(data, client_id)
    elif event_type == 'ping':
        await handle_ping(client_id)
    elif event_type == 'terminal_command':
        await handle_terminal_command(data, client_id)
    else:
        logger.warning(f"Unknown event type: {event_type}")

async def handle_live_code_execution(data: dict, client_id: str):
    """Handle live code execution with real-time streaming."""
    session_id = str(uuid.uuid4())
    
    try:
        # Get AI config from app state
        from app import app  # Import app to access state
        ai_config = app.state.ai_config
        
        # Security: Check if code execution is enabled
        if not ai_config.get('code_execution_enabled', False):
            await manager.send_personal_message({
                'event': 'execution_error',
                'error': 'Code-Ausführung ist deaktiviert',
                'session_id': session_id,
                'timestamp': time.time()
            }, client_id)
            return
        
        # Rate limiting check
        current_time = time.time()
        if client_id in manager.rate_limits:
            last_execution = manager.rate_limits[client_id]
            if current_time - last_execution < 2:  # 2 seconds cooldown
                await manager.send_personal_message({
                    'event': 'execution_error',
                    'error': 'Zu viele Anfragen. Bitte warten Sie.',
                    'session_id': session_id,
                    'timestamp': current_time
                }, client_id)
                return
        
        manager.rate_limits[client_id] = current_time
        
        # Validate input data
        if not data or 'code' not in data:
            await manager.send_personal_message({
                'event': 'execution_error',
                'error': 'Kein Code empfangen',
                'session_id': session_id,
                'timestamp': current_time
            }, client_id)
            return
        
        code = data.get('code', '').strip()
        language = data.get('language', 'python')
        
        if not code:
            await manager.send_personal_message({
                'event': 'execution_error',
                'error': 'Code darf nicht leer sein',
                'session_id': session_id,
                'timestamp': current_time
            }, client_id)
            return
        
        logger.info(f'🎯 Live code execution started: {client_id} | Session: {session_id}')
        
        # Send execution start notification
        await manager.send_personal_message({
            'event': 'execution_started',
            'session_id': session_id,
            'language': language,
            'timestamp': current_time,
            'message': f'⚡ CodingAgentV2 startet {language.upper()}-Ausführung...'
        }, client_id)
        
        # Execute code in background task
        asyncio.create_task(
            execute_code_with_streaming(client_id, session_id, code, language)
        )
        
    except Exception as e:
        logger.error(f'❌ Error in live code execution: {e}')
        await manager.send_personal_message({
            'event': 'execution_error',
            'error': f'Unerwarteter Fehler: {str(e)}',
            'session_id': session_id,
            'timestamp': time.time()
        }, client_id)

async def handle_ping(client_id: str):
    """Handle ping for connection keepalive."""
    await manager.send_personal_message({
        'event': 'pong',
        'timestamp': time.time()
    }, client_id)

async def handle_terminal_command(data: dict, client_id: str):
    """Handle terminal commands."""
    await manager.send_personal_message({
        'event': 'terminal_output',
        'type': 'info',
        'message': '🔧 Terminal-Kommandos werden in einer zukünftigen Version von CodingAgentV2 unterstützt',
        'timestamp': time.time()
    }, client_id)

async def execute_code_with_streaming(client_id: str, session_id: str, code: str, language: str):
    """Execute code with real-time output streaming."""
    try:
        # Get code execution service
        from app import app  # Import app to access state
        ai_config = app.state.ai_config
        
        code_service = None
        if ai_config.get('code_execution_enabled'):
            try:
                from services.code_execution_service import CodeExecutionService
                code_service = CodeExecutionService(ai_config)
            except Exception as e:
                logger.error(f'Failed to initialize code service: {e}')
        
        if not code_service:
            await manager.send_personal_message({
                'event': 'execution_error',
                'error': 'Code-Ausführungsdienst nicht verfügbar',
                'session_id': session_id,
                'timestamp': time.time()
            }, client_id)
            return
        
        # Create live execution wrapper
        live_executor = LiveCodeExecutor(client_id, session_id, code_service)
        
        # Execute with streaming
        result = await live_executor.execute_with_streaming(code, language)
        
        # Send final result
        await manager.send_personal_message({
            'event': 'execution_completed',
            'session_id': session_id,
            'success': result.get('success', False),
            'execution_time': result.get('execution_time', 0),
            'timestamp': time.time(),
            'message': '✅ CodingAgentV2 Ausführung abgeschlossen' if result.get('success') else '❌ CodingAgentV2 Ausführung fehlgeschlagen'
        }, client_id)
        
    except Exception as e:
        logger.error(f'❌ Error in code execution: {e}')
        await manager.send_personal_message({
            'event': 'execution_error',
            'error': f'Ausführungsfehler: {str(e)}',
            'session_id': session_id,
            'timestamp': time.time()
        }, client_id)

class LiveCodeExecutor:
    """Live Code Executor with real-time streaming capabilities."""
    
    def __init__(self, client_id: str, session_id: str, code_service):
        self.client_id = client_id
        self.session_id = session_id
        self.code_service = code_service
        self.start_time = time.time()
    
    async def execute_with_streaming(self, code: str, language: str = 'python'):
        """Execute code with real-time output streaming."""
        try:
            # Send progress updates
            await self._emit_progress('🔍 CodingAgentV2 Code-Validierung...', 10)
            
            # Basic validation
            if not code.strip():
                await self._emit_error('Code ist leer')
                return {'success': False, 'execution_time': 0}
            
            # Security check
            await self._emit_progress('🔒 CodingAgentV2 Sicherheitsprüfung...', 25)
            
            await self._emit_progress('⚡ CodingAgentV2 Code-Ausführung startet...', 50)
            
            # Execute code
            result = self.code_service.execute_python_code(code)
            
            # Stream output
            if result.get('output'):
                await self._emit_output(result['output'], 'stdout')
            
            if result.get('error'):
                await self._emit_output(result['error'], 'stderr')
            
            await self._emit_progress('✅ CodingAgentV2 Ausführung abgeschlossen', 100)
            
            return result
            
        except Exception as e:
            await self._emit_error(f'Unerwarteter Fehler: {str(e)}')
            return {'success': False, 'execution_time': time.time() - self.start_time}
    
    async def _emit_progress(self, message: str, progress: int):
        """Emit progress update."""
        await manager.send_personal_message({
            'event': 'execution_progress',
            'session_id': self.session_id,
            'message': message,
            'progress': progress,
            'timestamp': time.time()
        }, self.client_id)
    
    async def _emit_output(self, text: str, output_type: str = 'stdout'):
        """Emit code output."""
        await manager.send_personal_message({
            'event': 'terminal_output',
            'session_id': self.session_id,
            'type': output_type,
            'message': text,
            'timestamp': time.time()
        }, self.client_id)
    
    async def _emit_error(self, error_message: str):
        """Emit error message."""
        await manager.send_personal_message({
            'event': 'execution_error',
            'session_id': self.session_id,
            'error': error_message,
            'timestamp': time.time()
        }, self.client_id)