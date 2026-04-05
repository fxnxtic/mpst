from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

__all__ = (
    "get_engine",
    "get_sessionmaker",
    "get_session",
)


async def get_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(url=database_url, echo=echo)


async def get_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with sessionmaker.begin() as session:
        yield session
