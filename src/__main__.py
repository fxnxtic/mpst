import traceback
from contextlib import suppress

import uvicorn
from dishka.integrations.fastapi import setup_dishka as setup_fastapi_dishka
from fastapi import FastAPI

from src.api import router
from src.config import cfg
from src.core.telemetry import (
    get_logger,
    setup_telemetry,
    shutdown_telemetry,
)
from src.core.telemetry.instrumentation import instrument_fastapi
from src.di import PROVIDERS, create_container
from src.lifespan import lifespan

logger = get_logger(__name__)


def run(name: str, host: str, port: int) -> None:
    try:
        setup_telemetry(cfg)

        app = FastAPI(
            title=name,
            lifespan=lifespan,
        )

        instrument_fastapi(app, cfg)

        app.include_router(router)

        logger.debug("Setup DI container...")
        app.state.container = create_container(PROVIDERS)
        setup_fastapi_dishka(app.state.container, app=app)

        uvicorn.run(
            app=app,
            host=host,
            port=port,
            log_config=None,
        )
    except Exception:
        logger.critical(traceback.format_exc())
    finally:
        shutdown_telemetry()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        run(cfg.app_name, cfg.app.host, cfg.app.port)
