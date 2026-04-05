from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("UnitOfWork",)


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> UnitOfWork: ...

    # automatic rollback on any exception
    async def __aexit__(self, *args) -> None:
        await self.rollback()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def flush(self) -> None:
        await self.session.flush()
