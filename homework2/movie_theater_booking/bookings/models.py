from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Movie(models.Model):
    """A movie available for theater booking."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    release_date = models.DateField()
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["-release_date"]

    def __str__(self):
        return self.title


class Seat(models.Model):
    """A physical theater seat that may be available for booking."""

    seat_number = models.CharField(
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z][0-9]+$",
                message="Enter one uppercase letter followed by one or more digits.",
            )
        ],
    )
    booking_status = models.BooleanField(default=False)

    def __str__(self):
        return self.seat_number


class Booking(models.Model):
    """A user's reservation of one seat for one movie."""

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="bookings")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    booking_date = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "seat"],
                name="unique_movie_seat_booking",
            )
        ]
