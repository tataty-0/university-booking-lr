from tests.conftest import ALICE, BOB


def slot(hour, room=1):
    return {
        "room_id": room,
        "start": f"2026-10-20T{hour:02d}:00:00Z",
        "end": f"2026-10-20T{hour + 1:02d}:00:00Z",
    }


def test_user_sees_only_own_bookings(client):
    client.post("/api/bookings", json=slot(9), headers=ALICE)
    client.post("/api/bookings", json=slot(11), headers=BOB)
    mine = client.get("/api/bookings/my", headers=ALICE).json()
    assert len(mine) == 1 and mine[0]["user_id"] == 1


def test_my_bookings_requires_authentication(client):
    assert client.get("/api/bookings/my").status_code == 401


def test_my_bookings_are_sorted_by_start(client):
    client.post("/api/bookings", json=slot(13), headers=ALICE)
    client.post("/api/bookings", json=slot(9), headers=ALICE)
    starts = [b["start"] for b in client.get("/api/bookings/my", headers=ALICE).json()]
    assert starts == sorted(starts)
