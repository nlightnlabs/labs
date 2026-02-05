"""Add missing timestamp columns to fun tables

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-02-02 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6g7h8i9j0k1'
down_revision: Union[str, None] = 'e5f6g7h8i9j0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add timestamp columns to fun_settings if missing
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_settings'
                AND column_name = 'created_at') THEN
                ALTER TABLE data.fun_settings ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT NOW();
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_settings'
                AND column_name = 'updated_at') THEN
                ALTER TABLE data.fun_settings ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT NOW();
            END IF;
        END $$;
    """)

    # Add timestamp columns to fun_agents if missing
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'created_at') THEN
                ALTER TABLE data.fun_agents ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT NOW();
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'updated_at') THEN
                ALTER TABLE data.fun_agents ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT NOW();
            END IF;
        END $$;
    """)

    # Add timestamp columns to fun_lines if missing
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND column_name = 'created_at') THEN
                ALTER TABLE data.fun_lines ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT NOW();
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND column_name = 'updated_at') THEN
                ALTER TABLE data.fun_lines ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT NOW();
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE data.fun_settings
            DROP COLUMN IF EXISTS created_at,
            DROP COLUMN IF EXISTS updated_at;

        ALTER TABLE data.fun_agents
            DROP COLUMN IF EXISTS created_at,
            DROP COLUMN IF EXISTS updated_at;

        ALTER TABLE data.fun_lines
            DROP COLUMN IF EXISTS created_at,
            DROP COLUMN IF EXISTS updated_at;
    """)
