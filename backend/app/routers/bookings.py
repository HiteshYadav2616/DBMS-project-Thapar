import secrets
import string
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.dependencies import get_current_user, get_db
from app.models import (
    Booking,
    BookingSeat,
    BookingStatus,
    Payment,
    PaymentStatus,
    Schedule,
    Seat,
    User,
)
from app.schemas import BookingCreate, BookingResponse, BookingSeatResponse, BookingSummary, PaymentResponse

router = APIRouter(prefix="/bookings", tags=["bookings"])


def new_booking_reference() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(12))


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingResponse:
    schedule = database.scalar(
        select(Schedule).where(Schedule.schedule_id == payload.schedule_id).with_for_update()
    )
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule was not found.")
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if schedule.departure_time <= now_utc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This schedule has already departed.")

    seats = database.scalars(
        select(Seat).where(
            Seat.bus_id == schedule.bus_id,
            Seat.seat_id.in_(payload.seat_ids),
        )
    ).all()
    if len(seats) != len(payload.seat_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more seats do not belong to this bus.")

    occupied = set(
        database.scalars(
            select(BookingSeat.seat_id)
            .join(Booking, Booking.booking_id == BookingSeat.booking_id)
            .where(
                BookingSeat.schedule_id == schedule.schedule_id,
                BookingSeat.seat_id.in_(payload.seat_ids),
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            )
            .with_for_update()
        ).all()
    )
    if occupied:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "One or more seats are no longer available.", "seat_ids": sorted(occupied)},
        )

    total_amount = schedule.base_fare * len(seats)
    booking = Booking(
        booking_reference=new_booking_reference(),
        user_id=current_user.user_id,
        schedule_id=schedule.schedule_id,
        status=BookingStatus.CONFIRMED,
        total_amount=total_amount,
    )
    database.add(booking)
    database.flush()
    database.add_all(
        [
            BookingSeat(
                booking_id=booking.booking_id,
                schedule_id=schedule.schedule_id,
                seat_id=seat.seat_id,
                ticket_price=schedule.base_fare,
            )
            for seat in seats
        ]
    )
    database.add(
        Payment(
            booking_id=booking.booking_id,
            amount=total_amount,
            payment_status=PaymentStatus.SUCCESS,
        )
    )
    database.flush()
    booking_id = booking.booking_id
    database.commit()

    return _load_booking(database, booking_id, current_user.user_id)


@router.get("", response_model=list[BookingSummary])
def list_my_bookings(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Booking]:
    return list(
        database.scalars(
            select(Booking)
            .where(Booking.user_id == current_user.user_id)
            .order_by(Booking.booking_id.desc())
        ).all()
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingResponse:
    return _load_booking(database, booking_id, current_user.user_id)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingResponse:
    booking = database.scalar(
        select(Booking)
        .where(Booking.booking_id == booking_id, Booking.user_id == current_user.user_id)
        .with_for_update()
    )
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking was not found.")
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This booking has already been cancelled.")
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only confirmed bookings can be cancelled.")

    booking.status = BookingStatus.CANCELLED
    database.commit()
    return _load_booking(database, booking.booking_id, current_user.user_id)


def _load_booking(database: Session, booking_id: int, user_id: int) -> BookingResponse:
    booking = database.scalar(
        select(Booking)
        .options(selectinload(Booking.seats), selectinload(Booking.payments))
        .where(Booking.booking_id == booking_id, Booking.user_id == user_id)
    )
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking was not found.")
    if not booking.payments:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Booking payment record is missing.")
    return BookingResponse(
        booking_id=booking.booking_id,
        booking_reference=booking.booking_reference,
        user_id=booking.user_id,
        schedule_id=booking.schedule_id,
        status=booking.status,
        total_amount=booking.total_amount,
        seats=[
            BookingSeatResponse(seat_id=seat.seat_id, ticket_price=seat.ticket_price)
            for seat in sorted(booking.seats, key=lambda item: item.seat_id)
        ],
        payment=PaymentResponse.model_validate(booking.payments[0]),
    )
