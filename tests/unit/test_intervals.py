from datetime import datetime, timedelta, timezone

import pytest

from app.domain.errors import InvalidIntervalError
from app.domain.intervals import overlaps, validate_interval


def test_valid_interval_is_normalized_to_utc():
    kyiv = timezone(timedelta(hours=3))
    start, end = validate_interval(
        datetime(2026, 10, 20, 12, 0, tzinfo=kyiv), datetime(2026, 10, 20, 13, 0, tzinfo=kyiv)
    )
    assert start.hour == 9 and end.hour == 10
    assert start.utcoffset() == timedelta(0)


def test_start_after_end_is_rejected(at):
    with pytest.raises(InvalidIntervalError):
        validate_interval(at(11), at(10))


def test_empty_interval_is_rejected(at):
    with pytest.raises(InvalidIntervalError):
        validate_interval(at(10), at(10))


def test_naive_datetime_is_rejected():
    with pytest.raises(InvalidIntervalError):
        validate_interval(datetime(2026, 10, 20, 10), datetime(2026, 10, 20, 11))


def test_partial_overlap_is_detected(at):
    assert overlaps(at(9), at(11), at(10), at(12)) is True


def test_contained_interval_overlaps(at):
    assert overlaps(at(9), at(13), at(10), at(11)) is True


def test_distant_intervals_do_not_overlap(at):
    assert overlaps(at(8), at(9), at(10), at(11)) is False


def test_adjacent_intervals_overlap(at):
    assert overlaps(at(9), at(10), at(10), at(11)) is True
