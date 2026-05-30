from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.database.dao.mixins import BaseFilters

__all__ = (
    "UserSchema",
    "UserCS",
    "UserUS",
    "UserFilters",
)


class UserSchema(BaseModel):
    id_: UUID
    deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCS(BaseModel):
    id_: UUID | None = None


class UserUS(BaseModel): ...


class UserFilters(BaseFilters):
    id_: list[UUID] | None = None
    deleted: bool | None = None
