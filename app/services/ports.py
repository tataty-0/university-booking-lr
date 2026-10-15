"""Interfaces that application services depend on."""

from datetime import datetime
from typing import Protocol

from app.domain.models import Booking, Room


class RoomRepository(Protocol):
    def list_all(self) -> list[Room]: ...

    def get(self, room_id: int) -> Room | None: ...


class BookingRepository(Protocol):
    def find_conflicts(self, room_id: int, start: datetime, end: datetime) -> list[Booking]:
        """Active bookings of the room that overlap [start, end)."""
        ...
