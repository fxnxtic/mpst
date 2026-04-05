from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dao import BaseDAO

from .types.model import UserModel
from .types.schemas import UserCS, UserUS


class UserDAO(BaseDAO[UserModel, UUID, UserCS, UserUS]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
