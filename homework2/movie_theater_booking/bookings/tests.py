from django.test import TestCase

from .models import Movie


class MovieModelTests(TestCase):
    def test_movie_str_and_ordering(self):
        older_movie = Movie.objects.create(
            title="Dune",
            description="A noble family becomes embroiled in a war.",
            release_date="2021-10-22",
            duration=155,
        )
        newer_movie = Movie.objects.create(
            title="Dune: Part Two",
            description="Paul Atreides unites with Chani and the Fremen.",
            release_date="2024-03-01",
            duration=166,
        )

        self.assertEqual(str(older_movie), "Dune")
        self.assertEqual(list(Movie.objects.all()), [newer_movie, older_movie])
