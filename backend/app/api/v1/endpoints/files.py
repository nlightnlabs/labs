"""File upload and management API endpoints."""

import os
import hashlib
import uuid as uuid_lib
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Form, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.config import settings
from app.utils.database import get_db
from app.utils.storage import upload_file, download_file, delete_file, list_files, StorageError
from app.schemas.common import APIResponse
from app.models import (
    File, FileVersion, StorageProvider, UploadStatus, ProfilingStatus,
    Portco, PortcoMember, AccessLevel
)
from app.dependencies import get_current_user, CurrentUser

# Allowed file types for data upload
ALLOWED_FILE_TYPES = {
    "text/csv": ".csv",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}

# Extension to MIME type mapping (for when browser sends wrong MIME type)
EXTENSION_TO_MIME = {
    ".csv": "text/csv",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def get_validated_content_type(filename: str, content_type: str) -> Optional[str]:
    """
    Validate and return the correct content type for a file.

    First checks if the provided content_type is valid.
    Falls back to inferring from file extension if content_type is not recognized.
    Returns None if the file type is not allowed.
    """
    # Check if content type is directly allowed
    if content_type in ALLOWED_FILE_TYPES:
        return content_type

    # Fall back to extension-based detection
    if filename:
        ext = os.path.splitext(filename.lower())[1]
        if ext in EXTENSION_TO_MIME:
            return EXTENSION_TO_MIME[ext]

    return None

router = APIRouter()

# Sample data directory path
SAMPLE_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))),
    "sample_data"
)


# ============== Schemas ==============

class FileUploadResponse(BaseModel):
    """Response after file upload."""
    id: str
    file_id: str
    version_number: int
    filename: str
    original_filename: str
    size: int
    content_type: str
    storage_path: str
    app_id: str
    tenant_name: Optional[str] = None
    uploaded_by_id: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    uploaded_at: datetime
    upload_status: str
    profiling_status: str
    sheets: Optional[List[str]] = None


class FileInfo(BaseModel):
    """File information."""
    id: str
    file_id: str
    version_number: int
    filename: str
    original_filename: str
    size: int
    content_type: str
    storage_path: str
    app_id: str
    tenant_name: Optional[str] = None
    uploaded_by_id: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    uploaded_at: datetime
    upload_status: str
    profiling_status: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    sheets: Optional[List[str]] = None


class FileListResponse(BaseModel):
    """List of files response."""
    files: List[FileInfo]
    total: int


class SampleDataFile(BaseModel):
    """Sample data file info."""
    filename: str
    size: int
    path: str


# ============== Helper Functions ==============

def get_xlsx_sheets(file_content: bytes) -> List[str]:
    """Extract sheet names from XLSX file."""
    try:
        import openpyxl
        from io import BytesIO

        wb = openpyxl.load_workbook(BytesIO(file_content), read_only=True)
        sheets = wb.sheetnames
        wb.close()
        return sheets
    except Exception:
        return []


def compute_sha256(data: bytes) -> str:
    """Compute SHA256 hash of data."""
    return hashlib.sha256(data).hexdigest()


def get_storage_provider() -> StorageProvider:
    """Get current storage provider based on settings."""
    if settings.ENVIRONMENT == "development":
        return StorageProvider.LOCAL
    return StorageProvider.S3


def check_tenant_access(
    db: Session,
    current_user: CurrentUser,
    app_id: str,
    require_write: bool = False
) -> Portco:
    """Check if user has access to tenant and return it."""
    tenant = db.query(Portco).filter(Portco.id == app_id).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio company not found"
        )

    # Super admin has access to all
    if current_user.is_super_admin():
        return tenant

    # Check workspace match
    if tenant.workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this portfolio company"
        )

    # Customer admin has full workspace access
    if current_user.is_customer_admin():
        return tenant

    # Check tenant membership
    membership = db.query(PortcoMember).filter(
        PortcoMember.app_id == app_id,
        PortcoMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this portfolio company"
        )

    # Rollup-only users cannot upload/modify files
    if require_write and membership.access_level == AccessLevel.ROLLUP_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rollup-only access cannot upload or modify files"
        )

    return tenant


# ============== Endpoints ==============

@router.post("/upload/{app_id}", response_model=APIResponse[FileUploadResponse])
async def upload_tenant_file(
    app_id: str,
    file: UploadFile = FastAPIFile(...),
    sheet_name: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a data file for a portfolio company.

    Supports CSV and XLSX files up to 100MB.
    In development, files are stored locally.
    In production, files are stored in AWS S3.
    """
    # Check tenant access (requires write access)
    tenant = check_tenant_access(db, current_user, app_id, require_write=True)

    # Validate file type (check MIME type first, then fall back to extension)
    original_filename = file.filename or "unknown"
    content_type = get_validated_content_type(original_filename, file.content_type)
    if content_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: CSV, XLS, XLSX. Got: {file.content_type}"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 100MB"
        )

    # Compute hash
    file_hash = compute_sha256(content)

    # Get sheet names for XLSX files
    sheets = None
    if content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        sheets = get_xlsx_sheets(content)

    # Generate unique filename and storage path
    file_ext = ALLOWED_FILE_TYPES.get(content_type, ".csv")
    unique_key = str(uuid_lib.uuid4())
    storage_key = f"tenants/{app_id}/files/{unique_key}{file_ext}"

    # Check if file with same name exists (for versioning)
    existing_file = db.query(File).filter(
        File.app_id == app_id,
        File.logical_name == original_filename
    ).first()

    if existing_file:
        # Create new version
        max_version = db.query(FileVersion).filter(
            FileVersion.file_id == existing_file.id
        ).count()
        version_number = max_version + 1
        file_record = existing_file
    else:
        # Create new file record
        file_record = File(
            logical_name=original_filename,
            mime_type=content_type,
            workspace_id=tenant.workspace_id,
            app_id=tenant.id,
        )
        db.add(file_record)
        db.flush()
        version_number = 1

    # Create file version record
    storage_provider = get_storage_provider()
    file_version = FileVersion(
        version_number=version_number,
        storage_provider=storage_provider,
        storage_bucket=settings.AWS_S3_BUCKET if storage_provider == StorageProvider.S3 else None,
        storage_key=storage_key,
        byte_size=len(content),
        sha256=file_hash,
        xlsx_sheet=sheet_name,
        upload_status=UploadStatus.UPLOADING,
        profiling_status=ProfilingStatus.PENDING,
        file_id=file_record.id,
        workspace_id=tenant.workspace_id,
        app_id=tenant.id,
        uploaded_by_id=current_user.id,
    )
    db.add(file_version)
    db.commit()

    try:
        # Upload file to storage
        stored_path = upload_file(
            file_data=content,
            path=storage_key,
            content_type=content_type
        )

        # Update version with success status
        file_version.upload_status = UploadStatus.UPLOADED
        file_version.uploaded_at = datetime.utcnow()
        file_version.storage_uri = stored_path
        db.commit()
        db.refresh(file_version)

        return APIResponse(
            success=True,
            data=FileUploadResponse(
                id=str(file_version.id),
                file_id=str(file_record.id),
                version_number=file_version.version_number,
                filename=f"{unique_key}{file_ext}",
                original_filename=original_filename,
                size=len(content),
                content_type=content_type,
                storage_path=stored_path,
                app_id=str(tenant.id),
                tenant_name=tenant.name,
                uploaded_by_id=str(current_user.id),
                uploaded_by_name=current_user.user.full_name,
                uploaded_at=file_version.uploaded_at,
                upload_status=file_version.upload_status.value,
                profiling_status=file_version.profiling_status.value,
                sheets=sheets,
            )
        )

    except StorageError as e:
        # Update version with failure status
        file_version.upload_status = UploadStatus.FAILED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store file: {str(e)}"
        )


@router.get("/{app_id}", response_model=APIResponse[FileListResponse])
async def list_tenant_files(
    app_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all uploaded files for a portfolio company."""
    # Check tenant access
    tenant = check_tenant_access(db, current_user, app_id, require_write=False)

    # Query files with latest versions
    query = db.query(File).filter(
        File.app_id == app_id
    )

    total = query.count()
    offset = (page - 1) * per_page
    files = query.order_by(File.created_at.desc()).offset(offset).limit(per_page).all()

    file_list = []
    for f in files:
        # Get latest version
        latest_version = db.query(FileVersion).filter(
            FileVersion.file_id == f.id
        ).order_by(FileVersion.version_number.desc()).first()

        if latest_version:
            file_list.append(FileInfo(
                id=str(latest_version.id),
                file_id=str(f.id),
                version_number=latest_version.version_number,
                filename=os.path.basename(latest_version.storage_key),
                original_filename=f.logical_name,
                size=latest_version.byte_size or 0,
                content_type=f.mime_type,
                storage_path=latest_version.storage_key,
                app_id=str(tenant.id),
                tenant_name=tenant.name,
                uploaded_by_id=str(latest_version.uploaded_by_id) if latest_version.uploaded_by_id else None,
                uploaded_by_name=latest_version.uploaded_by.full_name if latest_version.uploaded_by else None,
                uploaded_at=latest_version.uploaded_at or latest_version.created_at,
                upload_status=latest_version.upload_status.value,
                profiling_status=latest_version.profiling_status.value,
                row_count=latest_version.row_count,
                column_count=latest_version.column_count,
            ))

    return APIResponse(
        success=True,
        data=FileListResponse(files=file_list, total=total),
        meta={
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 0,
        }
    )


@router.get("/{app_id}/{file_version_id}", response_model=APIResponse[FileInfo])
async def get_file_details(
    app_id: str,
    file_version_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific file version."""
    # Check tenant access
    tenant = check_tenant_access(db, current_user, app_id, require_write=False)

    # Get file version
    file_version = db.query(FileVersion).filter(
        FileVersion.id == file_version_id,
        FileVersion.app_id == app_id,
    ).first()

    if not file_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_record = db.query(File).filter(File.id == file_version.file_id).first()

    return APIResponse(
        success=True,
        data=FileInfo(
            id=str(file_version.id),
            file_id=str(file_record.id),
            version_number=file_version.version_number,
            filename=os.path.basename(file_version.storage_key),
            original_filename=file_record.logical_name,
            size=file_version.byte_size or 0,
            content_type=file_record.mime_type,
            storage_path=file_version.storage_key,
            app_id=str(tenant.id),
            tenant_name=tenant.name,
            uploaded_by_id=str(file_version.uploaded_by_id) if file_version.uploaded_by_id else None,
            uploaded_by_name=file_version.uploaded_by.full_name if file_version.uploaded_by else None,
            uploaded_at=file_version.uploaded_at or file_version.created_at,
            upload_status=file_version.upload_status.value,
            profiling_status=file_version.profiling_status.value,
            row_count=file_version.row_count,
            column_count=file_version.column_count,
        )
    )


@router.delete("/{app_id}/{file_version_id}", response_model=APIResponse)
async def delete_tenant_file(
    app_id: str,
    file_version_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an uploaded file version."""
    # Check tenant access (requires write access)
    tenant = check_tenant_access(db, current_user, app_id, require_write=True)

    # Get file version
    file_version = db.query(FileVersion).filter(
        FileVersion.id == file_version_id,
        FileVersion.app_id == app_id,
    ).first()

    if not file_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Delete from storage
    try:
        delete_file(file_version.storage_key)
    except StorageError:
        pass  # Continue even if storage delete fails

    # Get the parent file
    file_record = db.query(File).filter(File.id == file_version.file_id).first()

    # Delete version from database
    db.delete(file_version)

    # If this was the last version, delete the file record too
    remaining_versions = db.query(FileVersion).filter(
        FileVersion.file_id == file_record.id
    ).count()

    if remaining_versions == 0:
        db.delete(file_record)

    db.commit()

    return APIResponse(
        success=True,
        data={"message": "File deleted successfully"}
    )


@router.get("/download/{app_id}/{file_version_id}")
async def download_tenant_file(
    app_id: str,
    file_version_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a file."""
    # Check tenant access
    tenant = check_tenant_access(db, current_user, app_id, require_write=False)

    # Get file version
    file_version = db.query(FileVersion).filter(
        FileVersion.id == file_version_id,
        FileVersion.app_id == app_id,
    ).first()

    if not file_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_record = db.query(File).filter(File.id == file_version.file_id).first()

    try:
        content = download_file(file_version.storage_key)

        return Response(
            content=content,
            media_type=file_record.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_record.logical_name}"'
            }
        )
    except StorageError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage"
        )


# ============== Sample Data Endpoints ==============

@router.get("/sample-data/list", response_model=APIResponse[List[SampleDataFile]])
async def list_sample_data(
    current_user: CurrentUser = Depends(get_current_user),
):
    """List available sample data files."""
    sample_files = []

    if os.path.exists(SAMPLE_DATA_DIR):
        for filename in os.listdir(SAMPLE_DATA_DIR):
            if filename.endswith(('.csv', '.xlsx', '.xls')):
                file_path = os.path.join(SAMPLE_DATA_DIR, filename)
                sample_files.append(SampleDataFile(
                    filename=filename,
                    size=os.path.getsize(file_path),
                    path=file_path
                ))

    return APIResponse(success=True, data=sample_files)


@router.post("/sample-data/load/{app_id}", response_model=APIResponse)
async def load_sample_data(
    app_id: str,
    filenames: List[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Load sample data files into a portfolio company.

    If filenames is not provided, loads all sample files.
    """
    # Check tenant access (requires write access)
    tenant = check_tenant_access(db, current_user, app_id, require_write=True)

    if not os.path.exists(SAMPLE_DATA_DIR):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample data directory not found"
        )

    # Get list of files to load
    if filenames:
        files_to_load = [f for f in filenames if os.path.exists(os.path.join(SAMPLE_DATA_DIR, f))]
    else:
        files_to_load = [
            f for f in os.listdir(SAMPLE_DATA_DIR)
            if f.endswith(('.csv', '.xlsx', '.xls'))
        ]

    if not files_to_load:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid sample files to load"
        )

    loaded_files = []
    errors = []

    for filename in files_to_load:
        file_path = os.path.join(SAMPLE_DATA_DIR, filename)

        try:
            # Read file content
            with open(file_path, "rb") as f:
                content = f.read()

            # Determine content type
            if filename.endswith('.csv'):
                content_type = "text/csv"
            elif filename.endswith('.xlsx'):
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                content_type = "application/vnd.ms-excel"

            # Compute hash
            file_hash = compute_sha256(content)

            # Generate unique storage key
            unique_key = str(uuid_lib.uuid4())
            file_ext = os.path.splitext(filename)[1]
            storage_key = f"tenants/{app_id}/files/{unique_key}{file_ext}"

            # Create file record
            file_record = File(
                logical_name=filename,
                mime_type=content_type,
                workspace_id=tenant.workspace_id,
                app_id=tenant.id,
            )
            db.add(file_record)
            db.flush()

            # Create file version
            storage_provider = get_storage_provider()
            file_version = FileVersion(
                version_number=1,
                storage_provider=storage_provider,
                storage_bucket=settings.AWS_S3_BUCKET if storage_provider == StorageProvider.S3 else None,
                storage_key=storage_key,
                byte_size=len(content),
                sha256=file_hash,
                upload_status=UploadStatus.UPLOADING,
                profiling_status=ProfilingStatus.PENDING,
                file_id=file_record.id,
                workspace_id=tenant.workspace_id,
                app_id=tenant.id,
                uploaded_by_id=current_user.id,
            )
            db.add(file_version)
            db.commit()

            # Upload to storage
            upload_file(
                file_data=content,
                path=storage_key,
                content_type=content_type
            )

            # Update status
            file_version.upload_status = UploadStatus.UPLOADED
            file_version.uploaded_at = datetime.utcnow()
            db.commit()

            loaded_files.append({
                "file_id": str(file_record.id),
                "version_id": str(file_version.id),
                "original_filename": filename,
                "stored_filename": f"{unique_key}{file_ext}",
                "size": len(content)
            })

        except Exception as e:
            errors.append({
                "filename": filename,
                "error": str(e)
            })

    return APIResponse(
        success=True,
        data={
            "loaded": loaded_files,
            "errors": errors,
            "total_loaded": len(loaded_files),
            "total_errors": len(errors)
        }
    )


# ============== Profiling Endpoints ==============

class ProfileResponse(BaseModel):
    """File profile response."""
    file_version_id: str
    file_id: str
    filename: str
    row_count: int
    column_count: int
    profiling_status: str
    profile_json: Optional[dict] = None


@router.post("/profile/{app_id}/{file_version_id}", response_model=APIResponse[ProfileResponse])
async def profile_file_version(
    app_id: str,
    file_version_id: str,
    sheet_name: Optional[str] = Query(None, description="Sheet name for Excel files"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Run profiling on a file version.

    Analyzes the file to extract statistics including:
    - Row and column counts
    - Column data types
    - Null value statistics
    - Numeric statistics (min, max, mean, etc.)
    - Sample data
    - Duplicate detection
    """
    from app.services.profiler import profile_file as run_profile

    # Check tenant access
    tenant = check_tenant_access(db, current_user, app_id, require_write=False)

    # Get file version
    file_version = db.query(FileVersion).filter(
        FileVersion.id == file_version_id,
        FileVersion.app_id == app_id,
    ).first()

    if not file_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_record = db.query(File).filter(File.id == file_version.file_id).first()

    # Check if already profiled
    if file_version.profiling_status == ProfilingStatus.COMPLETED and file_version.profile_json:
        return APIResponse(
            success=True,
            data=ProfileResponse(
                file_version_id=str(file_version.id),
                file_id=str(file_record.id),
                filename=file_record.logical_name,
                row_count=file_version.row_count or 0,
                column_count=file_version.column_count or 0,
                profiling_status=file_version.profiling_status.value,
                profile_json=file_version.profile_json,
            ),
            meta={"cached": True}
        )

    # Download file content
    try:
        content = download_file(file_version.storage_key)
    except StorageError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage"
        )

    # Update status to running
    file_version.profiling_status = ProfilingStatus.RUNNING
    if sheet_name:
        file_version.xlsx_sheet = sheet_name
    db.commit()

    try:
        # Run profiling
        profile_data = run_profile(
            file_content=content,
            mime_type=file_record.mime_type,
            sheet_name=sheet_name or file_version.xlsx_sheet
        )

        # Update file version with profile data
        file_version.profiling_status = ProfilingStatus.COMPLETED
        file_version.profile_json = profile_data
        file_version.row_count = profile_data["summary"]["row_count"]
        file_version.column_count = profile_data["summary"]["column_count"]
        db.commit()
        db.refresh(file_version)

        return APIResponse(
            success=True,
            data=ProfileResponse(
                file_version_id=str(file_version.id),
                file_id=str(file_record.id),
                filename=file_record.logical_name,
                row_count=file_version.row_count,
                column_count=file_version.column_count,
                profiling_status=file_version.profiling_status.value,
                profile_json=file_version.profile_json,
            )
        )

    except ValueError as e:
        # Profiling failed - parsing error
        file_version.profiling_status = ProfilingStatus.FAILED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to profile file: {str(e)}"
        )
    except Exception as e:
        # Profiling failed - unexpected error
        file_version.profiling_status = ProfilingStatus.FAILED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profiling failed: {str(e)}"
        )


@router.get("/profile/{app_id}/{file_version_id}", response_model=APIResponse[ProfileResponse])
async def get_file_profile(
    app_id: str,
    file_version_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the profile for a file version."""
    # Check tenant access
    tenant = check_tenant_access(db, current_user, app_id, require_write=False)

    # Get file version
    file_version = db.query(FileVersion).filter(
        FileVersion.id == file_version_id,
        FileVersion.app_id == app_id,
    ).first()

    if not file_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_record = db.query(File).filter(File.id == file_version.file_id).first()

    # Check rollup access - rollup users can see profile summary but not sample data
    is_rollup = False
    if not current_user.is_super_admin() and not current_user.is_customer_admin():
        membership = db.query(PortcoMember).filter(
            PortcoMember.app_id == app_id,
            PortcoMember.user_id == current_user.id,
        ).first()
        if membership and membership.access_level == AccessLevel.ROLLUP_ONLY:
            is_rollup = True

    # Redact sample data for rollup users
    profile_json = file_version.profile_json
    if is_rollup and profile_json:
        profile_json = dict(profile_json)
        profile_json.pop("sample_data", None)
        profile_json.pop("string_statistics", None)

    return APIResponse(
        success=True,
        data=ProfileResponse(
            file_version_id=str(file_version.id),
            file_id=str(file_record.id),
            filename=file_record.logical_name,
            row_count=file_version.row_count or 0,
            column_count=file_version.column_count or 0,
            profiling_status=file_version.profiling_status.value,
            profile_json=profile_json,
        )
    )


# ============== Preview Endpoint ==============

class FilePreviewResponse(BaseModel):
    """File preview data."""
    headers: List[str]
    rows: List[List[str]]
    total_rows: int
    total_columns: int


@router.get("/preview/{app_id}/{file_version_id}", response_model=APIResponse[FilePreviewResponse])
async def preview_file(
    app_id: str,
    file_version_id: str,
    rows: int = Query(50, ge=1, le=500, description="Number of rows to preview"),
    sheet_name: Optional[str] = Query(None, description="Sheet name for Excel files"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Preview file contents.

    Returns headers and a limited number of rows for display in the UI.
    """
    import pandas as pd
    from io import BytesIO

    # Check tenant access
    tenant = check_tenant_access(db, current_user, app_id, require_write=False)

    # Get file version
    file_version = db.query(FileVersion).filter(
        FileVersion.id == file_version_id,
        FileVersion.app_id == app_id,
    ).first()

    if not file_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_record = db.query(File).filter(File.id == file_version.file_id).first()

    # Download file content
    try:
        content = download_file(file_version.storage_key)
    except StorageError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage"
        )

    # Parse file based on type
    try:
        if file_record.mime_type == "text/csv":
            df = pd.read_csv(BytesIO(content), nrows=rows)
        elif file_record.mime_type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]:
            sheet = sheet_name or file_version.xlsx_sheet or 0
            df = pd.read_excel(BytesIO(content), sheet_name=sheet, nrows=rows)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type for preview"
            )

        # Convert to list format
        headers = df.columns.tolist()
        data_rows = df.fillna('').astype(str).values.tolist()

        # Get total counts if already profiled
        total_rows = file_version.row_count or len(data_rows)
        total_columns = file_version.column_count or len(headers)

        return APIResponse(
            success=True,
            data=FilePreviewResponse(
                headers=headers,
                rows=data_rows,
                total_rows=total_rows,
                total_columns=total_columns,
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse file for preview: {str(e)}"
        )


# ============== S3 Direct Upload Endpoint ==============

class S3UploadResponse(BaseModel):
    """Response after S3 upload."""
    s3_path: str
    file_name: str
    file_size: int
    metadata_path: str
    app_id: str
    dataset_name: str
    table_created: bool = False
    table_name: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None


@router.post("/upload-s3/{app_id}", response_model=APIResponse[S3UploadResponse])
async def upload_to_s3(
    app_id: str,
    file: UploadFile = FastAPIFile(...),
    table_name: str = Form(...),
    metadata: str = Form(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a file directly to S3 with metadata.

    This endpoint:
    1. Uploads the data file to S3 at tenant/{app_id}/{table_name}/data.{ext}
    2. Uploads the metadata JSON to S3 at tenant/{app_id}/{table_name}/metadata.json

    Uses environment variables: S3_BUCKET, S3_ROOT_PREFIX, AWS_REGION
    """
    import json

    # Check tenant access (requires write access)
    tenant = check_tenant_access(db, current_user, app_id, require_write=True)

    # Validate file type
    original_filename = file.filename or "unknown"
    content_type = get_validated_content_type(original_filename, file.content_type)
    if content_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: CSV, XLS, XLSX. Got: {file.content_type}"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 100MB"
        )

    # Parse metadata JSON
    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid metadata JSON"
        )

    # Validate table name
    import re
    if not re.match(r'^[a-z][a-z0-9_]*$', table_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid table name. Must start with a letter and contain only lowercase letters, numbers, and underscores."
        )

    # Determine file extension
    file_ext = ALLOWED_FILE_TYPES.get(content_type, ".csv")

    # Create sanitized tenant folder name (lowercase, replace spaces/special chars with hyphens)
    tenant_folder_name = re.sub(r'[^a-z0-9]+', '-', tenant.name.lower()).strip('-')
    tenant_folder = f"tenant-{tenant_folder_name}-{app_id}"

    # Create S3 paths under data/{tenant-name-id}/{table_name}/
    # data/tenant-{name}-{id}/{table_name}/data.{ext}
    # data/tenant-{name}-{id}/{table_name}/metadata.json
    data_key = f"data/{tenant_folder}/{table_name}/data{file_ext}"
    metadata_key = f"data/{tenant_folder}/{table_name}/metadata.json"

    try:
        # Upload data file to S3
        data_path = upload_file(
            file_data=content,
            path=data_key,
            content_type=content_type
        )

        # Add upload info to metadata
        metadata_dict["uploaded_by"] = current_user.user.full_name
        metadata_dict["uploaded_by_id"] = str(current_user.id)
        metadata_dict["uploaded_at"] = datetime.utcnow().isoformat()
        metadata_dict["file_size"] = len(content)
        metadata_dict["s3_data_path"] = data_key
        metadata_dict["app_id"] = app_id
        metadata_dict["tenant_name"] = tenant.name

        # Upload metadata to S3
        metadata_bytes = json.dumps(metadata_dict, indent=2).encode('utf-8')
        metadata_path = upload_file(
            file_data=metadata_bytes,
            path=metadata_key,
            content_type="application/json"
        )

        # Process data and create PostgreSQL table
        table_created = False
        table_result = None
        try:
            from app.services.data_processor import process_and_create_table

            table_result = process_and_create_table(
                db=db,
                content=content,
                content_type=content_type,
                metadata=metadata_dict,
                table_name=table_name,
                app_id=app_id,
                tenant_name=tenant.name,
                workspace_id=str(tenant.workspace_id) if tenant.workspace_id else None,
                s3_data_path=data_key,
                s3_metadata_path=metadata_key,
                created_by_id=str(current_user.id),
                created_by_name=current_user.user.full_name,
                schema='data'
            )
            table_created = True
            print(f"[Data] Created table: {table_result['table_name']}")
            print(f"[Data] Rows: {table_result['row_count']}, Columns: {table_result['column_count']}")
        except Exception as e:
            # Log error but don't fail the upload - table creation is secondary
            import traceback
            print(f"[Data] Failed to create table: {str(e)}")
            traceback.print_exc()

        return APIResponse(
            success=True,
            data=S3UploadResponse(
                s3_path=data_path,
                file_name=original_filename,
                file_size=len(content),
                metadata_path=metadata_path,
                app_id=app_id,
                dataset_name=metadata_dict.get("name", table_name),
                table_created=table_created,
                table_name=table_result['table_name'] if table_result else None,
                row_count=table_result['row_count'] if table_result else None,
                column_count=table_result['column_count'] if table_result else None,
            ),
            meta={
                "message": "File uploaded to S3 and table created successfully" if table_created else "File uploaded to S3 successfully (table creation pending)"
            }
        )

    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload to S3: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


# ============== Finalize Dataset Endpoint ==============

class FieldMappingSchema(BaseModel):
    """Field mapping schema."""
    originalField: str
    mappedField: str
    dataType: str
    description: Optional[str] = ""


class DatasetMetadata(BaseModel):
    """Dataset metadata."""
    name: str
    description: Optional[str] = ""
    categories: List[str] = []
    field_mappings: List[FieldMappingSchema] = []
    original_filename: Optional[str] = None
    created_at: Optional[str] = None


class FinalizeDatasetRequest(BaseModel):
    """Request to finalize a dataset."""
    table_name: str
    meta_data: DatasetMetadata


class FinalizeDatasetResponse(BaseModel):
    """Response after finalizing a dataset."""
    dataset_id: str
    table_name: str
    status: str


@router.post("/finalize/{app_id}/{file_version_id}", response_model=APIResponse[FinalizeDatasetResponse])
async def finalize_dataset(
    app_id: str,
    file_version_id: str,
    request: FinalizeDatasetRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Finalize a dataset with metadata.

    This creates a logical dataset record with the provided metadata,
    associates it with the uploaded file, and optionally creates a
    database table with the data.
    """
    import json

    # Check tenant access (requires write access)
    tenant = check_tenant_access(db, current_user, app_id, require_write=True)

    # Get file version
    file_version = db.query(FileVersion).filter(
        FileVersion.id == file_version_id,
        FileVersion.app_id == app_id,
    ).first()

    if not file_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_record = db.query(File).filter(File.id == file_version.file_id).first()

    # Validate table name
    import re
    if not re.match(r'^[a-z][a-z0-9_]*$', request.table_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid table name. Must start with a letter and contain only lowercase letters, numbers, and underscores."
        )

    # Store metadata in file version
    metadata_dict = request.meta_data.model_dump()
    file_version.dataset_name = request.meta_data.name
    file_version.dataset_table_name = request.table_name
    file_version.dataset_metadata = metadata_dict

    # Update profiling status to indicate dataset is configured
    if file_version.profiling_status != ProfilingStatus.COMPLETED:
        file_version.profiling_status = ProfilingStatus.COMPLETED

    db.commit()
    db.refresh(file_version)

    return APIResponse(
        success=True,
        data=FinalizeDatasetResponse(
            dataset_id=str(file_version.id),
            table_name=request.table_name,
            status="finalized"
        ),
        meta={
            "message": "Dataset configured successfully"
        }
    )
