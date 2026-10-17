"""Interfaces that application services depend on."""

from datetime import datetime
from typing import Protocol

from app.domain.models import Booking, BookingStatus, Room, User


class RoomRepository(Protocol):
    def list_all(self) -> list[Room]: ...

    def get(self, room_id: int) -> Room | None: ...


class UserRepository(Protocol):
    def get(self, user_id: int) -> User | None: ...


class BookingRepository(Protocol):
    def find_conflicts(self, room_id: int, start: datetime, end: datetime) -> list[Booking]:
        """Active bookings of the room that overlap [start, end)."""
        ...

    def add_if_free(
        self, room_id: int, user_id: int, start: datetime, end: datetime, status: BookingStatus
    ) -> Booking:
        """Store the booking or raise SlotConflictError if the interval is taken."""
        ...

    def get(self, booking_id: int) -> Booking | None: ...

    def list_by_user(self, user_id: int) -> list[Booking]: ...

    def set_status(self, booking_id: int, status: BookingStatus) -> Booking: ...
