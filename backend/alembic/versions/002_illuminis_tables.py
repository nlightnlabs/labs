"""Add Illuminis-specific tables.

Revision ID: 002_illuminis
Revises: 3c87c94f578c
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_illuminis'
down_revision = '3c87c94f578c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create all enum types first
    op.execute("CREATE TYPE workspacerole AS ENUM ('SUPER_ADMIN', 'CUSTOMER_ADMIN', 'ANALYST', 'OPERATOR', 'VIEWER')")
    op.execute("CREATE TYPE portcostatus AS ENUM ('IN_DILIGENCE', 'ACTIVE_MONITORING', 'WATCHLIST', 'DISTRESSED', 'EXIT_PREP', 'EXITED', 'ON_HOLD', 'PROSPECT')")
    op.execute("CREATE TYPE portcorole AS ENUM ('OWNER', 'CONTRIBUTOR', 'VIEWER', 'ROLLUP_VIEWER')")
    op.execute("CREATE TYPE accesslevel AS ENUM ('DETAILED', 'ROLLUP_ONLY')")
    op.execute("CREATE TYPE storageprovider AS ENUM ('local', 's3', 'azure')")
    op.execute("CREATE TYPE uploadstatus AS ENUM ('INITIATED', 'UPLOADING', 'UPLOADED', 'FAILED')")
    op.execute("CREATE TYPE profilingstatus AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')")
    op.execute("CREATE TYPE billingstatus AS ENUM ('UNINITIALIZED', 'PAYMENT_METHOD_REQUIRED', 'TRIAL_ACTIVE', 'SUBSCRIPTION_ACTIVE', 'PAST_DUE', 'CANCELED', 'LOCKED')")
    op.execute("CREATE TYPE billingeventtype AS ENUM ('PAYMENT_METHOD_ADDED', 'PAYMENT_METHOD_REMOVED', 'TRIAL_STARTED', 'TRIAL_ENDED', 'SUBSCRIPTION_STARTED', 'SUBSCRIPTION_CANCELED', 'CREDITS_PURCHASED', 'CREDITS_USED', 'PAYMENT_SUCCEEDED', 'PAYMENT_FAILED')")
    op.execute("CREATE TYPE analysisstatus AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELED')")
    op.execute("CREATE TYPE detectortype AS ENUM ('MISSING_REQUIRED_IDS', 'INVALID_DATE_FORMAT', 'DUPLICATE_KEYS', 'PERIOD_GAPS', 'CURRENCY_INCONSISTENCY', 'OUTLIER_ZSCORE', 'DISCONTINUITY', 'IMPOSSIBLE_RATIO', 'TB_IMBALANCE', 'GL_TB_MISMATCH', 'VARIANCE_MISMATCH', 'NEGATIVE_REVENUE')")
    op.execute("CREATE TYPE findingseverity AS ENUM ('HIGH', 'MEDIUM', 'LOW')")
    op.execute("CREATE TYPE findingconfidence AS ENUM ('HIGH', 'MEDIUM', 'LOW')")
    op.execute("CREATE TYPE findingstatus AS ENUM ('OPEN', 'INVESTIGATING', 'ACCEPTED', 'RESOLVED')")
    op.execute("CREATE TYPE auditaction AS ENUM ('LOGIN', 'LOGOUT', 'REGISTER', 'PASSWORD_CHANGE', 'PASSWORD_RESET', 'PORTCO_CREATE', 'PORTCO_UPDATE', 'PORTCO_DELETE', 'PORTCO_STATUS_CHANGE', 'FILE_UPLOAD', 'FILE_DELETE', 'FILE_DOWNLOAD', 'ANALYSIS_RUN', 'FINDING_STATUS_CHANGE', 'FINDING_ASSIGN', 'FINDING_COMMENT', 'PAYMENT_METHOD_ADD', 'PAYMENT_METHOD_REMOVE', 'TRIAL_START', 'SUBSCRIPTION_CHANGE', 'MEMBER_ADD', 'MEMBER_REMOVE', 'ROLE_CHANGE', 'SETTINGS_UPDATE')")

    # Add workspace_role column to users table
    op.add_column('users', sa.Column('workspace_role', postgresql.ENUM('SUPER_ADMIN', 'CUSTOMER_ADMIN', 'ANALYST', 'OPERATOR', 'VIEWER', name='workspacerole', create_type=False), nullable=False, server_default='VIEWER'))

    # Create portcos table
    op.create_table(
        'portcos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', postgresql.ENUM('IN_DILIGENCE', 'ACTIVE_MONITORING', 'WATCHLIST', 'DISTRESSED', 'EXIT_PREP', 'EXITED', 'ON_HOLD', 'PROSPECT', name='portcostatus', create_type=False), nullable=False, server_default='PROSPECT'),
        sa.Column('status_notes', sa.Text, nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('geography', sa.String(100), nullable=True),
        sa.Column('tags', sa.String(500), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_portcos_workspace_id', 'portcos', ['workspace_id'])
    op.create_index('ix_portcos_workspace_status', 'portcos', ['workspace_id', 'status'])

    # Create portco_members table
    op.create_table(
        'portco_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portco_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portco_role', postgresql.ENUM('OWNER', 'CONTRIBUTOR', 'VIEWER', 'ROLLUP_VIEWER', name='portcorole', create_type=False), nullable=False, server_default='VIEWER'),
        sa.Column('access_level', postgresql.ENUM('DETAILED', 'ROLLUP_ONLY', name='accesslevel', create_type=False), nullable=False, server_default='DETAILED'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['portco_id'], ['portcos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('portco_id', 'user_id', name='uq_portco_member'),
    )
    op.create_index('ix_portco_members_portco_id', 'portco_members', ['portco_id'])
    op.create_index('ix_portco_members_user_id', 'portco_members', ['user_id'])

    # Create files table
    op.create_table(
        'files',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('logical_name', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portco_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['portco_id'], ['portcos.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_files_workspace_id', 'files', ['workspace_id'])
    op.create_index('ix_files_portco_id', 'files', ['portco_id'])
    op.create_index('ix_files_workspace_portco', 'files', ['workspace_id', 'portco_id'])

    # Create file_versions table
    op.create_table(
        'file_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.BigInteger, nullable=False, server_default='1'),
        sa.Column('storage_provider', postgresql.ENUM('local', 's3', 'azure', name='storageprovider', create_type=False), nullable=False),
        sa.Column('storage_bucket', sa.String(255), nullable=True),
        sa.Column('storage_key', sa.String(1000), nullable=False),
        sa.Column('storage_uri', sa.String(2000), nullable=True),
        sa.Column('byte_size', sa.BigInteger, nullable=True),
        sa.Column('sha256', sa.String(64), nullable=True),
        sa.Column('xlsx_sheet', sa.String(255), nullable=True),
        sa.Column('upload_status', postgresql.ENUM('INITIATED', 'UPLOADING', 'UPLOADED', 'FAILED', name='uploadstatus', create_type=False), nullable=False, server_default='INITIATED'),
        sa.Column('uploaded_at', sa.DateTime, nullable=True),
        sa.Column('profiling_status', postgresql.ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='profilingstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('profile_json', postgresql.JSONB, nullable=True),
        sa.Column('row_count', sa.BigInteger, nullable=True),
        sa.Column('column_count', sa.BigInteger, nullable=True),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portco_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['portco_id'], ['portcos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_file_versions_file_id', 'file_versions', ['file_id'])
    op.create_index('ix_file_versions_workspace_id', 'file_versions', ['workspace_id'])
    op.create_index('ix_file_versions_portco_id', 'file_versions', ['portco_id'])
    op.create_index('ix_file_versions_file_version', 'file_versions', ['file_id', 'version_number'])

    # Create billing_accounts table
    op.create_table(
        'billing_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('UNINITIALIZED', 'PAYMENT_METHOD_REQUIRED', 'TRIAL_ACTIVE', 'SUBSCRIPTION_ACTIVE', 'PAST_DUE', 'CANCELED', 'LOCKED', name='billingstatus', create_type=False), nullable=False, server_default='UNINITIALIZED'),
        sa.Column('has_payment_method', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('card_last4', sa.String(4), nullable=True),
        sa.Column('card_brand', sa.String(20), nullable=True),
        sa.Column('card_exp_month', sa.String(2), nullable=True),
        sa.Column('card_exp_year', sa.String(4), nullable=True),
        sa.Column('trial_active', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('trial_started_at', sa.DateTime, nullable=True),
        sa.Column('trial_ends_at', sa.DateTime, nullable=True),
        sa.Column('subscription_active', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('subscription_started_at', sa.DateTime, nullable=True),
        sa.Column('subscription_plan', sa.String(50), nullable=True),
        sa.Column('credits_balance', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('runs_remaining', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('stripe_customer_id', sa.String(100), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('workspace_id', name='uq_billing_account_workspace'),
    )
    op.create_index('ix_billing_accounts_workspace_id', 'billing_accounts', ['workspace_id'])

    # Create billing_events table
    op.create_table(
        'billing_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('billing_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', postgresql.ENUM('PAYMENT_METHOD_ADDED', 'PAYMENT_METHOD_REMOVED', 'TRIAL_STARTED', 'TRIAL_ENDED', 'SUBSCRIPTION_STARTED', 'SUBSCRIPTION_CANCELED', 'CREDITS_PURCHASED', 'CREDITS_USED', 'PAYMENT_SUCCEEDED', 'PAYMENT_FAILED', name='billingeventtype', create_type=False), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('event_metadata', postgresql.JSONB, nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['billing_account_id'], ['billing_accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_billing_events_billing_account_id', 'billing_events', ['billing_account_id'])

    # Create analysis_jobs table
    op.create_table(
        'analysis_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('idempotency_key', sa.String(100), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELED', name='analysisstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('findings_count', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('high_severity_count', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('medium_severity_count', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('low_severity_count', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('detectors_config', postgresql.JSONB, nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portco_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_version_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('triggered_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['portco_id'], ['portcos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['file_version_id'], ['file_versions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['triggered_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('idempotency_key', name='uq_analysis_job_idempotency'),
    )
    op.create_index('ix_analysis_jobs_workspace_id', 'analysis_jobs', ['workspace_id'])
    op.create_index('ix_analysis_jobs_portco_id', 'analysis_jobs', ['portco_id'])
    op.create_index('ix_analysis_jobs_workspace_portco', 'analysis_jobs', ['workspace_id', 'portco_id'])

    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('detector_type', postgresql.ENUM('MISSING_REQUIRED_IDS', 'INVALID_DATE_FORMAT', 'DUPLICATE_KEYS', 'PERIOD_GAPS', 'CURRENCY_INCONSISTENCY', 'OUTLIER_ZSCORE', 'DISCONTINUITY', 'IMPOSSIBLE_RATIO', 'TB_IMBALANCE', 'GL_TB_MISMATCH', 'VARIANCE_MISMATCH', 'NEGATIVE_REVENUE', name='detectortype', create_type=False), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('severity', postgresql.ENUM('HIGH', 'MEDIUM', 'LOW', name='findingseverity', create_type=False), nullable=False),
        sa.Column('confidence', postgresql.ENUM('HIGH', 'MEDIUM', 'LOW', name='findingconfidence', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('OPEN', 'INVESTIGATING', 'ACCEPTED', 'RESOLVED', name='findingstatus', create_type=False), nullable=False, server_default='OPEN'),
        sa.Column('evidence_json', postgresql.JSONB, nullable=True),
        sa.Column('affected_rows', sa.BigInteger, nullable=True),
        sa.Column('affected_columns', postgresql.JSONB, nullable=True),
        sa.Column('analysis_job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portco_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_job_id'], ['analysis_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['portco_id'], ['portcos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_findings_analysis_job_id', 'findings', ['analysis_job_id'])
    op.create_index('ix_findings_workspace_id', 'findings', ['workspace_id'])
    op.create_index('ix_findings_portco_id', 'findings', ['portco_id'])
    op.create_index('ix_findings_workspace_portco', 'findings', ['workspace_id', 'portco_id'])
    op.create_index('ix_findings_severity_status', 'findings', ['severity', 'status'])

    # Create finding_comments table
    op.create_table(
        'finding_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['finding_id'], ['findings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_finding_comments_finding_id', 'finding_comments', ['finding_id'])

    # Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', postgresql.ENUM('LOGIN', 'LOGOUT', 'REGISTER', 'PASSWORD_CHANGE', 'PASSWORD_RESET', 'PORTCO_CREATE', 'PORTCO_UPDATE', 'PORTCO_DELETE', 'PORTCO_STATUS_CHANGE', 'FILE_UPLOAD', 'FILE_DELETE', 'FILE_DOWNLOAD', 'ANALYSIS_RUN', 'FINDING_STATUS_CHANGE', 'FINDING_ASSIGN', 'FINDING_COMMENT', 'PAYMENT_METHOD_ADD', 'PAYMENT_METHOD_REMOVE', 'TRIAL_START', 'SUBSCRIPTION_CHANGE', 'MEMBER_ADD', 'MEMBER_REMOVE', 'ROLE_CHANGE', 'SETTINGS_UPDATE', name='auditaction', create_type=False), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('details', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('correlation_id', sa.String(100), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_audit_events_action', 'audit_events', ['action'])
    op.create_index('ix_audit_events_workspace_id', 'audit_events', ['workspace_id'])
    op.create_index('ix_audit_events_user_id', 'audit_events', ['user_id'])
    op.create_index('ix_audit_events_correlation_id', 'audit_events', ['correlation_id'])

    # Create fun_settings table
    op.create_table(
        'fun_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('enabled', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('allow_workspace_customization', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('rotation_interval_seconds', sa.BigInteger, nullable=False, server_default='8'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('workspace_id', name='uq_fun_settings_workspace'),
    )
    op.create_index('ix_fun_settings_workspace_id', 'fun_settings', ['workspace_id'])

    # Create fun_agents table
    op.create_table(
        'fun_agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('avatar_emoji', sa.String(10), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('display_order', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('settings_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['settings_id'], ['fun_settings.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_fun_agents_settings_id', 'fun_agents', ['settings_id'])

    # Create fun_lines table
    op.create_table(
        'fun_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('display_order', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('settings_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['settings_id'], ['fun_settings.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_fun_lines_settings_id', 'fun_lines', ['settings_id'])


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('fun_lines')
    op.drop_table('fun_agents')
    op.drop_table('fun_settings')
    op.drop_table('audit_events')
    op.drop_table('finding_comments')
    op.drop_table('findings')
    op.drop_table('analysis_jobs')
    op.drop_table('billing_events')
    op.drop_table('billing_accounts')
    op.drop_table('file_versions')
    op.drop_table('files')
    op.drop_table('portco_members')
    op.drop_table('portcos')

    # Drop column from users
    op.drop_column('users', 'workspace_role')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS workspacerole')
    op.execute('DROP TYPE IF EXISTS portcostatus')
    op.execute('DROP TYPE IF EXISTS portcorole')
    op.execute('DROP TYPE IF EXISTS accesslevel')
    op.execute('DROP TYPE IF EXISTS storageprovider')
    op.execute('DROP TYPE IF EXISTS uploadstatus')
    op.execute('DROP TYPE IF EXISTS profilingstatus')
    op.execute('DROP TYPE IF EXISTS billingstatus')
    op.execute('DROP TYPE IF EXISTS billingeventtype')
    op.execute('DROP TYPE IF EXISTS analysisstatus')
    op.execute('DROP TYPE IF EXISTS detectortype')
    op.execute('DROP TYPE IF EXISTS findingseverity')
    op.execute('DROP TYPE IF EXISTS findingconfidence')
    op.execute('DROP TYPE IF EXISTS findingstatus')
    op.execute('DROP TYPE IF EXISTS auditaction')
