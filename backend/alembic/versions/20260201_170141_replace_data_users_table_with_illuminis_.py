"""Replace data.users table with Illuminis users structure

Revision ID: 96022835ca29
Revises: 9d95cfd9c834
Create Date: 2026-02-01 17:01:41.870847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '96022835ca29'
down_revision: Union[str, None] = '9d95cfd9c834'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, rename the existing users table to preserve the data
    op.execute('ALTER TABLE IF EXISTS data.users RENAME TO users_legacy')

    # Drop any foreign key constraints from other tables pointing to users_legacy
    # (they would have been created pointing to the old users table)

    # Create the new Illuminis users table
    op.execute("""
        CREATE TABLE data.users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_verified BOOLEAN NOT NULL DEFAULT false,
            role VARCHAR(50) NOT NULL DEFAULT 'user',
            workspace_role VARCHAR(50) NOT NULL DEFAULT 'viewer',
            organization_id UUID REFERENCES data.organizations(id),
            last_login TIMESTAMP,
            failed_login_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Create indexes for the new users table
    op.execute('CREATE INDEX ix_data_users_email ON data.users(email)')
    op.execute('CREATE INDEX ix_data_users_organization_id ON data.users(organization_id)')

    # Update foreign key constraints from dependent tables to point to new users table
    # These tables reference users: user_preferences, sessions, password_reset_tokens,
    # notifications, portco_members, files, file_versions, analysis_jobs, findings,
    # finding_comments, audit_events

    # Drop and recreate foreign keys for tables that reference users
    # user_preferences
    op.execute("""
        ALTER TABLE data.user_preferences
        DROP CONSTRAINT IF EXISTS user_preferences_user_id_fkey
    """)
    op.execute("""
        ALTER TABLE data.user_preferences
        ADD CONSTRAINT user_preferences_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES data.users(id) ON DELETE CASCADE
    """)

    # sessions
    op.execute("""
        ALTER TABLE data.sessions
        DROP CONSTRAINT IF EXISTS sessions_user_id_fkey
    """)
    op.execute("""
        ALTER TABLE data.sessions
        ADD CONSTRAINT sessions_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES data.users(id) ON DELETE CASCADE
    """)

    # password_reset_tokens
    op.execute("""
        ALTER TABLE data.password_reset_tokens
        DROP CONSTRAINT IF EXISTS password_reset_tokens_user_id_fkey
    """)
    op.execute("""
        ALTER TABLE data.password_reset_tokens
        ADD CONSTRAINT password_reset_tokens_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES data.users(id) ON DELETE CASCADE
    """)

    # notifications
    op.execute("""
        ALTER TABLE data.notifications
        DROP CONSTRAINT IF EXISTS notifications_user_id_fkey
    """)
    op.execute("""
        ALTER TABLE data.notifications
        ADD CONSTRAINT notifications_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES data.users(id) ON DELETE CASCADE
    """)

    # portco_members
    op.execute("""
        ALTER TABLE data.portco_members
        DROP CONSTRAINT IF EXISTS portco_members_user_id_fkey
    """)
    op.execute("""
        ALTER TABLE data.portco_members
        ADD CONSTRAINT portco_members_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES data.users(id) ON DELETE CASCADE
    """)

    # files
    op.execute("""
        ALTER TABLE data.files
        DROP CONSTRAINT IF EXISTS files_uploaded_by_fkey
    """)
    op.execute("""
        ALTER TABLE data.files
        ADD CONSTRAINT files_uploaded_by_fkey
        FOREIGN KEY (uploaded_by) REFERENCES data.users(id)
    """)

    # file_versions
    op.execute("""
        ALTER TABLE data.file_versions
        DROP CONSTRAINT IF EXISTS file_versions_uploaded_by_fkey
    """)
    op.execute("""
        ALTER TABLE data.file_versions
        ADD CONSTRAINT file_versions_uploaded_by_fkey
        FOREIGN KEY (uploaded_by) REFERENCES data.users(id)
    """)

    # analysis_jobs
    op.execute("""
        ALTER TABLE data.analysis_jobs
        DROP CONSTRAINT IF EXISTS analysis_jobs_created_by_fkey
    """)
    op.execute("""
        ALTER TABLE data.analysis_jobs
        ADD CONSTRAINT analysis_jobs_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES data.users(id)
    """)

    # findings (assigned_to and resolved_by)
    op.execute("""
        ALTER TABLE data.findings
        DROP CONSTRAINT IF EXISTS findings_assigned_to_fkey
    """)
    op.execute("""
        ALTER TABLE data.findings
        ADD CONSTRAINT findings_assigned_to_fkey
        FOREIGN KEY (assigned_to) REFERENCES data.users(id)
    """)
    op.execute("""
        ALTER TABLE data.findings
        DROP CONSTRAINT IF EXISTS findings_resolved_by_fkey
    """)
    op.execute("""
        ALTER TABLE data.findings
        ADD CONSTRAINT findings_resolved_by_fkey
        FOREIGN KEY (resolved_by) REFERENCES data.users(id)
    """)

    # finding_comments
    op.execute("""
        ALTER TABLE data.finding_comments
        DROP CONSTRAINT IF EXISTS finding_comments_user_id_fkey
    """)
    op.execute("""
        ALTER TABLE data.finding_comments
        ADD CONSTRAINT finding_comments_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES data.users(id) ON DELETE CASCADE
    """)

    # audit_events
    op.execute("""
        ALTER TABLE data.audit_events
        DROP CONSTRAINT IF EXISTS audit_events_user_id_fkey
    """)
    op.execute("""
        ALTER TABLE data.audit_events
        ADD CONSTRAINT audit_events_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES data.users(id)
    """)

    # Update field_meta_data for the new users table
    # First delete old users field definitions
    op.execute("""
        DELETE FROM field_meta_data.field_definitions
        WHERE table_name = 'users'
    """)

    # Insert new field definitions for the Illuminis users table
    op.execute("""
        INSERT INTO field_meta_data.field_definitions (
            table_name, column_name, data_type, is_nullable,
            is_primary_key, display_name, is_sortable, is_visible, display_order,
            is_searchable, is_filterable
        )
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable = 'YES',
            COALESCE(pk.is_pk, false),
            INITCAP(REPLACE(c.column_name, '_', ' ')),
            true,
            NOT c.column_name IN ('created_at', 'updated_at', 'password_hash'),
            c.ordinal_position,
            c.data_type IN ('character varying', 'text') AND c.column_name NOT IN ('password_hash'),
            c.data_type = 'boolean' OR c.column_name IN ('role', 'workspace_role')
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT
                kcu.table_name,
                kcu.column_name,
                true as is_pk
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'data'
        ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
        WHERE c.table_schema = 'data'
        AND c.table_name = 'users'
        ORDER BY c.ordinal_position
    """)

    # Update foreign key info for new users table
    op.execute("""
        UPDATE field_meta_data.field_definitions fd
        SET
            is_foreign_key = true,
            foreign_key_table = 'organizations',
            foreign_key_column = 'id'
        WHERE fd.table_name = 'users'
        AND fd.column_name = 'organization_id'
    """)


def downgrade() -> None:
    # Drop the new users table
    op.execute('DROP TABLE IF EXISTS data.users CASCADE')

    # Rename the legacy table back to users
    op.execute('ALTER TABLE IF EXISTS data.users_legacy RENAME TO users')

    # Restore field_meta_data for the original users table
    op.execute("""
        DELETE FROM field_meta_data.field_definitions
        WHERE table_name = 'users'
    """)

    # Re-insert field definitions for the original users table
    op.execute("""
        INSERT INTO field_meta_data.field_definitions (
            table_name, column_name, data_type, is_nullable,
            is_primary_key, display_name, is_sortable, is_visible, display_order
        )
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable = 'YES',
            COALESCE(pk.is_pk, false),
            INITCAP(REPLACE(c.column_name, '_', ' ')),
            true,
            NOT c.column_name IN ('created_at', 'updated_at'),
            c.ordinal_position
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT
                kcu.table_name,
                kcu.column_name,
                true as is_pk
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'data'
        ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
        WHERE c.table_schema = 'data'
        AND c.table_name = 'users'
        ORDER BY c.ordinal_position
    """)
