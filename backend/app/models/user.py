"""User model."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    """User role enumeration - legacy roles for backward compatibility."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class WorkspaceRole(str, enum.Enum):
    """Workspace-level role enumeration for Illuminis."""
    SUPER_ADMIN = "SUPER_ADMIN"  # Illuminis staff
    CUSTOMER_ADMIN = "CUSTOMER_ADMIN"  # PE firm admin
    ANALYST = "ANALYST"  # Can run analysis, upload files
    OPERATOR = "OPERATOR"  # Can manage data but limited analysis
    VIEWER = "VIEWER"  # Read-only access


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication and profile."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for SSO-only users
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.USER,
        nullable=False
    )
    workspace_role = Column(
        Enum(WorkspaceRole, values_callable=lambda x: [e.value for e in x]),
        default=WorkspaceRole.VIEWER,
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(String(10), default="0", nullable=False)
    locked_until = Column(DateTime, nullable=True)

    # Foreign keys
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True
    )

    # Relationships
    organization = relationship("Organization", back_populates="users")
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    portco_memberships = relationship(
        "PortcoMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    fun_settings = relationship(
        "FunSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<User {self.email}>"
