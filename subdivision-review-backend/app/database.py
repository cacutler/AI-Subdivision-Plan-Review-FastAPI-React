from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# asyncpg driver — install with: pip install sqlalchemy[asyncio] asyncpg
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,       # logs SQL in dev; turn off in prod
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,           # drops stale connections automatically
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,       # avoids lazy-load errors after commit in async context
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a session and guarantees cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
