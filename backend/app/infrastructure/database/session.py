from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    """Own the asynchronous SQLAlchemy engine and session factory."""

    def __init__(self, url: str) -> None:
        self.engine: AsyncEngine = create_async_engine(url, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def dispose(self) -> None:
        await self.engine.dispose()


async def get_session(database: Database) -> AsyncIterator[AsyncSession]:
    """Yield a transaction-neutral database session."""
    async with database.session_factory() as session:
        yield session
