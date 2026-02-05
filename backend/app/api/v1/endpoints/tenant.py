"""Tenant configuration API endpoints."""

from urllib.parse import urlparse
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from app.utils.database import get_db, get_base_db
from app.utils.storage import reset_storage_provider
from app.config import (
    get_tenant_state,
    get_globals,
    set_tenant_config,
    TenantConfig,
    _DEFAULT_DBHOST,
    _DEFAULT_DBUSER,
    _DEFAULT_DBPORT,
    _DEFAULT_AWS_REGION,
    _DEFAULT_AWS_PROFILE,
    _DEFAULT_S3_BUCKET,
    _DEFAULT_S3_ROOT_PREFIX,
    _DEFAULT_DEFAULTDB,
)

router = APIRouter()


# ============== Schemas ==============

class TenantConfigResponse(BaseModel):
    """Response schema for tenant configuration."""
    tenant_name: str
    db_host: str
    db_name: str
    s3_bucket: str
    s3_root_prefix: str
    aws_region: str
    initialized: bool


class TenantInfo(BaseModel):
    """Schema for tenant lookup result."""
    tenant_name: str
    rds_endpoint: str
    database_name: str
    s3_bucket: str
    s3_root_prefix: str


# ============== Constants ==============

# Base database name for tenant lookup (always use this for lookups)
# The host is configured via environment variables in database.py
BASE_DB_NAME = "base"

# Default tenant configuration (for localhost development)
# Uses environment variables to match the configured database
DEFAULT_TENANT = TenantConfig(
    tenant_name="base-tenant",
    db_host=_DEFAULT_DBHOST,
    db_name=_DEFAULT_DEFAULTDB or "base_tenant_main",
    s3_bucket=_DEFAULT_S3_BUCKET or "tenants-s3",
    s3_root_prefix=_DEFAULT_S3_ROOT_PREFIX or "base-tenant/",
)


# ============== Helper Functions ==============

def extract_tenant_from_origin(origin: str) -> Optional[str]:
    """
    Extract tenant name from the origin URL.

    Examples:
        https://acme.illuminis.ai -> acme
        https://localhost:3000 -> None (localhost)
        https://demo.staging.illuminis.ai -> demo

    Returns:
        Tenant name or None if localhost
    """
    parsed = urlparse(origin)
    hostname = parsed.hostname

    if not hostname:
        return None

    # Check for localhost
    if "localhost" in hostname or hostname in ("127.0.0.1", "0.0.0.0"):
        return None

    # Extract subdomain (first part of hostname)
    # e.g., acme.illuminis.ai -> acme
    parts = hostname.split(".")
    if len(parts) >= 2:
        return parts[0]

    return None


async def lookup_tenant(tenant_name: str, db: Session) -> Optional[TenantInfo]:
    """
    Look up tenant configuration from the base database.

    Args:
        tenant_name: Name of the tenant to look up
        db: Database session (connected to base database)

    Returns:
        TenantInfo if found, None otherwise
    """
    try:
        # Query the tenants table in the base database
        query = text("""
            SELECT
                tenant_name,
                rds_endpoint,
                database_name,
                s3_bucket,
                s3_root_prefix
            FROM data.tenants
            WHERE tenant_name = :tenant_name
            AND is_active = true
        """)

        result = db.execute(query, {"tenant_name": tenant_name})
        row = result.fetchone()

        if row:
            return TenantInfo(
                tenant_name=row.tenant_name,
                rds_endpoint=row.rds_endpoint,
                database_name=row.database_name,
                s3_bucket=row.s3_bucket,
                s3_root_prefix=row.s3_root_prefix,
            )

        return None

    except Exception as e:
        print(f"Error looking up tenant {tenant_name}: {e}")
        return None


# ============== Endpoints ==============

@router.post("/config", response_model=TenantConfigResponse)
async def get_tenant_config(
    request: Request,
    db: Session = Depends(get_base_db),
):
    """
    Determine and configure tenant based on request origin.

    This endpoint should be called when the frontend application loads
    to initialize the correct tenant configuration.

    The tenant is determined by:
    1. Extracting the subdomain from the Origin/Referer header
    2. Looking up the tenant in the base database
    3. Configuring global state with the tenant's infrastructure settings

    For localhost development, it defaults to 'base-tenant'.
    """
    # Get origin from headers
    origin = request.headers.get("origin") or request.headers.get("referer")

    if not origin:
        raise HTTPException(
            status_code=400,
            detail="Missing Origin or Referer header"
        )

    parsed = urlparse(origin)
    hostname = parsed.hostname

    if not hostname:
        raise HTTPException(
            status_code=400,
            detail="Invalid Origin header - could not parse hostname"
        )

    state = get_tenant_state()

    # Check for localhost/development
    if "localhost" in origin or "127.0.0.1" in origin or "0.0.0.0" in origin:
        print(f"[Tenant] Development mode - using default tenant")

        set_tenant_config(
            tenant_name=DEFAULT_TENANT.tenant_name,
            db_host=DEFAULT_TENANT.db_host,
            db_name=DEFAULT_TENANT.db_name,
            s3_bucket=DEFAULT_TENANT.s3_bucket,
            s3_root_prefix=DEFAULT_TENANT.s3_root_prefix,
        )

        # Reset storage provider to use new tenant config
        reset_storage_provider()

        config = state.config
        return TenantConfigResponse(
            tenant_name=config.tenant_name,
            db_host=config.db_host,
            db_name=config.db_name,
            s3_bucket=config.s3_bucket,
            s3_root_prefix=config.s3_root_prefix,
            aws_region=config.aws_region,
            initialized=True,
        )

    # Production - extract tenant from subdomain
    tenant_name = extract_tenant_from_origin(origin)

    if not tenant_name:
        raise HTTPException(
            status_code=400,
            detail=f"Could not determine tenant from hostname: {hostname}"
        )

    print(f"[Tenant] Looking up tenant: {tenant_name}")

    # Look up tenant in the base database
    tenant_info = await lookup_tenant(tenant_name, db)

    if not tenant_info:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant not found: {tenant_name}"
        )

    # Configure global state with tenant settings
    set_tenant_config(
        tenant_name=tenant_info.tenant_name,
        db_host=tenant_info.rds_endpoint,
        db_name=tenant_info.database_name,
        s3_bucket=tenant_info.s3_bucket,
        s3_root_prefix=tenant_info.s3_root_prefix,
    )

    # Reset storage provider to use new tenant config
    reset_storage_provider()

    config = state.config
    print(f"[Tenant] Configured tenant: {config.tenant_name}")
    print(f"[Tenant] S3 Bucket: {config.s3_bucket}")
    print(f"[Tenant] S3 Prefix: {config.s3_root_prefix}")

    return TenantConfigResponse(
        tenant_name=config.tenant_name,
        db_host=config.db_host,
        db_name=config.db_name,
        s3_bucket=config.s3_bucket,
        s3_root_prefix=config.s3_root_prefix,
        aws_region=config.aws_region,
        initialized=True,
    )


@router.get("/current", response_model=TenantConfigResponse)
async def get_current_tenant():
    """
    Get the current tenant configuration.

    Returns the currently configured tenant settings.
    If tenant has not been initialized, returns default configuration.
    """
    state = get_tenant_state()
    config = state.config

    return TenantConfigResponse(
        tenant_name=config.tenant_name,
        db_host=config.db_host,
        db_name=config.db_name,
        s3_bucket=config.s3_bucket,
        s3_root_prefix=config.s3_root_prefix,
        aws_region=config.aws_region,
        initialized=state.is_initialized,
    )


@router.get("/globals")
async def get_global_state():
    """
    Get the full global state dictionary.

    This endpoint is useful for debugging and verifying configuration.
    """
    return get_globals()
