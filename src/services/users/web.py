import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from src.core.exceptions import NotFoundError
from src.core.publisher import MessagePublisher
from src.core.telemetry import Telemetry
from src.database.uow import UnitOfWork

from .service import UserService
from .types.dto import CreateUser, UserView
from .types.schemas import UserCS, UserFilters

router = APIRouter(
    prefix="/users",
    tags=["users"],
    route_class=DishkaRoute,
)


@router.post("", response_model=UserView)
async def create_user(
    data: CreateUser,
    user_svc: FromDishka[UserService],
    uow: FromDishka[UnitOfWork],
    publisher: FromDishka[MessagePublisher],
    tm: FromDishka[Telemetry],
) -> UserView:
    with tm.tracer.start_as_current_span("user.create"):
        async with uow and publisher:
            schema = UserCS.model_validate(data.model_dump())
            user = await user_svc.create_one(schema)
            await uow.commit()
            await publisher.flush()
            tm.metrics.users_counter.add(1)

        tm.logger.info("user created", extra={"user_id": user.id_})

        return UserView.model_validate(user.model_dump(), extra="ignore")


@router.get("/{id_}", response_model=UserView)
async def get_user(
    id_: uuid.UUID,
    user_svc: FromDishka[UserService],
) -> UserView:
    user = await user_svc.get_by_id(id_=id_)

    if user is None:
        raise NotFoundError(entity="user", pk=str(id_))

    return UserView.model_validate(user.model_dump())


@router.get("", response_model=list[UserView])
async def get_users(
    user_svc: FromDishka[UserService],
    filters: UserFilters | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[UserView]:
    users = await user_svc.get_many(filters, limit, offset)

    return [UserView.model_validate(user.model_dump()) for user in users]
