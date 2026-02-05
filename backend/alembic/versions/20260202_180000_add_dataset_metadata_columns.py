"""Add dataset metadata columns to file_versions

Revision ID: a1b2c3d4e5f6
Revises: e322707c47bd
Create Date: 2026-02-02 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e322707c47bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add dataset configuration columns to file_versions table in data schema
    op.add_column('file_versions', sa.Column('dataset_name', sa.String(255), nullable=True), schema='data')
    op.add_column('file_versions', sa.Column('dataset_table_name', sa.String(255), nullable=True), schema='data')
    op.add_column('file_versions', sa.Column('dataset_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='data')


def downgrade() -> None:
    op.drop_column('file_versions', 'dataset_metadata', schema='data')
    op.drop_column('file_versions', 'dataset_table_name', schema='data')
    op.drop_column('file_versions', 'dataset_name', schema='data')
