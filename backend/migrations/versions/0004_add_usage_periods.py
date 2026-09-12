"""add usage periods

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "usage_periods",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("subject_id", sa.String(255), nullable=False),
        sa.Column("period_key", sa.String(7), nullable=False),
        sa.Column("words_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("subject_id", "period_key"),
    )


def downgrade():
    op.drop_table("usage_periods")
