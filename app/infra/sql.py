"""SQLAlchemy adapters. Datetimes are stored as naive UTC."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.errors import SlotConflictError
from app.domain.models import Booking, BookingStatus, Room, User
from app.infra.tables import BookingRow, RoomRow, UserRow


def _naive(value: datetime) -> datetime:
    return value.astimezone(UTC).replace(tzinfo=None)


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC)


def _booking(row: BookingRow) -> Booking:
    status = BookingStatus.CANCELLED if row.is_cancelled else BookingStatus.ACTIVE
    return Booking(
        id=row.id,
        room_id=row.room_id,
        user_id=row.user_id,
        start=_aware(row.start_at),
        end=_aware(row.end_at),
        status=status,
        created_at=_aware(row.created_at),
    )


class SqlRoomRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self._sessions = sessions

    def list_all(self) -> list[Room]:
        with self._sessions() as session:
            rows = session.scalars(select(RoomRow).order_by(RoomRow.id))
            return [Room(r.id, r.name, r.capacity) for r in rows]

    def get(self, room_id: int) -> Room | None:
        with self._sessions() as session:
            row = session.get(RoomRow, room_id)
            return Room(row.id, row.name, row.capacity) if row else None


class SqlUserRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self._sessions = sessions

    def get(self, user_id: int) -> User | None:
        with self._sessions() as session:
            row = session.get(UserRow, user_id)
            return User(row.id, row.name) if row else None


class SqlBookingRepository:
    def __init__(self, sessions: sessionmaker[Session]):
        self._sessions = sessions

    @staticmethod
    def _conflict_query(room_id: int, start: datetime, end: datetime):
        return select(BookingRow).where(
            BookingRow.room_id == room_id,
            BookingRow.is_cancelled.is_(False),
            BookingRow.start_at < _naive(end),
            BookingRow.end_at > _naive(start),
        )

    def find_conflicts(self, room_id: int, start: datetime, end: datetime) -> list[Booking]:
        with self._sessions() as session:
            rows = session.scalars(self._conflict_query(room_id, start, end))
            return [_booking(r) for r in rows]

    def add_if_free(
        self, room_id: int, user_id: int, start: datetime, end: datetime, status: BookingStatus
    ) -> Booking:
        with self._sessions() as session:
            if session.scalars(self._conflict_query(room_id, start, end)).first():
                raise SlotConflictError("the room is already booked for this interval")
            row = BookingRow(
                room_id=room_id,
                user_id=user_id,
                start_at=_naive(start),
                end_at=_naive(end),
                is_cancelled=status == BookingStatus.CANCELLED,
                created_at=_naive(datetime.now(UTC)),
            )
            session.add(row)
            session.commit()
            return _booking(row)

    def get(self, booking_id: int) -> Booking | None:
        with self._sessions() as session:
            row = session.get(BookingRow, booking_id)
            return _booking(row) if row else None
