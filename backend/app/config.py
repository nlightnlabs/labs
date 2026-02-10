"""
Global configuration loaded from .env file.
Tenant config is overridden at runtime in main.py after tenant lookup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory (parent of app/)
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
print(f"📂 Loading .env from: {ENV_PATH}", flush=True)
print(f"📂 .env file exists: {ENV_PATH.exists()}", flush=True)
load_dotenv(ENV_PATH, override=True)  # override=True to ensure .env takes precedence over shell env

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# ============================================================================
# AWS
# ============================================================================
if IS_PRODUCTION:
    AWS_REGION = os.getenv("AWS_REGION", "us-west-1")
    AWS_PROFILE = None
else:
    AWS_REGION = os.getenv("AWS_REGION_NLIGHTNLABS", "us-west-1")
    AWS_PROFILE = os.getenv("AWS_PROFILE_NLIGHTNLABS", "nlightnlabs")

# ============================================================================
# DATABASE & S3 (defaults from .env, overridden per tenant at runtime)
# ============================================================================
if IS_PRODUCTION:
    TENANT_NAME = os.getenv("TENANT_NAME", "base-tenant")
    DBHOST = os.getenv("DBHOST")
    DBUSER = os.getenv("DBUSER", "dbadmin")
    DBPORT = int(os.getenv("DBPORT", "5432"))
    DEFAULTDB = os.getenv("DEFAULT_DB", "base_tenant_main")
    S3_BUCKET = os.getenv("S3_BUCKET", "tenants-s3")
    S3_ROOT_PREFIX = os.getenv("S3_ROOT_PREFIX", "base-tenant/")
else:
    TENANT_NAME = os.getenv("TENANT_NAME", "base")
    DBHOST = os.getenv("DBHOST_NLIGHTNLABS_TENANT")
    DBUSER = os.getenv("DBUSER_NLIGHTNLABS_TENANT", "dbadmin")
    DBPORT = int(os.getenv("DBPORT_NLIGHTNLABS_TENANT", "5432"))
    DEFAULTDB = os.getenv("DEFAULT_DB_NLIGHTNLABS", "base_tenant_main")
    S3_BUCKET = os.getenv("S3_BUCKET_NLIGHTNLABS", "nlightnlabs-tenants-s3")
    S3_ROOT_PREFIX = os.getenv("S3_ROOT_PREFIX_NLIGHTNLABS", "tenants/base-tenant/")


def set_tenant_config(tenant_name: str, db_host: str, db_name: str, s3_bucket: str, s3_root_prefix: str):
    """Override global tenant config (called from main.py after tenant lookup)."""
    global TENANT_NAME, DBHOST, DEFAULTDB, S3_BUCKET, S3_ROOT_PREFIX
    TENANT_NAME = tenant_name
    DBHOST = db_host
    DEFAULTDB = db_name
    S3_BUCKET = s3_bucket
    S3_ROOT_PREFIX = s3_root_prefix
