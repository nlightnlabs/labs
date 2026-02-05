"""add missing portco columns

Revision ID: 4c11182195c2
Revises: 20260202_161414
Create Date: 2026-02-02 16:17:24.047764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c11182195c2'
down_revision: Union[str, None] = '20260202_161414'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename organization_id to workspace_id if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'portcos'
                AND column_name = 'organization_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'portcos'
                AND column_name = 'workspace_id'
            ) THEN
                ALTER TABLE data.portcos RENAME COLUMN organization_id TO workspace_id;
            END IF;
        END $$;
    """)

    # Add missing columns to portcos table
    op.execute("""
        ALTER TABLE data.portcos
        ADD COLUMN IF NOT EXISTS status_notes TEXT,
        ADD COLUMN IF NOT EXISTS industry VARCHAR(100),
        ADD COLUMN IF NOT EXISTS geography VARCHAR(100),
        ADD COLUMN IF NOT EXISTS tags VARCHAR(500),
        ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES data.users(id) ON DELETE SET NULL
    """)

    # Create index on workspace_id and status if not exists
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_portcos_workspace_status
        ON data.portcos(workspace_id, status)
    """)


def downgrade() -> None:
    # Drop index
    op.execute("""
        DROP INDEX IF EXISTS data.ix_portcos_workspace_status
    """)

    # Remove added columns
    op.execute("""
        ALTER TABLE data.portcos
        DROP COLUMN IF EXISTS status_notes,
        DROP COLUMN IF EXISTS industry,
        DROP COLUMN IF EXISTS geography,
        DROP COLUMN IF EXISTS tags,
        DROP COLUMN IF EXISTS created_by_id
    """)

    # Rename workspace_id back to organization_id
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'portcos'
                AND column_name = 'workspace_id'
            ) THEN
                ALTER TABLE data.portcos RENAME COLUMN workspace_id TO organization_id;
            END IF;
        END $$;
    """)
