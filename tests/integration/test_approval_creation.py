from tests.conftest import ALICE, BOB

LARGE_ROOM = 5  # 150 seats
SMALL_ROOM = 1  # 30 seats


def slot(room_id, start="09:00", end="10:00"):
    return {
        "room_id": room_id,
        "start": f"2026-10-20T{start}:00Z",
        "end": f"2026-10-20T{end}:00Z",
    }


def test_large_room_booking_starts_pending(client):
    response = client.post("/api/bookings", json=slot(LARGE_ROOM), headers=ALICE)
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"


def test_small_room_booking_stays_active(client):
    response = client.post("/api/bookings", json=slot(SMALL_ROOM), headers=ALICE)
    assert response.json()["status"] == "ACTIVE"


def test_pending_booking_reserves_the_slot(client):
    client.post("/api/bookings", json=slot(LARGE_ROOM), headers=ALICE)
    response = client.post("/api/bookings", json=slot(LARGE_ROOM, "09:30", "10:30"), headers=BOB)
    assert response.status_code == 409


def test_applicant_can_cancel_pending_booking_and_release_slot(client):
    booking_id = client.post("/api/bookings", json=slot(LARGE_ROOM), headers=ALICE).json()["id"]
    cancelled = client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE)
    assert cancelled.json()["status"] == "CANCELLED"
    assert client.post("/api/bookings", json=slot(LARGE_ROOM), headers=BOB).status_code == 201
