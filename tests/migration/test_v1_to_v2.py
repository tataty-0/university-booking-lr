"""Migration of a database created by the released v1.0 schema to the v2.0 schema."""

import sqlite3

from app import migrations


def make_v1_database(path: str) -> None:
    migrations.upgrade(path, "0001")
    connection = sqlite3.connect(path)
    connection.executemany(
        "INSERT INTO bookings (id, room_id, user_id, start_at, end_at, is_cancelled, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (10, 1, 1, "2026-10-20 09:00:00", "2026-10-20 10:00:00", 0, "2026-10-01 08:00:00"),
            (11, 1, 2, "2026-10-20 10:00:00", "2026-10-20 11:00:00", 1, "2026-10-01 08:05:00"),
            (12, 4, 3, "2026-10-21 12:00:00", "2026-10-21 13:00:00", 0, "2026-10-01 08:10:00"),
        ],
    )
    connection.commit()
    connection.close()


def rows(path: str, sql: str):
    connection = sqlite3.connect(path)
    try:
        return connection.execute(sql).fetchall()
    finally:
        connection.close()


def test_existing_bookings_keep_identity_owner_and_interval(tmp_path):
    path = str(tmp_path / "v1.db")
    make_v1_database(path)
    before = rows(path, "SELECT id, room_id, user_id, start_at, end_at FROM bookings ORDER BY id")

    migrations.upgrade(path)

    after = rows(path, "SELECT id, room_id, user_id, start_at, end_at FROM bookings ORDER BY id")
    assert after == before


def test_cancelled_flag_is_converted_to_status(tmp_path):
    path = str(tmp_path / "v1.db")
    make_v1_database(path)
    migrations.upgrade(path)

    statuses = dict(rows(path, "SELECT id, status FROM bookings"))
    assert statuses == {10: "ACTIVE", 11: "CANCELLED", 12: "ACTIVE"}


def test_existing_large_room_booking_needs_no_retroactive_approval(tmp_path):
    path = str(tmp_path / "v1.db")
    make_v1_database(path)
    migrations.upgrade(path)

    (row,) = rows(path, "SELECT status, decided_by FROM bookings WHERE id = 12")
    assert row == ("ACTIVE", None)


def test_admin_user_is_added_and_existing_users_stay_regular(tmp_path):
    path = str(tmp_path / "v1.db")
    make_v1_database(path)
    migrations.upgrade(path)

    roles = dict(rows(path, "SELECT name, role FROM users"))
    assert roles["admin"] == "ADMIN"
    assert roles["alice"] == roles["bob"] == roles["carol"] == "USER"


def test_downgrade_restores_v1_schema_with_known_data_loss(tmp_path):
    path = str(tmp_path / "v1.db")
    make_v1_database(path)
    migrations.upgrade(path)
    connection = sqlite3.connect(path)
    connection.execute("UPDATE bookings SET status = 'REJECTED' WHERE id = 12")
    connection.commit()
    connection.close()

    migrations.upgrade(path, "0001") if False else None
    from alembic.config import Config

    from alembic import command

    cfg = Config(str(migrations.ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(migrations.ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{path}")
    command.downgrade(cfg, "0001")

    flags = dict(rows(path, "SELECT id, is_cancelled FROM bookings"))
    assert flags == {10: 0, 11: 1, 12: 1}
