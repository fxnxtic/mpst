import logging

from opentelemetry import metrics, trace

from src.config.env import Settings

from .instrumentation import configure_instrumentation
from .logging import configure_logging, get_logger
from .metrics import _meter_provider, configure_metrics, get_meter
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
    configure_logging(
        level=settings.logging.level,
        json_output=settings.logging.json_output,
        muted=settings.logging.muted_loggers,
    )

    if not settings.otel.enabled:
        _configure_noop()
        return

    configure_traces(settings)
    configure_metrics(settings)
    configure_instrumentation(settings)


def shutdown_telemetry() -> None:
    global _tracer_provider, _meter_provider

    if _tracer_provider is not None:
        _tracer_provider.shutdown()

    if _meter_provider is not None:
        _meter_provider.shutdown()


class Telemetry:
    @property
    def logger(self) -> logging.Logger:
        return get_logger(__name__)

    @property
    def tracer(self) -> trace.Tracer:
        return get_tracer(__name__)

    @property
    def meter(self) -> metrics.Meter:
        return get_meter(__name__)

    @property
    def trace_context(self) -> dict[str, str]:
        return get_trace_context()
