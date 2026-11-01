import logging

from tests.conftest import ALICE, BOB

PAYLOAD = {"room_id": 1, "start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"}


def test_metrics_count_successful_and_rejected_operations(client):
    assert client.post("/api/bookings", json=PAYLOAD, headers=ALICE).status_code == 201
    assert client.post("/api/bookings", json=PAYLOAD, headers=BOB).status_code == 409
    stats = client.get("/metrics").json()["POST /api/bookings"]
    assert stats["ok"] == 1 and stats["rejected"] == 1 and stats["technical_error"] == 0
    assert stats["max_ms"] >= stats["avg_ms"] >= 0


def test_operation_is_grouped_by_route_template(client):
    client.get("/api/rooms", headers=ALICE)
    client.get("/api/bookings/my", headers=ALICE)
    operations = client.get("/metrics").json()
    assert "GET /api/rooms" in operations and "GET /api/bookings/my" in operations


def test_log_line_has_operation_outcome_duration_and_request_id(client, caplog):
    with caplog.at_level(logging.INFO, logger="booking.request"):
        response = client.get("/api/rooms", headers=ALICE)
    request_id = response.headers["X-Request-Id"]
    line = next(r.getMessage() for r in caplog.records if request_id in r.getMessage())
    assert "operation='GET /api/rooms'" in line and "outcome=ok" in line and "duration_ms=" in line
