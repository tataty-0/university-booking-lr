"""Time interval rules.

Intervals are half-open: [start, end). Two intervals that share only an endpoint
are adjacent and do not overlap.
"""

from datetime import UTC, datetime

from app.domain.errors import InvalidIntervalError


def to_utc(value: datetime) -> datetime:
    """Convert an aware datetime to UTC. Naive values are rejected."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidIntervalError("datetime must include a timezone offset")
    return value.astimezone(UTC)


def validate_interval(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """Return the interval normalized to UTC or raise InvalidIntervalError."""
    start_utc, end_utc = to_utc(start), to_utc(end)
    if start_utc >= end_utc:
        raise InvalidIntervalError("start must be earlier than end")
    return start_utc, end_utc


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end
