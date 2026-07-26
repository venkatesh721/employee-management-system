"""add phone and password reset tokens

Revision ID: 20260726_02
Revises: 20260726_01
"""

from alembic import op
import sqlalchemy as sa

from app.core.database import Base
import app.models  # noqa: F401

revision = "20260726_02"
down_revision = "20260726_01"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "phone" not in columns:
        with op.batch_alter_table("users") as batch:
            batch.add_column(sa.Column("phone", sa.String(length=30), nullable=True))


def downgrade():
    bind = op.get_bind()
    if sa.inspect(bind).has_table("password_reset_tokens"):
        op.drop_table("password_reset_tokens")
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "phone" in columns:
        with op.batch_alter_table("users") as batch:
            batch.drop_column("phone")
