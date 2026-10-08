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
