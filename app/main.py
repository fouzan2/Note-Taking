"""
Main FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import AsyncGenerator, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import os

from app.core.config import settings
from app.api.v1 import api_router
from app.utils.exceptions import BaseAPIException
from app.core.database import get_db, AsyncSessionLocal
from app.core.redis import init_redis, close_redis, redis_health_check

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            logger.info("Database connection successful")
    except Exception as e:
        logger.warning(f"Database not ready: {e}")
        logger.info("Starting without database - some features may be unavailable")
    
    try:
        # Initialize Redis connection
        await init_redis()
        logger.info("Redis initialization complete")
    except Exception as e:
        logger.warning(f"Redis not ready: {e}")
        logger.info("Starting without Redis - caching disabled")
    
    # Startup complete
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown initiated")
    await close_redis()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request, exc: BaseAPIException):
    """
    Handle custom API exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """
    Handle general exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
            }
        }
    )


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint - simple health check
@app.get(
    "/",
    summary="Root Endpoint",
    description="""
    Root endpoint - used for health checks.
    
    This endpoint returns a simple message to confirm the API is running.
    It's useful for monitoring tools, health checks, and initial verification
    that the service is accessible.
    """,
    response_description="Welcome message with API information",
    tags=["Health"],
    responses={
        200: {
            "description": "API is running successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to Note Taking API",
                        "version": "1.0.0",
                        "docs": "/api/v1/docs",
                        "health": "/health"
                    }
                }
            }
        }
    }
)
async def read_root() -> dict[str, Any]:
    """
    Get API root information.
    
    Returns:
        dict: API information including version and documentation links
    """
    return {
        "message": "Welcome to Note Taking API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get(
    "/health",
    summary="Health Check",
    description="Check the health status of the API and its dependencies",
    response_description="Health status of the API",
    tags=["Health"],
    status_code=200,
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "services": {
                            "api": "healthy",
                            "database": "healthy",
                            "redis": "healthy"
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Health check endpoint with database and Redis status.
    """
    try:
        health_status = {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "port": settings.PORT,
            "services": {
                "database": "not_configured",
                "redis": "not_configured"
            }
        }
        
        # Check database health
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                row = result.fetchone()
                logger.info(f"Database health check successful: {row}")
                health_status["services"]["database"] = "healthy"
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Database health check failed: {error_msg}")
            health_status["services"]["database"] = {
                "status": "unhealthy",
                "error": error_msg
            }
            health_status["status"] = "degraded"
        
        # Check Redis health if configured
        if settings.REDIS_URL:
            try:
                redis_status = await redis_health_check()
                health_status["services"]["redis"] = redis_status
                
                # Determine overall health
                if redis_status.get("status") == "unhealthy":
                    health_status["status"] = "degraded"
                    
            except Exception as e:
                health_status["services"]["redis"] = {
                    "status": "unhealthy", 
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "message": "Health check failed",
                "error": str(e)
            }
        ) 