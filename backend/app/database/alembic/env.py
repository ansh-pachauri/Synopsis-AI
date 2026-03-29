from logging.config import fileConfig
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# Allow imports from the backend root (so `app.*` resolves)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from dotenv import load_dotenv
from app.database.base import Base
import app.database.models  # noqa: F401 — registers all models with Base

# Load .env directly — avoids pydantic-settings Python 3.14 annotation bug
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
DB_URL = os.environ["DATABASE_URL"]

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(DB_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
