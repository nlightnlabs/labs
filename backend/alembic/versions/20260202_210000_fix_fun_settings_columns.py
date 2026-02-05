"""Fix fun_settings and related tables columns

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-02-02 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix fun_settings table
    op.execute("""
        DO $$
        BEGIN
            -- allow_workspace_customization
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_settings'
                AND column_name = 'allow_workspace_customization') THEN
                ALTER TABLE data.fun_settings ADD COLUMN allow_workspace_customization BOOLEAN NOT NULL DEFAULT true;
            END IF;

            -- rotation_interval_seconds
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_settings'
                AND column_name = 'rotation_interval_seconds') THEN
                ALTER TABLE data.fun_settings ADD COLUMN rotation_interval_seconds BIGINT NOT NULL DEFAULT 8;
            END IF;

            -- Drop old 'settings' column if it exists (was JSONB in migration, not in model)
            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_settings'
                AND column_name = 'settings') THEN
                ALTER TABLE data.fun_settings DROP COLUMN settings;
            END IF;
        END $$;
    """)

    # Fix fun_agents table
    op.execute("""
        DO $$
        BEGIN
            -- avatar_emoji
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'avatar_emoji') THEN
                ALTER TABLE data.fun_agents ADD COLUMN avatar_emoji VARCHAR(10);
            END IF;

            -- is_active
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'is_active') THEN
                ALTER TABLE data.fun_agents ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
            END IF;

            -- display_order
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'display_order') THEN
                ALTER TABLE data.fun_agents ADD COLUMN display_order BIGINT NOT NULL DEFAULT 0;
            END IF;

            -- settings_id (foreign key to fun_settings)
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'settings_id') THEN
                ALTER TABLE data.fun_agents ADD COLUMN settings_id UUID;
                -- Note: You may need to populate settings_id for existing records
            END IF;

            -- Drop old columns that are not in the model
            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'description') THEN
                ALTER TABLE data.fun_agents DROP COLUMN description;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'personality') THEN
                ALTER TABLE data.fun_agents DROP COLUMN personality;
            END IF;
        END $$;
    """)

    # Fix fun_lines table - rename agent_id to settings_id if needed
    op.execute("""
        DO $$
        BEGIN
            -- Rename agent_id to settings_id if agent_id exists and settings_id doesn't
            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND column_name = 'agent_id')
            AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND column_name = 'settings_id') THEN
                ALTER TABLE data.fun_lines RENAME COLUMN agent_id TO settings_id;
            ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND column_name = 'settings_id') THEN
                ALTER TABLE data.fun_lines ADD COLUMN settings_id UUID;
            END IF;

            -- display_order
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND column_name = 'display_order') THEN
                ALTER TABLE data.fun_lines ADD COLUMN display_order BIGINT NOT NULL DEFAULT 0;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            -- Revert fun_settings changes
            ALTER TABLE data.fun_settings
                DROP COLUMN IF EXISTS allow_workspace_customization,
                DROP COLUMN IF EXISTS rotation_interval_seconds;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_settings'
                AND column_name = 'settings') THEN
                ALTER TABLE data.fun_settings ADD COLUMN settings JSONB NOT NULL DEFAULT '{}';
            END IF;

            -- Revert fun_agents changes
            ALTER TABLE data.fun_agents
                DROP COLUMN IF EXISTS avatar_emoji,
                DROP COLUMN IF EXISTS is_active,
                DROP COLUMN IF EXISTS display_order,
                DROP COLUMN IF EXISTS settings_id;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'description') THEN
                ALTER TABLE data.fun_agents ADD COLUMN description TEXT;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_agents'
                AND column_name = 'personality') THEN
                ALTER TABLE data.fun_agents ADD COLUMN personality JSONB NOT NULL DEFAULT '{}';
            END IF;

            -- Revert fun_lines changes
            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'fun_lines'
                AND column_name = 'settings_id') THEN
                ALTER TABLE data.fun_lines RENAME COLUMN settings_id TO agent_id;
            END IF;

            ALTER TABLE data.fun_lines DROP COLUMN IF EXISTS display_order;
        END $$;
    """)
