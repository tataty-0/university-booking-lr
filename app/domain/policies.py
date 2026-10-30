"""Booking business rules that do not depend on persistence or HTTP."""

from app.domain.errors import ForbiddenError, InvalidTransitionError
from app.domain.models import Booking, BookingStatus, Role, Room, User

APPROVAL_CAPACITY_THRESHOLD = 100

# PENDING and ACTIVE reserve the slot; REJECTED and CANCELLED release it.
SLOT_BLOCKING_STATUSES = frozenset({BookingStatus.PENDING, BookingStatus.ACTIVE})

ALLOWED_TRANSITIONS: dict[BookingStatus, frozenset[BookingStatus]] = {
    BookingStatus.PENDING: frozenset(
        {BookingStatus.ACTIVE, BookingStatus.REJECTED, BookingStatus.CANCELLED}
    ),
    BookingStatus.ACTIVE: frozenset({BookingStatus.CANCELLED}),
    BookingStatus.REJECTED: frozenset(),
    BookingStatus.CANCELLED: frozenset(),
}


def initial_status(room: Room) -> BookingStatus:
    """Rooms with more than 100 seats require administrator approval."""
    if room.capacity > APPROVAL_CAPACITY_THRESHOLD:
        return BookingStatus.PENDING
    return BookingStatus.ACTIVE


def ensure_owner(booking: Booking, user_id: int) -> None:
    if booking.user_id != user_id:
        raise ForbiddenError("the booking belongs to another user")


def ensure_admin(user: User) -> None:
    if user.role != Role.ADMIN:
        raise ForbiddenError("administrator role is required")


def ensure_transition(booking: Booking, target: BookingStatus) -> None:
    if target not in ALLOWED_TRANSITIONS[booking.status]:
        raise InvalidTransitionError(
            f"booking is {booking.status.value}, cannot change to {target.value}"
        )


def ensure_cancellable(booking: Booking) -> None:
    ensure_transition(booking, BookingStatus.CANCELLED)
