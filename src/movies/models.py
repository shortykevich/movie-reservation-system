from datetime import datetime

from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy import func, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.reservations.models import Reservation, Seat


class MovieGenre(Base):
    __tablename__ = "movie_genre"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), primary_key=True)


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    release_date: Mapped[datetime] = mapped_column(nullable=False)
    poster_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )

    genres: Mapped[list["Genre"]] = relationship(secondary="movie_genre", back_populates="movies")


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    movies: Mapped[list["Movie"]] = relationship(secondary="movie_genre", back_populates="genres")


class Showtime(Base):
    __tablename__ = 'showtimes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="RESTRICT"),
        nullable=False
    )
    cinema_hall_id: Mapped[int] = mapped_column(
        ForeignKey("cinema_halls.id", ondelete="RESTRICT"),
        nullable=False
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="showtime"
    )


class CinemaHall(Base):
    __tablename__ = "cinema_halls"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )

    showtimes: Mapped[list["Showtime"]] = relationship(
        back_populates="cinema_hall"
    )
    seats: Mapped[list["Seat"]] = relationship(
        back_populates="cinema_hall"
    )
