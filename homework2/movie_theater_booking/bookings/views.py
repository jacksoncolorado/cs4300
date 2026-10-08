from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Movie, Seat
from .serializers import MovieSerializer, SeatMovieFilterSerializer, SeatSerializer


class MovieViewSet(viewsets.ModelViewSet):
    """Expose movie listings through the REST API."""

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """List seats, with optional availability for a validated movie."""

    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [AllowAny]

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


def movie_list(request):
    """Render all movies available for booking."""

    return render(
        request,
        "bookings/movie_list.html",
        {"movies": Movie.objects.all()},
    )
