from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from tests.conftest import ALICE


class BrokenBookings:
    def create(self, *args):
        raise OperationalError("INSERT", {}, Exception("unable to open database file"))


def test_database_failure_is_reported_as_technical_error(client):
    client.app.state.container.bookings = BrokenBookings()
    payload = {"room_id": 1, "start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"}
    response = TestClient(client.app, raise_server_exceptions=False).post(
        "/api/bookings", json=payload, headers=ALICE
    )
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"

