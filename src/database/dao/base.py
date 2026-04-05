from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.database.models.base import ModelBase

from .mixins import BaseFilters, LimitOffset

M = TypeVar("M", bound=ModelBase)  # SQLAlchemy ORM model
PK = TypeVar("PK")  # Primary key type  (UUID, int, str, ...)
CS = TypeVar("CS", bound=BaseModel)  # Create schema
US = TypeVar("US", bound=BaseModel)  # Update schema


class BaseDAO[M, PK, CS: BaseModel, US: BaseModel]:
    """
    Generic data-access layer bound to one SQLAlchemy model.

    All write methods call session.flush() so that DB-generated fields
    (id, timestamps) are populated immediately — but nothing is committed.
    The caller (UnitOfWork owner) is responsible for commit/rollback.

    Subclass requirements:
        model: ClassVar[type[M]]   — must be set on every concrete DAO / service

    Example:
        class ItemDAO(BaseDAO[Item, UUID]):
            model = Item

            async def find_by_owner(self, owner_id: UUID) -> list[Item]:
                result = await self.session.execute(
                    select(self.model).where(self.model.owner_id == owner_id)
                )
                return list(result.scalars())
    """

    model: ClassVar[type]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, pk: PK) -> M | None:
        """Return the instance or None if not found."""
        return await self.session.get(self.model, pk)

    async def get_or_raise(self, pk: PK) -> M:
        """Return the instance or raise NotFoundError."""
        obj = await self.get_by_id(pk)
        if obj is None:
            raise NotFoundError(self.model, pk)
        return obj

    async def get_many(
        self,
        pagination: LimitOffset | None = None,
        filters: BaseFilters | None = None,
    ) -> tuple[list[M], int]:
        """Return a paginated list and the total count matching the filters."""
        pagination = pagination or LimitOffset()

        where_clauses = filters.to_clauses(self.model) if filters else []

        count_stmt = select(func.count()).select_from(self.model)
        if where_clauses:
            count_stmt = count_stmt.where(*where_clauses)
        total: int = (await self.session.scalar(count_stmt)) or 0

        data_stmt = select(self.model)
        if where_clauses:
            data_stmt = data_stmt.where(*where_clauses)
        data_stmt = data_stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(data_stmt)
        items = list(result.scalars())

        return items, total

    async def exists(self, **kwargs: Any) -> bool:
        """Check whether a row matching all kwargs exists."""
        conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
        stmt = select(func.count()).select_from(self.model).where(*conditions)
        count = await self.session.scalar(stmt)
        return bool(count)

    async def create(self, data: CS) -> M:
        """Insert a new row and flush so DB-generated fields are populated."""
        obj: M = self.model(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, instance: M, data: US) -> M:
        """Update fields on an existing instance and flush."""
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: M) -> None:
        """Delete a row and flush."""
        await self.session.delete(instance)
        await self.session.flush()

    async def bulk_create(self, data: list[CS]) -> list[M]:
        """Insert multiple rows in one flush."""
        objs: list[M] = [self.model(**row.model_dump()) for row in data]
        self.session.add_all(objs)
        await self.session.flush()
        for obj in objs:
            await self.session.refresh(obj)
        return objs
