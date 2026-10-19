"""Executable checks for the quality requirements QR-01..QR-03 (docs/requirements.md)."""

import statistics
import time

from tests.conftest import ALICE, BOB

SLOT = {"room_id": 1, "start": "2026-10-20T09:00:00Z", "end": "2026-10-20T10:00:00Z"}


def day_slot(day: int, room_id: int = 1) -> dict:
    return {
        "room_id": room_id,
        "start": f"2026-11-{day:02d}T09:00:00Z",
        "end": f"2026-11-{day:02d}T10:00:00Z",
    }


def test_qr01_foreign_cancellation_is_always_rejected(client):
    attempts, rejected = 20, 0
    for day in range(1, attempts + 1):
        booking_id = client.post("/api/bookings", json=day_slot(day), headers=ALICE).json()["id"]
        if client.post(f"/api/bookings/{booking_id}/cancel", headers=BOB).status_code == 403:
            rejected += 1
    assert rejected == attempts
    mine = client.get("/api/bookings/my", headers=ALICE).json()
    assert len(mine) == attempts and all(b["status"] == "ACTIVE" for b in mine)


def test_qr02_bookings_are_preserved_after_restart(db_path, make_client):
    first = make_client(db_path)
    ids = [
        first.post("/api/bookings", json=day_slot(day), headers=ALICE).json()["id"]
        for day in range(1, 11)
    ]
    restarted = make_client(db_path)
    stored = {b["id"] for b in restarted.get("/api/bookings/my", headers=ALICE).json()}
    assert stored == set(ids)


def test_qr03_booking_creation_p95_is_below_threshold(client):
    durations = []
    for index in range(200):
        day, hour = index // 20 + 1, index % 20 + 1
        slot = {
            "room_id": 2,
            "start": f"2027-01-{day:02d}T{hour:02d}:00:00Z",
            "end": f"2027-01-{day:02d}T{hour:02d}:30:00Z",
        }
        started = time.perf_counter()
        response = client.post("/api/bookings", json=slot, headers=ALICE)
        durations.append((time.perf_counter() - started) * 1000)
        assert response.status_code == 201
    p95 = statistics.quantiles(durations, n=20)[-1]
    print(f"QR-03 p95={p95:.1f} ms over {len(durations)} requests")
    assert p95 <= 200, f"p95 {p95:.1f} ms exceeds 200 ms"
