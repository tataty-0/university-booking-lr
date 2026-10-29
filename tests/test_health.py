def test_health_reports_database_state(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok" and body["database"] == "ok"
    assert body["rooms"] == 5 and body["bookings"] == 0


def test_index_page_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Бронювання аудиторій" in response.text
