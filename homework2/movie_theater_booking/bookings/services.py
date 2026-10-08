from django.db import IntegrityError, transaction

from .models import Booking, Seat


class SeatBookingError(Exception):
    """A booking failure that can be shown safely to a user or API client."""


def book_seat(user, movie, seat):
    """Book one available seat while preserving database-level uniqueness."""

    taken_message = f"Seat {seat.seat_number} is already booked for {movie.title}."

    try:
        with transaction.atomic():
            locked_seat = Seat.objects.select_for_update().get(pk=seat.pk)
            if locked_seat.booking_status:
                raise SeatBookingError(
                    f"Seat {locked_seat.seat_number} is out of service."
                )
            if Booking.objects.filter(movie=movie, seat=locked_seat).exists():
                raise SeatBookingError(taken_message)
            return Booking.objects.create(
                user=user,
                movie=movie,
                seat=locked_seat,
            )
    except IntegrityError as error:
        raise SeatBookingError(taken_message) from error
