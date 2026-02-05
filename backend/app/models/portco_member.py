"""Portfolio company member model."""

import enum
from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PortcoRole(str, enum.Enum):
    """Role within a portfolio company."""
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class AccessLevel(str, enum.Enum):
    """Access level for portfolio company data."""
    DETAILED = "detailed"
    ROLLUP_ONLY = "rollup_only"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class PortcoMember(Base, UUIDMixin, TimestampMixin):
    """Portfolio company member model."""
    __tablename__ = "portco_members"

    portco_id = Column(UUID(as_uuid=True), ForeignKey("portcos.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(PortcoRole), default=PortcoRole.MEMBER, nullable=False)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.READ, nullable=False)

    # Relationships
    portco = relationship("Portco", back_populates="members")
    user = relationship("User")
