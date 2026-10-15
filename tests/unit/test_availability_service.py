import pytest

from app.domain.errors import InvalidIntervalError, NotFoundError
from app.domain.models import Booking, BookingStatus
from app.infra.memory import InMemoryBookingRepository, InMemoryRoomRepository
from app.services.availability_service import AvailabilityService
from app.services.room_service import RoomService


def make_service(bookings):
    rooms = RoomService(InMemoryRoomRepository())
    return AvailabilityService(rooms, InMemoryBookingRepository(bookings))


def booking(at, start, end, status=BookingStatus.ACTIVE, room_id=1):
    return Booking(1, room_id, 1, at(start), at(end), status)


def test_free_room_is_available(at):
    result = make_service([]).check(1, at(9), at(10))
    assert result.available is True and result.conflicts == []


def test_overlapping_booking_makes_room_unavailable(at):
    result = make_service([booking(at, 9, 11)]).check(1, at(10), at(12))
    assert result.available is False
    assert len(result.conflicts) == 1


def test_cancelled_booking_does_not_block(at):
    cancelled = booking(at, 9, 11, BookingStatus.CANCELLED)
    assert make_service([cancelled]).check(1, at(10), at(12)).available is True


def test_other_room_is_not_affected(at):
    assert make_service([booking(at, 9, 11, room_id=2)]).check(1, at(9), at(11)).available


def test_unknown_room_raises(at):
    with pytest.raises(NotFoundError):
        make_service([]).check(99, at(9), at(10))


def test_invalid_interval_raises(at):
    with pytest.raises(InvalidIntervalError):
        make_service([]).check(1, at(11), at(10))
