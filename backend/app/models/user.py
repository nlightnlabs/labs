"""User model."""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import enum

from app.models.base import Base


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


class User(Base):
    """User model matching the existing users table in the database."""

    __tablename__ = "users"

    # Primary key
    id = Column(Text, primary_key=True, server_default=func.gen_random_uuid())

    # Contact reference
    contact_id = Column(String(255), nullable=True)

    # Basic info
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    mobile_phone = Column(String(255), nullable=True)

    # Organization info
    job_title = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    tenant_name = Column(String(255), nullable=True)

    # Access control
    access_level = Column(String(255), nullable=True)
    business_unit = Column(String(255), nullable=True)

    # Profile
    photo_url = Column(String(255), nullable=True)

    # Authentication
    password = Column(String(255), nullable=True)

    # User classification
    user_type = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    stage = Column(String(255), nullable=True)

    # Timestamps
    creation_date = Column(DateTime, server_default=func.current_timestamp(), nullable=True)
    last_updated = Column(DateTime, onupdate=func.current_timestamp(), nullable=True)

    # Additional data
    notes = Column(Text, nullable=True)
    attachments = Column(JSONB, nullable=True)
    additional_data = Column(JSONB, nullable=True)

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        first = self.first_name or ""
        last = self.last_name or ""
        return f"{first} {last}".strip()

    @property
    def is_active(self) -> bool:
        """Check if user is active based on status field."""
        return self.status and self.status.lower() == "active"

    def __repr__(self) -> str:
        return f"<User {self.username or self.email}>"
