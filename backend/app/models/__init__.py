"""SQLAlchemy database models."""

from app.models.base import Base
from app.models.user import User, UserRole, WorkspaceRole
from app.models.organization import Organization
from app.models.user_preferences import UserPreferences
from app.models.session import Session
from app.models.saml_provider import SAMLProvider
from app.models.password_reset_token import PasswordResetToken
from app.models.notification import Notification

# Illuminis-specific models
from app.models.portco import Portco, PortcoStatus
from app.models.portco_member import PortcoMember, PortcoRole, AccessLevel
from app.models.file import File, FileVersion, StorageProvider, UploadStatus, ProfilingStatus
from app.models.billing import BillingAccount, BillingEvent, BillingStatus, BillingEventType, BlockReason
from app.models.analysis import (
    AnalysisJob, Finding, FindingComment,
    AnalysisStatus, DetectorType, FindingSeverity, FindingConfidence, FindingStatus
)
from app.models.audit import AuditEvent, AuditAction
from app.models.fun import FunSettings, FunAgent, FunLine

__all__ = [
    # Base
    "Base",

    # Core models
    "User",
    "UserRole",
    "WorkspaceRole",
    "Organization",
    "UserPreferences",
    "Session",
    "SAMLProvider",
    "PasswordResetToken",
    "Notification",

    # PortCo models
    "Portco",
    "PortcoStatus",
    "PortcoMember",
    "PortcoRole",
    "AccessLevel",

    # File models
    "File",
    "FileVersion",
    "StorageProvider",
    "UploadStatus",
    "ProfilingStatus",

    # Billing models
    "BillingAccount",
    "BillingEvent",
    "BillingStatus",
    "BillingEventType",
    "BlockReason",

    # Analysis models
    "AnalysisJob",
    "Finding",
    "FindingComment",
    "AnalysisStatus",
    "DetectorType",
    "FindingSeverity",
    "FindingConfidence",
    "FindingStatus",

    # Audit models
    "AuditEvent",
    "AuditAction",

    # Fun layer models
    "FunSettings",
    "FunAgent",
    "FunLine",
]
