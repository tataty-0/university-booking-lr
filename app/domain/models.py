from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class BookingStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Room:
    id: int
    name: str
    capacity: int


@dataclass(frozen=True)
class User:
    id: int
    name: str


@dataclass
class Booking:
    id: int | None
    room_id: int
    user_id: int
    start: datetime
    end: datetime
    status: BookingStatus
    created_at: datetime | None = None
