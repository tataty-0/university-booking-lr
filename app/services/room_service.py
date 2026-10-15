from app.domain.errors import NotFoundError
from app.domain.models import Room
from app.services.ports import RoomRepository


class RoomService:
    def __init__(self, rooms: RoomRepository):
        self._rooms = rooms

    def list_rooms(self) -> list[Room]:
        return self._rooms.list_all()

    def get_room(self, room_id: int) -> Room:
        room = self._rooms.get(room_id)
        if room is None:
            raise NotFoundError(f"room {room_id} not found")
        return room
