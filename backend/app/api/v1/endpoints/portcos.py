"""Portfolio Companies API endpoints."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from app.utils.database import get_db
from app.models import (
    Portco, PortcoStatus, PortcoMember, PortcoRole, AccessLevel,
    User, WorkspaceRole, Finding, FindingSeverity, AnalysisJob
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from app.dependencies import (
    get_current_user, CurrentUser, get_portco_access, PortcoAccess,
    require_detailed_access
)

router = APIRouter()


# ============== Schemas ==============

class PortcoCreate(BaseModel):
    """Schema for creating a portfolio company."""
    name: str = Field(..., min_length=1, max_length=255)
    status: PortcoStatus = PortcoStatus.PROSPECT
    status_notes: Optional[str] = None
    industry: Optional[str] = None
    geography: Optional[str] = None
    tags: Optional[str] = None


class PortcoUpdate(BaseModel):
    """Schema for updating a portfolio company."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[PortcoStatus] = None
    status_notes: Optional[str] = None
    industry: Optional[str] = None
    geography: Optional[str] = None
    tags: Optional[str] = None


class PortcoMemberResponse(BaseModel):
    """Schema for portco member in responses."""
    id: str
    user_id: str
    user_email: str
    user_name: str
    portco_role: PortcoRole
    access_level: AccessLevel

    class Config:
        from_attributes = True


class FindingSummary(BaseModel):
    """Summary of findings for a portco."""
    total: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    open: int = 0


class PortcoResponse(BaseModel):
    """Schema for portfolio company in responses."""
    id: str
    name: str
    status: PortcoStatus
    status_notes: Optional[str]
    industry: Optional[str]
    geography: Optional[str]
    tags: Optional[str]
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    findings_summary: Optional[FindingSummary] = None
    last_analysis_at: Optional[datetime] = None
    access_level: Optional[AccessLevel] = None

    class Config:
        from_attributes = True


class PortcoRollupResponse(BaseModel):
    """Schema for rollup-only portco view."""
    id: str
    name: str
    status: PortcoStatus
    industry: Optional[str]
    geography: Optional[str]
    findings_summary: FindingSummary
    last_analysis_at: Optional[datetime] = None


class PortcoMemberAdd(BaseModel):
    """Schema for adding a member to a portco."""
    user_id: str
    portco_role: PortcoRole = PortcoRole.VIEWER
    access_level: AccessLevel = AccessLevel.DETAILED


# ============== Endpoints ==============

@router.get("", response_model=APIResponse[List[PortcoResponse]])
async def list_portcos(
    status: Optional[PortcoStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List portfolio companies for the current user's workspace."""
    query = db.query(Portco)

    # Filter by workspace
    if current_user.is_super_admin():
        # Super admin can see all, but filter by workspace_id if provided
        pass
    elif current_user.is_customer_admin():
        # Customer admin sees all in their workspace
        query = query.filter(Portco.workspace_id == current_user.workspace_id)
    else:
        # Other users see only portcos they're members of
        member_portco_ids = db.query(PortcoMember.portco_id).filter(
            PortcoMember.user_id == current_user.id
        ).subquery()
        query = query.filter(Portco.id.in_(member_portco_ids))

    # Apply filters
    if status:
        query = query.filter(Portco.status == status)
    if search:
        query = query.filter(Portco.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Paginate
    offset = (page - 1) * per_page
    portcos = query.order_by(Portco.updated_at.desc()).offset(offset).limit(per_page).all()

    # Build responses with findings summary
    responses = []
    for portco in portcos:
        # Get findings summary
        findings_counts = db.query(
            func.count(Finding.id).label('total'),
            func.sum(func.cast(Finding.severity == FindingSeverity.HIGH, Integer)).label('high'),
            func.sum(func.cast(Finding.severity == FindingSeverity.MEDIUM, Integer)).label('medium'),
            func.sum(func.cast(Finding.severity == FindingSeverity.LOW, Integer)).label('low'),
        ).filter(Finding.portco_id == portco.id).first()

        open_count = db.query(func.count(Finding.id)).filter(
            Finding.portco_id == portco.id,
            Finding.status == "OPEN"
        ).scalar() or 0

        # Get last analysis
        last_job = db.query(AnalysisJob).filter(
            AnalysisJob.portco_id == portco.id,
            AnalysisJob.status == "COMPLETED"
        ).order_by(AnalysisJob.completed_at.desc()).first()

        # Get user's access level for this portco
        access_level = AccessLevel.DETAILED
        if not current_user.is_super_admin() and not current_user.is_customer_admin():
            membership = db.query(PortcoMember).filter(
                PortcoMember.portco_id == portco.id,
                PortcoMember.user_id == current_user.id
            ).first()
            if membership:
                access_level = membership.access_level

        response = PortcoResponse(
            id=str(portco.id),
            name=portco.name,
            status=portco.status,
            status_notes=portco.status_notes,
            industry=portco.industry,
            geography=portco.geography,
            tags=portco.tags,
            workspace_id=str(portco.workspace_id),
            created_at=portco.created_at,
            updated_at=portco.updated_at,
            findings_summary=FindingSummary(
                total=findings_counts.total or 0 if findings_counts else 0,
                high=findings_counts.high or 0 if findings_counts else 0,
                medium=findings_counts.medium or 0 if findings_counts else 0,
                low=findings_counts.low or 0 if findings_counts else 0,
                open=open_count,
            ),
            last_analysis_at=last_job.completed_at if last_job else None,
            access_level=access_level,
        )
        responses.append(response)

    return APIResponse(
        success=True,
        data=responses,
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        }
    )


@router.post("", response_model=APIResponse[PortcoResponse])
async def create_portco(
    data: PortcoCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new portfolio company."""
    # Only admins can create portcos
    if not current_user.can_manage_workspace():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create portfolio companies",
        )

    portco = Portco(
        name=data.name,
        status=data.status,
        status_notes=data.status_notes,
        industry=data.industry,
        geography=data.geography,
        tags=data.tags,
        workspace_id=current_user.workspace_id,
        created_by_id=current_user.id,
    )

    db.add(portco)
    db.commit()
    db.refresh(portco)

    return APIResponse(
        success=True,
        data=PortcoResponse(
            id=str(portco.id),
            name=portco.name,
            status=portco.status,
            status_notes=portco.status_notes,
            industry=portco.industry,
            geography=portco.geography,
            tags=portco.tags,
            workspace_id=str(portco.workspace_id),
            created_at=portco.created_at,
            updated_at=portco.updated_at,
            findings_summary=FindingSummary(),
            access_level=AccessLevel.DETAILED,
        )
    )


@router.get("/{portco_id}", response_model=APIResponse[PortcoResponse])
async def get_portco(
    portco_access: PortcoAccess = Depends(get_portco_access),
    db: Session = Depends(get_db),
):
    """Get portfolio company details."""
    portco = portco_access.portco

    # Get findings summary
    high_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.severity == FindingSeverity.HIGH
    ).scalar() or 0

    medium_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.severity == FindingSeverity.MEDIUM
    ).scalar() or 0

    low_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.severity == FindingSeverity.LOW
    ).scalar() or 0

    open_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.status == "OPEN"
    ).scalar() or 0

    # Get last analysis
    last_job = db.query(AnalysisJob).filter(
        AnalysisJob.portco_id == portco.id,
        AnalysisJob.status == "COMPLETED"
    ).order_by(AnalysisJob.completed_at.desc()).first()

    return APIResponse(
        success=True,
        data=PortcoResponse(
            id=str(portco.id),
            name=portco.name,
            status=portco.status,
            status_notes=portco.status_notes if portco_access.has_detailed_access() else None,
            industry=portco.industry,
            geography=portco.geography,
            tags=portco.tags if portco_access.has_detailed_access() else None,
            workspace_id=str(portco.workspace_id),
            created_at=portco.created_at,
            updated_at=portco.updated_at,
            findings_summary=FindingSummary(
                total=high_count + medium_count + low_count,
                high=high_count,
                medium=medium_count,
                low=low_count,
                open=open_count,
            ),
            last_analysis_at=last_job.completed_at if last_job else None,
            access_level=portco_access.access_level,
        )
    )


@router.get("/{portco_id}/rollup", response_model=APIResponse[PortcoRollupResponse])
async def get_portco_rollup(
    portco_access: PortcoAccess = Depends(get_portco_access),
    db: Session = Depends(get_db),
):
    """Get portfolio company rollup view (for rollup-only users)."""
    portco = portco_access.portco

    # Get findings summary
    high_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.severity == FindingSeverity.HIGH
    ).scalar() or 0

    medium_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.severity == FindingSeverity.MEDIUM
    ).scalar() or 0

    low_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.severity == FindingSeverity.LOW
    ).scalar() or 0

    open_count = db.query(func.count(Finding.id)).filter(
        Finding.portco_id == portco.id,
        Finding.status == "OPEN"
    ).scalar() or 0

    # Get last analysis
    last_job = db.query(AnalysisJob).filter(
        AnalysisJob.portco_id == portco.id,
        AnalysisJob.status == "COMPLETED"
    ).order_by(AnalysisJob.completed_at.desc()).first()

    return APIResponse(
        success=True,
        data=PortcoRollupResponse(
            id=str(portco.id),
            name=portco.name,
            status=portco.status,
            industry=portco.industry,
            geography=portco.geography,
            findings_summary=FindingSummary(
                total=high_count + medium_count + low_count,
                high=high_count,
                medium=medium_count,
                low=low_count,
                open=open_count,
            ),
            last_analysis_at=last_job.completed_at if last_job else None,
        )
    )


@router.patch("/{portco_id}", response_model=APIResponse[PortcoResponse])
async def update_portco(
    data: PortcoUpdate,
    portco_access: PortcoAccess = Depends(get_portco_access),
    db: Session = Depends(get_db),
):
    """Update portfolio company."""
    # Only detailed access can update
    if portco_access.is_rollup_only():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rollup-only access cannot update portfolio companies",
        )

    portco = portco_access.portco
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(portco, field, value)

    portco.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(portco)

    return APIResponse(
        success=True,
        data=PortcoResponse(
            id=str(portco.id),
            name=portco.name,
            status=portco.status,
            status_notes=portco.status_notes,
            industry=portco.industry,
            geography=portco.geography,
            tags=portco.tags,
            workspace_id=str(portco.workspace_id),
            created_at=portco.created_at,
            updated_at=portco.updated_at,
            access_level=portco_access.access_level,
        )
    )


@router.delete("/{portco_id}")
async def delete_portco(
    portco_access: PortcoAccess = Depends(get_portco_access),
    db: Session = Depends(get_db),
):
    """Delete portfolio company."""
    # Only admins can delete
    if not portco_access.current_user.can_manage_workspace():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete portfolio companies",
        )

    db.delete(portco_access.portco)
    db.commit()

    return APIResponse(success=True, data={"message": "Portfolio company deleted"})


# ============== Member Management ==============

@router.get("/{portco_id}/members", response_model=APIResponse[List[PortcoMemberResponse]])
async def list_portco_members(
    portco_access: PortcoAccess = Depends(get_portco_access),
    db: Session = Depends(get_db),
):
    """List members of a portfolio company."""
    # Only detailed access can see members
    if portco_access.is_rollup_only():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rollup-only access cannot view members",
        )

    members = db.query(PortcoMember).filter(
        PortcoMember.portco_id == portco_access.portco.id
    ).all()

    responses = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user:
            responses.append(PortcoMemberResponse(
                id=str(member.id),
                user_id=str(member.user_id),
                user_email=user.email,
                user_name=user.full_name,
                portco_role=member.portco_role,
                access_level=member.access_level,
            ))

    return APIResponse(success=True, data=responses)


@router.post("/{portco_id}/members", response_model=APIResponse[PortcoMemberResponse])
async def add_portco_member(
    data: PortcoMemberAdd,
    portco_access: PortcoAccess = Depends(get_portco_access),
    db: Session = Depends(get_db),
):
    """Add a member to a portfolio company."""
    # Only admins can add members
    if not portco_access.current_user.can_manage_workspace():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage members",
        )

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if already a member
    existing = db.query(PortcoMember).filter(
        PortcoMember.portco_id == portco_access.portco.id,
        PortcoMember.user_id == data.user_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member",
        )

    member = PortcoMember(
        portco_id=portco_access.portco.id,
        user_id=UUID(data.user_id),
        portco_role=data.portco_role,
        access_level=data.access_level,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return APIResponse(
        success=True,
        data=PortcoMemberResponse(
            id=str(member.id),
            user_id=str(member.user_id),
            user_email=user.email,
            user_name=user.full_name,
            portco_role=member.portco_role,
            access_level=member.access_level,
        )
    )


@router.delete("/{portco_id}/members/{member_id}")
async def remove_portco_member(
    member_id: UUID,
    portco_access: PortcoAccess = Depends(get_portco_access),
    db: Session = Depends(get_db),
):
    """Remove a member from a portfolio company."""
    # Only admins can remove members
    if not portco_access.current_user.can_manage_workspace():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage members",
        )

    member = db.query(PortcoMember).filter(
        PortcoMember.id == member_id,
        PortcoMember.portco_id == portco_access.portco.id,
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    db.delete(member)
    db.commit()

    return APIResponse(success=True, data={"message": "Member removed"})


# Import Integer for type casting in queries
from sqlalchemy import Integer
