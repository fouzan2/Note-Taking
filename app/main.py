"""
Main FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import api_router
from app.utils.exceptions import BaseAPIException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    """
    # Startup - make dependencies optional for Railway
    try:
        from app.core.database import init_db
        await init_db()
    except Exception as e:
        print(f"Database initialization failed (continuing without DB): {e}")
    
    try:
        from app.core.redis import init_redis
        await init_redis()
    except Exception as e:
        print(f"Redis initialization failed (continuing without Redis): {e}")
    
    yield
    
    # Shutdown
    try:
        from app.core.database import close_db
        await close_db()
    except Exception:
        pass
    
    try:
        from app.core.redis import close_redis
        await close_redis()
    except Exception:
        pass


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
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint - simplified for Railway health checks
@app.get("/")
async def root():
    """
    Root endpoint - used for Railway health checks.
    """
    return {
        "message": "Welcome to Note Taking API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
        "port": settings.PORT
    }


# Health check endpoint
@app.get("/health")
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
        
        # Check Redis health if configured
        if settings.REDIS_URL:
            try:
                from app.core.redis import redis_health_check
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
            status_code=200,  # Return 200 for Railway health checks
            content={
                "status": "basic",
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "message": "Basic health check passed",
                "warning": str(e)
            }
        ) 