from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.database.dao.mixins import BaseFilters

__all__ = (
    "UserSchema",
    "UserCS",
    "UserUS",
    "UserFilters",
)


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_: UUID
    deleted: bool
    created_at: datetime
    updated_at: datetime


class UserCS(BaseModel):
    id_: UUID | None = None


class UserUS(BaseModel): ...


class UserFilters(BaseFilters):
    id_: list[UUID] | None = None
    deleted: bool | None = None
