from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

__all__ = (
    "setup_alembic",
    "run_migrations",
)


def setup_alembic(
    alembic_ini_path: Path,
    alembic_dir: Path,
) -> Config:
    config = Config(alembic_ini_path)
    config.set_main_option("script_location", str(alembic_dir))
    return config


async def run_migrations(engine: AsyncEngine, config: Config) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(upgrade_head, config)


def upgrade_head(connection: Connection, config: Config) -> None:
    config.attributes["connection"] = connection
    command.upgrade(config, "head")
