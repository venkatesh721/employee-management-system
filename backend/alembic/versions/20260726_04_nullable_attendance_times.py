"""allow attendance without check-in for absent and leave statuses

Revision ID: 20260726_04
Revises: 20260726_03
"""

from alembic import op
import sqlalchemy as sa

revision = "20260726_04"
down_revision = "20260726_03"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("attendance") as batch:
        batch.alter_column(
            "check_in",
            existing_type=sa.DateTime(timezone=True),
            nullable=True,
        )


def downgrade():
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE attendance SET check_in = date || ' 00:00:00' "
            "WHERE check_in IS NULL"
        )
    )
    with op.batch_alter_table("attendance") as batch:
        batch.alter_column(
            "check_in",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )
