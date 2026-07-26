"""enforce a single consistent administrator account

Revision ID: 20260727_05
Revises: 20260726_04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260727_05"
down_revision = "20260726_04"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    users = sa.table(
        "users",
        sa.column("id"),
        sa.column("role"),
        sa.column("is_superuser"),
        sa.column("created_at"),
    )

    bind.execute(
        users.update().where(users.c.is_superuser.is_(None)).values(is_superuser=False)
    )
    administrator_ids = list(
        bind.execute(
            sa.select(users.c.id)
            .where(sa.or_(users.c.role == "admin", users.c.is_superuser.is_(True)))
            .order_by(users.c.created_at.asc(), users.c.id.asc())
        ).scalars()
    )
    if administrator_ids:
        canonical_id = administrator_ids[0]
        bind.execute(
            users.update()
            .where(users.c.id == canonical_id)
            .values(role="admin", is_superuser=True)
        )
        if len(administrator_ids) > 1:
            bind.execute(
                users.update()
                .where(users.c.id.in_(administrator_ids[1:]))
                .values(role="employee", is_superuser=False)
            )

    inspector = sa.inspect(bind)
    check_names = {
        constraint["name"]
        for constraint in inspector.get_check_constraints("users")
        if constraint["name"]
    }
    columns = {column["name"]: column for column in inspector.get_columns("users")}
    if columns["is_superuser"]["nullable"] or (
        "ck_users_admin_role_consistent" not in check_names
    ):
        with op.batch_alter_table("users") as batch:
            if columns["is_superuser"]["nullable"]:
                batch.alter_column(
                    "is_superuser",
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                )
            if "ck_users_admin_role_consistent" not in check_names:
                batch.create_check_constraint(
                    "ck_users_admin_role_consistent",
                    "(role = 'admin' AND is_superuser = true) OR "
                    "(role <> 'admin' AND is_superuser = false)",
                )

    index_names = {index["name"] for index in sa.inspect(bind).get_indexes("users")}
    if "uq_users_single_admin" not in index_names:
        op.create_index(
            "uq_users_single_admin",
            "users",
            ["role"],
            unique=True,
            postgresql_where=sa.text("role = 'admin'"),
            sqlite_where=sa.text("role = 'admin'"),
        )


def downgrade():
    bind = op.get_bind()
    index_names = {index["name"] for index in sa.inspect(bind).get_indexes("users")}
    if "uq_users_single_admin" in index_names:
        op.drop_index("uq_users_single_admin", table_name="users")
    check_names = {
        constraint["name"]
        for constraint in sa.inspect(bind).get_check_constraints("users")
        if constraint["name"]
    }
    with op.batch_alter_table("users") as batch:
        if "ck_users_admin_role_consistent" in check_names:
            batch.drop_constraint("ck_users_admin_role_consistent", type_="check")
        batch.alter_column("is_superuser", existing_type=sa.Boolean(), nullable=True)
