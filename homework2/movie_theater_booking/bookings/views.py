from django.shortcuts import render
from rest_framework import viewsets

from .models import Movie
from .serializers import MovieSerializer


class MovieViewSet(viewsets.ModelViewSet):
    """Expose movie listings through the REST API."""

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


def movie_list(request):
    """Render all movies available for booking."""

    return render(
        request,
        "bookings/movie_list.html",
        {"movies": Movie.objects.all()},
    )
