"""Portfolio company model."""

import enum
from sqlalchemy import Column, String, Enum, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PortcoStatus(str, enum.Enum):
    """Portfolio company status."""
    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    ONBOARDING = "onboarding"


class Portco(Base, UUIDMixin, TimestampMixin):
    """Portfolio company model."""
    __tablename__ = "portcos"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(PortcoStatus), default=PortcoStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)

    # Relationships
    members = relationship("PortcoMember", back_populates="portco", lazy="dynamic")
    files = relationship("File", back_populates="portco", lazy="dynamic")
    analysis_jobs = relationship("AnalysisJob", back_populates="portco", lazy="dynamic")
