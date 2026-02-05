"""Analysis and Finding models for anomaly detection."""

from sqlalchemy import Column, String, BigInteger, Text, ForeignKey, Enum, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class AnalysisStatus(str, enum.Enum):
    """Analysis job status enumeration."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class DetectorType(str, enum.Enum):
    """Detector types for analysis."""
    MISSING_REQUIRED_IDS = "MISSING_REQUIRED_IDS"
    INVALID_DATE_FORMAT = "INVALID_DATE_FORMAT"
    DUPLICATE_KEYS = "DUPLICATE_KEYS"
    PERIOD_GAPS = "PERIOD_GAPS"
    CURRENCY_INCONSISTENCY = "CURRENCY_INCONSISTENCY"
    OUTLIER_ZSCORE = "OUTLIER_ZSCORE"
    DISCONTINUITY = "DISCONTINUITY"
    IMPOSSIBLE_RATIO = "IMPOSSIBLE_RATIO"
    TB_IMBALANCE = "TB_IMBALANCE"
    GL_TB_MISMATCH = "GL_TB_MISMATCH"
    VARIANCE_MISMATCH = "VARIANCE_MISMATCH"
    NEGATIVE_REVENUE = "NEGATIVE_REVENUE"


class FindingSeverity(str, enum.Enum):
    """Finding severity levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FindingConfidence(str, enum.Enum):
    """Finding confidence levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FindingStatus(str, enum.Enum):
    """Finding workflow status."""
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    ACCEPTED = "ACCEPTED"
    RESOLVED = "RESOLVED"


class AnalysisJob(Base, UUIDMixin, TimestampMixin):
    """Analysis job model."""

    __tablename__ = "analysis_jobs"

    # Idempotency key to prevent duplicate runs
    idempotency_key = Column(String(100), nullable=True, unique=True)

    # Status
    status = Column(
        Enum(AnalysisStatus, values_callable=lambda x: [e.value for e in x]),
        default=AnalysisStatus.PENDING,
        nullable=False
    )
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Results summary
    findings_count = Column(BigInteger, default=0, nullable=False)
    high_severity_count = Column(BigInteger, default=0, nullable=False)
    medium_severity_count = Column(BigInteger, default=0, nullable=False)
    low_severity_count = Column(BigInteger, default=0, nullable=False)

    # Configuration
    detectors_config = Column(JSONB, nullable=True)  # Which detectors to run

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
    file_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("file_versions.id", ondelete="SET NULL"),
        nullable=True
    )
    triggered_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    workspace = relationship("Organization", foreign_keys=[workspace_id])
    portco = relationship("Portco", back_populates="analysis_jobs")
    file_version = relationship("FileVersion")
    triggered_by = relationship("User", foreign_keys=[triggered_by_id])
    findings = relationship("Finding", back_populates="analysis_job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_analysis_jobs_workspace_portco", "workspace_id", "portco_id"),
    )

    def __repr__(self) -> str:
        return f"<AnalysisJob {self.id} status={self.status}>"


class Finding(Base, UUIDMixin, TimestampMixin):
    """Finding model for detected anomalies."""

    __tablename__ = "findings"

    # Detection info
    detector_type = Column(
        Enum(DetectorType, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Severity and confidence
    severity = Column(
        Enum(FindingSeverity, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    confidence = Column(
        Enum(FindingConfidence, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    # Workflow status
    status = Column(
        Enum(FindingStatus, values_callable=lambda x: [e.value for e in x]),
        default=FindingStatus.OPEN,
        nullable=False
    )

    # Evidence (redacted for rollup-only users)
    evidence_json = Column(JSONB, nullable=True)  # Raw evidence data
    affected_rows = Column(BigInteger, nullable=True)
    affected_columns = Column(JSONB, nullable=True)  # List of column names

    # Foreign keys
    analysis_job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analysis_jobs.id", ondelete="CASCADE"),
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
    assigned_to_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    analysis_job = relationship("AnalysisJob", back_populates="findings")
    workspace = relationship("Organization", foreign_keys=[workspace_id])
    portco = relationship("Portco")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    comments = relationship("FindingComment", back_populates="finding", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_findings_workspace_portco", "workspace_id", "portco_id"),
        Index("ix_findings_severity_status", "severity", "status"),
    )

    def __repr__(self) -> str:
        return f"<Finding {self.id} {self.detector_type} {self.severity}>"


class FindingComment(Base, UUIDMixin, TimestampMixin):
    """Finding comment model for workflow discussions."""

    __tablename__ = "finding_comments"

    content = Column(Text, nullable=False)

    # Foreign keys
    finding_id = Column(
        UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    finding = relationship("Finding", back_populates="comments")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<FindingComment {self.id}>"
