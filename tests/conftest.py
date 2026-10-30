from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app import migrations
from app.config import Settings
from app.container import build_container
from app.main import create_app


@pytest.fixture
def at():
    """Build an aware UTC datetime on a fixed test day: at(9) or at(9, 30)."""

    def make(hour: int, minute: int = 0) -> datetime:
        return datetime(2026, 10, 20, hour, minute, tzinfo=UTC)

    return make


@pytest.fixture
def db_path(tmp_path) -> str:
    """An isolated real SQLite database migrated to the latest schema."""
    path = str(tmp_path / "test.db")
    migrations.upgrade(path)
    return path


@pytest.fixture
def make_client():
    def make(path: str) -> TestClient:
        return TestClient(create_app(build_container(Settings(db_path=path))))

    return make


@pytest.fixture
def client(db_path, make_client) -> TestClient:
    return make_client(db_path)


ALICE = {"X-User-Id": "1"}
BOB = {"X-User-Id": "2"}
CAROL = {"X-User-Id": "3"}
ADMIN = {"X-User-Id": "4"}
