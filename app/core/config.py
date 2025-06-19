"""
Application configuration management using Pydantic settings.
"""
import json
import os
from typing import List, Optional, Union, Any
from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Note Taking API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False  # Default to False for production
    
    # Server Configuration (Railway provides PORT)
    PORT: int = 8000  # Default port, Railway will override this
    HOST: str = "0.0.0.0"
    
    # Database Configuration (Railway provides DATABASE_URL for PostgreSQL)
    DATABASE_URL: str = "sqlite+aiosqlite:///./note_taking.db"
    
    # Security Configuration
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Environment (Railway provides RAILWAY_ENVIRONMENT)
    ENVIRONMENT: str = "production"
    RAILWAY_ENVIRONMENT: Optional[str] = None
    
    # Redis Configuration (Railway provides REDIS_URL when Redis is added)
    REDIS_URL: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_HEALTH_CHECK_INTERVAL: int = 30
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default
    CACHE_KEY_PREFIX: str = "note_api"
    
    # CORS Configuration - Railway domain friendly
    BACKEND_CORS_ORIGINS: Any = ["https://takenote.up.railway.app"]
    
    @field_validator("PORT", mode="before")
    @classmethod
    def validate_port(cls, v: Any) -> int:
        """
        Validate and convert PORT to integer.
        Railway provides PORT as string, we need to convert it.
        """
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return 8000
        return v if v else 8000
    
    @field_validator("ENVIRONMENT", mode="after")
    @classmethod
    def set_environment(cls, v: str, info: ValidationInfo) -> str:
        """
        Use RAILWAY_ENVIRONMENT if available, otherwise use ENVIRONMENT.
        """
        railway_env = info.data.get("RAILWAY_ENVIRONMENT")
        if railway_env:
            return railway_env
        return v
    
    @field_validator("DEBUG", mode="after")
    @classmethod
    def set_debug_mode(cls, v: bool, info: ValidationInfo) -> bool:
        """
        Set debug mode based on environment.
        """
        environment = info.data.get("ENVIRONMENT", "production")
        if environment in ["development", "dev", "local"]:
            return True
        return False
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """
        Parse CORS origins from environment variable.
        Supports JSON array format, comma-separated string, or fallback to Railway defaults.
        """
        if v is None or v == "":
            # Return Railway-friendly defaults
            return ["https://takenote.up.railway.app", "http://localhost:3000"]
        
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            # Clean up the value
            v = v.strip()
            if v.startswith("@"):
                v = v[1:]
            v = v.strip()
            
            # Try to parse as JSON array
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
                except (json.JSONDecodeError, ValueError):
                    pass
            
            # If not JSON, treat as comma-separated string
            if "," in v:
                return [i.strip() for i in v.split(",") if i.strip()]
            
            # Single origin
            if v.strip():
                return [v.strip()]
        
        # Fallback to Railway defaults
        return ["https://takenote.up.railway.app", "http://localhost:3000"]
    
    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def validate_database_url(cls, v: str, info: ValidationInfo) -> str:
        """
        Ensure proper async database drivers.
        """
        if not v:
            return "sqlite+aiosqlite:///./note_taking.db"
            
        if v.startswith("sqlite"):
            # For SQLite, ensure async driver
            if "aiosqlite" not in v:
                return v.replace("sqlite://", "sqlite+aiosqlite://")
        elif v.startswith("postgresql"):
            # For PostgreSQL, ensure async driver
            if "asyncpg" not in v:
                return v.replace("postgresql://", "postgresql+asyncpg://")
        return v


# Create settings instance
settings = Settings()

# Print configuration for Railway logs
print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
print(f"🌍 Environment: {settings.ENVIRONMENT}")
print(f"🔧 Port: {settings.PORT}")
print(f"🗄️  Database: {'PostgreSQL' if 'postgresql' in settings.DATABASE_URL else 'SQLite'}")
print(f"📡 Redis: {'Configured' if settings.REDIS_URL else 'Not configured'}")
print(f"🛡️  CORS Origins: {settings.BACKEND_CORS_ORIGINS}") 