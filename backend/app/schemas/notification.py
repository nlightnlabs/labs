"""Notification schemas."""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    title: str = Field(..., min_length=1, max_length=255)
    message: str
    type: str = Field("info", pattern=r"^(info|success|warning|error)$")
    link: Optional[str] = Field(None, max_length=500)


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: UUID
    user_id: UUID = Field(..., alias="userId")
    title: str
    message: str
    type: str
    is_read: bool = Field(..., alias="isRead")
    link: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")
    read_at: Optional[datetime] = Field(None, alias="readAt")

    class Config:
        from_attributes = True
        populate_by_name = True
