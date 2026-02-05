"""Add missing user columns

Revision ID: 20260202_161414
Revises: 96022835ca29
Create Date: 2026-02-02 16:14:14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260202_161414'
down_revision: Union[str, None] = '96022835ca29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to users table
    op.execute("""
        ALTER TABLE data.users
        ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500),
        ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
        ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP
    """)

    # Rename last_login to last_login_at if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'users'
                AND column_name = 'last_login'
            ) THEN
                ALTER TABLE data.users RENAME COLUMN last_login TO last_login_at;
            ELSIF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'users'
                AND column_name = 'last_login_at'
            ) THEN
                ALTER TABLE data.users ADD COLUMN last_login_at TIMESTAMP;
            END IF;
        END $$;
    """)

    # Change failed_login_attempts from INTEGER to VARCHAR(10) to match model
    op.execute("""
        ALTER TABLE data.users
        ALTER COLUMN failed_login_attempts TYPE VARCHAR(10)
        USING COALESCE(failed_login_attempts::text, '0')
    """)

    # Set default for failed_login_attempts
    op.execute("""
        ALTER TABLE data.users
        ALTER COLUMN failed_login_attempts SET DEFAULT '0'
    """)

    # Make first_name and last_name NOT NULL
    op.execute("""
        UPDATE data.users SET first_name = 'Unknown' WHERE first_name IS NULL;
        UPDATE data.users SET last_name = 'User' WHERE last_name IS NULL;
        ALTER TABLE data.users ALTER COLUMN first_name SET NOT NULL;
        ALTER TABLE data.users ALTER COLUMN last_name SET NOT NULL;
    """)


def downgrade() -> None:
    # Remove added columns
    op.execute("""
        ALTER TABLE data.users
        DROP COLUMN IF EXISTS avatar_url,
        DROP COLUMN IF EXISTS phone,
        DROP COLUMN IF EXISTS email_verified_at
    """)

    # Rename last_login_at back to last_login
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data'
                AND table_name = 'users'
                AND column_name = 'last_login_at'
            ) THEN
                ALTER TABLE data.users RENAME COLUMN last_login_at TO last_login;
            END IF;
        END $$;
    """)

    # Revert failed_login_attempts to INTEGER
    op.execute("""
        ALTER TABLE data.users
        ALTER COLUMN failed_login_attempts TYPE INTEGER
        USING COALESCE(failed_login_attempts::integer, 0)
    """)

    op.execute("""
        ALTER TABLE data.users
        ALTER COLUMN failed_login_attempts SET DEFAULT 0
    """)

    # Allow NULL for first_name and last_name
    op.execute("""
        ALTER TABLE data.users ALTER COLUMN first_name DROP NOT NULL;
        ALTER TABLE data.users ALTER COLUMN last_name DROP NOT NULL;
    """)
