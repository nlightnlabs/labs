"""File and FileVersion models for data uploads."""

from sqlalchemy import Column, String, BigInteger, Text, ForeignKey, Enum, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class StorageProvider(str, enum.Enum):
    """Storage provider enumeration."""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"


class UploadStatus(str, enum.Enum):
    """Upload status enumeration."""
    INITIATED = "INITIATED"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    FAILED = "FAILED"


class ProfilingStatus(str, enum.Enum):
    """Profiling status enumeration."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class File(Base, UUIDMixin, TimestampMixin):
    """File model representing a logical file."""

    __tablename__ = "files"

    # Basic info
    logical_name = Column(String(255), nullable=False)  # Original filename
    mime_type = Column(String(100), nullable=False)

    # Foreign keys
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    portco_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portcos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationships
    workspace = relationship("Organization", backref="files")
    portco = relationship("Portco", back_populates="files")
    versions = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_files_workspace_portco", "workspace_id", "portco_id"),
    )

    def __repr__(self) -> str:
        return f"<File {self.logical_name}>"


class FileVersion(Base, UUIDMixin, TimestampMixin):
    """FileVersion model for version tracking and storage details."""

    __tablename__ = "file_versions"

    # Version tracking
    version_number = Column(BigInteger, default=1, nullable=False)

    # Storage details
    storage_provider = Column(
        Enum(StorageProvider, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    storage_bucket = Column(String(255), nullable=True)
    storage_key = Column(String(1000), nullable=False)  # path/key/blob name
    storage_uri = Column(String(2000), nullable=True)  # Full URI for auditing

    # File metadata
    byte_size = Column(BigInteger, nullable=True)
    sha256 = Column(String(64), nullable=True)
    xlsx_sheet = Column(String(255), nullable=True)  # Selected sheet for XLSX files

    # Status tracking
    upload_status = Column(
        Enum(UploadStatus, values_callable=lambda x: [e.value for e in x]),
        default=UploadStatus.INITIATED,
        nullable=False
    )
    uploaded_at = Column(DateTime, nullable=True)

    # Profiling data
    profiling_status = Column(
        Enum(ProfilingStatus, values_callable=lambda x: [e.value for e in x]),
        default=ProfilingStatus.PENDING,
        nullable=False
    )
    profile_json = Column(JSONB, nullable=True)
    row_count = Column(BigInteger, nullable=True)
    column_count = Column(BigInteger, nullable=True)

    # Dataset configuration (from finalize step)
    dataset_name = Column(String(255), nullable=True)
    dataset_table_name = Column(String(255), nullable=True)
    dataset_metadata = Column(JSONB, nullable=True)  # Stores field mappings, categories, etc.

    # Foreign keys (denormalized for query efficiency)
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    portco_id = Column(
        UUID(as_uuid=True),
        ForeignKey("portcos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    uploaded_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    file = relationship("File", back_populates="versions")
    workspace = relationship("Organization", foreign_keys=[workspace_id])
    portco = relationship("Portco", foreign_keys=[portco_id])
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])

    __table_args__ = (
        Index("ix_file_versions_file_version", "file_id", "version_number"),
    )

    def __repr__(self) -> str:
        return f"<FileVersion {self.file_id} v{self.version_number}>"
