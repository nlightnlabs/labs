"""Current user API endpoint."""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.utils.database import get_db
from app.models import WorkspaceRole, Organization
from app.schemas.common import APIResponse
from app.dependencies import get_current_user, CurrentUser

router = APIRouter()


class WorkspaceInfo(BaseModel):
    """Workspace information."""
    id: str
    name: str
    slug: str


class UserMeResponse(BaseModel):
    """Response for /api/me endpoint."""
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    avatar_url: Optional[str]
    workspace_role: WorkspaceRole
    workspace: Optional[WorkspaceInfo]
    is_super_admin: bool
    is_customer_admin: bool


@router.get("", response_model=APIResponse[UserMeResponse])
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user information.

    In development, use X-Demo-User header to switch users:
    - super: super@illuminis.com (SUPER_ADMIN)
    - admin: admin@demo.com (CUSTOMER_ADMIN)
    - analyst: analyst@demo.com (ANALYST)
    - exec: exec@demo.com (VIEWER)
    """
    user = current_user.user

    # Get workspace info
    workspace_info = None
    if user.organization_id:
        workspace = db.query(Organization).filter(
            Organization.id == user.organization_id
        ).first()
        if workspace:
            workspace_info = WorkspaceInfo(
                id=str(workspace.id),
                name=workspace.name,
                slug=workspace.slug,
            )

    return APIResponse(
        success=True,
        data=UserMeResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            workspace_role=user.workspace_role,
            workspace=workspace_info,
            is_super_admin=current_user.is_super_admin(),
            is_customer_admin=current_user.is_customer_admin(),
        )
    )
