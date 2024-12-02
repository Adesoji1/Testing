# app/core/cache.py

from functools import wraps
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from cachetools import TTLCache
import hashlib
import json

# Initialize cache with 1 hour TTL and 100 items max
_cache = TTLCache(maxsize=100, ttl=3600)

def get_cache_key(*args, **kwargs) -> str:
    """Generate a unique cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cache_response(
    ttl: int = 3600,
    prefix: str = "",
    key_builder: Optional[Callable] = None
):
    """Cache decorator for function responses."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = get_cache_key(*args, **kwargs)
            
            if prefix:
                cache_key = f"{prefix}:{cache_key}"

            # Check cache
            if cache_key in _cache:
                return _cache[cache_key]

            # Get fresh result
            result = await func(*args, **kwargs)
            _cache[cache_key] = result
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str = None):
    """Invalidate cache entries matching pattern."""
    if pattern:
        keys_to_delete = [
            k for k in _cache.keys()
            if pattern in k
        ]
        for k in keys_to_delete:
            _cache.pop(k, None)
    else:
        _cache.clear()

def get_cache():
    """Get cache instance."""
    return _cache

def set_cache_item(key: str, value: Any, ttl: int = 3600):
    """Set cache item with optional TTL."""
    _cache[key] = value

def get_cache_item(key: str) -> Optional[Any]:
    """Get cache item."""
    return _cache.get(key)

def delete_cache_item(key: str):
    """Delete cache item."""
    _cache.pop(key, None)