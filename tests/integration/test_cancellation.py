from tests.conftest import ALICE, BOB

SLOT = {"room_id": 1, "start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"}


def create(client, headers=ALICE):
    return client.post("/api/bookings", json=SLOT, headers=headers).json()["id"]


def test_owner_can_cancel_booking(client):
    booking_id = create(client)
    response = client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_other_user_cannot_cancel_booking(client):
    booking_id = create(client)
    response = client.post(f"/api/bookings/{booking_id}/cancel", headers=BOB)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    still = client.get(f"/api/bookings/{booking_id}", headers=ALICE).json()
    assert still["status"] == "ACTIVE"


def test_cancelled_slot_can_be_booked_again(client):
    booking_id = create(client)
    client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE)
    assert client.post("/api/bookings", json=SLOT, headers=BOB).status_code == 201


def test_repeated_cancellation_is_rejected(client):
    booking_id = create(client)
    client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE)
    response = client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_TRANSITION"


def test_cancel_unknown_booking_returns_404(client):
    assert client.post("/api/bookings/999/cancel", headers=ALICE).status_code == 404
