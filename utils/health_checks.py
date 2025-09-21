import logging
import time
from typing import Dict, Any, Optional
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class HealthChecker:
    """Health check utilities for external dependencies."""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def check_openai_connection(self, timeout: int = 5) -> Dict[str, Any]:
        """
        Check OpenAI API connectivity.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Health check result
        """
        start_time = time.time()
        
        try:
            api_key = self.config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
            
            if not api_key:
                return {
                    'status': 'unhealthy',
                    'message': 'OpenAI API key not configured',
                    'response_time': 0,
                    'error': 'Missing API key'
                }
            
            client = OpenAI(api_key=api_key)
            
            # Make a minimal request to test connectivity
            response = client.chat.completions.create(
                model=self.config.get('OPENAI_MODEL', 'gpt-4'),
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'message': 'OpenAI API is accessible',
                'response_time': round(response_time, 3),
                'model': self.config.get('OPENAI_MODEL', 'gpt-4')
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.warning(f"OpenAI health check failed: {e}")
            
            return {
                'status': 'unhealthy',
                'message': 'OpenAI API is not accessible',
                'response_time': round(response_time, 3),
                'error': str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource availability.
        
        Returns:
            System resource status
        """
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'status': 'healthy',
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': round((disk.used / disk.total) * 100, 1)
                }
            }
            
        except ImportError:
            # psutil not available, provide basic info
            return {
                'status': 'limited',
                'message': 'System monitoring not available (psutil not installed)',
                'basic_check': 'Application is running'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'System check failed: {str(e)}'
            }
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Complete health status
        """
        start_time = time.time()
        
        checks = {
            'openai': self.check_openai_connection(),
            'system': self.check_system_resources(),
            'timestamp': time.time(),
            'application': {
                'status': 'healthy',
                'uptime': time.time() - start_time
            }
        }
        
        # Determine overall health
        overall_status = 'healthy'
        if checks['openai']['status'] == 'unhealthy':
            overall_status = 'degraded'
        
        checks['overall_status'] = overall_status
        checks['total_check_time'] = round(time.time() - start_time, 3)
        
        return checks

def quick_health_check(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick health check function.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Health status
    """
    checker = HealthChecker(config)
    return {
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'openai': 'available' if config and config.get('OPENAI_API_KEY') else 'unavailable',
            'code_execution': 'enabled' if config and config.get('code_execution_enabled') else 'disabled'
        }
    }