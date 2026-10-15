from dataclasses import dataclass
from datetime import datetime

from app.domain.intervals import validate_interval
from app.domain.models import Booking
from app.services.ports import BookingRepository
from app.services.room_service import RoomService


@dataclass
class Availability:
    room_id: int
    start: datetime
    end: datetime
    available: bool
    conflicts: list[Booking]


class AvailabilityService:
    def __init__(self, rooms: RoomService, bookings: BookingRepository):
        self._rooms = rooms
        self._bookings = bookings

    def check(self, room_id: int, start: datetime, end: datetime) -> Availability:
        self._rooms.get_room(room_id)
        start_utc, end_utc = validate_interval(start, end)
        conflicts = self._bookings.find_conflicts(room_id, start_utc, end_utc)
        return Availability(room_id, start_utc, end_utc, not conflicts, conflicts)
