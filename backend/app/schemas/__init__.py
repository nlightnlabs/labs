"""Pydantic schemas for request/response validation."""

from app.schemas.common import (
    APIResponse,
    PaginatedResponse,
    PaginationMeta,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)
from app.schemas.preferences import (
    UserPreferencesUpdate,
    UserPreferencesResponse,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)

__all__ = [
    # Common
    "APIResponse",
    "PaginatedResponse",
    "PaginationMeta",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "ChangePasswordRequest",
    # Organization
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    # Preferences
    "UserPreferencesUpdate",
    "UserPreferencesResponse",
    # Notification
    "NotificationCreate",
    "NotificationResponse",
]
