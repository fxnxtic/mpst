from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from faststream.nats import NatsBroker

from src.core.exceptions import AppError
from src.database.uow import UnitOfWork

router = APIRouter(tags=["health"], route_class=DishkaRoute)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readiness")
async def readiness(
    uow: FromDishka[UnitOfWork],
    broker: FromDishka[NatsBroker],
) -> dict[str, str]:
    await uow.flush()
    if broker.ping(timeout=10):
        raise AppError("Broker ping failed.")

    return {"status": "ok"}
