import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka.integrations.faststream import setup_dishka as setup_faststream_dishka
from fastapi import FastAPI
from faststream.nats import NatsBroker
from sqlalchemy.ext.asyncio import AsyncEngine

from src.config import cfg
from src.config.paths import ALEMBIC_DIR, ALEMBIC_INI_PATH
from src.core.telemetry import get_logger
from src.core.telemetry.instrumentation import instrument_faststream, instrument_sqlalchemy
from src.database.migrations import run_migrations, setup_alembic

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    try:
        app.state.broker = await app.state.container.get(NatsBroker)
        app.state.engine = await app.state.container.get(AsyncEngine)
        setup_faststream_dishka(app.state.container, broker=app.state.broker)

        instrument_faststream(app.state.broker)
        instrument_sqlalchemy(app.state.engine)

        logger.debug("Setup database...")
        _alembic_config = setup_alembic(ALEMBIC_INI_PATH, ALEMBIC_DIR)

        if cfg.database.run_migrations:
            logger.info("Running migrations...")
            await run_migrations(app.state.engine, _alembic_config)

        await app.state.broker.start()

        logger.info("Application started.")

        yield

    except Exception:
        logger.critical(traceback.format_exc())
    finally:
        if getattr(app.state, "broker", None) is not None:
            await app.state.broker.stop()

        if getattr(app.state, "container", None) is not None:
            await app.state.container.close()

        logger.info("Application stopped.")
