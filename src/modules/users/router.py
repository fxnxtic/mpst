from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from src.core.publisher import MessagePublisher
from src.core.telemetry import Telemetry
from src.database.uow import UnitOfWork

from .service import UserService
from .types.dto import UserView

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

    tm.logger.info("user created", extra={"user_id": user.id_})

    return UserView.model_validate(user, extra="ignore")
