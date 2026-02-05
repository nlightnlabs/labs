"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Schema for login request."""
    model_config = {"populate_by_name": True}

    email: EmailStr
    password: str
    remember_me: bool = Field(False, alias="rememberMe")


class RegisterRequest(BaseModel):
    """Schema for registration request."""
    model_config = {"populate_by_name": True}

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100, alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=100, alias="lastName")
    accept_terms: bool = Field(..., alias="acceptTerms")


class TokenResponse(BaseModel):
    """Schema for token response."""
    model_config = {"populate_by_name": True}

    user: UserResponse
    token: str
    refresh_token: str = Field(..., alias="refreshToken", serialization_alias="refreshToken")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    model_config = {"populate_by_name": True}

    refresh_token: str = Field(..., alias="refreshToken")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""
    model_config = {"populate_by_name": True}

    current_password: str = Field(..., alias="currentPassword")
    new_password: str = Field(..., min_length=8, alias="newPassword")


class EmailVerificationRequest(BaseModel):
    """Schema for email verification."""
    token: str
