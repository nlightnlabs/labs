"""
Global configuration variables for backward compatibility.

This module provides the global variables expected by postgres_db.py
by re-exporting values from the config module's TenantState.
"""

from app.config import get_tenant_state, _DEFAULT_DBHOST, _DEFAULT_DBUSER, _DEFAULT_DBPORT, _DEFAULT_DEFAULTDB
from app.config import _DEFAULT_S3_BUCKET, _DEFAULT_S3_ROOT_PREFIX, _DEFAULT_AWS_REGION, _DEFAULT_AWS_PROFILE
from app.config import ENVIRONMENT, IS_PRODUCTION

# Get the tenant state instance
_state = get_tenant_state()

# Export variables that postgres_db.py expects
AWS_REGION = _DEFAULT_AWS_REGION
AWS_PROFILE = _DEFAULT_AWS_PROFILE
TENANT_NAME = _state.TENANT_NAME
DBHOST = _DEFAULT_DBHOST
DBUSER = _DEFAULT_DBUSER
DBPORT = _DEFAULT_DBPORT
DEFAULT_DB = _DEFAULT_DEFAULTDB
S3_BUCKET = _DEFAULT_S3_BUCKET
S3_ROOT_PREFIX = _DEFAULT_S3_ROOT_PREFIX
