"""SAML Provider model."""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SAMLProvider(Base, UUIDMixin, TimestampMixin):
    """SAML Provider model for SSO configuration."""

    __tablename__ = "saml_providers"

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    provider_name = Column(String(100), nullable=False)
    entity_id = Column(String(255), nullable=False)
    sso_url = Column(String(500), nullable=False)
    x509_cert = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="saml_providers")

    def __repr__(self) -> str:
        return f"<SAMLProvider {self.provider_name}>"
