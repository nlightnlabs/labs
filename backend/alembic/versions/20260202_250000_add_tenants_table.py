"""Add tenants table for multi-tenant configuration

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-02-02 25:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h8i9j0k1l2m3'
down_revision: Union[str, None] = 'g7h8i9j0k1l2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing table if it exists (safe since this is a new feature)
    # This ensures we get the correct schema
    op.execute("""
        DROP TABLE IF EXISTS data.tenants CASCADE;
    """)

    # Create tenants table for multi-tenant configuration lookup
    op.execute("""
        CREATE TABLE data.tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_name VARCHAR(100) UNIQUE NOT NULL,
            display_name VARCHAR(255),

            -- Infrastructure configuration
            rds_endpoint VARCHAR(255) NOT NULL,
            database_name VARCHAR(100) NOT NULL,
            s3_bucket VARCHAR(100) NOT NULL,
            s3_root_prefix VARCHAR(255) NOT NULL,

            -- AWS configuration
            aws_region VARCHAR(50) DEFAULT 'us-west-2',

            -- Tenant metadata
            admin_email VARCHAR(255),
            subscription_tier VARCHAR(50) DEFAULT 'standard',
            max_users INTEGER DEFAULT 100,
            max_portcos INTEGER DEFAULT 50,

            -- Status
            is_active BOOLEAN DEFAULT true,

            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create indexes
    op.execute("""
        CREATE INDEX idx_tenants_tenant_name ON data.tenants(tenant_name);
    """)

    op.execute("""
        CREATE INDEX idx_tenants_is_active ON data.tenants(is_active);
    """)

    # Insert base tenant as default
    op.execute("""
        INSERT INTO data.tenants (
            tenant_name,
            display_name,
            rds_endpoint,
            database_name,
            s3_bucket,
            s3_root_prefix,
            aws_region,
            is_active
        ) VALUES (
            'base-tenant',
            'Base Tenant (Development)',
            'tenant-rds.c5ws0iyoa9k7.us-west-2.rds.amazonaws.com',
            'base_tenant_main',
            'tenants-s3',
            'base-tenant/',
            'us-west-2',
            true
        );
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS data.tenants CASCADE;
    """)
