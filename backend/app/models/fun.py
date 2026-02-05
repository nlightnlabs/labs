"""Fun layer models for gamification features."""

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class FunSettings(Base, UUIDMixin, TimestampMixin):
    """Fun layer settings model."""
    __tablename__ = "fun_settings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    enabled = Column(Boolean, default=True, nullable=False)
    theme = Column(String(50), default="default", nullable=False)
    preferences = Column(JSONB, nullable=True)

    # Relationships
    user = relationship("User")


class FunAgent(Base, UUIDMixin, TimestampMixin):
    """Fun agent/character model."""
    __tablename__ = "fun_agents"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    personality = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    lines = relationship("FunLine", back_populates="agent", lazy="dynamic")


class FunLine(Base, UUIDMixin, TimestampMixin):
    """Fun dialogue line model."""
    __tablename__ = "fun_lines"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("fun_agents.id"), nullable=False)
    trigger = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Integer, default=0, nullable=False)

    # Relationships
    agent = relationship("FunAgent", back_populates="lines")
