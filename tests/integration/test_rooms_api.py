from fastapi.testclient import TestClient

from app.main import create_app


def client():
    return TestClient(create_app())


def test_list_rooms_returns_seeded_rooms():
    response = client().get("/api/rooms")
    assert response.status_code == 200
    names = [room["name"] for room in response.json()]
    assert "A-101" in names and len(names) == 5


def test_availability_of_free_room():
    response = client().get(
        "/api/rooms/1/availability",
        params={"start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"},
    )
    assert response.status_code == 200
    assert response.json()["available"] is True


def test_availability_rejects_invalid_interval():
    response = client().get(
        "/api/rooms/1/availability",
        params={"start": "2026-10-20T11:00:00Z", "end": "2026-10-20T10:00:00Z"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INTERVAL"


def test_availability_rejects_missing_timezone():
    response = client().get(
        "/api/rooms/1/availability",
        params={"start": "2026-10-20T09:00:00", "end": "2026-10-20T10:00:00"},
    )
    assert response.status_code == 422


def test_unknown_room_returns_404():
    response = client().get(
        "/api/rooms/99/availability",
        params={"start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
