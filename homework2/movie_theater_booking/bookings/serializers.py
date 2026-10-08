from rest_framework import serializers

from .models import Booking, Movie, Seat


class MovieSerializer(serializers.ModelSerializer):
    """Translate Movie instances to and from API data."""

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_date", "duration"]


class SeatMovieFilterSerializer(serializers.Serializer):
    """Validate the optional movie used to calculate seat availability."""

    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        required=False,
    )


class SeatSerializer(serializers.ModelSerializer):
    """Serialize seats, optionally with availability for one movie."""

    available = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["id", "seat_number", "booking_status", "available"]

    def get_fields(self):
        fields = super().get_fields()
        if "movie" not in self.context:
            fields.pop("available")
        return fields

    def get_available(self, seat):
        movie = self.context["movie"]
        return not seat.booking_status and not Booking.objects.filter(
            movie=movie,
            seat=seat,
        ).exists()


class SeatBookingInputSerializer(serializers.Serializer):
    """Validate the movie and seat selected for a booking."""

    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all())
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())


class BookingSerializer(serializers.ModelSerializer):
    """Return a created booking without accepting ownership from clients."""

    class Meta:
        model = Booking
        fields = ["id", "movie", "seat", "user", "booking_date"]
        read_only_fields = fields
