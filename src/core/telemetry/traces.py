from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_ON,
    ParentBased,
    TraceIdRatioBased,
)

from src.config.env import Settings

from .resource import build_resource

__all__ = (
    "configure_traces",
    "get_tracer",
)

_tracer_provider: TracerProvider | None = None


def get_tracer(name: str) -> trace.Tracer:
    return trace.get_tracer(name)


def get_trace_context() -> dict[str, str]:
    span = trace.get_current_span()
    ctx = span.get_span_context()

    if ctx.is_valid:
        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
        }
    return {"trace_id": "", "span_id": ""}


def _build_sampler(settings: Settings):
    if settings.otel.sample_ratio >= 1.0:
        return ALWAYS_ON
    return ParentBased(root=TraceIdRatioBased(settings.otel.sample_ratio))


def configure_traces(settings: Settings) -> None:
    global _tracer_provider

    if _tracer_provider is not None:
        return

    exporter = OTLPSpanExporter(
        endpoint=settings.otel.endpoint,
    )

    _tracer_provider = TracerProvider(
        resource=build_resource(settings),
        sampler=_build_sampler(settings),
    )

    _tracer_provider.add_span_processor(
        BatchSpanProcessor(
            exporter,
            max_export_batch_size=512,
            export_timeout_millis=30_000,
        )
    )

    trace.set_tracer_provider(_tracer_provider)
