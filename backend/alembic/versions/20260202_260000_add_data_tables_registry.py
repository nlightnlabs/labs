"""Add data_tables registry table.

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-02-02

This creates a registry table to track all data tables uploaded for portfolio companies.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i9j0k1l2m3n4'
down_revision = 'h8i9j0k1l2m3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create data schema if it doesn't exist
    op.execute("CREATE SCHEMA IF NOT EXISTS data")

    # Create the data_tables registry
    op.create_table(
        'data_tables',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('table_name', sa.String(255), nullable=False, comment='Actual PostgreSQL table name in data schema'),
        sa.Column('display_name', sa.String(255), nullable=False, comment='Human-readable display name'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('portco_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portco_name', sa.String(255), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('row_count', sa.Integer, nullable=True),
        sa.Column('column_count', sa.Integer, nullable=True),
        sa.Column('file_name', sa.String(255), nullable=True, comment='Original uploaded file name'),
        sa.Column('s3_data_path', sa.String(512), nullable=True, comment='S3 path to the data file'),
        sa.Column('s3_metadata_path', sa.String(512), nullable=True, comment='S3 path to the metadata file'),
        sa.Column('categories', postgresql.ARRAY(sa.String), nullable=True, comment='Business categories'),
        sa.Column('field_mappings', postgresql.JSONB, nullable=True, comment='Column mapping configuration'),
        sa.Column('metadata', postgresql.JSONB, nullable=True, comment='Full metadata from upload'),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('true')),
        schema='data'
    )

    # Add indexes
    op.create_index(
        'idx_data_tables_portco_id',
        'data_tables',
        ['portco_id'],
        schema='data'
    )
    op.create_index(
        'idx_data_tables_workspace_id',
        'data_tables',
        ['workspace_id'],
        schema='data'
    )
    op.create_index(
        'idx_data_tables_table_name',
        'data_tables',
        ['table_name'],
        unique=True,
        schema='data'
    )


def downgrade() -> None:
    op.drop_index('idx_data_tables_table_name', table_name='data_tables', schema='data')
    op.drop_index('idx_data_tables_workspace_id', table_name='data_tables', schema='data')
    op.drop_index('idx_data_tables_portco_id', table_name='data_tables', schema='data')
    op.drop_table('data_tables', schema='data')
