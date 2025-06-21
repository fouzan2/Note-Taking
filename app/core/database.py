"""
Database connection and session management using SQLAlchemy async.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        poolclass=NullPool,  # SQLite doesn't support connection pooling well
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
else:
    # PostgreSQL and other databases
    connect_args = {}
    
    # For Cloud SQL Unix socket connections
    if settings.ENVIRONMENT == "production" and settings.DB_HOST and settings.DB_HOST.startswith("/cloudsql/"):
        # Ensure proper socket permissions and connection settings
        connect_args = {
            "server_settings": {
                "application_name": settings.PROJECT_NAME,
                "jit": "off"
            },
            "command_timeout": 60,
            "ssl": None  # Disable SSL for Unix socket connections
        }
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_size=10,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args=connect_args
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Create declarative base
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    """
    await engine.dispose() 