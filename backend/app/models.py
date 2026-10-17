from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class BookingStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


class PaymentStatus(str, Enum):
    PENDING = "Pending"
    SUCCESSFUL = "Successful"
    FAILED = "Failed"
    REFUNDED = "Refunded"


def enum_values(enum_type: type[Enum]) -> list[str]:
    return [item.value for item in enum_type]


def varchar_enum(enum_type: type[Enum], name: str, length: int) -> SqlEnum:
    return SqlEnum(
        enum_type,
        name=name,
        values_callable=enum_values,
        native_enum=False,
        create_constraint=False,
        length=length,
    )


class User(Base):
    __tablename__ = "Users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(15))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        varchar_enum(UserRole, "user_role", 20),
        default=UserRole.USER,
        server_default=UserRole.USER.value,
        nullable=False,
    )


class Bus(Base):
    __tablename__ = "Buses"

    bus_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bus_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    bus_type: Mapped[str | None] = mapped_column(String(50))
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)


class Route(Base):
    __tablename__ = "Routes"
    __table_args__ = (
        CheckConstraint("distance IS NULL OR distance >= 0", name="ck_routes_distance_nonnegative"),
        CheckConstraint("source <> destination", name="ck_routes_source_destination_different"),
    )

    route_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)
    distance: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))


class Schedule(Base):
    __tablename__ = "Schedules"
    __table_args__ = (CheckConstraint("fare >= 0", name="ck_schedules_fare_nonnegative"),)

    schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bus_id: Mapped[int] = mapped_column(Integer, ForeignKey("Buses.bus_id"), nullable=False)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("Routes.route_id"), nullable=False)
    travel_date: Mapped[date] = mapped_column(Date, nullable=False)
    departure_time: Mapped[time] = mapped_column(Time, nullable=False)
    arrival_time: Mapped[time] = mapped_column(Time, nullable=False)
    fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class Seat(Base):
    __tablename__ = "Seats"
    __table_args__ = (UniqueConstraint("bus_id", "seat_number", name="uq_seats_bus_seat_number"),)

    seat_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bus_id: Mapped[int] = mapped_column(Integer, ForeignKey("Buses.bus_id"), nullable=False)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)


class Booking(Base):
    __tablename__ = "Bookings"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_bookings_total_amount_nonnegative"),
        CheckConstraint(
            "status IN ('Pending', 'Confirmed', 'Cancelled')",
            name="ck_bookings_status",
        ),
    )

    booking_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.user_id"), nullable=False)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("Schedules.schedule_id"), nullable=False)
    booking_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
    )
    status: Mapped[BookingStatus] = mapped_column(
        varchar_enum(BookingStatus, "booking_status", 20),
        default=BookingStatus.PENDING,
        server_default=BookingStatus.PENDING.value,
        nullable=False,
    )
    seats: Mapped[list["BookingSeat"]] = relationship(back_populates="booking")
    payments: Mapped[list["Payment"]] = relationship(back_populates="booking")


class BookingSeat(Base):
    __tablename__ = "Booking_Seats"
    __table_args__ = (
        CheckConstraint("ticket_price >= 0", name="ck_booking_seats_ticket_price_nonnegative"),
    )

    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Bookings.booking_id"),
        primary_key=True,
    )
    seat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Seats.seat_id"),
        primary_key=True,
    )
    ticket_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    booking: Mapped[Booking] = relationship(back_populates="seats")


class Payment(Base):
    __tablename__ = "Payments"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),
        CheckConstraint(
            "payment_status IN ('Pending', 'Successful', 'Failed', 'Refunded')",
            name="ck_payments_status",
        ),
    )

    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(Integer, ForeignKey("Bookings.booking_id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(30))
    payment_status: Mapped[PaymentStatus] = mapped_column(
        varchar_enum(PaymentStatus, "payment_status", 20),
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
        nullable=False,
    )
    booking: Mapped[Booking] = relationship(back_populates="payments")
