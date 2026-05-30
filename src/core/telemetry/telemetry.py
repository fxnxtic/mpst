import logging

from opentelemetry import metrics, trace

from src.config.env import Settings

from .logging import configure_logging, get_logger
from .metrics import Metrics, _meter_provider, configure_metrics, get_meter
from .traces import _tracer_provider, configure_traces, get_trace_context, get_tracer

__all__ = (
    "setup_telemetry",
    "shutdown_telemetry",
    "Telemetry",
)


def _configure_noop() -> None:
    trace.set_tracer_provider(trace.NoOpTracerProvider())
    metrics.set_meter_provider(metrics.NoOpMeterProvider())


def setup_telemetry(settings: Settings) -> None:
    configure_logging(settings)
    configure_traces(settings)
    configure_metrics(settings)

    if not settings.otel.enabled:
        _configure_noop()


def shutdown_telemetry() -> None:
    global _tracer_provider, _meter_provider

    if _tracer_provider is not None:
        _tracer_provider.shutdown()

    if _meter_provider is not None:
        _meter_provider.shutdown()


class Telemetry:
    @property
    def logger(self) -> logging.Logger:
        ctx = get_trace_context()
        if all(ctx.values()):
            return get_logger("telemetry", **ctx)
        else:
            return get_logger("telemetry")

    @property
    def tracer(self) -> trace.Tracer:
        return get_tracer("telemetry")

    @property
    def meter(self) -> metrics.Meter:
        return get_meter("telemetry")

    @property
    def metrics(self) -> Metrics:
        return Metrics()

    @property
    def trace_context(self) -> dict[str, str]:
        return get_trace_context()
