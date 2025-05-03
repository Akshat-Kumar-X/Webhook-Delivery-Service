"""
migrations/env.py

"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ⬇️  NEW – pull in settings, Base, and models so Alembic knows the tables
from app.config import settings
from app.db import Base
from app import models   # noqa: F401  (imports all ORM classes for autogenerate)

# ---------------------------------------------------------------------------

config = context.config
fileConfig(config.config_file_name)

# tell Alembic which MetaData to compare against the DB
target_metadata = Base.metadata

# make sure the URL in alembic.ini gets overwritten by the real one
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.database_url        # ← use the same URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
