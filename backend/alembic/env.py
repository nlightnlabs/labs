"""Alembic environment configuration with IAM authentication support."""

import logging
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection

from alembic import context

# Import models and config
from app.core.config import settings
from app.models import Base
from app.utils.database import get_database_provider

# Set up logging
logger = logging.getLogger("alembic.env")

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata


def get_engine():
    """
    Get the database engine using the appropriate provider.

    This supports IAM authentication for AWS RDS when configured.
    """
    provider = get_database_provider()
    logger.info(f"Using database provider: {settings.DATABASE_PROVIDER}")
    logger.info(f"IAM auth enabled: {settings.AWS_RDS_USE_IAM_AUTH}")
    return provider.get_engine()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This generates SQL scripts without connecting to the database.
    Note: This mode doesn't work with IAM auth since we can't generate
    a static connection string with IAM tokens.
    """
    if settings.AWS_RDS_USE_IAM_AUTH:
        logger.warning(
            "Offline migrations are not fully supported with IAM auth. "
            "The generated SQL may need manual token substitution."
        )

    # For offline mode, we still need a URL even if it's not used for connection
    # Use a placeholder or the basic URL format
    url = f"postgresql://{settings.DB_USER}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DEFAULT_DB}"

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    This connects to the database using the configured provider,
    supporting IAM authentication when enabled.
    """
    # Get engine from the database provider (supports IAM auth)
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
