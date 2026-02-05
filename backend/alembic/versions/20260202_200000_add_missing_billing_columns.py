"""Add missing columns to billing_accounts table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-02 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to billing_accounts table in data schema
    # Using raw SQL to conditionally add columns if they don't exist

    op.execute("""
        DO $$
        BEGIN
            -- has_payment_method
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'has_payment_method') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN has_payment_method BOOLEAN NOT NULL DEFAULT false;
            END IF;

            -- card_last4
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'card_last4') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN card_last4 VARCHAR(4);
            END IF;

            -- card_brand
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'card_brand') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN card_brand VARCHAR(20);
            END IF;

            -- card_exp_month
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'card_exp_month') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN card_exp_month VARCHAR(2);
            END IF;

            -- card_exp_year
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'card_exp_year') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN card_exp_year VARCHAR(4);
            END IF;

            -- trial_active
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'trial_active') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN trial_active BOOLEAN NOT NULL DEFAULT false;
            END IF;

            -- trial_started_at
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'trial_started_at') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN trial_started_at TIMESTAMP;
            END IF;

            -- trial_ends_at
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'trial_ends_at') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN trial_ends_at TIMESTAMP;
            END IF;

            -- subscription_active
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'subscription_active') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN subscription_active BOOLEAN NOT NULL DEFAULT false;
            END IF;

            -- subscription_started_at
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'subscription_started_at') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN subscription_started_at TIMESTAMP;
            END IF;

            -- subscription_plan
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'subscription_plan') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN subscription_plan VARCHAR(50);
            END IF;

            -- credits_balance (rename from credits_remaining if it exists)
            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'credits_remaining')
            AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'credits_balance') THEN
                ALTER TABLE data.billing_accounts RENAME COLUMN credits_remaining TO credits_balance;
            ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'credits_balance') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN credits_balance BIGINT NOT NULL DEFAULT 0;
            END IF;

            -- runs_remaining
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'runs_remaining') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN runs_remaining BIGINT NOT NULL DEFAULT 0;
            END IF;

            -- stripe_customer_id
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'stripe_customer_id') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN stripe_customer_id VARCHAR(100);
            END IF;

            -- stripe_subscription_id
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'stripe_subscription_id') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN stripe_subscription_id VARCHAR(100);
            END IF;

            -- Drop old columns that are not in the model
            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'plan') THEN
                ALTER TABLE data.billing_accounts DROP COLUMN plan;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'block_reason') THEN
                ALTER TABLE data.billing_accounts DROP COLUMN block_reason;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'blocked_at') THEN
                ALTER TABLE data.billing_accounts DROP COLUMN blocked_at;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # This is a complex migration, downgrade would need to reverse all changes
    # For simplicity, we'll just drop the new columns
    op.execute("""
        DO $$
        BEGIN
            -- Re-add old columns
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'plan') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN plan VARCHAR(50) NOT NULL DEFAULT 'free';
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'block_reason') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN block_reason VARCHAR(50);
            END IF;

            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'blocked_at') THEN
                ALTER TABLE data.billing_accounts ADD COLUMN blocked_at TIMESTAMP;
            END IF;

            -- Rename credits_balance back to credits_remaining
            IF EXISTS (SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'data' AND table_name = 'billing_accounts'
                AND column_name = 'credits_balance') THEN
                ALTER TABLE data.billing_accounts RENAME COLUMN credits_balance TO credits_remaining;
            END IF;

            -- Drop new columns
            ALTER TABLE data.billing_accounts
                DROP COLUMN IF EXISTS has_payment_method,
                DROP COLUMN IF EXISTS card_last4,
                DROP COLUMN IF EXISTS card_brand,
                DROP COLUMN IF EXISTS card_exp_month,
                DROP COLUMN IF EXISTS card_exp_year,
                DROP COLUMN IF EXISTS trial_active,
                DROP COLUMN IF EXISTS trial_started_at,
                DROP COLUMN IF EXISTS trial_ends_at,
                DROP COLUMN IF EXISTS subscription_active,
                DROP COLUMN IF EXISTS subscription_started_at,
                DROP COLUMN IF EXISTS subscription_plan,
                DROP COLUMN IF EXISTS runs_remaining,
                DROP COLUMN IF EXISTS stripe_customer_id,
                DROP COLUMN IF EXISTS stripe_subscription_id;
        END $$;
    """)
