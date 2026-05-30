from uuid import UUID

from pydantic import BaseModel


class CreateUser(BaseModel): ...


class UserView(BaseModel):
    id_: UUID
