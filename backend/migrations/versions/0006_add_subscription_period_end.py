"""add current_period_end to user subscriptions

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user_subscriptions", sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("user_subscriptions", "current_period_end")
