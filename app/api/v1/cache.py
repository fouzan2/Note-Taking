"""
Redis cache management endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.redis import RedisCache, redis_health_check, get_redis
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cache", tags=["cache"])


class CacheStatsResponse(BaseModel):
    """Cache statistics response model."""
    redis_health: Dict[str, Any]
    cache_prefix: str


class CacheKeyRequest(BaseModel):
    """Cache key operation request model."""
    key: str


class CacheSetRequest(BaseModel):
    """Cache set operation request model."""
    key: str
    value: Any
    ttl: int = 300


@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
) -> CacheStatsResponse:
    """
    Get cache statistics and health information.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Cache statistics and Redis health info
    """
    redis_stats = await redis_health_check()
    
    return CacheStatsResponse(
        redis_health=redis_stats,
        cache_prefix="note_api"
    )


@router.delete("/clear/user")
async def clear_user_cache(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clear all cache entries for the current user.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Number of keys cleared
    """
    # Clear user's notes cache
    notes_cleared = await RedisCache.clear_pattern(f"notes:user:{current_user.id}:*")
    
    # Clear individual note caches for this user
    note_pattern = f"note:*:user:{current_user.id}"
    notes_individual_cleared = await RedisCache.clear_pattern(note_pattern)
    
    total_cleared = notes_cleared + notes_individual_cleared
    
    return {
        "success": True,
        "message": f"Cleared {total_cleared} cache entries for user {current_user.id}",
        "details": {
            "notes_lists_cleared": notes_cleared,
            "individual_notes_cleared": notes_individual_cleared,
            "total_cleared": total_cleared
        }
    }


@router.delete("/clear/pattern")
async def clear_cache_pattern(
    pattern: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clear cache entries matching a pattern (admin-like functionality).
    
    Args:
        pattern: Pattern to match (use * for wildcards)
        current_user: Authenticated user
        
    Returns:
        Number of keys cleared
    """
    # For security, only allow clearing patterns related to the current user
    if f"user:{current_user.id}" not in pattern:
        raise HTTPException(
            status_code=403,
            detail="You can only clear cache entries for your own user"
        )
    
    cleared_count = await RedisCache.clear_pattern(pattern)
    
    return {
        "success": True,
        "message": f"Cleared {cleared_count} cache entries matching pattern: {pattern}",
        "pattern": pattern,
        "cleared_count": cleared_count
    }


@router.get("/key/{key}")
async def get_cache_key(
    key: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get a specific cache key value.
    
    Args:
        key: Cache key to retrieve
        current_user: Authenticated user
        
    Returns:
        Cache key value and metadata
    """
    # Security: only allow access to user's own cache keys
    if f"user:{current_user.id}" not in key:
        raise HTTPException(
            status_code=403,
            detail="You can only access cache entries for your own user"
        )
    
    exists = await RedisCache.exists(key)
    if not exists:
        raise HTTPException(status_code=404, detail="Cache key not found")
    
    value = await RedisCache.get(key)
    
    return {
        "success": True,
        "key": key,
        "value": value,
        "exists": exists
    }


@router.delete("/key/{key}")
async def delete_cache_key(
    key: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a specific cache key.
    
    Args:
        key: Cache key to delete
        current_user: Authenticated user
        
    Returns:
        Success status
    """
    # Security: only allow deleting user's own cache keys
    if f"user:{current_user.id}" not in key:
        raise HTTPException(
            status_code=403,
            detail="You can only delete cache entries for your own user"
        )
    
    success = await RedisCache.delete(key)
    
    return {
        "success": success,
        "message": f"Cache key {'deleted' if success else 'not found'}: {key}",
        "key": key
    }


@router.post("/key")
async def set_cache_key(
    request: CacheSetRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Set a cache key (for testing/debugging).
    
    Args:
        request: Cache set request
        current_user: Authenticated user
        
    Returns:
        Success status
    """
    # Security: only allow setting user's own cache keys
    if f"user:{current_user.id}" not in request.key:
        raise HTTPException(
            status_code=403,
            detail="You can only set cache entries for your own user"
        )
    
    success = await RedisCache.set(request.key, request.value, request.ttl)
    
    return {
        "success": success,
        "message": f"Cache key {'set' if success else 'failed'}: {request.key}",
        "key": request.key,
        "ttl": request.ttl
    }


@router.get("/test")
async def test_cache_operations(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Test basic cache operations.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Test results
    """
    test_key = f"test:user:{current_user.id}:cache_test"
    test_value = {"message": "Hello Redis!", "user_id": current_user.id}
    
    # Test set
    set_success = await RedisCache.set(test_key, test_value, ttl=60)
    
    # Test get
    retrieved_value = await RedisCache.get(test_key)
    
    # Test exists
    exists = await RedisCache.exists(test_key)
    
    # Test delete
    delete_success = await RedisCache.delete(test_key)
    
    return {
        "success": True,
        "test_results": {
            "set_operation": set_success,
            "get_operation": retrieved_value == test_value,
            "exists_operation": exists,
            "delete_operation": delete_success,
            "retrieved_value": retrieved_value
        },
        "redis_available": set_success and retrieved_value is not None
    } 