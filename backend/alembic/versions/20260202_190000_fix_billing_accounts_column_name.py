"""Fix column names from organization_id to workspace_id in data schema tables

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-02 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename organization_id to workspace_id in billing_accounts table
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'billing_accounts'
                AND column_name = 'organization_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'billing_accounts'
                AND column_name = 'workspace_id'
            ) THEN
                ALTER TABLE data.billing_accounts RENAME COLUMN organization_id TO workspace_id;
            END IF;
        END $$;
    """)

    # Rename organization_id to workspace_id in fun_settings table
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'fun_settings'
                AND column_name = 'organization_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'fun_settings'
                AND column_name = 'workspace_id'
            ) THEN
                ALTER TABLE data.fun_settings RENAME COLUMN organization_id TO workspace_id;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Rename workspace_id back to organization_id in billing_accounts
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'billing_accounts'
                AND column_name = 'workspace_id'
            ) THEN
                ALTER TABLE data.billing_accounts RENAME COLUMN workspace_id TO organization_id;
            END IF;
        END $$;
    """)

    # Rename workspace_id back to organization_id in fun_settings
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'fun_settings'
                AND column_name = 'workspace_id'
            ) THEN
                ALTER TABLE data.fun_settings RENAME COLUMN workspace_id TO organization_id;
            END IF;
        END $$;
    """)
