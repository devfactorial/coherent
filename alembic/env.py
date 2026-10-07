from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool


# ---------------------------------------------------------
# Make src/ importable
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
print("HERE------------------------")
print(SRC_ROOT)
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


# ---------------------------------------------------------
# Now imports from src/app work
# ---------------------------------------------------------

from app.config.settings import Settings
from app.database.sqlalchemy.base import Base
from app.database.sqlalchemy import models  # noqa: F401


# ---------------------------------------------------------
# Alembic configuration
# ---------------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


settings = Settings()

settings.database_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

database_url = f"sqlite:///{settings.database_path}"

config.set_main_option(
    "sqlalchemy.url",
    database_url,
)


# IMPORTANT:
# Alembic uses this to discover your SQLAlchemy tables.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()