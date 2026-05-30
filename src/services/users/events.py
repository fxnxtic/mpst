from dishka.integrations.faststream import FromDishka, inject
from faststream.nats import NatsRouter

from src.core.telemetry import Telemetry

from .types.messages import UserCreatedMessage

router = NatsRouter()


@router.subscriber(UserCreatedMessage.subject)
@inject
async def on_user_created(
    event: UserCreatedMessage,
    tm: FromDishka[Telemetry],
) -> None:
    tm.logger.info(f"Received {event.__class__.__name__}.", extra={"user_id": event.user_id})
