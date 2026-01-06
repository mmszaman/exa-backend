from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Base class for models - defined first to avoid circular imports
Base = declarative_base()

# Create async engine with connection pool settings
# Only create if DATABASE_URL is configured with async driver
if settings.DATABASE_URL and "postgresql" in settings.DATABASE_URL:
    # Ensure async driver for runtime and clean up incompatible parameters
    async_url = settings.DATABASE_URL
    
    # Replace driver with asyncpg
    if "postgresql://" in async_url and "asyncpg" not in async_url:
        async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Remove incompatible parameters for asyncpg (sslmode, channel_binding)
    # asyncpg uses ssl='require' instead
    if "sslmode=" in async_url:
        # Remove sslmode and channel_binding parameters
        async_url = async_url.split("?")[0] + "?ssl=require"
    
    engine = create_async_engine(
        async_url,
        echo=settings.DEBUG,
        future=True,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "statement_cache_size": 0  # Disable prepared statement cache in dev to prevent schema change errors
        }
    )
else:
    # Fallback engine for when DB is not configured (e.g., during migrations)
    engine = None

# Create session factory
# expire_on_commit=False to prevent attributes from being expired after commit
if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
else:
    AsyncSessionLocal = None

# Dependency for getting database session
# Async generator that yields a database session
# Usage: async with get_db() as db:
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()