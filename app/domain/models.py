from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class BookingStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Room:
    id: int
    name: str
    capacity: int


class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


@dataclass(frozen=True)
class User:
    id: int
    name: str
    role: Role = Role.USER


@dataclass
class Booking:
    id: int | None
    room_id: int
    user_id: int
    start: datetime
    end: datetime
    status: BookingStatus
    created_at: datetime | None = None
    decided_by: int | None = None
    decided_at: datetime | None = None
