"""rename portco_members role to portco_role

Revision ID: e322707c47bd
Revises: 4c11182195c2
Create Date: 2026-02-02 16:18:54.417804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e322707c47bd'
down_revision: Union[str, None] = '4c11182195c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename role to portco_role in portco_members table
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'portco_members'
                AND column_name = 'role'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'portco_members'
                AND column_name = 'portco_role'
            ) THEN
                ALTER TABLE data.portco_members RENAME COLUMN role TO portco_role;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Rename portco_role back to role
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'portco_members'
                AND column_name = 'portco_role'
            ) THEN
                ALTER TABLE data.portco_members RENAME COLUMN portco_role TO role;
            END IF;
        END $$;
    """)
