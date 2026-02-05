"""Fix fun_lines foreign key to reference fun_settings instead of fun_agents

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-02-02 24:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g7h8i9j0k1l2'
down_revision: Union[str, None] = 'f6g7h8i9j0k1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old foreign key constraint that referenced fun_agents
    op.execute("""
        DO $$
        BEGIN
            -- Drop old FK constraint if it exists (may have different names)
            IF EXISTS (SELECT 1 FROM information_schema.table_constraints
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND constraint_name = 'fun_lines_agent_id_fkey') THEN
                ALTER TABLE data.fun_lines DROP CONSTRAINT fun_lines_agent_id_fkey;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.table_constraints
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND constraint_name = 'fun_lines_settings_id_fkey') THEN
                ALTER TABLE data.fun_lines DROP CONSTRAINT fun_lines_settings_id_fkey;
            END IF;

            -- Add the correct FK constraint referencing fun_settings
            ALTER TABLE data.fun_lines
                ADD CONSTRAINT fun_lines_settings_id_fkey
                FOREIGN KEY (settings_id)
                REFERENCES data.fun_settings(id)
                ON DELETE CASCADE;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.table_constraints
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND constraint_name = 'fun_lines_settings_id_fkey') THEN
                ALTER TABLE data.fun_lines DROP CONSTRAINT fun_lines_settings_id_fkey;
            END IF;
        END $$;
    """)
