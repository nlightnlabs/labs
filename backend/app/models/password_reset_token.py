"""Password Reset Token model."""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PasswordResetToken(Base, UUIDMixin, TimestampMixin):
    """Password reset token model for password recovery."""

    __tablename__ = "password_reset_tokens"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<PasswordResetToken user_id={self.user_id}>"
