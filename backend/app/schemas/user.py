"""User schemas."""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)
    accept_terms: bool = Field(..., alias="acceptTerms")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    model_config = {"populate_by_name": True}

    first_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="firstName")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="lastName")
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: EmailStr
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    phone: Optional[str] = None
    role: UserRole
    is_active: bool = Field(..., alias="isActive")
    is_verified: bool = Field(..., alias="isVerified")
    organization_id: Optional[UUID] = Field(None, alias="organizationId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    last_login_at: Optional[datetime] = Field(None, alias="lastLoginAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserInDB(UserResponse):
    """Schema for user in database (includes password hash)."""
    password_hash: Optional[str] = None
