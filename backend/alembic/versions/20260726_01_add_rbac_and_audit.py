"""add role-based access control and audit logs

Revision ID: 20260726_01
Revises:
"""

from alembic import op
import sqlalchemy as sa

from app.core.database import Base
import app.models  # noqa: F401

revision = "20260726_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    # This project predates migrations. Create the existing schema for clean
    # installations, then safely evolve databases created by create_all().
    Base.metadata.create_all(bind=bind)
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "role" not in columns:
        with op.batch_alter_table("users") as batch:
            batch.add_column(
                sa.Column("role", sa.String(length=20), nullable=False, server_default="employee")
            )
    bind.execute(
        sa.text("UPDATE users SET role = 'admin' WHERE is_superuser = :enabled"),
        {"enabled": True},
    )


def downgrade():
    bind = op.get_bind()
    if sa.inspect(bind).has_table("audit_logs"):
        op.drop_table("audit_logs")
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "role" in columns:
        with op.batch_alter_table("users") as batch:
            batch.drop_column("role")
