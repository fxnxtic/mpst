import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.publisher import MessagePublisher

from .dao import UserDAO
from .types.messages import UserCreatedMessage
from .types.schemas import UserCS, UserSchema


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
