"""booking states, decision audit fields and user roles

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("role", sa.String(20), nullable=False, server_default="USER"))

    with op.batch_alter_table("bookings") as batch:
        batch.add_column(
            sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE")
        )
        batch.add_column(sa.Column("decided_by", sa.Integer))
        batch.add_column(sa.Column("decided_at", sa.DateTime))
        batch.create_foreign_key("fk_bookings_decided_by", "users", ["decided_by"], ["id"])

    op.execute("UPDATE bookings SET status = 'CANCELLED' WHERE is_cancelled = 1")

    with op.batch_alter_table("bookings") as batch:
        batch.drop_column("is_cancelled")
    op.create_index("ix_bookings_room_status", "bookings", ["room_id", "status", "start_at"])
    op.execute("INSERT INTO users (id, name, role) VALUES (4, 'admin', 'ADMIN')")


def downgrade() -> None:
    """Lossy rollback: PENDING becomes active, REJECTED becomes cancelled, decisions are dropped."""
    op.execute("UPDATE bookings SET decided_by = NULL")
    op.execute("DELETE FROM users WHERE role = 'ADMIN'")
    op.drop_index("ix_bookings_room_status", table_name="bookings")
    with op.batch_alter_table("bookings") as batch:
        batch.add_column(
            sa.Column("is_cancelled", sa.Boolean, nullable=False, server_default=sa.false())
        )
    op.execute("UPDATE bookings SET is_cancelled = 1 WHERE status IN ('CANCELLED', 'REJECTED')")
    with op.batch_alter_table("bookings") as batch:
        batch.drop_constraint("fk_bookings_decided_by", type_="foreignkey")
        batch.drop_column("decided_at")
        batch.drop_column("decided_by")
        batch.drop_column("status")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("role")
