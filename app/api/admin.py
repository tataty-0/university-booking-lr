from fastapi import APIRouter, Depends, Request

from app.api.bookings import to_out
from app.api.deps import current_user
from app.api.schemas import BookingOut, PendingBookingOut
from app.domain.models import User

router = APIRouter(prefix="/api/admin/bookings", tags=["admin"])


@router.get("/pending", response_model=list[PendingBookingOut])
def pending(request: Request, admin: User = Depends(current_user)):
    container = request.app.state.container
    result = []
    for booking in container.bookings.list_pending(admin):
        room = container.rooms.get_room(booking.room_id)
        applicant = container.users.get(booking.user_id)
        result.append(
            PendingBookingOut(
                **to_out(booking).model_dump(),
                applicant=applicant.name if applicant else str(booking.user_id),
                room_name=room.name,
                room_capacity=room.capacity,
            )
        )
    return result


@router.post("/{booking_id}/approve", response_model=BookingOut)
def approve(booking_id: int, request: Request, admin: User = Depends(current_user)):
    return to_out(request.app.state.container.bookings.approve(admin, booking_id))


@router.post("/{booking_id}/reject", response_model=BookingOut)
def reject(booking_id: int, request: Request, admin: User = Depends(current_user)):
    return to_out(request.app.state.container.bookings.reject(admin, booking_id))
