import traceback
from contextlib import suppress

import uvicorn
from fastapi import FastAPI

from src.api import router
from src.config import cfg
from src.core.telemetry import get_logger, setup_telemetry, shutdown_telemetry
from src.lifespan import lifespan

logger = get_logger(__name__)


def run(name: str, host: str, port: int) -> None:
    try:
        setup_telemetry(cfg)

        app = FastAPI(
            title=name,
            lifespan=lifespan,
        )
        app.include_router(router)

        uvicorn.run(
            app=app,
            host=host,
            port=port,
        )
    except Exception:
        logger.critical(traceback.format_exc())
    finally:
        shutdown_telemetry()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        run(cfg.app_name, cfg.app.host, cfg.app.port)
