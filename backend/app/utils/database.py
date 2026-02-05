"""Database utilities for SQLAlchemy session management."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

from app.config import get_tenant_state

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
