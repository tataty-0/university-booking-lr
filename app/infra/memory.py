"""In-memory adapters. Persistence adapters are introduced with the booking model."""

from datetime import datetime

from app.domain.intervals import overlaps
from app.domain.models import Booking, BookingStatus, Room

SEED_ROOMS = [
    Room(1, "A-101", 30),
    Room(2, "B-204", 60),
    Room(3, "Лабораторія L-12", 20),
    Room(4, "Центральна аудиторія", 120),
    Room(5, "Велика зала", 150),
]


class InMemoryRoomRepository:
    def __init__(self, rooms: list[Room] | None = None):
        self._rooms = {room.id: room for room in (rooms or SEED_ROOMS)}

    def list_all(self) -> list[Room]:
        return sorted(self._rooms.values(), key=lambda room: room.id)

    def get(self, room_id: int) -> Room | None:
        return self._rooms.get(room_id)


class InMemoryBookingRepository:
    def __init__(self, bookings: list[Booking] | None = None):
        self.bookings = bookings or []

    def find_conflicts(self, room_id: int, start: datetime, end: datetime) -> list[Booking]:
        return [
            b
            for b in self.bookings
            if b.room_id == room_id
            and b.status == BookingStatus.ACTIVE
            and overlaps(b.start, b.end, start, end)
        ]
