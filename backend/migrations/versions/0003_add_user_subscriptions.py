"""add user subscription linkage

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_subscriptions",
        sa.Column("subject_id", sa.String(255), primary_key=True),
        sa.Column("stripe_customer_id", sa.String(255), unique=True),
        sa.Column("stripe_subscription_id", sa.String(255), unique=True),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("plan_tier_id", sa.String(64), nullable=False, server_default="plan-free"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("user_subscriptions")
