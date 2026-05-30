from dishka import Provider, Scope, provide
from faststream.nats import NatsBroker

from src.api.events import router
from src.config import cfg
from src.core.telemetry import get_logger

__all__ = ("BrokerProvider",)

logger = get_logger("broker")


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_broker(self) -> NatsBroker:
        broker = NatsBroker(
            servers=[cfg.nats.url],
            logger=logger,
        )
        broker.include_router(router)
        return broker
