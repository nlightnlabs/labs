"""File schemas for API responses."""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    id: str
    filename: str
    original_filename: str
    size: int
    content_type: str
    storage_path: str
    portco_id: str
    uploaded_by: Optional[str] = None
    uploaded_at: datetime


class FileInfo(BaseModel):
    """File information."""
    id: str
    filename: str
    original_filename: str
    size: int
    content_type: str
    storage_path: str
    portco_id: str
    uploaded_by: Optional[str] = None
    uploaded_at: datetime
    sheets: Optional[List[str]] = None  # For XLSX files


class FileListResponse(BaseModel):
    """List of files response."""
    files: List[FileInfo]
    total: int


class SampleDataFile(BaseModel):
    """Sample data file info."""
    filename: str
    size: int
    path: str
