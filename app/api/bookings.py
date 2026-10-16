from fastapi import APIRouter, Depends, Request

from app.api.deps import current_user_id
from app.api.schemas import BookingIn, BookingOut
from app.domain.models import Booking

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


def to_out(booking: Booking) -> BookingOut:
    return BookingOut(
        id=booking.id,
        room_id=booking.room_id,
        user_id=booking.user_id,
        start=booking.start,
        end=booking.end,
        status=booking.status.value,
    )


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingIn, request: Request, user_id: int = Depends(current_user_id)):
    booking = request.app.state.container.bookings.create(
        user_id, payload.room_id, payload.start, payload.end
    )
    return to_out(booking)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, request: Request, user_id: int = Depends(current_user_id)):
    return to_out(request.app.state.container.bookings.get(user_id, booking_id))
