"""
Centralized caching service for AI results and intermediate computations.
Improves performance by caching expensive AI operations.
"""
import hashlib
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("maljrs.cache")


class CacheService:
    """
    In-memory caching service for AI processing results.
    
    In production, this could be replaced with Redis or similar.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache service.
        
        Args:
            default_ttl: Default time-to-live for cache entries (seconds)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0
        }
    
    def generate_cache_key(self, data: dict, prefix: str = "") -> str:
        """
        Generate cache key from data dict.
        
        Args:
            data: Data to hash
            prefix: Optional prefix for key
            
        Returns:
            SHA256 hash string
        """
        json_str = json.dumps(data, sort_keys=True)
        hash_value = hashlib.sha256(json_str.encode()).hexdigest()
        return f"{prefix}:{hash_value}" if prefix else hash_value
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        if key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if entry["expires_at"] < datetime.now():
            del self._cache[key]
            self._stats["evictions"] += 1
            self._stats["misses"] += 1
            logger.debug(f"Cache key expired: {key[:16]}...")
            return None
        
        self._stats["hits"] += 1
        logger.debug(f"Cache hit: {key[:16]}... (age: {entry['age_seconds']}s)")
        return entry["data"]
    
    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None):
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl or self.default_ttl
        self._cache[key] = {
            "data": data,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "age_seconds": 0
        }
        self._stats["sets"] += 1
        logger.debug(f"Cached result: {key[:16]}... (TTL: {ttl}s)")
    
    def invalidate(self, key: str):
        """Remove specific cache entry"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Invalidated cache: {key[:16]}...")
    
    def invalidate_prefix(self, prefix: str):
        """Remove all cache entries with given prefix"""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
        for key in keys_to_remove:
            del self._cache[key]
        logger.debug(f"Invalidated {len(keys_to_remove)} entries with prefix: {prefix}")
    
    def clear(self):
        """Clear entire cache"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared cache ({count} entries)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_entries": len(self._cache),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate_percent": round(hit_rate, 2),
            "sets": self._stats["sets"],
            "evictions": self._stats["evictions"]
        }
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry["expires_at"] < now
        ]
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


# Global cache instance
_global_cache = None

def get_cache_service() -> CacheService:
    """Get or create global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheService(default_ttl=3600)  # 1 hour default
    return _global_cache
