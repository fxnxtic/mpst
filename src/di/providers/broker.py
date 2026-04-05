from dishka import Provider, Scope, provide
from faststream.nats import NatsBroker

from src.config import cfg
from src.core.telemetry import get_logger

__all__ = ("BrokerProvider",)

logger = get_logger("broker")


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_broker(self) -> NatsBroker:
        return NatsBroker(
            servers=[cfg.nats.url],
            logger=logger,
        )
