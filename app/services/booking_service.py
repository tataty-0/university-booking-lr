from datetime import datetime

from app.domain.errors import NotFoundError
from app.domain.intervals import validate_interval
from app.domain.models import Booking, BookingStatus
from app.domain.policies import ensure_cancellable, ensure_owner
from app.services.ports import BookingRepository
from app.services.room_service import RoomService


class BookingService:
    def __init__(self, rooms: RoomService, bookings: BookingRepository):
        self._rooms = rooms
        self._bookings = bookings

    def create(self, user_id: int, room_id: int, start: datetime, end: datetime) -> Booking:
        start_utc, end_utc = validate_interval(start, end)
        self._rooms.get_room(room_id)
        return self._bookings.add_if_free(
            room_id, user_id, start_utc, end_utc, BookingStatus.ACTIVE
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
