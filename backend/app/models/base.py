"""Base model with common functionality."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, MetaData, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base

from app.config import DB_SCHEMA

# Configure the schema for all models
metadata = MetaData(schema=DB_SCHEMA)
Base = declarative_base(metadata=metadata)

class BaseModel(Base):
    """Base model with common attributes."""
    name = Column(String, nullable=True, doc="Name of the entity")
    description = Column(String, nullable=True, doc="Description of the record")
    notes = Column(String, nullable=True, doc="Additional notes")
    data = Column(JSONB, nullable=True, doc="Additional structured data")
    __abstract__ = True


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class UUIDMixin:
    """Mixin that adds a UUID primary key."""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
