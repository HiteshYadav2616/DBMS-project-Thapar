from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models import Booking, BookingSeat, BookingStatus, Bus, Route, Schedule, Seat, User
from app.schemas import (
    BusCreate,
    BusResponse,
    RouteCreate,
    RouteResponse,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleSearchResponse,
    SeatAvailability,
)

router = APIRouter(tags=["schedules", "admin catalog"])


@router.post("/admin/buses", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
def create_bus(
    payload: BusCreate,
    database: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Bus:
    bus = Bus(**payload.model_dump())
    database.add(bus)
    try:
        database.flush()
        database.add_all(
            [Seat(bus_id=bus.bus_id, seat_number=str(seat_number)) for seat_number in range(1, payload.total_seats + 1)]
        )
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A bus with this number already exists.") from error
    database.refresh(bus)
    return bus


@router.post("/admin/routes", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(
    payload: RouteCreate,
    database: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Route:
    route = Route(**payload.model_dump())
    database.add(route)
    database.commit()
    database.refresh(route)
    return route


@router.post("/admin/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    database: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Schedule:
    bus = database.get(Bus, payload.bus_id)
    route = database.get(Route, payload.route_id)
    if bus is None or route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bus or route was not found.")
    schedule = Schedule(**payload.model_dump())
    database.add(schedule)
    database.commit()
    database.refresh(schedule)
    return schedule


@router.get("/schedules", response_model=list[ScheduleSearchResponse])
def search_schedules(
    source: str = Query(min_length=1),
    destination: str = Query(min_length=1),
    travel_date: date | None = None,
    database: Session = Depends(get_db),
) -> list[ScheduleSearchResponse]:
    query = (
        select(
            Schedule,
            Route.source,
            Route.destination,
            Bus.bus_number,
            Bus.bus_type,
        )
        .join(Route, Schedule.route_id == Route.route_id)
        .join(Bus, Schedule.bus_id == Bus.bus_id)
        .where(
            Route.source == source,
            Route.destination == destination,
        )
    )
    if travel_date is not None:
        query = query.where(Schedule.travel_date == travel_date)
    rows = database.execute(query.order_by(Schedule.travel_date, Schedule.departure_time)).all()
    return [
        ScheduleSearchResponse(
            schedule_id=schedule.schedule_id,
            bus_id=schedule.bus_id,
            route_id=schedule.route_id,
            travel_date=schedule.travel_date,
            departure_time=schedule.departure_time,
            arrival_time=schedule.arrival_time,
            fare=schedule.fare,
            source=route_source,
            destination=route_destination,
            bus_number=bus_number,
            bus_type=bus_type,
        )
        for schedule, route_source, route_destination, bus_number, bus_type in rows
    ]


@router.get("/schedules/{schedule_id}/seats", response_model=list[SeatAvailability])
def get_seat_availability(schedule_id: int, database: Session = Depends(get_db)) -> list[SeatAvailability]:
    schedule = database.get(Schedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule was not found.")

    rows = database.execute(
        select(Seat.seat_id, Seat.seat_number)
        .join(Schedule, Schedule.bus_id == Seat.bus_id)
        .where(Schedule.schedule_id == schedule_id)
        .order_by(Seat.seat_id)
    ).all()
    occupied_seat_ids = set(
        database.scalars(
            select(BookingSeat.seat_id)
            .join(Booking, Booking.booking_id == BookingSeat.booking_id)
            .where(
                Booking.schedule_id == schedule_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            )
        ).all()
    )
    return [
        SeatAvailability(
            seat_id=seat_id,
            seat_number=seat_number,
            available=seat_id not in occupied_seat_ids,
        )
        for seat_id, seat_number in rows
    ]
