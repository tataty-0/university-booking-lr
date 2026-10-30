from datetime import UTC, datetime

import pytest

from app.domain.errors import ForbiddenError, InvalidTransitionError
from app.domain.models import Booking, BookingStatus, Role, Room, User
from app.domain.policies import (
    ensure_admin,
    ensure_cancellable,
    ensure_owner,
    ensure_transition,
    initial_status,
)


def make(status=BookingStatus.ACTIVE, user_id=1):
    moment = datetime(2026, 10, 20, 9, tzinfo=UTC)
    return Booking(1, 1, user_id, moment, moment, status)


def test_owner_passes_ownership_check():
    ensure_owner(make(user_id=1), 1)


def test_other_user_is_forbidden():
    with pytest.raises(ForbiddenError):
        ensure_owner(make(user_id=1), 2)


def test_active_booking_is_cancellable():
    ensure_cancellable(make())


def test_cancelled_booking_cannot_be_cancelled_again():
    with pytest.raises(InvalidTransitionError):
        ensure_cancellable(make(BookingStatus.CANCELLED))


def test_pending_booking_is_cancellable():
    ensure_cancellable(make(BookingStatus.PENDING))


@pytest.mark.parametrize("status", [BookingStatus.REJECTED, BookingStatus.CANCELLED])
def test_final_states_have_no_transitions(status):
    for target in BookingStatus:
        with pytest.raises(InvalidTransitionError):
            ensure_transition(make(status), target)


def test_pending_can_be_approved_or_rejected():
    ensure_transition(make(BookingStatus.PENDING), BookingStatus.ACTIVE)
    ensure_transition(make(BookingStatus.PENDING), BookingStatus.REJECTED)


def test_active_cannot_be_approved_again():
    with pytest.raises(InvalidTransitionError):
        ensure_transition(make(BookingStatus.ACTIVE), BookingStatus.ACTIVE)


@pytest.mark.parametrize(
    ("capacity", "expected"),
    [(30, BookingStatus.ACTIVE), (100, BookingStatus.ACTIVE), (101, BookingStatus.PENDING)],
)
def test_approval_threshold_is_more_than_100_seats(capacity, expected):
    assert initial_status(Room(1, "R", capacity)) == expected


def test_only_admin_passes_admin_check():
    ensure_admin(User(4, "admin", Role.ADMIN))
    with pytest.raises(ForbiddenError):
        ensure_admin(User(1, "alice", Role.USER))
