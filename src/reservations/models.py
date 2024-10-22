from datetime import datetime

from sqlalchemy import func, ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ReservationSeat(Base):
    __tablename__ = "reservation_seat"

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id"), primary_key=True
    )
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), primary_key=True)


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    total_amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    showtime_id: Mapped[int] = mapped_column(
        ForeignKey("showtimes.id", ondelete="RESTRICT"), nullable=False
    )

    seats: Mapped[list["Seat"]] = relationship(
        secondary="ReservationSeat", back_populates="reservations"
    )
    user: Mapped["User"] = relationship(back_populates="reservations")
    showtime: Mapped["Showtime"] = relationship(back_populates="reservations")


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seat_code: Mapped[str] = mapped_column(String(10), unique=True)
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    cinema_hall_id: Mapped[int] = mapped_column(
        ForeignKey("cinema_halls.id", ondelete="RESTRICT"), nullable=False
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        secondary="ReservationSeat",
        back_populates="seats",
    )
    cinema_hall: Mapped["CinemaHall"] = relationship(back_populates="seats")
