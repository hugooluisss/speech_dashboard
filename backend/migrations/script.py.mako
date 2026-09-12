"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
"""
from alembic import op
import sqlalchemy as sa

${upgrades if upgrades else "pass"}

${downgrades if downgrades else "pass"}
