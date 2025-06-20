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
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Note Taking API"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT encoding"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Server Configuration
    PORT: int = 8000  # Default port for local development
    HOST: str = "0.0.0.0"
    RELOAD: bool = True
    
    # Database Configuration
    DATABASE_URL: Optional[str] = Field(
        default="postgresql+asyncpg://noteuser:notepass@postgres:5432/note_taking_db",
        description="PostgreSQL connection string"
    )
    
    # Database components for production
    DB_HOST: Optional[str] = Field(default=None, description="Database host")
    DB_NAME: Optional[str] = Field(default=None, description="Database name")
    DB_USER: Optional[str] = Field(default=None, description="Database user")
    DB_PASSWORD: Optional[str] = Field(default=None, description="Database password")
    
    @model_validator(mode="after")
    def construct_database_url(self) -> "Settings":
        """Construct DATABASE_URL from components if in production."""
        if self.ENVIRONMENT == "production" and self.DB_HOST and self.DB_NAME and self.DB_USER and self.DB_PASSWORD:
            # For Cloud SQL Unix socket connections, use special format
            if self.DB_HOST.startswith("/cloudsql/"):
                # Unix socket format: empty host with socket path as query parameter
                self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@/{self.DB_NAME}?host={self.DB_HOST}"
            else:
                # Standard TCP connection format
                self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"
        return self
    
    # Test database (SQLite for testing)
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Current environment")
    
    # Debug mode - automatically set based on environment
    @property
    def DEBUG(self) -> bool:
        """Debug mode based on environment."""
        return self.ENVIRONMENT == "development"
    
    # Redis Configuration
    REDIS_URL: Optional[str] = Field(
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
    
    # Print configuration for logs
    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Log configuration on startup."""
        super().__init_subclass__(**kwargs)


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
if settings.ENVIRONMENT == "production" and settings.DB_HOST and settings.DB_HOST.startswith("/cloudsql/"):
    print(f"🔌 Using Cloud SQL Unix socket: {settings.DB_HOST}")
print(f"📡 Redis: {'Configured' if settings.REDIS_URL else 'Not configured'}")
print(f"🛡️  CORS Origins: {settings.BACKEND_CORS_ORIGINS}") 