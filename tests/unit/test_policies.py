from datetime import UTC, datetime

import pytest

from app.domain.errors import ForbiddenError, InvalidTransitionError
from app.domain.models import Booking, BookingStatus
from app.domain.policies import ensure_cancellable, ensure_owner


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
