"""
Application configuration management using Pydantic settings.
"""
import json
import os
from typing import List, Optional, Union, Any
from pydantic import field_validator, ValidationInfo, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from datetime import timedelta


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        # Don't require .env file since we're using docker-compose environment variables
        env_file=".env.development" if os.path.exists(".env.development") else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Note Taking API"
    VERSION: str = "1.0.0"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Current environment")
    
    # Debug mode - defined here before the validator
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT encoding"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Server Configuration
    PORT: int = Field(
        default=8000,
        description="Server port"
    )
    HOST: str = "0.0.0.0"
    RELOAD: bool = True
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://noteuser:notepassword@postgres:5432/note_taking_db",
        description="PostgreSQL connection string"
    )
    
    # Test database (SQLite for testing)
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Debug mode - automatically set based on environment
    @model_validator(mode="after")
    def set_debug_mode(self) -> "Settings":
        """Set debug mode based on environment."""
        self.DEBUG = self.ENVIRONMENT == "development"
        return self
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://redis:6379/0",
        description="Redis connection string"
    )
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Max Redis connections")
    REDIS_RETRY_ON_TIMEOUT: bool = Field(default=True, description="Retry on timeout")
    REDIS_HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval in seconds")
    
    # Cache Configuration
    CACHE_KEY_PREFIX: str = Field(default="note_api", description="Cache key prefix")
    CACHE_TTL_SECONDS: int = Field(default=3600, description="Default cache TTL in seconds")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        Parse CORS origins from string or list.
        Supports JSON array format or comma-separated string.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Celery Configuration
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @model_validator(mode="after")
    def set_celery_urls(self) -> "Settings":
        """Set Celery URLs based on Redis URL if not explicitly set."""
        if self.REDIS_URL and not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if self.REDIS_URL and not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
        return self
    
    # Security Headers
    SECURE_HEADERS: bool = Field(
        default=True,
        description="Enable secure headers"
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Requests per minute"
    )


# Create global settings instance
settings = Settings()

# JWT Token settings
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DELTA = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

# Print configuration for logs
print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
print(f"🌍 Environment: {settings.ENVIRONMENT}")
print(f"🔧 Port: {settings.PORT}")
print(f"🗄️  Database: {'PostgreSQL' if 'postgresql' in settings.DATABASE_URL else 'SQLite'}")
print(f"📡 Redis: {'Configured' if settings.REDIS_URL else 'Not configured'}") 