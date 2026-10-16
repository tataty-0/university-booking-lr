"""initial schema with demo rooms and users

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

ROOMS = [
    (1, "A-101", 30),
    (2, "B-204", 60),
    (3, "Лабораторія L-12", 20),
    (4, "Центральна аудиторія", 120),
    (5, "Велика зала", 150),
]
USERS = [(1, "alice"), (2, "bob"), (3, "carol")]


def upgrade() -> None:
    rooms = op.create_table(
        "rooms",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("capacity", sa.Integer, nullable=False),
    )
    users = op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("start_at", sa.DateTime, nullable=False),
        sa.Column("end_at", sa.DateTime, nullable=False),
        sa.Column("is_cancelled", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_bookings_room_interval", "bookings", ["room_id", "start_at", "end_at"])
    op.create_index("ix_bookings_user", "bookings", ["user_id"])
    op.bulk_insert(rooms, [{"id": i, "name": n, "capacity": c} for i, n, c in ROOMS])
    op.bulk_insert(users, [{"id": i, "name": n} for i, n in USERS])


def downgrade() -> None:
    op.drop_table("bookings")
    op.drop_table("users")
    op.drop_table("rooms")
