"""
Global tenant state management.

This module maintains mutable global state for multi-tenant configuration.
Tenant configuration is resolved at runtime based on the request origin/subdomain.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from typing import Optional
from dataclasses import dataclass, field
from threading import Lock
from pydantic import BaseModel

class Settings(BaseModel):
    """Application configuration settings."""

    APP_NAME: str = "Labs"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Create settings singleton
settings = Settings()

# Database schema
DB_SCHEMA: str = os.getenv("DB_SCHEMA", "data")

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"


# ============================================================================
# DEFAULT VALUES (from environment)
# ============================================================================
if IS_PRODUCTION:
    _DEFAULT_DBHOST = os.getenv("DBHOST")
    _DEFAULT_DBUSER = os.getenv("DBUSER", "dbadmin")
    _DEFAULT_DBPORT = int(os.getenv("DBPORT", "5432"))
    _DEFAULT_S3_BUCKET = os.getenv("S3_BUCKET", "tenants-s3")
    _DEFAULT_S3_ROOT_PREFIX = os.getenv("S3_ROOT_PREFIX", "base-tenant/")
    _DEFAULT_AWS_REGION = os.getenv("AWS_REGION", "us-west-1")
    _DEFAULT_AWS_PROFILE = None
    _DEFAULT_DEFAULTDB = os.getenv("DEFAULT_DB", "base_tenant_main")
else:
    _DEFAULT_DBHOST = os.getenv("DBHOST_NLIGHTNLABS_TENANT", "tenant-rds.c5ws0iyoa9k7.us-west-1.rds.amazonaws.com")
    _DEFAULT_DBUSER = os.getenv("DBUSER_NLIGHTNLABS_TENANT", "dbadmin")
    _DEFAULT_DBPORT = int(os.getenv("DBPORT_NLIGHTNLABS_TENANT", "5432"))
    _DEFAULT_S3_BUCKET = os.getenv("S3_BUCKET_NLIGHTNLABS", "tenants-s3")
    _DEFAULT_S3_ROOT_PREFIX = os.getenv("S3_ROOT_PREFIX_NLIGHTNLABS", "base-tenant/")
    _DEFAULT_AWS_REGION = os.getenv("AWS_REGION_NLIGHTNLABS", "us-west-1")
    _DEFAULT_AWS_PROFILE = os.getenv("AWS_PROFILE_NLIGHTNLABS", "NLIGHTNLABS")
    _DEFAULT_DEFAULTDB = os.getenv("DEFAULT_DB_NLIGHTNLABS", "base_tenant_main")


# ============================================================================
# TENANT STATE
# ============================================================================

@dataclass
class TenantConfig:
    """Configuration for a specific tenant."""
    tenant_name: str = "base-tenant"
    db_host: str = field(default_factory=lambda: _DEFAULT_DBHOST)
    db_user: str = field(default_factory=lambda: _DEFAULT_DBUSER)
    db_port: int = field(default_factory=lambda: _DEFAULT_DBPORT)
    db_name: str = field(default_factory=lambda: _DEFAULT_DEFAULTDB)
    s3_bucket: str = field(default_factory=lambda: _DEFAULT_S3_BUCKET)
    s3_root_prefix: str = field(default_factory=lambda: _DEFAULT_S3_ROOT_PREFIX)
    aws_region: str = field(default_factory=lambda: _DEFAULT_AWS_REGION)
    aws_profile: Optional[str] = field(default_factory=lambda: _DEFAULT_AWS_PROFILE)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "tenant_name": self.tenant_name,
            "db_host": self.db_host,
            "db_user": self.db_user,
            "db_port": self.db_port,
            "db_name": self.db_name,
            "s3_bucket": self.s3_bucket,
            "s3_root_prefix": self.s3_root_prefix,
            "aws_region": self.aws_region,
            "aws_profile": self.aws_profile,
        }


class TenantState:
    """
    Thread-safe global tenant state manager.

    This class manages the current tenant configuration and provides
    methods for updating and accessing tenant-specific settings.
    """

    def __init__(self):
        self._lock = Lock()
        self._config = TenantConfig()
        self._initialized = False

    @property
    def config(self) -> TenantConfig:
        """Get the current tenant configuration."""
        with self._lock:
            return self._config

    @property
    def is_initialized(self) -> bool:
        """Check if tenant has been initialized."""
        with self._lock:
            return self._initialized

    def set_config(self, config: TenantConfig):
        """Set the tenant configuration."""
        with self._lock:
            self._config = config
            self._initialized = True

    def update_config(self, **kwargs):
        """Update specific fields of the tenant configuration."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
            self._initialized = True

    def reset(self):
        """Reset to default configuration."""
        with self._lock:
            self._config = TenantConfig()
            self._initialized = False

    # Convenience properties for backward compatibility
    @property
    def TENANT_NAME(self) -> str:
        return self.config.tenant_name

    @TENANT_NAME.setter
    def TENANT_NAME(self, value: str):
        self.update_config(tenant_name=value)

    @property
    def DBHOST(self) -> str:
        return self.config.db_host

    @DBHOST.setter
    def DBHOST(self, value: str):
        self.update_config(db_host=value)

    @property
    def DBUSER(self) -> str:
        return self.config.db_user

    @property
    def DBPORT(self) -> int:
        return self.config.db_port

    @property
    def DEFAULTDB(self) -> str:
        return self.config.db_name

    @DEFAULTDB.setter
    def DEFAULTDB(self, value: str):
        self.update_config(db_name=value)

    @property
    def S3_BUCKET(self) -> str:
        return self.config.s3_bucket

    @S3_BUCKET.setter
    def S3_BUCKET(self, value: str):
        self.update_config(s3_bucket=value)

    @property
    def S3_ROOT_PREFIX(self) -> str:
        return self.config.s3_root_prefix

    @S3_ROOT_PREFIX.setter
    def S3_ROOT_PREFIX(self, value: str):
        self.update_config(s3_root_prefix=value)

    @property
    def AWS_REGION(self) -> str:
        return self.config.aws_region

    @property
    def AWS_PROFILE(self) -> Optional[str]:
        return self.config.aws_profile


# Global singleton instance
_tenant_state = TenantState()


def get_tenant_state() -> TenantState:
    """Get the global tenant state instance."""
    return _tenant_state


def get_globals() -> dict:
    """
    Get current global tenant configuration as a dictionary.

    Returns a dict with keys matching the original globals pattern:
    - tenant_name
    - db_host
    - db_name
    - s3_bucket
    - s3_root_prefix
    - aws_region
    """
    state = get_tenant_state()
    return state.config.to_dict()


def set_tenant_config(
    tenant_name: str,
    db_host: str,
    db_name: str,
    s3_bucket: str,
    s3_root_prefix: str,
    **kwargs
):
    """
    Set the tenant configuration.

    Args:
        tenant_name: Name of the tenant
        db_host: Database host endpoint
        db_name: Database name
        s3_bucket: S3 bucket name
        s3_root_prefix: S3 key prefix for this tenant
        **kwargs: Additional configuration options
    """
    state = get_tenant_state()
    config = TenantConfig(
        tenant_name=tenant_name,
        db_host=db_host,
        db_name=db_name,
        s3_bucket=s3_bucket,
        s3_root_prefix=s3_root_prefix,
        db_user=kwargs.get('db_user', _DEFAULT_DBUSER),
        db_port=kwargs.get('db_port', _DEFAULT_DBPORT),
        aws_region=kwargs.get('aws_region', _DEFAULT_AWS_REGION),
        aws_profile=kwargs.get('aws_profile', _DEFAULT_AWS_PROFILE),
    )
    state.set_config(config)


def reset_tenant_config():
    """Reset tenant configuration to defaults."""
    get_tenant_state().reset()


# ============================================================================
# BACKWARD COMPATIBLE GLOBAL VARIABLES
# ============================================================================
# These provide direct access similar to the original globals.py pattern

# Create a proxy that allows both reading and writing
class _GlobalProxy:
    """Proxy class for backward-compatible global variable access."""

    def __getattr__(self, name):
        state = get_tenant_state()
        if hasattr(state, name):
            return getattr(state, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __setattr__(self, name, value):
        state = get_tenant_state()
        if hasattr(state, name):
            setattr(state, name, value)
        else:
            object.__setattr__(self, name, value)


# Export proxy instance for backward compatibility
globals_proxy = _GlobalProxy()


# Direct exports for module-level access
TENANT_NAME = property(lambda self: get_tenant_state().TENANT_NAME)
DBHOST = property(lambda self: get_tenant_state().DBHOST)
DBUSER = property(lambda self: get_tenant_state().DBUSER)
DBPORT = property(lambda self: get_tenant_state().DBPORT)
DEFAULTDB = property(lambda self: get_tenant_state().DEFAULTDB)
S3_BUCKET = property(lambda self: get_tenant_state().S3_BUCKET)
S3_ROOT_PREFIX = property(lambda self: get_tenant_state().S3_ROOT_PREFIX)
AWS_REGION = property(lambda self: get_tenant_state().AWS_REGION)
AWS_PROFILE = property(lambda self: get_tenant_state().AWS_PROFILE)
