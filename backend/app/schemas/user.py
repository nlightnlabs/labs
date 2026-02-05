"""User schemas."""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")


class UserCreate(UserBase):
    """Schema for creating a user."""
    model_config = {"populate_by_name": True}

    password: str = Field(..., min_length=1)
    accept_terms: bool = Field(False, alias="acceptTerms")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    model_config = {"populate_by_name": True}

    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    username: Optional[str] = None
    mobile_phone: Optional[str] = Field(None, alias="mobilePhone")
    job_title: Optional[str] = Field(None, alias="jobTitle")
    company_name: Optional[str] = Field(None, alias="companyName")
    photo_url: Optional[str] = Field(None, alias="photoUrl")


class UserResponse(BaseModel):
    """Schema for user response."""
    model_config = {"from_attributes": True, "populate_by_name": True}

    id: str
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    mobile_phone: Optional[str] = Field(None, alias="mobilePhone")
    job_title: Optional[str] = Field(None, alias="jobTitle")
    company_name: Optional[str] = Field(None, alias="companyName")
    tenant_name: Optional[str] = Field(None, alias="tenantName")
    access_level: Optional[str] = Field(None, alias="accessLevel")
    business_unit: Optional[str] = Field(None, alias="businessUnit")
    photo_url: Optional[str] = Field(None, alias="avatarUrl")  # Map to avatarUrl for frontend compatibility
    user_type: Optional[str] = Field(None, alias="userType")
    status: Optional[str] = None
    stage: Optional[str] = None
    creation_date: Optional[datetime] = Field(None, alias="createdAt")
    last_updated: Optional[datetime] = Field(None, alias="updatedAt")

    # Computed properties for frontend compatibility
    @property
    def is_active(self) -> bool:
        return self.status and self.status.lower() == "active"

    @property
    def role(self) -> str:
        """Map access_level to role for frontend compatibility."""
        if self.access_level:
            level = self.access_level.lower()
            if "super" in level or "admin" in level:
                return "admin"
            elif "power" in level or "manager" in level:
                return "manager"
        return "user"


class UserInDB(UserResponse):
    """Schema for user in database (includes password)."""
    password: Optional[str] = None
