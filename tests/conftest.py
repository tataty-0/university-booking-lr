from datetime import UTC, datetime

import pytest


@pytest.fixture
def at():
    """Build an aware UTC datetime on a fixed test day: at(9) or at(9, 30)."""

    def make(hour: int, minute: int = 0) -> datetime:
        return datetime(2026, 10, 20, hour, minute, tzinfo=UTC)

    return make
