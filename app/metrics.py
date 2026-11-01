"""In-process operation metrics: counts of successful and failed operations and their duration."""

from collections import defaultdict
from threading import Lock


def outcome_for(status: int) -> str:
    if status >= 500:
        return "technical_error"
    if status >= 400:
        return "rejected"
    return "ok"


class OperationMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._data: dict[str, dict[str, float]] = defaultdict(
            lambda: {"ok": 0, "rejected": 0, "technical_error": 0, "total_ms": 0.0, "max_ms": 0.0}
        )

    def record(self, operation: str, status: int, duration_ms: float) -> None:
        with self._lock:
            item = self._data[operation]
            item[outcome_for(status)] += 1
            item["total_ms"] += duration_ms
            item["max_ms"] = max(item["max_ms"], duration_ms)

    def snapshot(self) -> dict[str, dict[str, float]]:
        with self._lock:
            result = {}
            for operation, item in sorted(self._data.items()):
                count = item["ok"] + item["rejected"] + item["technical_error"]
                result[operation] = {
                    "ok": int(item["ok"]),
                    "rejected": int(item["rejected"]),
                    "technical_error": int(item["technical_error"]),
                    "avg_ms": round(item["total_ms"] / count, 2),
                    "max_ms": round(item["max_ms"], 2),
                }
            return result
