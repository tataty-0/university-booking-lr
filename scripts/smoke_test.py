"""Smoke test of a running instance: python scripts/smoke_test.py http://127.0.0.1:8000"""

import json
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta


def call(base: str, method: str, path: str, user: int | None = None, body: dict | None = None):
    headers = {"Content-Type": "application/json"}
    if user is not None:
        headers["X-User-Id"] = str(user)
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read() or "{}")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or "{}")


def expect(condition: bool, label: str) -> None:
    print(("PASS " if condition else "FAIL ") + label)
    if not condition:
        sys.exit(1)


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
    status, health = call(base, "GET", "/health")
    expect(status == 200 and health.get("status") == "ok", f"health {health.get('version')}")

    status, rooms = call(base, "GET", "/api/rooms")
    expect(status == 200 and len(rooms) > 0, "rooms listed")
    room = next(r for r in rooms if r["capacity"] <= 100)

    # a far-future slot that differs between runs, so repeated smoke tests do not collide
    start = datetime.now(UTC).replace(second=0, microsecond=0) + timedelta(days=400)
    start += timedelta(minutes=int(datetime.now().timestamp()) % 100000)
    end = start + timedelta(hours=1)
    window = {"room_id": room["id"], "start": start.isoformat(), "end": end.isoformat()}
    status, created = call(base, "POST", "/api/bookings", 1, window)
    expect(status == 201 and created["status"] == "ACTIVE", "booking created")

    status, mine = call(base, "GET", "/api/bookings/my", 1)
    listed = any(b["id"] == created["id"] for b in mine)
    expect(status == 200 and listed, "booking listed in my bookings")

    status, _ = call(base, "POST", f"/api/bookings/{created['id']}/cancel", 2)
    expect(status == 403, "foreign cancellation rejected")

    status, cancelled = call(base, "POST", f"/api/bookings/{created['id']}/cancel", 1)
    expect(status == 200 and cancelled["status"] == "CANCELLED", "booking cancelled")
    print("smoke test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
