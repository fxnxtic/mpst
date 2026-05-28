from dishka import Provider, Scope, provide
from faststream.nats import NatsBroker
from faststream.nats.opentelemetry import NatsTelemetryMiddleware

from src.config import cfg
from src.core.telemetry import get_logger
from src.core.telemetry.metrics import _meter_provider, get_meter
from src.core.telemetry.traces import _tracer_provider

__all__ = ("BrokerProvider",)

logger = get_logger("broker")


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_broker(self) -> NatsBroker:
        return NatsBroker(
            middlewares=[
                NatsTelemetryMiddleware(
                    tracer_provider=_tracer_provider,
                    meter=get_meter(),
                    meter_provider=_meter_provider,
                )
            ],
            servers=[cfg.nats.url],
            logger=logger,
        )
