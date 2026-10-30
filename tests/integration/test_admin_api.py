from tests.conftest import ADMIN, ALICE, BOB

LARGE_ROOM = 5
SMALL_ROOM = 1


def slot(room_id=LARGE_ROOM, start="09:00", end="10:00"):
    return {
        "room_id": room_id,
        "start": f"2026-10-20T{start}:00Z",
        "end": f"2026-10-20T{end}:00Z",
    }


def create_pending(client, **kwargs):
    return client.post("/api/bookings", json=slot(**kwargs), headers=ALICE).json()["id"]


def test_admin_sees_pending_requests_with_details(client):
    booking_id = create_pending(client)
    client.post("/api/bookings", json=slot(SMALL_ROOM), headers=ALICE)  # active, not listed

    response = client.get("/api/admin/bookings/pending", headers=ADMIN)

    assert response.status_code == 200
    (item,) = response.json()
    assert item["id"] == booking_id
    assert item["applicant"] == "alice" and item["room_name"] == "Велика зала"
    assert item["status"] == "PENDING"


def test_regular_user_cannot_list_or_decide(client):
    booking_id = create_pending(client)
    assert client.get("/api/admin/bookings/pending", headers=ALICE).status_code == 403
    approve = client.post(f"/api/admin/bookings/{booking_id}/approve", headers=ALICE)
    reject = client.post(f"/api/admin/bookings/{booking_id}/reject", headers=BOB)
    assert approve.status_code == 403 and reject.status_code == 403
    still = client.get(f"/api/bookings/{booking_id}", headers=ALICE).json()
    assert still["status"] == "PENDING" and still["decided_by"] is None


def test_approval_activates_booking_and_records_decision(client):
    booking_id = create_pending(client)
    response = client.post(f"/api/admin/bookings/{booking_id}/approve", headers=ADMIN)
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ACTIVE" and body["decided_by"] == 4 and body["decided_at"]


def test_rejection_releases_the_slot(client):
    booking_id = create_pending(client)
    rejected = client.post(f"/api/admin/bookings/{booking_id}/reject", headers=ADMIN)
    assert rejected.json()["status"] == "REJECTED"
    assert client.post("/api/bookings", json=slot(), headers=BOB).status_code == 201


def test_repeated_decisions_do_not_create_contradictory_state(client):
    booking_id = create_pending(client)
    first = client.post(f"/api/admin/bookings/{booking_id}/approve", headers=ADMIN)
    assert first.status_code == 200
    again = client.post(f"/api/admin/bookings/{booking_id}/approve", headers=ADMIN)
    opposite = client.post(f"/api/admin/bookings/{booking_id}/reject", headers=ADMIN)
    assert again.status_code == 409 and opposite.status_code == 409
    final = client.get(f"/api/bookings/{booking_id}", headers=ALICE).json()
    assert final["status"] == "ACTIVE"


def test_cannot_decide_a_cancelled_request(client):
    booking_id = create_pending(client)
    client.post(f"/api/bookings/{booking_id}/cancel", headers=ALICE)
    response = client.post(f"/api/admin/bookings/{booking_id}/approve", headers=ADMIN)
    assert response.status_code == 409


def test_active_booking_of_small_room_cannot_be_decided(client):
    booking_id = client.post("/api/bookings", json=slot(SMALL_ROOM), headers=ALICE).json()["id"]
    response = client.post(f"/api/admin/bookings/{booking_id}/reject", headers=ADMIN)
    assert response.status_code == 409


def test_unknown_booking_returns_404(client):
    assert client.post("/api/admin/bookings/999/approve", headers=ADMIN).status_code == 404
