"""User preferences model."""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserPreferences(Base, UUIDMixin, TimestampMixin):
    """User preferences model for storing user settings."""

    __tablename__ = "user_preferences"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    theme = Column(String(50), default="light", nullable=False)
    language = Column(String(10), default="en-US", nullable=False)
    timezone = Column(String(100), nullable=True)
    notification_settings = Column(
        JSONB,
        default={
            "email": True,
            "inApp": True,
            "marketing": False,
            "security": True
        },
        nullable=False
    )
    nav_collapsed = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<UserPreferences user_id={self.user_id}>"
