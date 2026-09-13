"""localize and seed the three-plan catalog

Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plans", sa.Column("name_en", sa.String(255), nullable=True))
    op.add_column("plans", sa.Column("name_es", sa.String(255), nullable=True))
    op.execute(sa.text("DELETE FROM plans WHERE tier_id NOT IN ('plan-free', 'plan-basica', 'plan-pro')"))

    for tier, name_en, name_es, role, price, limit in [
        ("plan-free", "Free", "Gratis", "plan-free", None, 0),
        ("plan-basica", "Basic", "Básica", "plan-basica", "price_1Tks55GUJ5bWCJoqwgXfl1Gs", 10000),
        ("plan-pro", "Pro", "Pro", "plan-pro", "price_1Tks5YGUJ5bWCJoqCVS7we6q", 50000),
    ]:
        op.execute(sa.text("""
            UPDATE plans
            SET name_en = :name_en, name_es = :name_es, keycloak_role = :role,
                stripe_price_id = :price, word_limit = :word_limit,
                period_unit = 'month', active = true
            WHERE tier_id = :tier
        """).bindparams(name_en=name_en, name_es=name_es, role=role, price=price,
                        word_limit=limit, tier=tier))
        op.execute(sa.text("""
            INSERT INTO plans (tier_id, display_name, name_en, name_es, keycloak_role, stripe_price_id, word_limit, period_unit, active)
            SELECT :tier, :name_en, :name_en, :name_es, :role, :price, :word_limit, 'month', true
            WHERE NOT EXISTS (SELECT 1 FROM plans WHERE tier_id = :tier)
        """).bindparams(name_en=name_en, name_es=name_es, role=role, price=price,
                        word_limit=limit, tier=tier))

    op.drop_column("plans", "display_name")
    op.alter_column("plans", "name_en", nullable=False)
    op.alter_column("plans", "name_es", nullable=False)


def downgrade():
    op.add_column("plans", sa.Column("display_name", sa.String(255), nullable=True))
    op.execute(sa.text("UPDATE plans SET display_name = name_en"))
    op.alter_column("plans", "display_name", nullable=False)
    op.drop_column("plans", "name_en")
    op.drop_column("plans", "name_es")
