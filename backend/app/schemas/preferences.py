"""User preferences schemas."""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class NotificationSettingsSchema(BaseModel):
    """Schema for notification settings."""
    email: bool = True
    in_app: bool = Field(True, alias="inApp")
    marketing: bool = False
    security: bool = True

    class Config:
        populate_by_name = True


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    theme: Optional[str] = Field(None, pattern=r"^(light|dark|system)$")
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=100)
    notification_settings: Optional[Dict[str, bool]] = Field(None, alias="notificationSettings")
    nav_collapsed: Optional[bool] = Field(None, alias="navCollapsed")


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response."""
    id: UUID
    user_id: UUID = Field(..., alias="userId")
    theme: str
    language: str
    timezone: Optional[str] = None
    notification_settings: Dict[str, bool] = Field(..., alias="notificationSettings")
    nav_collapsed: bool = Field(..., alias="navCollapsed")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
