from tests.conftest import ALICE, BOB

SLOT = {"room_id": 1, "start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"}


def test_create_booking_returns_active_booking(client):
    response = client.post("/api/bookings", json=SLOT, headers=ALICE)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ACTIVE" and body["user_id"] == 1


def test_booking_requires_user_header(client):
    assert client.post("/api/bookings", json=SLOT).status_code == 401


def test_invalid_interval_is_rejected(client):
    payload = {**SLOT, "start": "2026-10-20T10:00:00Z", "end": "2026-10-20T09:00:00Z"}
    response = client.post("/api/bookings", json=payload, headers=ALICE)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INTERVAL"


def test_overlapping_booking_is_rejected(client):
    client.post("/api/bookings", json=SLOT, headers=ALICE)
    overlapping = {**SLOT, "start": "2026-10-20T09:30:00Z", "end": "2026-10-20T10:30:00Z"}
    response = client.post("/api/bookings", json=overlapping, headers=BOB)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SLOT_CONFLICT"


def test_adjacent_booking_is_accepted(client):
    client.post("/api/bookings", json=SLOT, headers=ALICE)
    adjacent = {**SLOT, "start": "2026-10-20T10:00:00Z", "end": "2026-10-20T11:00:00Z"}
    assert client.post("/api/bookings", json=adjacent, headers=BOB).status_code == 201


def test_other_room_is_independent(client):
    client.post("/api/bookings", json=SLOT, headers=ALICE)
    other = {**SLOT, "room_id": 2}
    assert client.post("/api/bookings", json=other, headers=BOB).status_code == 201


def test_unknown_room_returns_404(client):
    response = client.post("/api/bookings", json={**SLOT, "room_id": 99}, headers=ALICE)
    assert response.status_code == 404


def test_booking_is_visible_to_owner_only(client):
    booking_id = client.post("/api/bookings", json=SLOT, headers=ALICE).json()["id"]
    assert client.get(f"/api/bookings/{booking_id}", headers=ALICE).status_code == 200
    assert client.get(f"/api/bookings/{booking_id}", headers=BOB).status_code == 403


def test_availability_reflects_created_booking(client):
    client.post("/api/bookings", json=SLOT, headers=ALICE)
    response = client.get(
        "/api/rooms/1/availability",
        params={"start": "2026-10-20T09:30:00Z", "end": "2026-10-20T10:30:00Z"},
    )
    assert response.json()["available"] is False
