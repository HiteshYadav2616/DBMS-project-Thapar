from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models import BookingStatus, PaymentStatus, UserRole


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=15)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    phone: str | None
    role: UserRole


class BusCreate(BaseModel):
    bus_number: str = Field(min_length=1, max_length=30)
    bus_type: str | None = Field(default=None, max_length=50)
    total_seats: int = Field(gt=0, le=300)


class BusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bus_id: int
    bus_number: str
    bus_type: str | None
    total_seats: int


class RouteCreate(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=100)
    distance: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)

    @model_validator(mode="after")
    def locations_must_differ(self) -> "RouteCreate":
        if self.source == self.destination:
            raise ValueError("source and destination must differ")
        return self


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    route_id: int
    source: str
    destination: str
    distance: Decimal | None


class ScheduleCreate(BaseModel):
    bus_id: int = Field(gt=0)
    route_id: int = Field(gt=0)
    travel_date: date
    departure_time: time
    arrival_time: time
    fare: Decimal = Field(ge=0, max_digits=10, decimal_places=2)

    @field_validator("departure_time", "arrival_time")
    @classmethod
    def schedule_times_are_utc_naive(cls, value: time) -> time:
        if value.tzinfo is not None:
            raise ValueError("schedule times must not include a timezone")
        return value


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: int
    bus_id: int
    route_id: int
    travel_date: date
    departure_time: time
    arrival_time: time
    fare: Decimal


class SeatAvailability(BaseModel):
    seat_id: int
    seat_number: str
    available: bool


class BookingCreate(BaseModel):
    schedule_id: int = Field(gt=0)
    seat_ids: list[int] = Field(min_length=1, max_length=300)

    @model_validator(mode="after")
    def seat_ids_must_be_unique(self) -> "BookingCreate":
        if len(set(self.seat_ids)) != len(self.seat_ids):
            raise ValueError("seat_ids must not contain duplicates")
        return self


class BookingSeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seat_id: int
    ticket_price: Decimal


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    amount: Decimal
    payment_method: str | None
    payment_status: PaymentStatus


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    user_id: int
    schedule_id: int
    booking_date: datetime
    status: BookingStatus
    total_amount: Decimal
    seats: list[BookingSeatResponse]
    payment: PaymentResponse


class BookingSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    schedule_id: int
    booking_date: datetime
    status: BookingStatus
    total_amount: Decimal


class ScheduleSearchResponse(ScheduleResponse):
    source: str
    destination: str
    bus_number: str
    bus_type: str | None
