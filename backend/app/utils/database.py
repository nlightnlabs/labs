"""Database utilities for SQLAlchemy session management."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

from app.config import get_tenant_state, _DEFAULT_DBHOST, _DEFAULT_DBUSER, _DEFAULT_DBPORT

# Base database constants for tenant lookups
# Uses the same host/user/port as the default tenant config, but connects to 'base' database
BASE_DB_HOST = os.getenv("BASE_DB_HOST", _DEFAULT_DBHOST)
BASE_DB_NAME = "base"
BASE_DB_USER = os.getenv("BASE_DB_USER", _DEFAULT_DBUSER)
BASE_DB_PORT = int(os.getenv("BASE_DB_PORT", str(_DEFAULT_DBPORT)))


def get_database_url() -> str:
    """Get database URL from tenant configuration."""
    state = get_tenant_state()

    # For AWS RDS with IAM auth, we'll use the postgres_db module instead
    # This is a fallback for local development with password auth
    db_host = state.DBHOST
    db_port = state.DBPORT
    db_user = state.DBUSER
    db_name = state.DEFAULTDB
    db_password = os.getenv("DB_PASSWORD", "")

    if db_password:
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # When using IAM auth, we don't include password in URL
        return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"


def get_base_database_url() -> str:
    """Get database URL for the base database (used for tenant lookups)."""
    db_password = os.getenv("DB_PASSWORD", "")

    if db_password:
        return f"postgresql://{BASE_DB_USER}:{db_password}@{BASE_DB_HOST}:{BASE_DB_PORT}/{BASE_DB_NAME}"
    else:
        return f"postgresql://{BASE_DB_USER}@{BASE_DB_HOST}:{BASE_DB_PORT}/{BASE_DB_NAME}"


# Create engine lazily
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_local():
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Base database engine and session (for tenant lookups)
_base_engine = None
_BaseSessionLocal = None


def get_base_engine():
    """Get or create database engine for the base database."""
    global _base_engine
    if _base_engine is None:
        _base_engine = create_engine(
            get_base_database_url(),
            pool_pre_ping=True,
            pool_size=3,
            max_overflow=5,
        )
    return _base_engine


def get_base_session_local():
    """Get or create session factory for the base database."""
    global _BaseSessionLocal
    if _BaseSessionLocal is None:
        _BaseSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_base_engine()
        )
    return _BaseSessionLocal


def get_base_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session to the BASE database.

    This is specifically for tenant lookups, which always need to query
    the base database regardless of the current tenant configuration.

    Usage:
        @router.get("/tenant/config")
        def get_tenant(db: Session = Depends(get_base_db)):
            # This will always connect to the 'base' database
            ...
    """
    BaseSessionLocal = get_base_session_local()
    db = BaseSessionLocal()
    try:
        yield db
    finally:
        db.close()
