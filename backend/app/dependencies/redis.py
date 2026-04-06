"""
Redis client dependency for caching
"""
import os
from typing import Optional
import redis.asyncio as redis


_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client for caching

    Returns:
        Redis client if REDIS_URL configured, None otherwise
    """
    global _redis_client

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None

    if _redis_client is None:
        try:
            _redis_client = redis.from_url(redis_url, decode_responses=True)
        except Exception:
            return None

    return _redis_client
