"""
🚀 AI Agent 2025 - Cache Service
Hash-based file caching system for code execution results.

Clean Code implementation with external references:
- Redis caching patterns for key generation
- File-based cache strategies from Django/Flask communities
- Hash-based deduplication techniques
"""
import os
import json
import hashlib
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class CacheService:
    """
    Production-ready file-based cache service for code execution results.
    
    Features:
    - Hash-based cache keys (SHA-256)
    - Code + Input deduplication
    - Automatic cleanup and expiration
    - Thread-safe file operations
    - Cache statistics and monitoring
    """
    
    def __init__(self, cache_dir: str = "cache", max_cache_size_mb: int = 100, 
                 default_ttl_hours: int = 24):
        """
        Initialize cache service with configurable parameters.
        
        Args:
            cache_dir: Directory for cache files
            max_cache_size_mb: Maximum cache size in MB
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.default_ttl_seconds = default_ttl_hours * 3600
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'cleanups': 0
        }
        
        logger.info(f"✅ Cache Service initialized: {self.cache_dir}")
    
    def generate_cache_key(self, code: str, language: str = 'python', 
                          inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate SHA-256 hash-based cache key for code + inputs.
        
        Args:
            code: Source code to execute
            language: Programming language
            inputs: Additional execution inputs/parameters
            
        Returns:
            Hexadecimal hash string as cache key
        """
        # Normalize inputs for consistent hashing
        normalized_inputs = inputs or {}
        
        # Create deterministic string for hashing
        cache_content = {
            'code': code.strip(),
            'language': language.lower(),
            'inputs': sorted(normalized_inputs.items()) if normalized_inputs else []
        }
        
        # Generate SHA-256 hash
        content_string = json.dumps(cache_content, sort_keys=True, separators=(',', ':'))
        hash_object = hashlib.sha256(content_string.encode('utf-8'))
        
        return hash_object.hexdigest()
    
    def get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached execution result.
        
        Args:
            cache_key: Hash-based cache key
            
        Returns:
            Cached result dictionary or None if not found/expired
        """
        cache_path = self.get_cache_path(cache_key)
        
        try:
            if not cache_path.exists():
                self.stats['misses'] += 1
                return None
            
            # Read and validate cache file
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration
            expiry_time = cache_data.get('expires_at', 0)
            if time.time() > expiry_time:
                # Cache expired - remove file
                cache_path.unlink(missing_ok=True)
                self.stats['misses'] += 1
                logger.debug(f"Cache expired: {cache_key}")
                return None
            
            # Cache hit
            self.stats['hits'] += 1
            logger.debug(f"Cache hit: {cache_key}")
            return cache_data.get('result')
            
        except (json.JSONDecodeError, IOError, KeyError) as e:
            # Corrupted cache file - remove it
            cache_path.unlink(missing_ok=True)
            self.stats['misses'] += 1
            logger.warning(f"Corrupted cache file removed: {cache_key} - {e}")
            return None
    
    def set(self, cache_key: str, result: Dict[str, Any], 
            ttl_seconds: Optional[int] = None) -> bool:
        """
        Store execution result in cache.
        
        Args:
            cache_key: Hash-based cache key
            result: Execution result to cache
            ttl_seconds: Time-to-live override
            
        Returns:
            True if successfully cached, False otherwise
        """
        cache_path = self.get_cache_path(cache_key)
        ttl = ttl_seconds or self.default_ttl_seconds
        
        try:
            # Prepare cache data with metadata
            cache_data = {
                'result': result,
                'cached_at': time.time(),
                'expires_at': time.time() + ttl,
                'cache_key': cache_key,
                'ttl_seconds': ttl
            }
            
            # Write cache file atomically
            temp_path = cache_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            # Atomic move
            temp_path.rename(cache_path)
            
            self.stats['writes'] += 1
            logger.debug(f"Cache stored: {cache_key}")
            
            # Check cache size and cleanup if needed
            self._check_cache_size()
            
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to write cache: {cache_key} - {e}")
            return False
    
    def invalidate(self, cache_key: str) -> bool:
        """
        Remove specific cache entry.
        
        Args:
            cache_key: Cache key to invalidate
            
        Returns:
            True if invalidated, False if not found
        """
        cache_path = self.get_cache_path(cache_key)
        
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Cache invalidated: {cache_key}")
            return True
        
        return False
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                expires_at = cache_data.get('expires_at', 0)
                if current_time > expires_at:
                    cache_file.unlink()
                    removed_count += 1
                    
            except (json.JSONDecodeError, IOError, KeyError):
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)
                removed_count += 1
        
        if removed_count > 0:
            self.stats['cleanups'] += 1
            logger.info(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    def _check_cache_size(self) -> None:
        """Check cache size and cleanup oldest entries if needed."""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        
        if total_size > self.max_cache_size_bytes:
            # Get all cache files sorted by modification time (oldest first)
            cache_files = sorted(
                self.cache_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime
            )
            
            # Remove oldest files until under limit
            removed_count = 0
            for cache_file in cache_files:
                if total_size <= self.max_cache_size_bytes * 0.8:  # 80% threshold
                    break
                
                file_size = cache_file.stat().st_size
                cache_file.unlink(missing_ok=True)
                total_size -= file_size
                removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cache size cleanup: removed {removed_count} files")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics and information.
        
        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        hit_rate = (
            self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])
            if (self.stats['hits'] + self.stats['misses']) > 0 else 0
        )
        
        return {
            'stats': self.stats.copy(),
            'hit_rate': round(hit_rate * 100, 2),
            'total_entries': len(cache_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_size_mb': round(self.max_cache_size_bytes / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
    
    def clear_all(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries removed
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        removed_count = 0
        
        for cache_file in cache_files:
            try:
                cache_file.unlink()
                removed_count += 1
            except OSError:
                pass
        
        # Reset statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'cleanups': 0
        }
        
        logger.info(f"Cache cleared: {removed_count} entries removed")
        return removed_count


# Global cache service instance
_cache_service = None


def get_cache_service() -> CacheService:
    """Get or create global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service