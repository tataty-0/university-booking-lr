from datetime import datetime

from fastapi import APIRouter, Request

from app.api.schemas import AvailabilityOut, ConflictOut, RoomOut

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomOut])
def list_rooms(request: Request):
    rooms = request.app.state.container.rooms.list_rooms()
    return [RoomOut(id=r.id, name=r.name, capacity=r.capacity) for r in rooms]


@router.get("/{room_id}/availability", response_model=AvailabilityOut)
def availability(room_id: int, start: datetime, end: datetime, request: Request):
    result = request.app.state.container.availability.check(room_id, start, end)
    return AvailabilityOut(
        room_id=result.room_id,
        start=result.start,
        end=result.end,
        available=result.available,
        conflicts=[ConflictOut(id=b.id, start=b.start, end=b.end) for b in result.conflicts],
    )
