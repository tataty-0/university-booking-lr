from dataclasses import dataclass

from app.config import Settings
from app.db import make_engine, make_session_factory
from app.infra.sql import (
    SqlBookingRepository,
    SqlHealthCheck,
    SqlRoomRepository,
    SqlUserRepository,
)
from app.services.availability_service import AvailabilityService
from app.services.booking_service import BookingService
from app.services.ports import UserRepository
from app.services.room_service import RoomService


@dataclass
class Container:
    rooms: RoomService
    availability: AvailabilityService
    bookings: BookingService
    users: UserRepository
    health: SqlHealthCheck
    db_path: str = ""


def build_container(settings: Settings | None = None) -> Container:
    settings = settings or Settings.from_env()
    settings.validate()
    sessions = make_session_factory(make_engine(settings.db_path))
    rooms = RoomService(SqlRoomRepository(sessions))
    booking_repo = SqlBookingRepository(sessions)
    return Container(
        rooms=rooms,
        availability=AvailabilityService(rooms, booking_repo),
        bookings=BookingService(rooms, booking_repo),
        users=SqlUserRepository(sessions),
        health=SqlHealthCheck(sessions),
        db_path=settings.db_path,
    )
