"""business modules, ownership constraints, and safe profile repair

Revision ID: 20260726_03
Revises: 20260726_02
"""

import uuid
from alembic import op
import sqlalchemy as sa
from app.core.database import Base
import app.models  # noqa: F401

revision = "20260726_03"
down_revision = "20260726_02"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    inspector = sa.inspect(bind)
    attendance_cols = {c["name"] for c in inspector.get_columns("attendance")}
    additions = [
        ("created_by", sa.Column("created_by", sa.String(36), nullable=True)),
        ("updated_by", sa.Column("updated_by", sa.String(36), nullable=True)),
        (
            "created_at",
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        ),
        (
            "updated_at",
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        ),
    ]
    with op.batch_alter_table("attendance") as batch:
        for name, column in additions:
            if name not in attendance_cols:
                batch.add_column(column)
    now = "CURRENT_TIMESTAMP"
    bind.execute(
        sa.text(
            f"UPDATE attendance SET created_at={now}, updated_at={now} WHERE created_at IS NULL OR updated_at IS NULL"
        )
    )
    # Link existing employee users by matching email; create only where no profile exists.
    users = bind.execute(
        sa.text(
            "SELECT id,email,full_name FROM users WHERE role='employee' AND id NOT IN (SELECT user_id FROM employees WHERE user_id IS NOT NULL)"
        )
    ).mappings()
    for user in users:
        matched = bind.execute(
            sa.text(
                "SELECT id FROM employees WHERE lower(email)=lower(:email) AND user_id IS NULL"
            ),
            {"email": user["email"]},
        ).first()
        if matched:
            bind.execute(
                sa.text("UPDATE employees SET user_id=:uid WHERE id=:eid"),
                {"uid": user["id"], "eid": matched[0]},
            )
        else:
            count = bind.execute(sa.text("SELECT count(*) FROM employees")).scalar() + 1
            first, *rest = (user["full_name"] or user["email"].split("@")[0]).split(
                maxsplit=1
            )
            bind.execute(
                sa.text(
                    "INSERT INTO employees (id,employee_id,user_id,first_name,last_name,email,status,created_at,updated_at) VALUES (:id,:code,:uid,:first,:last,:email,'active',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "code": f"EMP{count:03d}",
                    "uid": user["id"],
                    "first": first,
                    "last": rest[0] if rest else "",
                    "email": user["email"],
                },
            )
    # SQLite batch mode safely adds uniqueness while preserving rows.
    existing_uq = {
        u["name"] for u in sa.inspect(bind).get_unique_constraints("employees")
    }
    if "uq_employees_user_id" not in existing_uq:
        with op.batch_alter_table("employees") as batch:
            batch.create_unique_constraint("uq_employees_user_id", ["user_id"])
    existing_att_uq = {
        u["name"] for u in sa.inspect(bind).get_unique_constraints("attendance")
    }
    if "uq_attendance_employee_date" not in existing_att_uq:
        with op.batch_alter_table("attendance") as batch:
            batch.create_unique_constraint(
                "uq_attendance_employee_date", ["employee_id", "date"]
            )


def downgrade():
    pass
