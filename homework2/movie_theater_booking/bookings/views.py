from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Movie, Seat
from .serializers import (
    BookingSerializer,
    MovieSerializer,
    SeatBookingInputSerializer,
    SeatMovieFilterSerializer,
    SeatSerializer,
)
from .services import book_seat


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
        booking = book_seat(
            request.user,
            booking_input.validated_data["movie"],
            booking_input.validated_data["seat"],
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
