import logging
import sys

import structlog
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from src.config.env import Settings

from .resource import build_resource

__all__ = (
    "configure_logging",
    "get_logger",
)


class TraceContextProcessor:
    """
    Structlog processor that adds trace_id and span_id from the current span.
    """

    def __call__(self, logger: logging.Logger, method: str, event: dict) -> dict:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()

        if ctx.is_valid:
            event["trace_id"] = format(ctx.trace_id, "032x")
            event["span_id"] = format(ctx.span_id, "016x")

        return event


_trace_context_processor = TraceContextProcessor()


def configure_logs_export(settings: Settings) -> LoggerProvider:
    _logs_provider = LoggerProvider(resource=build_resource(settings))

    _logs_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{settings.otel.endpoint}/v1/logs"))
    )

    return _logs_provider


def get_logger(name: str, **kwargs) -> logging.Logger:
    return structlog.getLogger(name, **kwargs)


class MuteDropper(logging.Filter):
    def __init__(self, names_to_mute: list[str]):
        super().__init__()
        self.names_to_mute = set(names_to_mute)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name not in self.names_to_mute


def configure_logging(settings: Settings) -> None:
    if settings.logging.level not in logging._nameToLevel.keys():
        raise ValueError(
            "Invalid logging level '%s'. Must be one of %s",
            str(settings.logging.level),
            ", ".join(logging._nameToLevel.keys()),
        )

    logging.captureWarnings(True)

    logging.basicConfig(
        level=logging._nameToLevel[settings.logging.level],
        stream=sys.stdout,
        format="%(message)s",
    )

    if settings.logging.json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _trace_context_processor,
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    base_handler = logging.StreamHandler(sys.stdout)

    base_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=shared_processors,
        )
    )

    logs_provider = configure_logs_export(settings=settings)

    otel_handler = LoggingHandler(
        level=logging._nameToLevel[settings.logging.level],
        logger_provider=logs_provider,
    )
    otel_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addFilter(MuteDropper(settings.logging.muted_loggers))
    root.addHandler(base_handler)
    root.addHandler(otel_handler)
