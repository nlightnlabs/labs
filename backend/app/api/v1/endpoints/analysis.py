"""Analysis API endpoints for anomaly detection and findings."""

import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from app.utils.database import get_db
from app.models import (
    AnalysisJob, AnalysisStatus, Finding, FindingComment,
    FindingSeverity, FindingConfidence, FindingStatus, DetectorType,
    BillingAccount, BillingEventType, Portco, FileVersion,
    PortcoMember, AccessLevel
)
from app.schemas.common import APIResponse
from app.dependencies import (
    get_current_user, CurrentUser, get_portco_access, PortcoAccess
)

router = APIRouter()


# ============== Schemas ==============

class AnalysisRunRequest(BaseModel):
    """Request to run analysis."""
    portco_id: str
    file_version_id: Optional[str] = None
    detectors: Optional[List[str]] = None  # List of detector types to run


class AnalysisJobResponse(BaseModel):
    """Analysis job response."""
    id: str
    status: AnalysisStatus
    portco_id: str
    portco_name: Optional[str] = None
    file_version_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    findings_count: int = 0
    high_severity_count: int = 0
    medium_severity_count: int = 0
    low_severity_count: int = 0
    created_at: datetime


class FindingResponse(BaseModel):
    """Finding response."""
    id: str
    detector_type: DetectorType
    title: str
    description: Optional[str] = None
    severity: FindingSeverity
    confidence: FindingConfidence
    status: FindingStatus
    evidence_json: Optional[dict] = None  # Redacted for rollup-only
    affected_rows: Optional[int] = None
    affected_columns: Optional[List[str]] = None
    portco_id: str
    portco_name: Optional[str] = None
    analysis_job_id: str
    assigned_to_id: Optional[str] = None
    assigned_to_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FindingUpdate(BaseModel):
    """Finding update request."""
    status: Optional[FindingStatus] = None
    assigned_to_id: Optional[str] = None


class FindingCommentCreate(BaseModel):
    """Finding comment create request."""
    content: str = Field(..., min_length=1)


class FindingCommentResponse(BaseModel):
    """Finding comment response."""
    id: str
    content: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime


# ============== Helper Functions ==============

def check_billing_can_run(db: Session, workspace_id) -> tuple[bool, str]:
    """Check if workspace can run analysis based on billing."""
    billing = db.query(BillingAccount).filter(
        BillingAccount.workspace_id == workspace_id
    ).first()

    if not billing:
        return False, "Billing account not set up"

    can_run, block_reason = billing.can_run_analysis()
    if not can_run:
        return False, block_reason.value if block_reason else "Cannot run analysis"

    return True, None


def deduct_run_credit(db: Session, workspace_id, user_id):
    """Deduct one run credit from billing account."""
    from app.api.v1.endpoints.billing import log_billing_event

    billing = db.query(BillingAccount).filter(
        BillingAccount.workspace_id == workspace_id
    ).first()

    if billing and billing.runs_remaining > 0:
        billing.runs_remaining -= 1
        if billing.credits_balance > 0:
            billing.credits_balance -= 1

        log_billing_event(
            db,
            billing.id,
            BillingEventType.CREDITS_USED,
            user_id,
            "Analysis run credit used",
            {"runs_remaining": billing.runs_remaining},
        )


def run_mock_analysis(db: Session, job: AnalysisJob):
    """
    Run mock analysis and generate sample findings.

    In production, this would:
    1. Load the file from storage
    2. Parse and profile the data
    3. Run each configured detector
    4. Generate findings with evidence
    """
    import random

    # Mock detectors to run
    detectors = [
        (DetectorType.DUPLICATE_KEYS, "Duplicate Key Detection", FindingSeverity.HIGH),
        (DetectorType.OUTLIER_ZSCORE, "Statistical Outlier Detection", FindingSeverity.MEDIUM),
        (DetectorType.NEGATIVE_REVENUE, "Negative Revenue Values", FindingSeverity.HIGH),
        (DetectorType.MISSING_REQUIRED_IDS, "Missing Required IDs", FindingSeverity.MEDIUM),
        (DetectorType.PERIOD_GAPS, "Period Gap Detection", FindingSeverity.LOW),
    ]

    findings_created = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    for detector_type, title_prefix, severity in detectors:
        # Randomly decide if this detector finds something
        if random.random() < 0.6:  # 60% chance of finding something
            finding = Finding(
                detector_type=detector_type,
                title=f"{title_prefix}: Issues found in data",
                description=f"The {detector_type.value} detector found potential data quality issues.",
                severity=severity,
                confidence=random.choice([FindingConfidence.HIGH, FindingConfidence.MEDIUM]),
                status=FindingStatus.OPEN,
                evidence_json={
                    "sample_rows": [
                        {"row": i, "value": f"sample_{i}"}
                        for i in range(min(5, random.randint(1, 10)))
                    ],
                    "column": "sample_column",
                    "threshold": 2.5 if detector_type == DetectorType.OUTLIER_ZSCORE else None,
                },
                affected_rows=random.randint(1, 100),
                affected_columns=["column_a", "column_b"] if random.random() > 0.5 else None,
                analysis_job_id=job.id,
                workspace_id=job.workspace_id,
                portco_id=job.portco_id,
            )
            db.add(finding)
            findings_created += 1

            if severity == FindingSeverity.HIGH:
                high_count += 1
            elif severity == FindingSeverity.MEDIUM:
                medium_count += 1
            else:
                low_count += 1

    # Update job with results
    job.status = AnalysisStatus.COMPLETED
    job.completed_at = datetime.utcnow()
    job.findings_count = findings_created
    job.high_severity_count = high_count
    job.medium_severity_count = medium_count
    job.low_severity_count = low_count

    db.commit()


# ============== Endpoints ==============

@router.post("/run", response_model=APIResponse[AnalysisJobResponse])
async def run_analysis(
    data: AnalysisRunRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Run analysis on a portfolio company.

    Requires billing entitlement (trial, subscription, or credits).
    Uses idempotency key to prevent duplicate runs.
    """
    # Check idempotency
    if idempotency_key:
        existing_job = db.query(AnalysisJob).filter(
            AnalysisJob.idempotency_key == idempotency_key
        ).first()
        if existing_job:
            portco = db.query(Portco).filter(Portco.id == existing_job.portco_id).first()
            return APIResponse(
                success=True,
                data=AnalysisJobResponse(
                    id=str(existing_job.id),
                    status=existing_job.status,
                    portco_id=str(existing_job.portco_id),
                    portco_name=portco.name if portco else None,
                    file_version_id=str(existing_job.file_version_id) if existing_job.file_version_id else None,
                    started_at=existing_job.started_at,
                    completed_at=existing_job.completed_at,
                    error_message=existing_job.error_message,
                    findings_count=existing_job.findings_count,
                    high_severity_count=existing_job.high_severity_count,
                    medium_severity_count=existing_job.medium_severity_count,
                    low_severity_count=existing_job.low_severity_count,
                    created_at=existing_job.created_at,
                ),
                meta={"idempotent": True}
            )

    # Verify portco access
    portco = db.query(Portco).filter(Portco.id == data.portco_id).first()
    if not portco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio company not found",
        )

    # Check workspace match
    if not current_user.is_super_admin():
        if portco.workspace_id != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this portfolio company",
            )

    # Check portco membership for non-admins
    if not current_user.is_super_admin() and not current_user.is_customer_admin():
        membership = db.query(PortcoMember).filter(
            PortcoMember.portco_id == data.portco_id,
            PortcoMember.user_id == current_user.id,
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this portfolio company",
            )

        if membership.access_level == AccessLevel.ROLLUP_ONLY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rollup-only access cannot run analysis",
            )

    # Check billing
    can_run, error_msg = check_billing_can_run(db, portco.workspace_id)
    if not can_run:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=error_msg,
        )

    # Verify file version if provided
    file_version = None
    if data.file_version_id:
        file_version = db.query(FileVersion).filter(
            FileVersion.id == data.file_version_id,
            FileVersion.portco_id == data.portco_id,
        ).first()
        if not file_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File version not found",
            )

    # Create analysis job
    job = AnalysisJob(
        idempotency_key=idempotency_key or str(uuid.uuid4()),
        status=AnalysisStatus.RUNNING,
        started_at=datetime.utcnow(),
        workspace_id=portco.workspace_id,
        portco_id=portco.id,
        file_version_id=file_version.id if file_version else None,
        triggered_by_id=current_user.id,
        detectors_config={"detectors": data.detectors} if data.detectors else None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Deduct run credit
    deduct_run_credit(db, portco.workspace_id, current_user.id)

    # Run mock analysis (in production, this would be async/background)
    try:
        run_mock_analysis(db, job)
    except Exception as e:
        job.status = AnalysisStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()

    db.refresh(job)

    return APIResponse(
        success=True,
        data=AnalysisJobResponse(
            id=str(job.id),
            status=job.status,
            portco_id=str(job.portco_id),
            portco_name=portco.name,
            file_version_id=str(job.file_version_id) if job.file_version_id else None,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            findings_count=job.findings_count,
            high_severity_count=job.high_severity_count,
            medium_severity_count=job.medium_severity_count,
            low_severity_count=job.low_severity_count,
            created_at=job.created_at,
        )
    )


@router.get("/jobs/{job_id}", response_model=APIResponse[AnalysisJobResponse])
async def get_analysis_job(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analysis job details."""
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )

    # Check access
    if not current_user.is_super_admin():
        if job.workspace_id != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    portco = db.query(Portco).filter(Portco.id == job.portco_id).first()

    return APIResponse(
        success=True,
        data=AnalysisJobResponse(
            id=str(job.id),
            status=job.status,
            portco_id=str(job.portco_id),
            portco_name=portco.name if portco else None,
            file_version_id=str(job.file_version_id) if job.file_version_id else None,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            findings_count=job.findings_count,
            high_severity_count=job.high_severity_count,
            medium_severity_count=job.medium_severity_count,
            low_severity_count=job.low_severity_count,
            created_at=job.created_at,
        )
    )


@router.get("/findings", response_model=APIResponse[List[FindingResponse]])
async def list_findings(
    portco_id: Optional[str] = Query(None),
    severity: Optional[FindingSeverity] = Query(None),
    finding_status: Optional[FindingStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List findings with optional filters."""
    query = db.query(Finding)

    # Filter by workspace
    if not current_user.is_super_admin():
        query = query.filter(Finding.workspace_id == current_user.workspace_id)

    # Apply filters
    if portco_id:
        query = query.filter(Finding.portco_id == portco_id)
    if severity:
        query = query.filter(Finding.severity == severity)
    if finding_status:
        query = query.filter(Finding.status == finding_status)

    # Get total count
    total = query.count()

    # Paginate
    offset = (page - 1) * per_page
    findings = query.order_by(Finding.created_at.desc()).offset(offset).limit(per_page).all()

    # Check rollup access for each portco
    rollup_portco_ids = set()
    if not current_user.is_super_admin() and not current_user.is_customer_admin():
        memberships = db.query(PortcoMember).filter(
            PortcoMember.user_id == current_user.id,
            PortcoMember.access_level == AccessLevel.ROLLUP_ONLY,
        ).all()
        rollup_portco_ids = {str(m.portco_id) for m in memberships}

    responses = []
    for finding in findings:
        portco = db.query(Portco).filter(Portco.id == finding.portco_id).first()
        is_rollup = str(finding.portco_id) in rollup_portco_ids

        responses.append(FindingResponse(
            id=str(finding.id),
            detector_type=finding.detector_type,
            title=finding.title,
            description=finding.description,
            severity=finding.severity,
            confidence=finding.confidence,
            status=finding.status,
            evidence_json=None if is_rollup else finding.evidence_json,  # Redact for rollup
            affected_rows=finding.affected_rows if not is_rollup else None,
            affected_columns=finding.affected_columns if not is_rollup else None,
            portco_id=str(finding.portco_id),
            portco_name=portco.name if portco else None,
            analysis_job_id=str(finding.analysis_job_id),
            assigned_to_id=str(finding.assigned_to_id) if finding.assigned_to_id else None,
            assigned_to_name=None,  # Would fetch user name in production
            created_at=finding.created_at,
            updated_at=finding.updated_at,
        ))

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


@router.get("/findings/{finding_id}", response_model=APIResponse[FindingResponse])
async def get_finding(
    finding_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get finding details."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Check access
    if not current_user.is_super_admin():
        if finding.workspace_id != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    # Check rollup access
    is_rollup = False
    if not current_user.is_super_admin() and not current_user.is_customer_admin():
        membership = db.query(PortcoMember).filter(
            PortcoMember.portco_id == finding.portco_id,
            PortcoMember.user_id == current_user.id,
        ).first()
        if membership and membership.access_level == AccessLevel.ROLLUP_ONLY:
            is_rollup = True

    portco = db.query(Portco).filter(Portco.id == finding.portco_id).first()

    return APIResponse(
        success=True,
        data=FindingResponse(
            id=str(finding.id),
            detector_type=finding.detector_type,
            title=finding.title,
            description=finding.description,
            severity=finding.severity,
            confidence=finding.confidence,
            status=finding.status,
            evidence_json=None if is_rollup else finding.evidence_json,
            affected_rows=finding.affected_rows if not is_rollup else None,
            affected_columns=finding.affected_columns if not is_rollup else None,
            portco_id=str(finding.portco_id),
            portco_name=portco.name if portco else None,
            analysis_job_id=str(finding.analysis_job_id),
            assigned_to_id=str(finding.assigned_to_id) if finding.assigned_to_id else None,
            assigned_to_name=None,
            created_at=finding.created_at,
            updated_at=finding.updated_at,
        )
    )


@router.patch("/findings/{finding_id}", response_model=APIResponse[FindingResponse])
async def update_finding(
    finding_id: str,
    data: FindingUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update finding status or assignment."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Check access
    if not current_user.is_super_admin():
        if finding.workspace_id != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    # Check rollup access
    if not current_user.is_super_admin() and not current_user.is_customer_admin():
        membership = db.query(PortcoMember).filter(
            PortcoMember.portco_id == finding.portco_id,
            PortcoMember.user_id == current_user.id,
        ).first()
        if membership and membership.access_level == AccessLevel.ROLLUP_ONLY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rollup-only access cannot update findings",
            )

    # Update fields
    if data.status is not None:
        finding.status = data.status
    if data.assigned_to_id is not None:
        finding.assigned_to_id = data.assigned_to_id if data.assigned_to_id else None

    finding.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(finding)

    portco = db.query(Portco).filter(Portco.id == finding.portco_id).first()

    return APIResponse(
        success=True,
        data=FindingResponse(
            id=str(finding.id),
            detector_type=finding.detector_type,
            title=finding.title,
            description=finding.description,
            severity=finding.severity,
            confidence=finding.confidence,
            status=finding.status,
            evidence_json=finding.evidence_json,
            affected_rows=finding.affected_rows,
            affected_columns=finding.affected_columns,
            portco_id=str(finding.portco_id),
            portco_name=portco.name if portco else None,
            analysis_job_id=str(finding.analysis_job_id),
            assigned_to_id=str(finding.assigned_to_id) if finding.assigned_to_id else None,
            assigned_to_name=None,
            created_at=finding.created_at,
            updated_at=finding.updated_at,
        )
    )


@router.post("/findings/{finding_id}/comments", response_model=APIResponse[FindingCommentResponse])
async def add_finding_comment(
    finding_id: str,
    data: FindingCommentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a comment to a finding."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Check access
    if not current_user.is_super_admin():
        if finding.workspace_id != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    comment = FindingComment(
        content=data.content,
        finding_id=finding.id,
        user_id=current_user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return APIResponse(
        success=True,
        data=FindingCommentResponse(
            id=str(comment.id),
            content=comment.content,
            user_id=str(comment.user_id) if comment.user_id else None,
            user_name=current_user.user.full_name,
            created_at=comment.created_at,
        )
    )


@router.get("/findings/{finding_id}/comments", response_model=APIResponse[List[FindingCommentResponse]])
async def list_finding_comments(
    finding_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List comments for a finding."""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Check access
    if not current_user.is_super_admin():
        if finding.workspace_id != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    comments = db.query(FindingComment).filter(
        FindingComment.finding_id == finding_id
    ).order_by(FindingComment.created_at.asc()).all()

    from app.models import User

    responses = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first() if comment.user_id else None
        responses.append(FindingCommentResponse(
            id=str(comment.id),
            content=comment.content,
            user_id=str(comment.user_id) if comment.user_id else None,
            user_name=user.full_name if user else None,
            created_at=comment.created_at,
        ))

    return APIResponse(success=True, data=responses)
