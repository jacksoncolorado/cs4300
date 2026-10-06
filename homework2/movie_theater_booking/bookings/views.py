from rest_framework import viewsets

from .models import Movie
from .serializers import MovieSerializer


class MovieViewSet(viewsets.ModelViewSet):
    """Expose movie listings through the REST API."""

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
