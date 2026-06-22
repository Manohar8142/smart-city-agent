"""
In-memory cache with TTL (Time To Live).

CONCEPT: Caching
- Store API responses temporarily in memory
- Serve from cache instead of calling API
- Expires after TTL (e.g., 5 minutes)

WHY Cache?
- Reduce API costs (fewer API calls)
- Faster responses (memory >> network)
- Reduce rate limit usage
- Better user experience

WHEN to Cache?
- Weather: 5-10 minutes (changes slowly)
- News: 15 minutes (updates periodically)
- Location: 24 hours (rarely changes)
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import hashlib
import json
from ...utils.logging import logger


class CacheManager:
    """
    In-memory cache with TTL support.

    CONCEPT: How it works
    - Key: hash of request parameters
    - Value: (cached_data, expiration_time)
    - On get: check if expired, return data or None
    """

    def __init__(self):
        """
        Initialize cache.

        CONCEPT: Why dict for cache?
        - O(1) lookup time (very fast)
        - Simple to implement
        - Good for single-process apps

        For multi-process: use Redis
        """
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        logger.debug("Cache manager initialized")

    def _make_key(self, **kwargs) -> str:
        """
        Create cache key from parameters.

        CONCEPT: Cache key design
        - Must be unique for unique requests
        - Same params → same key → cache hit
        - Use hash of sorted params for consistency

        Example:
            _make_key(city="London", units="metric")
            → "abc123..." (hash)
        """
        # Sort dict for consistent hashing
        key_str = json.dumps(kwargs, sort_keys=True)
        # Use SHA-256 for unique hash
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, ttl: int, **kwargs) -> Optional[Any]:
        """
        Get cached value if not expired.

        Args:
            ttl: Time to live in seconds (not used for get, just for consistency)
            **kwargs: Request parameters for cache key

        Returns:
            Cached data if valid, None if expired/missing

        CONCEPT: Cache expiration
        - Check current time vs expiration time
        - If expired, delete from cache (cleanup)
        - Return None to trigger API call
        """
        key = self._make_key(**kwargs)

        if key in self._cache:
            data, expiration = self._cache[key]

            # Check if expired
            if datetime.now() < expiration:
                logger.debug(f"Cache HIT: {key[:8]}...")
                return data
            else:
                # Expired, remove it
                logger.debug(f"Cache EXPIRED: {key[:8]}...")
                del self._cache[key]

        logger.debug(f"Cache MISS: {key[:8]}...")
        return None

    def set(self, data: Any, ttl: int, **kwargs):
        """
        Store data in cache with TTL.

        Args:
            data: Data to cache
            ttl: Time to live in seconds
            **kwargs: Request parameters for cache key

        CONCEPT: TTL (Time To Live)
        - Set expiration = now + TTL
        - Example: TTL=300 → expires in 5 minutes
        - Different data types need different TTLs
        """
        key = self._make_key(**kwargs)
        expiration = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = (data, expiration)
        logger.debug(f"Cache SET: {key[:8]}... (TTL: {ttl}s)")

    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        logger.debug("Cache cleared")

    def cleanup_expired(self):
        """
        Remove expired entries.

        CONCEPT: Cache maintenance
        - Over time, expired entries accumulate
        - Periodic cleanup frees memory
        - Call this in background task or on API calls
        """
        now = datetime.now()
        expired_keys = [
            key for key, (_, expiration) in self._cache.items() if now >= expiration
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics (for monitoring)"""
        total = len(self._cache)
        expired = sum(
            1 for _, expiration in self._cache.values() if datetime.now() >= expiration
        )
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
        }
