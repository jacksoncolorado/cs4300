from rest_framework import serializers

from .models import Movie


class MovieSerializer(serializers.ModelSerializer):
    """Translate Movie instances to and from API data."""

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_date", "duration"]
