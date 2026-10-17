from tests.conftest import ALICE


def test_create_view_cancel_flow(client):
    rooms = client.get("/api/rooms").json()
    room_id = rooms[0]["id"]
    window = {"start": "2026-10-21T08:00:00Z", "end": "2026-10-21T09:30:00Z"}

    assert client.get(f"/api/rooms/{room_id}/availability", params=window).json()["available"]
    created = client.post("/api/bookings", json={"room_id": room_id, **window}, headers=ALICE)
    assert created.status_code == 201

    listed = client.get("/api/bookings/my", headers=ALICE).json()
    assert [b["id"] for b in listed] == [created.json()["id"]]

    cancelled = client.post(f"/api/bookings/{created.json()['id']}/cancel", headers=ALICE)
    assert cancelled.json()["status"] == "CANCELLED"
    assert client.get(f"/api/rooms/{room_id}/availability", params=window).json()["available"]


def test_error_responses_have_uniform_shape(client):
    response = client.get("/api/bookings/my")
    assert set(response.json()["error"]) == {"code", "message"}
