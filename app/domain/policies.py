"""Booking business rules that do not depend on persistence or HTTP."""

from app.domain.errors import ForbiddenError, InvalidTransitionError
from app.domain.models import Booking, BookingStatus

SLOT_BLOCKING_STATUSES = frozenset({BookingStatus.ACTIVE})


def ensure_owner(booking: Booking, user_id: int) -> None:
    if booking.user_id != user_id:
        raise ForbiddenError("the booking belongs to another user")


def ensure_cancellable(booking: Booking) -> None:
    if booking.status != BookingStatus.ACTIVE:
        raise InvalidTransitionError(f"booking is already {booking.status.value}")
