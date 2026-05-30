from faststream.nats import NatsRouter

from src.services.users import events as users_events

router = NatsRouter()

router.include_router(users_events.router)
