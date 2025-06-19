"""
Redis connection and cache management using redis-py async.
"""
import json
import logging
from typing import Optional, Any, Union
from contextlib import asynccontextmanager

try:
    import redis.asyncio as redis
    from redis.asyncio import ConnectionPool
except ImportError:
    redis = None
    ConnectionPool = None

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection pool
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """
    Initialize Redis connection pool.
    """
    global redis_pool, redis_client
    
    if not settings.REDIS_URL or not redis:
        logger.warning("Redis not available: REDIS_URL not set or redis package not installed")
        return
    
    try:
        # Create connection pool
        redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
            health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,
            decode_responses=True
        )
        
        # Create Redis client
        redis_client = redis.Redis(connection_pool=redis_pool)
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        redis_pool = None
        redis_client = None


async def close_redis() -> None:
    """
    Close Redis connections.
    """
    global redis_pool, redis_client
    
    if redis_client:
        await redis_client.close()
        redis_client = None
    
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None
    
    logger.info("Redis connections closed")


async def get_redis() -> Optional[redis.Redis]:
    """
    Get Redis client instance.
    
    Returns:
        Optional[redis.Redis]: Redis client or None if not available
    """
    if not redis_client:
        await init_redis()
    return redis_client


@asynccontextmanager
async def redis_session():
    """
    Context manager for Redis operations with automatic cleanup.
    
    Usage:
        async with redis_session() as r:
            await r.set("key", "value")
    """
    client = await get_redis()
    if client:
        try:
            yield client
        except Exception as e:
            logger.error(f"Redis operation error: {e}")
            raise
    else:
        yield None


class RedisCache:
    """
    Redis cache utility class for common caching operations.
    """
    
    @staticmethod
    def _make_key(key: str) -> str:
        """Create cache key with prefix."""
        return f"{settings.CACHE_KEY_PREFIX}:{key}"
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        async with redis_session() as r:
            if not r:
                return None
            
            try:
                value = await r.get(RedisCache._make_key(key))
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (defaults to CACHE_TTL_SECONDS)
            
        Returns:
            True if successful, False otherwise
        """
        async with redis_session() as r:
            if not r:
                return False
            
            try:
                ttl = ttl or settings.CACHE_TTL_SECONDS
                serialized_value = json.dumps(value, default=str)
                await r.setex(RedisCache._make_key(key), ttl, serialized_value)
                return True
            except Exception as e:
                logger.error(f"Redis set error for key {key}: {e}")
                return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        async with redis_session() as r:
            if not r:
                return False
            
            try:
                await r.delete(RedisCache._make_key(key))
                return True
            except Exception as e:
                logger.error(f"Redis delete error for key {key}: {e}")
                return False
    
    @staticmethod
    async def exists(key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        async with redis_session() as r:
            if not r:
                return False
            
            try:
                return bool(await r.exists(RedisCache._make_key(key)))
            except Exception as e:
                logger.error(f"Redis exists error for key {key}: {e}")
                return False
    
    @staticmethod
    async def clear_pattern(pattern: str) -> int:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Pattern to match (use * for wildcards)
            
        Returns:
            Number of keys deleted
        """
        async with redis_session() as r:
            if not r:
                return 0
            
            try:
                full_pattern = RedisCache._make_key(pattern)
                keys = await r.keys(full_pattern)
                if keys:
                    return await r.delete(*keys)
                return 0
            except Exception as e:
                logger.error(f"Redis clear pattern error for {pattern}: {e}")
                return 0


# Cache decorators for common use cases
def cache_result(key_prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache first
            cached_result = await RedisCache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await RedisCache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


# Health check function for monitoring
async def redis_health_check() -> dict:
    """
    Check Redis health status.
    
    Returns:
        Dict with health status information
    """
    try:
        async with redis_session() as r:
            if not r:
                return {"status": "unhealthy", "error": "Redis not available"}
            
            # Test basic operations
            await r.ping()
            
            # Get Redis info
            info = await r.info()
            
            return {
                "status": "healthy",
                "version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)} 