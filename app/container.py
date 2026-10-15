from dataclasses import dataclass

from app.infra.memory import InMemoryBookingRepository, InMemoryRoomRepository
from app.services.availability_service import AvailabilityService
from app.services.room_service import RoomService


@dataclass
class Container:
    rooms: RoomService
    availability: AvailabilityService


def build_container() -> Container:
    room_repo = InMemoryRoomRepository()
    booking_repo = InMemoryBookingRepository()
    rooms = RoomService(room_repo)
    return Container(rooms=rooms, availability=AvailabilityService(rooms, booking_repo))
