"""Settings API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.organization import Organization
from app.api.v1.endpoints.users import get_current_user
from app.schemas.preferences import UserPreferencesResponse, UserPreferencesUpdate
from app.schemas.organization import OrganizationResponse, OrganizationUpdate
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/preferences", response_model=APIResponse[UserPreferencesResponse])
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user preferences."""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()

    if not preferences:
        # Create default preferences
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return APIResponse(
        success=True,
        data=UserPreferencesResponse.model_validate(preferences)
    )


@router.put("/preferences", response_model=APIResponse[UserPreferencesResponse])
async def update_preferences(
    data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user preferences."""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()

    if not preferences:
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)

    update_data = data.model_dump(exclude_unset=True, by_alias=False)

    for field, value in update_data.items():
        setattr(preferences, field, value)

    preferences.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preferences)

    return APIResponse(
        success=True,
        data=UserPreferencesResponse.model_validate(preferences)
    )


@router.get("/organization", response_model=APIResponse[OrganizationResponse])
async def get_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization details (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization associated"
        )

    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return APIResponse(
        success=True,
        data=OrganizationResponse.model_validate(organization)
    )


@router.put("/organization", response_model=APIResponse[OrganizationResponse])
async def update_organization(
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update organization details (admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization associated"
        )

    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    # Check slug uniqueness
    if "slug" in update_data:
        existing = db.query(Organization).filter(
            Organization.slug == update_data["slug"],
            Organization.id != organization.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization slug already in use"
            )

    for field, value in update_data.items():
        setattr(organization, field, value)

    organization.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(organization)

    return APIResponse(
        success=True,
        data=OrganizationResponse.model_validate(organization)
    )
