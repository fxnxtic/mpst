from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.publisher import MessagePublisher
from src.services.users import UserService


class UserServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_user_service(
        self,
        session: AsyncSession,
        publisher: MessagePublisher,
    ) -> UserService:
        return UserService(
            session=session,
            publisher=publisher,
        )
