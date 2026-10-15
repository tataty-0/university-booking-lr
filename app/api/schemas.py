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
