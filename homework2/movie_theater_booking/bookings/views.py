from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Booking, Movie, Seat
from .serializers import (
    BookingSerializer,
    MovieSerializer,
    SeatBookingInputSerializer,
    SeatMovieFilterSerializer,
    SeatSerializer,
)
from .services import SeatBookingError, book_seat


class MovieViewSet(viewsets.ModelViewSet):
    """Expose movie listings through the REST API."""

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """List seats, with optional availability for a validated movie."""

    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == "book":
            return [IsAuthenticated()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        movie_filter = SeatMovieFilterSerializer(data=request.query_params)
        movie_filter.is_valid(raise_exception=True)
        movie = movie_filter.validated_data.get("movie")
        context = self.get_serializer_context()
        if movie is not None:
            context["movie"] = movie
        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context=context,
        )
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="book")
    def book(self, request):
        booking_input = SeatBookingInputSerializer(data=request.data)
        booking_input.is_valid(raise_exception=True)
        try:
            booking = book_seat(
                request.user,
                booking_input.validated_data["movie"],
                booking_input.validated_data["seat"],
            )
        except SeatBookingError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )


def movie_list(request):
    """Render all movies available for booking."""

    return render(
        request,
        "bookings/movie_list.html",
        {"movies": Movie.objects.all()},
    )


@login_required
def book_seat_view(request, movie_id):
    """Render the authenticated seat-booking page."""

    movie = get_object_or_404(Movie, pk=movie_id)
    booking_error = None
    if request.method == "POST":
        seat = get_object_or_404(Seat, pk=request.POST.get("seat"))
        try:
            book_seat(request.user, movie, seat)
        except SeatBookingError as error:
            booking_error = str(error)
        else:
            messages.success(
                request,
                f"Seat {seat.seat_number} booked for {movie.title}.",
            )
            return redirect("book_seat", movie_id=movie.id)

    booked_seat_ids = set(
        Booking.objects.filter(movie=movie).values_list("seat_id", flat=True)
    )
    seat_options = [
        {
            "seat": seat,
            "available": not seat.booking_status and seat.id not in booked_seat_ids,
        }
        for seat in Seat.objects.all()
    ]
    return render(
        request,
        "bookings/seat_booking.html",
        {
            "movie": movie,
            "seat_options": seat_options,
            "booking_error": booking_error,
        },
    )
