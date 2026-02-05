"""Move tables to data schema and add field metadata

Revision ID: 9d95cfd9c834
Revises: 002_illuminis
Create Date: 2026-02-01 16:55:55.137703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9d95cfd9c834'
down_revision: Union[str, None] = '002_illuminis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tables to migrate (in dependency order for foreign keys)
TABLES_TO_MIGRATE = [
    'organizations',
    'users',
    'user_preferences',
    'sessions',
    'saml_providers',
    'password_reset_tokens',
    'notifications',
    'portcos',
    'portco_members',
    'files',
    'file_versions',
    'billing_accounts',
    'billing_events',
    'analysis_jobs',
    'findings',
    'finding_comments',
    'audit_events',
    'fun_settings',
    'fun_agents',
    'fun_lines',
]


def upgrade() -> None:
    # Create schemas if they don't exist
    op.execute('CREATE SCHEMA IF NOT EXISTS data')
    op.execute('CREATE SCHEMA IF NOT EXISTS field_meta_data')

    # Drop tables from public schema (they're empty, we'll recreate in data schema)
    # Must drop in reverse order due to foreign key constraints
    for table in reversed(TABLES_TO_MIGRATE):
        op.execute(f'DROP TABLE IF EXISTS public.{table} CASCADE')

    # Note: Keep alembic_version in public schema so Alembic can still find it

    # Now recreate all tables in the data schema
    # Organizations
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.organizations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(100) NOT NULL UNIQUE,
            settings JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Users
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.users (
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

    # User preferences
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.user_preferences (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE REFERENCES data.users(id) ON DELETE CASCADE,
            theme VARCHAR(50) NOT NULL DEFAULT 'system',
            notifications_enabled BOOLEAN NOT NULL DEFAULT true,
            email_notifications BOOLEAN NOT NULL DEFAULT true,
            language VARCHAR(10) NOT NULL DEFAULT 'en',
            timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
            settings JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Sessions
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES data.users(id) ON DELETE CASCADE,
            token VARCHAR(500) NOT NULL UNIQUE,
            refresh_token VARCHAR(500) UNIQUE,
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # SAML providers
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.saml_providers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id UUID NOT NULL REFERENCES data.organizations(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            entity_id VARCHAR(500) NOT NULL,
            sso_url VARCHAR(500) NOT NULL,
            certificate TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            attribute_mapping JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Password reset tokens
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.password_reset_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES data.users(id) ON DELETE CASCADE,
            token VARCHAR(255) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Notifications
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES data.users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            type VARCHAR(50) NOT NULL DEFAULT 'info',
            is_read BOOLEAN NOT NULL DEFAULT false,
            data JSONB DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Portcos
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.portcos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            organization_id UUID NOT NULL REFERENCES data.organizations(id) ON DELETE CASCADE,
            status VARCHAR(50) NOT NULL DEFAULT 'active',
            settings JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Portco members
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.portco_members (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            portco_id UUID NOT NULL REFERENCES data.portcos(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES data.users(id) ON DELETE CASCADE,
            role VARCHAR(50) NOT NULL DEFAULT 'viewer',
            access_level VARCHAR(50) NOT NULL DEFAULT 'read',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now(),
            UNIQUE(portco_id, user_id)
        )
    """)

    # Files
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.files (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            original_name VARCHAR(255) NOT NULL,
            mime_type VARCHAR(100) NOT NULL,
            size BIGINT NOT NULL,
            storage_path VARCHAR(500) NOT NULL,
            storage_provider VARCHAR(50) NOT NULL DEFAULT 'local',
            portco_id UUID NOT NULL REFERENCES data.portcos(id) ON DELETE CASCADE,
            uploaded_by UUID NOT NULL REFERENCES data.users(id),
            upload_status VARCHAR(50) NOT NULL DEFAULT 'pending',
            profiling_status VARCHAR(50) NOT NULL DEFAULT 'pending',
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # File versions
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.file_versions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            file_id UUID NOT NULL REFERENCES data.files(id) ON DELETE CASCADE,
            version INTEGER NOT NULL,
            storage_path VARCHAR(500) NOT NULL,
            size BIGINT NOT NULL,
            uploaded_by UUID NOT NULL REFERENCES data.users(id),
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Billing accounts
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.billing_accounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id UUID NOT NULL UNIQUE REFERENCES data.organizations(id) ON DELETE CASCADE,
            status VARCHAR(50) NOT NULL DEFAULT 'active',
            plan VARCHAR(50) NOT NULL DEFAULT 'free',
            credits_remaining INTEGER NOT NULL DEFAULT 0,
            block_reason VARCHAR(50),
            blocked_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Billing events
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.billing_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            billing_account_id UUID NOT NULL REFERENCES data.billing_accounts(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Analysis jobs
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.analysis_jobs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            portco_id UUID NOT NULL REFERENCES data.portcos(id) ON DELETE CASCADE,
            file_id UUID REFERENCES data.files(id) ON DELETE SET NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            detector_type VARCHAR(50) NOT NULL,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT,
            metadata JSONB DEFAULT '{}',
            created_by UUID NOT NULL REFERENCES data.users(id),
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Findings
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.findings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            analysis_job_id UUID NOT NULL REFERENCES data.analysis_jobs(id) ON DELETE CASCADE,
            portco_id UUID NOT NULL REFERENCES data.portcos(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            severity VARCHAR(50) NOT NULL DEFAULT 'medium',
            confidence VARCHAR(50) NOT NULL DEFAULT 'medium',
            status VARCHAR(50) NOT NULL DEFAULT 'open',
            category VARCHAR(100),
            location JSONB DEFAULT '{}',
            evidence JSONB DEFAULT '{}',
            remediation TEXT,
            assigned_to UUID REFERENCES data.users(id),
            resolved_at TIMESTAMP,
            resolved_by UUID REFERENCES data.users(id),
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Finding comments
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.finding_comments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            finding_id UUID NOT NULL REFERENCES data.findings(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES data.users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Audit events
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.audit_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES data.users(id),
            organization_id UUID REFERENCES data.organizations(id),
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(100),
            resource_id UUID,
            details JSONB DEFAULT '{}',
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Fun settings
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.fun_settings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id UUID NOT NULL UNIQUE REFERENCES data.organizations(id) ON DELETE CASCADE,
            enabled BOOLEAN NOT NULL DEFAULT false,
            settings JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Fun agents
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.fun_agents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            personality JSONB NOT NULL DEFAULT '{}',
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Fun lines
    op.execute("""
        CREATE TABLE IF NOT EXISTS data.fun_lines (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID NOT NULL REFERENCES data.fun_agents(id) ON DELETE CASCADE,
            category VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)

    # Create the field_metadata tracking table in field_meta_data schema
    op.create_table(
        'field_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('table_name', sa.String(255), nullable=False),
        sa.Column('column_name', sa.String(255), nullable=False),
        sa.Column('data_type', sa.String(100), nullable=False),
        sa.Column('is_nullable', sa.Boolean(), default=True),
        sa.Column('is_primary_key', sa.Boolean(), default=False),
        sa.Column('is_foreign_key', sa.Boolean(), default=False),
        sa.Column('foreign_key_table', sa.String(255), nullable=True),
        sa.Column('foreign_key_column', sa.String(255), nullable=True),
        sa.Column('default_value', sa.String(500), nullable=True),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_searchable', sa.Boolean(), default=False),
        sa.Column('is_filterable', sa.Boolean(), default=False),
        sa.Column('is_sortable', sa.Boolean(), default=True),
        sa.Column('is_visible', sa.Boolean(), default=True),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('validation_rules', postgresql.JSONB(), nullable=True),
        sa.Column('ui_hints', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        schema='field_meta_data'
    )

    # Create unique constraint on table_name + column_name
    op.create_unique_constraint(
        'uq_field_definitions_table_column',
        'field_definitions',
        ['table_name', 'column_name'],
        schema='field_meta_data'
    )

    # Create index for faster lookups by table
    op.create_index(
        'ix_field_definitions_table_name',
        'field_definitions',
        ['table_name'],
        schema='field_meta_data'
    )

    # Populate field_meta_data for each table by introspecting the data schema
    # This uses PostgreSQL's information_schema to get column metadata
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
        AND c.table_name IN (
            'organizations', 'users', 'user_preferences', 'sessions', 'saml_providers',
            'password_reset_tokens', 'notifications', 'portcos', 'portco_members',
            'files', 'file_versions', 'billing_accounts', 'billing_events',
            'analysis_jobs', 'findings', 'finding_comments', 'audit_events',
            'fun_settings', 'fun_agents', 'fun_lines'
        )
        ORDER BY c.table_name, c.ordinal_position
        ON CONFLICT (table_name, column_name) DO NOTHING
    """)

    # Update foreign key information
    op.execute("""
        UPDATE field_meta_data.field_definitions fd
        SET
            is_foreign_key = true,
            foreign_key_table = ccu.table_name,
            foreign_key_column = ccu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'data'
        AND fd.table_name = kcu.table_name
        AND fd.column_name = kcu.column_name
    """)

    # Mark certain columns as searchable (text-like columns)
    op.execute("""
        UPDATE field_meta_data.field_definitions
        SET is_searchable = true
        WHERE data_type IN ('character varying', 'text', 'varchar')
        AND column_name NOT IN ('id', 'password_hash', 'token', 'refresh_token')
    """)

    # Mark enum and boolean columns as filterable
    op.execute("""
        UPDATE field_meta_data.field_definitions
        SET is_filterable = true
        WHERE data_type IN ('boolean', 'USER-DEFINED')
        OR column_name LIKE '%_status'
        OR column_name LIKE '%_type'
        OR column_name LIKE '%_role'
    """)


def downgrade() -> None:
    # Drop the field_definitions table
    op.drop_index('ix_field_definitions_table_name', table_name='field_definitions', schema='field_meta_data')
    op.drop_constraint('uq_field_definitions_table_column', 'field_definitions', schema='field_meta_data')
    op.drop_table('field_definitions', schema='field_meta_data')

    # Drop tables from data schema (in reverse order due to FK constraints)
    for table in reversed(TABLES_TO_MIGRATE):
        op.execute(f'DROP TABLE IF EXISTS data.{table} CASCADE')
