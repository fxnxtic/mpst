from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.config import cfg
from src.database.engine import get_engine, get_session, get_sessionmaker
from src.database.uow import UnitOfWork

__all__ = ("DatabaseProvider",)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_engine() -> AsyncEngine:
        return await get_engine(cfg.database.url, cfg.database.echo)

    @provide(scope=Scope.APP)
    async def provide_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return await get_sessionmaker(engine)

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncGenerator[AsyncSession, None]:
        return get_session(sessionmaker)

    @provide(scope=Scope.REQUEST)
    async def provide_uow(
        self,
        session: AsyncSession,
    ) -> AsyncGenerator[UnitOfWork, None]:
        async with UnitOfWork(session) as uow:
            yield uow
