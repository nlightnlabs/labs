"""Billing models."""

import enum
from sqlalchemy import Column, String, Enum, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class BillingStatus(str, enum.Enum):
    """Billing account status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    TRIAL = "trial"


class BillingEventType(str, enum.Enum):
    """Types of billing events."""
    CHARGE = "charge"
    REFUND = "refund"
    CREDIT = "credit"
    ADJUSTMENT = "adjustment"


class BlockReason(str, enum.Enum):
    """Reasons for account blocking."""
    PAYMENT_FAILED = "payment_failed"
    USAGE_LIMIT = "usage_limit"
    MANUAL = "manual"
    TERMS_VIOLATION = "terms_violation"


class BillingAccount(Base, UUIDMixin, TimestampMixin):
    """Billing account model."""
    __tablename__ = "billing_accounts"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    status = Column(Enum(BillingStatus), default=BillingStatus.TRIAL, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    current_balance = Column(Float, default=0.0, nullable=False)
    block_reason = Column(Enum(BlockReason), nullable=True)

    # Relationships
    events = relationship("BillingEvent", back_populates="account", lazy="dynamic")


class BillingEvent(Base, UUIDMixin, TimestampMixin):
    """Billing event model."""
    __tablename__ = "billing_events"

    account_id = Column(UUID(as_uuid=True), ForeignKey("billing_accounts.id"), nullable=False)
    event_type = Column(Enum(BillingEventType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    stripe_invoice_id = Column(String(255), nullable=True)

    # Relationships
    account = relationship("BillingAccount", back_populates="events")
