import asyncio
import os
import pkgutil
import re

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from src.config import cfg, paths
from src.database.models import ModelBase

modules = pkgutil.walk_packages(
    path=[str(paths.MODULES_DIR)],
    prefix="src.modules.",
)

for module in modules:
    __import__(module.name)

config = context.config

if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", cfg.database.url)

target_metadata = ModelBase.metadata


def process_revision_directives(context, revision, directives):
    if not directives:
        return

    script = directives[0]
    script_location = config.get_main_option("script_location")

    if not script_location:
        return

    migration_path = script_location + "/versions"

    revisions = []
    for filename in os.listdir(migration_path):
        match = re.match(r"^(\d+)_", filename)
        if match:
            revisions.append(int(match.group(1)))

    next_rev = max(revisions, default=0) + 1
    script.rev_id = f"{next_rev:04d}"


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise RuntimeError("Missing sqlalchemy.url in Alembic configuration.")

    connectable = create_async_engine(url, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_with_connection(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
elif config.attributes.get("connection"):
    run_migrations_with_connection(config.attributes["connection"])
else:
    asyncio.run(run_migrations_online())
