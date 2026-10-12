from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    BigInteger,
    CHAR,
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class BusType(str, Enum):
    AC_SEATER = "ac_seater"
    NON_AC_SEATER = "non_ac_seater"
    AC_SLEEPER = "ac_sleeper"
    NON_AC_SLEEPER = "non_ac_sleeper"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


def enum_values(enum_type: type[Enum]) -> list[str]:
    return [item.value for item in enum_type]


BIGINT_ID = BigInteger().with_variant(Integer, "sqlite")


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="user_role", values_callable=enum_values),
        default=UserRole.USER,
        nullable=False,
    )


class Bus(Base):
    __tablename__ = "buses"
    __table_args__ = (CheckConstraint("total_seats > 0", name="ck_buses_total_seats_positive"),)

    bus_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    bus_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    operator_name: Mapped[str] = mapped_column(String(120), nullable=False)
    bus_type: Mapped[BusType] = mapped_column(
        SqlEnum(BusType, name="bus_type", values_callable=enum_values),
        nullable=False,
    )
    total_seats: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class Route(Base):
    __tablename__ = "routes"
    __table_args__ = (
        CheckConstraint("distance_km > 0", name="ck_routes_distance_positive"),
    )

    route_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    source_city: Mapped[str] = mapped_column(String(120), nullable=False)
    destination_city: Mapped[str] = mapped_column(String(120), nullable=False)
    distance_km: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        CheckConstraint("arrival_time > departure_time", name="ck_schedules_arrival_after_departure"),
        CheckConstraint("base_fare >= 0", name="ck_schedules_base_fare_nonnegative"),
    )

    schedule_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    bus_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("buses.bus_id"), nullable=False, index=True)
    route_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("routes.route_id"), nullable=False, index=True)
    departure_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    base_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("bus_id", "seat_number", name="uq_seats_bus_seat_number"),
    )

    seat_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    bus_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("buses.bus_id"), nullable=False, index=True)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)


class Booking(Base):
    __tablename__ = "bookings"

    booking_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    booking_reference: Mapped[str] = mapped_column(CHAR(12), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("users.user_id"), nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("schedules.schedule_id"), nullable=False, index=True)
    status: Mapped[BookingStatus] = mapped_column(
        SqlEnum(BookingStatus, name="booking_status", values_callable=enum_values),
        default=BookingStatus.PENDING,
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    seats: Mapped[list["BookingSeat"]] = relationship(back_populates="booking")
    payments: Mapped[list["Payment"]] = relationship(back_populates="booking")


class BookingSeat(Base):
    __tablename__ = "booking_seats"
    __table_args__ = (
        UniqueConstraint("booking_id", "seat_id", name="uq_booking_seats_booking_seat"),
        CheckConstraint("ticket_price >= 0", name="ck_booking_seats_ticket_price_nonnegative"),
    )

    booking_seat_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("bookings.booking_id"), nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("schedules.schedule_id"), nullable=False, index=True)
    seat_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("seats.seat_id"), nullable=False, index=True)
    ticket_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    booking: Mapped[Booking] = relationship(back_populates="seats")


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),)

    payment_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey("bookings.booking_id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SqlEnum(PaymentStatus, name="payment_status", values_callable=enum_values),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    booking: Mapped[Booking] = relationship(back_populates="payments")
