"""Fix fun_settings workspace_id to allow NULL for global settings

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-02-02 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Allow NULL values in workspace_id for global fun_settings
    op.execute("""
        ALTER TABLE data.fun_settings ALTER COLUMN workspace_id DROP NOT NULL;
    """)


def downgrade() -> None:
    # Restore NOT NULL constraint (first delete any NULL rows)
    op.execute("""
        DELETE FROM data.fun_settings WHERE workspace_id IS NULL;
        ALTER TABLE data.fun_settings ALTER COLUMN workspace_id SET NOT NULL;
    """)
