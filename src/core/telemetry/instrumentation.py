from fastapi import FastAPI
from faststream.nats import NatsBroker
from faststream.nats.opentelemetry import NatsTelemetryMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncEngine

from src.config.env import Settings

from .metrics import _meter_provider, get_meter
from .middlewares import FastAPITraceMiddleware
from .traces import _tracer_provider

__all__ = (
    "instrument_fastapi",
    "instrument_faststream",
    "instrument_sqlalchemy",
)


def instrument_fastapi(app: FastAPI, settings: Settings) -> None:
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls=(f"{settings.otel.excluded_urls},/health,/readiness,/metrics").strip(","),
        http_capture_headers_server_request=[
            "x-request-id",
            "x-correlation-id",
        ],
        http_capture_headers_server_response=[
            "x-request-id",
        ],
    )
    app.add_middleware(FastAPITraceMiddleware)


def instrument_sqlalchemy(engine: AsyncEngine) -> None:
    SQLAlchemyInstrumentor().instrument(
        enable_commenter=True,
        commenter_options={},
        engine=engine.sync_engine,
    )


def instrument_faststream(broker: NatsBroker) -> None:
    broker.add_middleware(
        NatsTelemetryMiddleware(
            tracer_provider=_tracer_provider,
            meter=get_meter(),
            meter_provider=_meter_provider,
        )
    )
