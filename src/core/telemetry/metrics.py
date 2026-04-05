from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from src.config.env import Settings

from .resource import build_resource

__all__ = (
    "configure_metrics",
    "get_meter",
)

_meter_provider: MeterProvider | None = None


def get_meter(name: str) -> metrics.Meter:
    return metrics.get_meter(name)


def configure_metrics(settings: Settings) -> None:
    global _meter_provider

    if _meter_provider is not None:
        return

    exporter = OTLPMetricExporter(endpoint=settings.otel.endpoint)

    _meter_provider = MeterProvider(
        resource=build_resource(settings),
        metric_readers=[
            PeriodicExportingMetricReader(
                exporter,
                export_interval_millis=settings.otel.metrics_export_interval_ms,
            )
        ],
    )

    metrics.set_meter_provider(_meter_provider)
