from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models import BookingStatus, BusType, PaymentStatus, UserRole


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
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
    full_name: str
    email: EmailStr
    role: UserRole


class BusCreate(BaseModel):
    bus_number: str = Field(min_length=1, max_length=30)
    operator_name: str = Field(min_length=1, max_length=120)
    bus_type: BusType
    total_seats: int = Field(gt=0, le=300)


class BusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bus_id: int
    bus_number: str
    operator_name: str
    bus_type: BusType
    total_seats: int


class RouteCreate(BaseModel):
    source_city: str = Field(min_length=1, max_length=120)
    destination_city: str = Field(min_length=1, max_length=120)
    distance_km: Decimal = Field(gt=0, max_digits=8, decimal_places=2)


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    route_id: int
    source_city: str
    destination_city: str
    distance_km: Decimal


class ScheduleCreate(BaseModel):
    bus_id: int = Field(gt=0)
    route_id: int = Field(gt=0)
    departure_time: datetime
    arrival_time: datetime
    base_fare: Decimal = Field(ge=0, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def arrival_after_departure(self) -> "ScheduleCreate":
        if self.departure_time.tzinfo is not None:
            self.departure_time = self.departure_time.astimezone(timezone.utc).replace(tzinfo=None)
        if self.arrival_time.tzinfo is not None:
            self.arrival_time = self.arrival_time.astimezone(timezone.utc).replace(tzinfo=None)
        if self.arrival_time <= self.departure_time:
            raise ValueError("arrival_time must be after departure_time")
        return self


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: int
    bus_id: int
    route_id: int
    departure_time: datetime
    arrival_time: datetime
    base_fare: Decimal


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
    payment_status: PaymentStatus


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    booking_reference: str
    user_id: int
    schedule_id: int
    status: BookingStatus
    total_amount: Decimal
    seats: list[BookingSeatResponse]
    payment: PaymentResponse


class BookingSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_id: int
    booking_reference: str
    schedule_id: int
    status: BookingStatus
    total_amount: Decimal


class ScheduleSearchResponse(ScheduleResponse):
    source_city: str
    destination_city: str
    bus_number: str
    operator_name: str
    bus_type: BusType
