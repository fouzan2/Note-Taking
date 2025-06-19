"""
Application configuration management using Pydantic settings.
"""
from typing import List, Optional, Union
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
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./note_taking.db"
    
    # Security Configuration
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis Configuration (optional)
    REDIS_URL: Optional[str] = None
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
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