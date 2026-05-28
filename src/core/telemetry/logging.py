import logging
import sys

import structlog

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


def get_logger(name: str, **kwargs) -> logging.Logger:
    return structlog.getLogger(name, **kwargs)


class MuteDropper(logging.Filter):
    def __init__(self, names_to_mute: list[str]):
        super().__init__()
        self.names_to_mute = set(names_to_mute)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name not in self.names_to_mute


def configure_logging(
    level: str = "INFO",
    json_output: bool = True,
    muted: list[str] | None = None,
) -> None:
    if level not in logging._nameToLevel.keys():
        raise ValueError(
            "Invalid logging level '%s'. Must be one of %s",
            str(level),
            ", ".join(logging._nameToLevel.keys()),
        )

    muted_loggers = [] if muted is None else muted

    logging.captureWarnings(True)

    logging.basicConfig(
        level=logging._nameToLevel[level],
        stream=sys.stdout,
        format="%(message)s",
    )

    if json_output:
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

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(MuteDropper(muted_loggers))

    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=shared_processors,
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
