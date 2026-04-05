from dishka import Provider, Scope, provide

from src.core.telemetry import Telemetry

__all__ = ("TelemetryProvider",)


class TelemetryProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_telemetry(self) -> Telemetry:
        return Telemetry()
