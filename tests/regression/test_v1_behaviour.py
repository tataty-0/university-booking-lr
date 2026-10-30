"""Regression safeguards for the released v1.0 behaviour.

These tests describe observable behaviour only, so they must keep passing
through refactoring and through the v2.0 changes for rooms up to 100 seats.
"""

import pytest

from tests.conftest import ALICE, BOB

SMALL_ROOM = 1


def booking(start: str, end: str, room_id: int = SMALL_ROOM) -> dict:
    return {
        "room_id": room_id,
        "start": f"2026-10-20T{start}:00Z",
        "end": f"2026-10-20T{end}:00Z",
    }


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        (("09:00", "10:00"), ("09:30", "10:30"), 409),  # partial overlap
        (("09:00", "11:00"), ("09:30", "10:00"), 409),  # containment
        (("09:00", "10:00"), ("09:00", "10:00"), 409),  # identical
        (("09:00", "10:00"), ("10:00", "11:00"), 201),  # adjacent after
        (("10:00", "11:00"), ("09:00", "10:00"), 201),  # adjacent before
        (("09:00", "10:00"), ("12:00", "13:00"), 201),  # distant
    ],
)
def test_interval_conflict_matrix(client, first, second, expected):
    assert client.post("/api/bookings", json=booking(*first), headers=ALICE).status_code == 201
    response = client.post("/api/bookings", json=booking(*second), headers=BOB)
    assert response.status_code == expected


@pytest.mark.parametrize(("start", "end"), [("10:00", "10:00"), ("11:00", "10:00")])
def test_invalid_intervals_are_rejected(client, start, end):
    response = client.post("/api/bookings", json=booking(start, end), headers=ALICE)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INTERVAL"


def test_small_room_booking_is_active_immediately(client):
    created = client.post("/api/bookings", json=booking("09:00", "10:00"), headers=ALICE).json()
    assert created["status"] == "ACTIVE"


def test_cancellation_rules(client):
    created = client.post("/api/bookings", json=booking("09:00", "10:00"), headers=ALICE)
    booking_id = created.json()["id"]
    assert client.post(f"/api/bookings/{booking_id}/cancel", headers=BOB).status_code == 403
    assert client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE).status_code == 200
    assert client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE).status_code == 409
    rebooked = client.post("/api/bookings", json=booking("09:00", "10:00"), headers=BOB)
    assert rebooked.status_code == 201


def test_error_codes_are_distinguishable(client):
    codes = {
        client.post("/api/bookings", json=booking("10:00", "09:00"), headers=ALICE).status_code,
        client.post("/api/bookings", json=booking("09:00", "10:00")).status_code,
        client.get("/api/bookings/999", headers=ALICE).status_code,
    }
    assert codes == {422, 401, 404}
