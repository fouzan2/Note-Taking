"""
Main FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis, redis_health_check
from app.api.v1 import api_router
from app.utils.exceptions import BaseAPIException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    """
    # Startup
    await init_db()
    await init_redis()
    yield
    # Shutdown
    await close_db()
    await close_redis()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
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


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to Note Taking API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint with database and Redis status.
    """
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "services": {
            "database": "healthy",  # TODO: Add actual DB health check
            "redis": await redis_health_check()
        }
    }
    
    # Determine overall health
    redis_status = health_status["services"]["redis"]["status"]
    if redis_status == "unhealthy" and settings.REDIS_URL:
        health_status["status"] = "degraded"
    
    return health_status 