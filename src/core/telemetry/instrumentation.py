from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.faststream import FastStreamInstrumentator
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from src.config.env import Settings

__all__ = ("configure_instrumentation",)


def configure_instrumentation(settings: Settings) -> None:
    FastAPIInstrumentor().instrument(
        excluded_urls=(f"{settings.otel.excluded_urls},/health,/readiness,/metrics").strip(","),
        http_capture_headers_server_request=["x-request-id", "x-correlation-id"],
        http_capture_headers_server_response=["x-request-id"],
    )

    FastStreamInstrumentator().instrument()

    SQLAlchemyInstrumentor().instrument(
        enable_commenter=True,
        commenter_options={},
    )

    HTTPXClientInstrumentor().instrument()
