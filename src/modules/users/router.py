import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from src.core.exceptions import NotFoundError
from src.core.publisher import MessagePublisher
from src.core.telemetry import Telemetry
from src.core.telemetry.metrics import USERS_COUNTER
from src.database.uow import UnitOfWork

from .service import UserService
from .types.dto import UserView
from .types.schemas import UserFilters

router = APIRouter(prefix="/users", route_class=DishkaRoute)


@router.post("", response_model=UserView)
async def create_user(
    user_svc: FromDishka[UserService],
    uow: FromDishka[UnitOfWork],
    publisher: FromDishka[MessagePublisher],
    tm: FromDishka[Telemetry],
) -> UserView:
    async with uow and publisher:
        user = await user_svc.create_one()
        await uow.commit()
        await publisher.flush()
        USERS_COUNTER.add(1)

    tm.logger.info("user created", extra={"user_id": user.id_})

    return UserView.model_validate(user, extra="ignore")


@router.get("/{id_}", response_model=UserView)
async def get_user(
    id_: uuid.UUID,
    user_svc: FromDishka[UserService],
) -> UserView:
    user = await user_svc.get_by_id(id_=id_)

    if user is None:
        raise NotFoundError(entity="user", pk=str(id_))

    return UserView.model_validate(user)


@router.get("", response_model=list[UserView])
async def get_users(
    user_svc: FromDishka[UserService],
    filters: UserFilters | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[UserView]:
    users = await user_svc.get_many(filters, limit, offset)

    return [UserView.model_validate(user) for user in users]
