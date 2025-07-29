import time
import json
import os
from typing import Any, Dict, Optional, Union
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache with TTL and size limits - no Redis needed!"""
    
    def __init__(self, max_size_mb: int = 512, ttl_seconds: int = 3600):
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._size_bytes = 0
        self._max_size_bytes = max_size_mb * 1024 * 1024
        
    def _get_size(self, obj: Any) -> int:
        """Estimate size of object in bytes"""
        try:
            return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            return 1024  # Default estimate
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > self.ttl_seconds
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items()
            if self._is_expired(value['timestamp'])
        ]
        for key in expired_keys:
            self._remove_entry(key)
    
    def _remove_entry(self, key: str):
        """Remove a specific entry and update size"""
        if key in self._cache:
            entry = self._cache[key]
            self._size_bytes -= entry['size']
            del self._cache[key]
    
    def _evict_if_needed(self):
        """Evict oldest entries if cache is too large"""
        while self._size_bytes > self._max_size_bytes and self._cache:
            oldest_key = next(iter(self._cache))
            self._remove_entry(oldest_key)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        self._cleanup_expired()
        
        if key in self._cache:
            entry = self._cache[key]
            if not self._is_expired(entry['timestamp']):
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                logger.debug(f"Cache hit: {key}")
                return entry['value']
            else:
                self._remove_entry(key)
        
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache"""
        self._cleanup_expired()
        
        # Remove existing entry if present
        if key in self._cache:
            self._remove_entry(key)
        
        # Calculate size
        size = self._get_size(value)
        
        # Check if we can fit this entry
        if size > self._max_size_bytes:
            logger.warning(f"Entry too large for cache: {key} ({size} bytes)")
            return False
        
        # Evict if needed
        self._evict_if_needed()
        
        # Add entry
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        self._cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl,
            'size': size
        }
        self._size_bytes += size
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        
        logger.debug(f"Cache set: {key} ({size} bytes)")
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            self._remove_entry(key)
            logger.debug(f"Cache delete: {key}")
            return True
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._size_bytes = 0
        logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        self._cleanup_expired()
        return {
            'size_bytes': self._size_bytes,
            'max_size_bytes': self._max_size_bytes,
            'entry_count': len(self._cache),
            'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1),
            'memory_usage_mb': self._size_bytes / (1024 * 1024)
        }
    
    def keys(self) -> list:
        """Get all cache keys"""
        self._cleanup_expired()
        return list(self._cache.keys())


class FileCache:
    """Simple file-based cache for persistent storage"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_filepath(self, key: str) -> str:
        """Get file path for cache key"""
        # Create a safe filename from the key
        safe_key = "".join(c for c in key if c.isalnum() or c in ('-', '_')).rstrip()
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache"""
        try:
            filepath = self._get_filepath(key)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Check if expired
                    if time.time() - data['timestamp'] < data['ttl']:
                        return data['value']
                    else:
                        # Remove expired file
                        os.remove(filepath)
        except Exception as e:
            logger.warning(f"Error reading cache file for {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set value in file cache"""
        try:
            filepath = self._get_filepath(key)
            data = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl_seconds
            }
            with open(filepath, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            logger.warning(f"Error writing cache file for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from file cache"""
        try:
            filepath = self._get_filepath(key)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            logger.warning(f"Error deleting cache file for {key}: {e}")
        return False
    
    def clear(self):
        """Clear all cache files"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")


# Global cache instances
memory_cache = SimpleCache()
file_cache = FileCache()

def get_cache(cache_type: str = "memory") -> Union[SimpleCache, FileCache]:
    """Get cache instance by type"""
    if cache_type == "file":
        return file_cache
    return memory_cache 