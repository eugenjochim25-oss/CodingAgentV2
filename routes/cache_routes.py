"""
🚀 AI Agent 2025 - Cache Management Routes
REST API endpoints for cache management and statistics.

Clean Code implementation with external references:
- RESTful API design patterns from Flask/FastAPI communities
- Cache management patterns from Redis/Memcached documentation
- Error handling from Flask best practices
"""
from flask import Blueprint, jsonify, request, current_app
from services.cache_service import get_cache_service
import logging


logger = logging.getLogger(__name__)


# Create blueprint for cache routes
cache_bp = Blueprint('cache', __name__, url_prefix='/api/cache')


@cache_bp.route('/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache statistics and information.
    
    Returns:
        JSON response with cache statistics
    """
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Abrufen der Cache-Statistiken'
        }), 500


@cache_bp.route('/clear', methods=['POST'])
def clear_cache():
    """
    Clear all cache entries.
    
    Returns:
        JSON response with operation result
    """
    try:
        cache_service = get_cache_service()
        cleared_count = cache_service.clear_all()
        
        logger.info(f"Cache cleared: {cleared_count} entries removed")
        
        return jsonify({
            'success': True,
            'message': f'Cache geleert: {cleared_count} Einträge entfernt',
            'cleared_count': cleared_count
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Leeren des Caches'
        }), 500


@cache_bp.route('/cleanup', methods=['POST'])
def cleanup_expired():
    """
    Remove expired cache entries.
    
    Returns:
        JSON response with cleanup result
    """
    try:
        cache_service = get_cache_service()
        removed_count = cache_service.cleanup_expired()
        
        logger.info(f"Cache cleanup: {removed_count} expired entries removed")
        
        return jsonify({
            'success': True,
            'message': f'Cache bereinigt: {removed_count} abgelaufene Einträge entfernt',
            'removed_count': removed_count
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up cache: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Bereinigen des Caches'
        }), 500


@cache_bp.route('/invalidate', methods=['POST'])
def invalidate_cache_entry():
    """
    Invalidate specific cache entry by key.
    
    Request JSON:
        {
            "cache_key": "string"
        }
    
    Returns:
        JSON response with invalidation result
    """
    try:
        data = request.get_json()
        if not data or 'cache_key' not in data:
            return jsonify({
                'success': False,
                'error': 'Cache-Schlüssel ist erforderlich'
            }), 400
        
        cache_key = data['cache_key']
        cache_service = get_cache_service()
        
        invalidated = cache_service.invalidate(cache_key)
        
        if invalidated:
            return jsonify({
                'success': True,
                'message': f'Cache-Eintrag invalidiert: {cache_key[:8]}...'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Cache-Eintrag nicht gefunden: {cache_key[:8]}...'
            }), 404
            
    except Exception as e:
        logger.error(f"Error invalidating cache entry: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Invalidieren des Cache-Eintrags'
        }), 500


@cache_bp.route('/config', methods=['GET'])
def get_cache_config():
    """
    Get current cache configuration.
    
    Returns:
        JSON response with cache configuration
    """
    try:
        cache_service = get_cache_service()
        
        config = {
            'caching_enabled': True,
            'cache_directory': str(cache_service.cache_dir),
            'max_cache_size_mb': round(cache_service.max_cache_size_bytes / (1024 * 1024), 2),
            'default_ttl_hours': round(cache_service.default_ttl_seconds / 3600, 2)
        }
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        logger.error(f"Error getting cache config: {e}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Abrufen der Cache-Konfiguration'
        }), 500