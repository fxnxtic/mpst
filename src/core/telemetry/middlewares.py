from __future__ import annotations

from typing import TYPE_CHECKING, ParamSpec, TypeVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

if TYPE_CHECKING:
    pass

__all__ = (
    "FastAPITraceMiddleware",
    "TraceContext",
    "inject_trace_context",
    "extract_trace_context",
)


P = ParamSpec("P")
R = TypeVar("R")


class TraceContext:
    """
    Container for W3C Trace Context information.
    """

    __slots__ = ("trace_id", "span_id", "trace_flags", "trace_state")

    def __init__(
        self,
        trace_id: str | None = None,
        span_id: str | None = None,
        trace_flags: str | None = None,
        trace_state: str | None = None,
    ) -> None:
        self.trace_id = trace_id
        self.span_id = span_id
        self.trace_flags = trace_flags
        self.trace_state = trace_state

    def to_headers(self) -> dict[str, str]:
        headers = {}
        if self.trace_id and self.span_id:
            headers["traceparent"] = f"00-{self.trace_id}-{self.span_id}-{self.trace_flags or '01'}"
        if self.trace_state:
            headers["tracestate"] = self.trace_state
        return headers

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> TraceContext:
        traceparent = headers.get("traceparent", "")
        tracestate = headers.get("tracestate", "")

        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 4:
                return cls(
                    trace_id=parts[1],
                    span_id=parts[2],
                    trace_flags=parts[3],
                    trace_state=tracestate or None,
                )
        return cls()


def inject_trace_context(headers: dict[str, str]) -> dict[str, str]:
    """
    Inject current trace context into headers dict.
    Uses W3C Trace Context propagation format.
    """
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    propagator = TraceContextTextMapPropagator()
    carrier: dict[str, str] = {}
    propagator.inject(carrier)
    headers.update(carrier)
    return headers


def extract_trace_context(headers: dict[str, str]) -> TraceContext:
    """
    Extract trace context from headers using W3C Trace Context format.
    """
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    propagator = TraceContextTextMapPropagator()
    propagator.extract(carrier=headers)
    return TraceContext.from_headers(headers)


class FastAPITraceMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for W3C Trace Context propagation.

    Extracts trace context from incoming request headers and:
    - Stores it in request.state for downstream access
    - Injects it into response headers for propagation

    Note: The FastAPIInstrumentor handles span creation. This middleware
    focuses on context propagation and header injection.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        headers = dict(request.headers)

        ctx = extract_trace_context(headers)
        request.state.trace_context = ctx

        inject_trace_context(headers)

        response = await call_next(request)

        response.headers["traceparent"] = headers.get("traceparent", "")
        if headers.get("tracestate"):
            response.headers["tracestate"] = headers["tracestate"]

        return response
