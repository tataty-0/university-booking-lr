from tests.conftest import ALICE

SLOT = {"room_id": 1, "start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"}


def test_booking_survives_application_restart(db_path, make_client):
    first = make_client(db_path)
    booking_id = first.post("/api/bookings", json=SLOT, headers=ALICE).json()["id"]

    restarted = make_client(db_path)
    response = restarted.get(f"/api/bookings/{booking_id}", headers=ALICE)

    assert response.status_code == 200
    assert response.json()["start"].startswith("2026-10-20T09:00:00")
