import logging
import sys

import structlog

__all__ = (
    "configure_logging",
    "get_logger",
)


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

    structlog.configure(
        processors=[
            structlog.processors.format_exc_info,
            renderer,
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
            foreign_pre_chain=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
            ],
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
