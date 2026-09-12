"""add plans catalog

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plans",
        sa.Column("tier_id", sa.String(64), primary_key=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("keycloak_role", sa.String(255), nullable=False, unique=True),
        sa.Column("stripe_price_id", sa.String(255), nullable=True),
        sa.Column("word_limit", sa.Integer, nullable=False),
        sa.Column("period_unit", sa.String(32), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
    )
    op.execute(sa.text("INSERT INTO plans (tier_id, display_name, keycloak_role, stripe_price_id, word_limit, period_unit, active) VALUES ('plan-free', 'Free', 'plan-free', NULL, 0, 'month', true)"))


def downgrade():
    op.drop_table("plans")
