import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.publisher import MessagePublisher
from src.database.dao.mixins import LimitOffset

from .dao import UserDAO
from .types.messages import UserCreatedMessage
from .types.schemas import UserCS, UserFilters, UserSchema


class UserService:
    def __init__(self, session: AsyncSession, publisher: MessagePublisher):
        self._session = session
        self._publisher = publisher
        self._user_dao = UserDAO(session)

    async def create_one(self, data: UserCS | None = None, **kwargs) -> UserSchema:
        if data is None:
            data = UserCS.model_validate(kwargs)

        id_ = uuid.uuid4()
        user = await self._user_dao.create(data=UserCS(id_=id_))
        self._publisher.collect(UserCreatedMessage(user_id=id_))
        return UserSchema.model_validate(user)

    async def get_by_id(self, id_: uuid.UUID) -> UserSchema | None:
        user = await self._user_dao.get_by_id(pk=id_)

        if user is None:
            return None
        else:
            return UserSchema.model_validate(user)

    async def get_many(
        self,
        filters: UserFilters | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UserSchema]:
        pagination = LimitOffset(limit=limit, offset=offset)
        users, _ = await self._user_dao.get_many(pagination, filters)
        return [UserSchema.model_validate(user) for user in users]
