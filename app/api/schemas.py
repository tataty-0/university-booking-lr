from datetime import datetime

from pydantic import BaseModel


class RoomOut(BaseModel):
    id: int
    name: str
    capacity: int


class ConflictOut(BaseModel):
    id: int
    start: datetime
    end: datetime


class AvailabilityOut(BaseModel):
    room_id: int
    start: datetime
    end: datetime
    available: bool
    conflicts: list[ConflictOut]


class BookingIn(BaseModel):
    room_id: int
    start: datetime
    end: datetime


class BookingOut(BaseModel):
    id: int
    room_id: int
    user_id: int
    start: datetime
    end: datetime
    status: str
