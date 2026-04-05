from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

__all__ = (
    "UserSchema",
    "UserCS",
    "UserUS",
)


class UserSchema(BaseModel):
    id_: UUID
    deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCS(BaseModel):
    id_: UUID


class UserUS(BaseModel): ...
