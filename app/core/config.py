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
        case_sensitive=True
    )
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Note Taking API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server Configuration
    PORT: int = 8000  # Default port, Railway will override this
    HOST: str = "0.0.0.0"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./note_taking.db"
    
    # Security Configuration
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Redis Configuration (optional)
    REDIS_URL: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_HEALTH_CHECK_INTERVAL: int = 30
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default
    CACHE_KEY_PREFIX: str = "note_api"
    
    # CORS Configuration - using Any to prevent automatic JSON parsing
    BACKEND_CORS_ORIGINS: Any = ["*"]
    
    @field_validator("PORT", mode="before")
    @classmethod
    def validate_port(cls, v: Any) -> int:
        """
        Validate and convert PORT to integer.
        Railway provides PORT as string, we need to convert it.
        """
        if isinstance(v, str):
            return int(v)
        return v
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """
        Parse CORS origins from environment variable.
        Supports JSON array format, comma-separated string, or fallback to default.
        """
        if v is None or v == "":
            # Return default origins for development
            return ["http://localhost:3000", "http://localhost:8000"]
        
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            # Clean up the value - remove @ symbol and extra whitespace
            v = v.strip()
            if v.startswith("@"):
                v = v[1:]  # Remove @ symbol
            v = v.strip()
            
            # First try to parse as JSON array
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
        
        # Fallback to default
        return ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def validate_database_url(cls, v: str, info: ValidationInfo) -> str:
        if v.startswith("sqlite"):
            # For SQLite, ensure async driver
            if "aiosqlite" not in v:
                return v.replace("sqlite://", "sqlite+aiosqlite://")
        elif v.startswith("postgresql"):
            # For PostgreSQL, ensure async driver
            if "asyncpg" not in v:
                return v.replace("postgresql://", "postgresql+asyncpg://")
        return v


settings = Settings() 