from tests.conftest import ALICE


def test_health_is_degraded_when_schema_is_missing(tmp_path, make_client):
    empty_database = str(tmp_path / "empty.db")  # exists as a file path but was never migrated
    client = make_client(empty_database)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["database"] == "unavailable"


def test_operations_keep_working_when_healthy(client):
    response = client.get("/api/bookings/my", headers=ALICE)
    assert response.status_code == 200
