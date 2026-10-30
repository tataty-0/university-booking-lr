from datetime import datetime

from app.domain.errors import InvalidTransitionError, NotFoundError
from app.domain.intervals import validate_interval
from app.domain.models import Booking, BookingStatus, User
from app.domain.policies import (
    ensure_admin,
    ensure_cancellable,
    ensure_owner,
    ensure_transition,
    initial_status,
)
from app.services.ports import BookingRepository
from app.services.room_service import RoomService


class BookingService:
    def __init__(self, rooms: RoomService, bookings: BookingRepository):
        self._rooms = rooms
        self._bookings = bookings

    def create(self, user_id: int, room_id: int, start: datetime, end: datetime) -> Booking:
        start_utc, end_utc = validate_interval(start, end)
        room = self._rooms.get_room(room_id)
        return self._bookings.add_if_free(
            room_id, user_id, start_utc, end_utc, initial_status(room)
        )

    def get(self, user_id: int, booking_id: int) -> Booking:
        booking = self._bookings.get(booking_id)
        if booking is None:
            raise NotFoundError(f"booking {booking_id} not found")
        ensure_owner(booking, user_id)
        return booking

    def list_for_user(self, user_id: int) -> list[Booking]:
        return self._bookings.list_by_user(user_id)

    def cancel(self, user_id: int, booking_id: int) -> Booking:
        booking = self.get(user_id, booking_id)
        ensure_cancellable(booking)
        return self._bookings.set_status(booking_id, BookingStatus.CANCELLED)

    def list_pending(self, admin: User) -> list[Booking]:
        ensure_admin(admin)
        return self._bookings.list_by_status(BookingStatus.PENDING)

    def approve(self, admin: User, booking_id: int) -> Booking:
        return self._decide(admin, booking_id, BookingStatus.ACTIVE)

    def reject(self, admin: User, booking_id: int) -> Booking:
        return self._decide(admin, booking_id, BookingStatus.REJECTED)

    def _decide(self, admin: User, booking_id: int, target: BookingStatus) -> Booking:
        ensure_admin(admin)
        booking = self._bookings.get(booking_id)
        if booking is None:
            raise NotFoundError(f"booking {booking_id} not found")
        ensure_transition(booking, target)
        decided = self._bookings.decide(booking_id, admin.id, BookingStatus.PENDING, target)
        if decided is None:
            # another decision or a cancellation won the race
            raise InvalidTransitionError("booking is no longer pending")
        return decided
