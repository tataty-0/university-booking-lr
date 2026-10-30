from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

from sqlalchemy import text

from app.config import Settings
from app.container import build_container
from app.db import make_engine
from app.domain.errors import SlotConflictError

START = datetime(2026, 10, 20, 9, tzinfo=UTC)
END = datetime(2026, 10, 20, 10, tzinfo=UTC)


def test_parallel_requests_create_only_one_active_booking(db_path):
    container = build_container(Settings(db_path=db_path))

    def attempt(user_id: int) -> str:
        try:
            container.bookings.create(user_id, 1, START, END)
            return "created"
        except SlotConflictError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(attempt, [1, 2, 3] * 8))

    assert results.count("created") == 1
    assert results.count("conflict") == 23

    with make_engine(db_path).connect() as connection:
        active = connection.execute(
            text("SELECT COUNT(*) FROM bookings WHERE room_id = 1 AND status = 'ACTIVE'")
        ).scalar_one()
    assert active == 1
